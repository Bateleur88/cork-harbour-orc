#!/usr/bin/env python3
"""Build a parallel TEST copy of the race officer page and marks.php, for /course-test/ and /marks-test/.

    python scripts/build_test.py [--page pages/course/course_v8.html] [--sw pages/course/sw.js] [--marks pages/marks/marks.php]
                                 [--out build/test]

Writes, and nothing else:
    OUT/course-test/index.html   the RO page, talking only to /marks-test/ and keeping its own browser data
    OUT/course-test/sw.js        the page's service worker (STATUS A65), keeping /marks-test/key.js instead of /marks/key.js
    OUT/marks-test/marks.php     an unchanged copy of marks.php (it keeps its data next to itself, in /marks-test/data/)
    OUT/BUILD.txt                source commit, where each file came from (A28), PAGE_VERSION and SHA-256 of each file

The test page differs from the live one in exactly these lines, each of which must occur exactly once:
    <script src="/marks/key.js">        -> /marks-test/key.js
    const MARKS_BASE='/marks/', STORE='' -> '/marks-test/', 'test-'   (every browser storage key gets "test-")
    const PAGE_VERSION='X'              -> 'X-test'
    <title>                             -> "TEST – " in front
plus a noindex meta tag and a red "TEST COPY" banner showing the PAGE_VERSION at the top of the page.
The test worker differs from the live one in exactly one line, its key.js (/marks/key.js -> /marks-test/key.js). It takes
its folder (/course-test/) and version from its own address, so its caches ("coursepage|/course-test/|<version>") never
share a name with the live worker's ("coursepage|/course/|<version>").

Refuses, and writes nothing, if:
    - a line to be replaced is missing or occurs more than once (the page changed: update this script);
    - any mention of localStorage or sessionStorage in the page (live source or test result), outside comments, is not
      a direct getItem, setItem or removeItem whose key is STORE+... or a name defined as STORE+... (a key the test copy
      would share with live), or the page uses IndexedDB, cookies, the Cache API or a service worker other than the one
      registration SW_REGISTER, at most once. This is a guard, not proof: the runtime key listing in the test browser
      stays mandatory for every build (see storage_problems);
    - the test page still contains "/marks" anywhere other than "/marks-test/" (it could reach live data);
    - the banner, the TEST title or the noindex tag is missing from the result;
    - the copied marks.php is not byte-identical to its source;
    - the worker's key.js line is missing or doubled, the live worker names /marks/ anywhere but that line, the test
      worker still contains "/marks" anywhere other than "/marks-test/", or either worker's code names a "record-" cache
      (the RIB worker deletes those, STATUS A18), names its cache other than "coursepage|"+folder+"|"+version, cleans up
      other than its own folder, or keeps a page that is not its own version (worker_problems).
The keys are never part of the build: key.js and data/ro-key.php are placed on the server by hand (see the README).
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_BASE, TEST_STORE = '/marks-test/', 'test-'
WORD = re.compile(r'\b(localStorage|sessionStorage)\b')
CALL = re.compile(r'(localStorage|sessionStorage)\.(getItem|setItem|removeItem)\(\s*([^,)]*)')
# browser storage the page must not use at all until a later commit gives it a prefixed form and updates this check
FORBIDDEN = {'indexedDB': r'\bindexedDB\b', 'cookies': r'\bcookie\b', 'the Cache API': r'\bcaches\b',
             'a service worker': r'\bserviceWorker\b'}
# the one service worker registration the page may hold (STATUS A65), at most once: relative, so the test copy registers
# /course-test/sw.js, with its own version, and only from the folder or index.html (a page opened as /course with no
# trailing slash would otherwise register /sw.js with the whole site as its scope)
SW_REGISTER = ("if('serviceWorker' in navigator&&(location.pathname.endsWith('/')||location.pathname.endsWith('/index.html')))"
               "navigator.serviceWorker.register('sw.js?v='+encodeURIComponent(PAGE_VERSION),{scope:'./'}).catch(()=>{});")
# the worker's key.js line, live and test, and the lines every worker must hold once (STATUS A65)
SW_KEY_LIVE = "const KEY=new URL('/marks/key.js',location.href).href;"
SW_KEY_TEST = f"const KEY=new URL('{TEST_BASE}key.js',location.href).href;"
SW_NEED = ("const CACHE='coursepage|'+PAGE_PATH+'|'+VERSION;",
           "const ownCache=k=>{const p=k.split('|');return p.length===3&&p[0]==='coursepage'&&p[1]===PAGE_PATH;};",
           "return !!m&&m[1]===VERSION;")


class Refused(Exception):
    pass


def strip_comments(html):
    """The page with its comments blanked (HTML <!-- -->, CSS and JavaScript /* */ and //), strings and regex literals
    kept, so a word in a comment is not counted but the same word in a string (window['localStorage']) is.
    A small tokenizer, not a JavaScript parser: it knows strings, regex literals (after an operator, a bracket or
    return/typeof) and character classes, which covers how this page is written."""
    out, i, n = [], 0, len(html)
    for m in re.finditer(r'(<script\b[^>]*>)(.*?)(</script>)|(<style\b[^>]*>)(.*?)(</style>)|<!--.*?-->', html, re.S):
        out.append(html[i:m.start()])
        if m.group(1):
            out.append(m.group(1) + strip_js(m.group(2)) + m.group(3))
        elif m.group(4):
            out.append(m.group(4) + re.sub(r'/\*.*?\*/', ' ', m.group(5), flags=re.S) + m.group(6))
        else:
            out.append(' ')
        i = m.end()
    out.append(html[i:n])
    return ''.join(out)


def strip_js(js):
    out, i, n, last = [], 0, len(js), ''
    while i < n:
        c = js[i]
        if c in '\'"`':
            j = i + 1
            while j < n and js[j] != c:
                j += 2 if js[j] == '\\' else 1
            out.append(js[i:j + 1]); last = c; i = j + 1; continue
        if c == '/' and js.startswith('//', i):
            j = js.find('\n', i); i = n if j < 0 else j; out.append(' '); continue
        if c == '/' and js.startswith('/*', i):
            j = js.find('*/', i + 2); i = n if j < 0 else j + 2; out.append(' '); continue
        if c == '/' and (last == '' or last in '(,=:[!&|?{};+-*%<>~^' or re.search(r'\b(return|typeof|case)\s*$', ''.join(out[-3:]))):
            j, cls = i + 1, False                     # a regex literal: up to the closing / outside a [...] class
            while j < n and js[j] != '\n':
                if js[j] == '\\':
                    j += 2; continue
                if js[j] == '[':
                    cls = True
                elif js[j] == ']':
                    cls = False
                elif js[j] == '/' and not cls:
                    break
                j += 1
            out.append(js[i:j + 1]); last = '/'; i = j + 1; continue
        out.append(c)
        if not c.isspace():
            last = c
        i += 1
    return ''.join(out)


def storage_problems(text):
    """Browser storage the page uses without the STORE prefix, as readable lines.
    THIS STATIC CHECK IS A GUARD, NOT PROOF: it reads the source, so code it cannot see through (a key built at run
    time behind an allowed name, eval) passes it. The runtime key listing in the test browser stays mandatory for
    every test build: open it, use it, list the stored keys, and every key it wrote must start with STORE ('test-').
    Rules: every mention of localStorage or sessionStorage outside comments must be a direct getItem, setItem or
    removeItem call whose key is STORE+... or a name defined as STORE+...; anything else (an alias such as
    const ls=localStorage, window['localStorage'], window.localStorage, typeof localStorage, passing it as an
    argument, [..] access, .key(), .clear()) is refused. IndexedDB, cookies, the Cache API and service workers are
    refused outright, apart from the one registration SW_REGISTER, allowed at most once (STATUS A65)."""
    code = strip_comments(text)
    if code.count(SW_REGISTER) > 1:
        return [f'the service worker registration occurs {code.count(SW_REGISTER)} times: at most once']
    code = code.replace(SW_REGISTER, ' ')
    prefixed = set(re.findall(r'\b([A-Za-z_$][\w$]*)\s*=\s*STORE\s*\+', code))
    out = []
    for w in WORD.finditer(code):
        line = code.count('\n', 0, w.start()) + 1
        before = code[w.start() - 1] if w.start() else ''
        c = CALL.match(code, w.start())
        if not c or (before and (before.isalnum() or before in '_$.[\'"`')):
            out.append(f'line {line}: {w.group(1)} used other than as a direct prefixed get/set/remove: '
                       f'{code[max(0, w.start() - 20):w.start() + 40]!r}')
            continue
        arg = c.group(3).strip()
        if not (re.match(r'STORE\s*\+', arg) or arg in prefixed):
            out.append(f'line {line}: {c.group(1)}.{c.group(2)} key {arg!r} does not start with STORE+')
    for what, rx in FORBIDDEN.items():
        for f in re.finditer(rx, code):
            line = code.count('\n', 0, f.start()) + 1
            out.append(f'line {line}: uses {what} ({code[max(0, f.start() - 20):f.start() + 30]!r}), which has no '
                       'prefixed form yet: refused until a later commit adds one and updates this check')
    return out


def replace_once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        raise Refused(f'{what}: expected exactly one {old!r}, found {n}')
    return text.replace(old, new)


def worker_problems(code):
    """What is wrong with a worker's code (comments blanked), as readable lines: no "record-" cache, the cache named from
    its folder and version, clean-up of its own folder only, and only a page of its own version kept (STATUS A65)."""
    out = [f'it must contain {need!r} exactly once (found {code.count(need)})' for need in SW_NEED if code.count(need) != 1]
    if 'record-' in code:
        out.append('it names a "record-" cache, which the RIB worker would delete (STATUS A18)')
    if code.count('await isOwn(res)') != 2:
        out.append('it must check isOwn before saving a page, at install and on refresh (2 places)')
    return out


def build_worker(src):
    code = strip_js(src)
    problems = worker_problems(code)
    if re.findall(r'/marks[^\'"]*', code) != ['/marks/key.js']:
        problems.append('it must name /marks/ in its key.js line only')
    if problems:
        raise Refused('the live worker:\n  ' + '\n  '.join(problems))
    t = replace_once(src, SW_KEY_LIVE, SW_KEY_TEST, "the worker's key.js line")
    stray = [t[max(0, x.start() - 30):x.start() + 30] for x in re.finditer(r'/marks(?!-test/)', t)]
    if stray:
        raise Refused('the test worker still refers to live /marks: ' + '; '.join(repr(s) for s in stray))
    problems = worker_problems(strip_js(t))
    if problems:
        raise Refused('the test worker:\n  ' + '\n  '.join(problems))
    return t


def build_page(src):
    problems = storage_problems(src)
    if problems:
        raise Refused('the live page uses a browser storage key without STORE:\n  ' + '\n  '.join(problems))
    m = re.findall(r"const PAGE_VERSION='([^']+)';", src)
    if len(m) != 1:
        raise Refused(f'expected exactly one PAGE_VERSION, found {len(m)}')
    version = m[0] + '-test'
    t = src
    t = replace_once(t, '<script src="/marks/key.js"></script>', f'<script src="{TEST_BASE}key.js"></script>', 'key.js tag')
    t = replace_once(t, "const MARKS_BASE='/marks/', STORE='';",
                     f"const MARKS_BASE='{TEST_BASE}', STORE='{TEST_STORE}';", 'MARKS_BASE and STORE')
    t = replace_once(t, f"const PAGE_VERSION='{m[0]}';", f"const PAGE_VERSION='{version}';", 'PAGE_VERSION')
    titles = re.findall(r'<title>([^<]*)</title>', t)
    if len(titles) != 1:
        raise Refused(f'expected exactly one <title>, found {len(titles)}')
    t = replace_once(t, f'<title>{titles[0]}</title>', f'<title>TEST – {titles[0]}</title>', 'title')
    t = replace_once(t, '<meta charset="utf-8">',
                     '<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">', 'charset meta')
    banner = ('<div id="testBanner" role="note" style="position:sticky;top:0;z-index:9999;background:#B3261E;color:#FFFFFF;'
              'font:700 14px/1.35 system-ui,sans-serif;text-align:center;padding:6px 10px">TEST COPY – not live data · '
              f'{TEST_BASE} · PAGE_VERSION {version}</div>')
    t = replace_once(t, '<body>', '<body>\n' + banner, 'body tag')
    # the result: no way back to live data, every storage key prefixed, the TEST markings present
    stray = [t[max(0, x.start() - 30):x.start() + 30] for x in re.finditer(r'/marks(?!-test/)', t)]
    if stray:
        raise Refused('the test page still refers to live /marks: ' + '; '.join(repr(s) for s in stray))
    problems = storage_problems(t)
    if problems:
        raise Refused('the test page uses a browser storage key without STORE:\n  ' + '\n  '.join(problems))
    for need in (f"STORE='{TEST_STORE}'", f"MARKS_BASE='{TEST_BASE}'", "ENDPOINT=MARKS_BASE+'marks.php'",
                 'id="testBanner"', f'PAGE_VERSION {version}</div>', '<title>TEST – ',
                 '<meta name="robots" content="noindex,nofollow">'):
        if t.count(need) != 1:
            raise Refused(f'the test page must contain {need!r} exactly once (found {t.count(need)})')
    return t, version


def sha(b):
    return hashlib.sha256(b).hexdigest()


def source_of(path, commit):
    """Where a built file came from, in words (STATUS A28): the committed file only when it is inside the repository,
    tracked, and the same as at HEAD; otherwise its path, said to be outside the repository, untracked or changed."""
    full = os.path.abspath(path)
    rel = os.path.relpath(full, ROOT) if os.path.splitdrive(full)[0].lower() == os.path.splitdrive(ROOT)[0].lower() else full
    if rel.startswith('..') or os.path.isabs(rel):
        return f'{full} (outside the repository: not a committed file)'
    rel = rel.replace(os.sep, '/')
    try:
        tracked = subprocess.run(['git', '-C', ROOT, 'ls-files', '--error-unmatch', '--', rel], capture_output=True).returncode == 0
        same = tracked and subprocess.run(['git', '-C', ROOT, 'diff', '--quiet', 'HEAD', '--', rel], capture_output=True).returncode == 0
    except OSError:
        return f'{rel} (git not available: commit unknown)'
    if not tracked:
        return f'{rel} (not tracked in the repository: not a committed file)'
    return f'{rel} at commit {commit}' if same else f'{rel} (uncommitted changes since commit {commit})'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--page', default=os.path.join(ROOT, 'pages', 'course', 'course_v8.html'))
    ap.add_argument('--sw', default=os.path.join(ROOT, 'pages', 'course', 'sw.js'))
    ap.add_argument('--marks', default=os.path.join(ROOT, 'pages', 'marks', 'marks.php'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'build', 'test'))
    a = ap.parse_args()
    try:
        with open(a.page, encoding='utf-8', newline='') as f:
            page, version = build_page(f.read())
        with open(a.sw, encoding='utf-8', newline='') as f:
            worker = build_worker(f.read())
        with open(a.marks, 'rb') as f:
            marks = f.read()
    except Refused as e:
        print('REFUSED, nothing written: ' + str(e))
        return 1
    try:
        commit = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(['git', '-C', ROOT, 'status', '--porcelain', '--', 'pages'], capture_output=True, text=True).stdout.strip()
    except OSError:
        commit, dirty = '', ''
    commit = commit or 'unknown'
    page_src, sw_src, marks_src = source_of(a.page, commit), source_of(a.sw, commit), source_of(a.marks, commit)
    pb, wb = page.encode('utf-8'), worker.encode('utf-8')
    # written to a temporary folder first, then moved into place, so a failure never leaves half a build
    os.makedirs(a.out, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='.build-', dir=a.out)
    try:
        os.makedirs(os.path.join(tmp, 'course-test'))
        os.makedirs(os.path.join(tmp, 'marks-test'))
        with open(os.path.join(tmp, 'course-test', 'index.html'), 'wb') as f:
            f.write(pb)
        with open(os.path.join(tmp, 'course-test', 'sw.js'), 'wb') as f:
            f.write(wb)
        shutil.copyfile(a.marks, os.path.join(tmp, 'marks-test', 'marks.php'))
        with open(os.path.join(tmp, 'marks-test', 'marks.php'), 'rb') as f:
            if f.read() != marks:
                raise Refused('the copied marks.php differs from its source')
        with open(os.path.join(tmp, 'BUILD.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(f'source commit {commit}{" (pages/ has uncommitted changes)" if dirty else ""}\n'
                    f'page built from {page_src}\n'
                    f'worker built from {sw_src}\n'
                    f'marks.php copied from {marks_src}\n'
                    f'PAGE_VERSION {version}\n'
                    f'course-test/index.html sha256 {sha(pb)}\n'
                    f'course-test/sw.js      sha256 {sha(wb)}\n'
                    f'marks-test/marks.php   sha256 {sha(marks)}\n'
                    'key.js and data/ro-key.php are not part of the build: place them on the server by hand.\n')
        for name in ('course-test', 'marks-test', 'BUILD.txt'):
            dst = os.path.join(a.out, name)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            elif os.path.exists(dst):
                os.remove(dst)
            os.replace(os.path.join(tmp, name), dst)
    except Refused as e:
        print('REFUSED, nothing written: ' + str(e))
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'test build {version} from {commit}{" (uncommitted changes in pages/)" if dirty else ""} written to {a.out}')
    print(f'  page built from {page_src}')
    print(f'  worker built from {sw_src}')
    print(f'  marks.php copied from {marks_src}')
    print(f'  course-test/index.html  {sha(pb)}')
    print(f'  course-test/sw.js       {sha(wb)}')
    print(f'  marks-test/marks.php    {sha(marks)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
