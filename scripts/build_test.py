#!/usr/bin/env python3
"""Build a parallel TEST copy of the race officer page and marks.php, for /course-test/ and /marks-test/.

    python scripts/build_test.py [--page pages/course/course_v8.html] [--sw pages/course/sw.js] [--marks pages/marks/marks.php]
                                 [--manifest pages/course/manifest.webmanifest] [--assets pages/course/assets]
                                 [--ss pages/course/sailscoring-test.js] [--out build/test] [--label LOCAL]

Writes, and nothing else:
    OUT/course-test/index.html   the RO page, talking only to /marks-test/ and keeping its own browser data
    OUT/course-test/sw.js        the page's service worker (STATUS A65), keeping /marks-test/key.js instead of /marks/key.js
    OUT/course-test/sailscoring-test.js   the Sail Scoring connection, Stage 1 (read-only), test copy only (see below)
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
A80 (Pat, 23 October 2026): the test copy installs as its own app. The build writes OUT/course-test/manifest.webmanifest
from the live manifest with the test copy's name ("TEST – Course plot", "TEST Course") and its id, start_url and scope
/course-test/, and copies the TEST icons (assets/icon-course-test-192.png, -512.png, -maskable-512.png) in as
icon-192.png, icon-512.png and icon-maskable-512.png. It refuses a live manifest that does not name /course/ for all
three, a test manifest that names /course/ anywhere, and a page whose manifest link is not the relative
manifest.webmanifest.
Sail Scoring, Stage 1 (Pat, 27 October 2026): the test page, and only the test page, loads sailscoring-test.js, copied
unchanged beside it, by one <script src="sailscoring-test.js?v=<version>"> before </body>, and its PAGE_VERSION ends
-test-ss1 (SS_LABEL). The live page must not name the file. Refused if the file's browser storage keys do not all start
with STORE (the page's check, with the file's STORE exactly 'test-'), or it names /marks, or names PUT, PATCH or DELETE,
or holds a request method other than its one POST (tokenPost: the token and revoke endpoints only) and its one GET
(ssApi, which refuses any other method). A LOCAL build leaves the file out: its sign-in returns only to
https://tradboats.ie/course-test/, which a LOCAL build may not name.
The keys are never part of the build: key.js and data/ro-key.php are placed on the server by hand (see the README).

--label LOCAL builds for the local test site on this PC (php -S), never for upload. It differs from the normal build only in:
    PAGE_VERSION 'X-test-L<HHMM>' (the build time, so every local rebuild is a new version), the title "LOCAL TEST – " and
    the banner "LOCAL TEST – not live data · /marks-test/ · PAGE_VERSION ...". It also refuses a page that names tradboats.ie
    or orc-ireland.org anywhere, or any full web address not in LOCAL_URLS. Without the flag the build is unchanged.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

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
           "return !!VERSION&&!!m&&m[1]===VERSION;",
           "const net=fetch(r).then(res=>{copy=res.clone();return res;});",
           "const copyOf=(res,buf)=>{const t=res.headers.get('Content-Type');return new Response(buf,{status:200,headers:t?{'Content-Type':t}:{}});};")
# --label LOCAL: the only full web addresses a local build may name (fonts, the map library and tiles, WhatsApp), each a
# whole address or, ending in /, the start of one; and the live hosts it must never name, in any form
SS_FILE, SS_LABEL, SS_STORE = 'sailscoring-test.js', 'ss1', "const STORE='test-';"
LOCAL_URLS = ('https://fonts.googleapis.com', 'https://fonts.gstatic.com', 'https://unpkg.com/leaflet@1.9.4/dist/',
              'https://tile.openstreetmap.de/', 'https://tiles.openseamap.org/seamark/', 'https://wa.me/')
LIVE_HOSTS = re.compile(r'tradboats|orc-ireland', re.I)
URL = re.compile(r'\b[a-z][a-z0-9+.-]*://[^\s\'"<>)\\`]*', re.I)
URL_NO_SCHEME = re.compile(r'(?<![\w:/])//[a-z0-9-]+(?:\.[a-z0-9-]+)+', re.I)


TEST_PAGE = '/course-test/'
TEST_NAMES = {'name': 'TEST – Course plot', 'short_name': 'TEST Course'}
TEST_ICONS = (('icon-course-test-192.png', 'icon-192.png'), ('icon-course-test-512.png', 'icon-512.png'),
              ('icon-course-test-maskable-512.png', 'icon-maskable-512.png'))


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
    if code.count('isOwn(new TextDecoder().decode(buf))') != 2:
        out.append('it must check isOwn before saving a page, at install and on refresh (2 places)')
    # the response handed to the browser must never wait on a read of a copy of itself: that stalled a navigation until
    # the worker's wait ran out (A65 test, Step 23)
    for bad in ('.clone().text()', '.clone().arrayBuffer()', '.clone().json()', 'await isOwn('):
        if bad in code:
            out.append(f'it reads a copy of a response before handing it over ({bad!r})')
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


def build_manifest(src):
    """The test copy's manifest (A80): the live one with the test name, and /course-test/ as its id, start_url and
    scope; nothing else changed."""
    try:
        m = json.loads(src)
    except ValueError as e:
        raise Refused(f'the manifest is not valid JSON ({e})')
    if not isinstance(m, dict):
        raise Refused('the manifest is not a JSON object')
    for k in ('id', 'start_url', 'scope'):
        if m.get(k) != '/course/':
            raise Refused(f'the live manifest\'s {k} must be /course/, not {m.get(k)!r}')
    m.update(TEST_NAMES)
    for k in ('id', 'start_url', 'scope'):
        m[k] = TEST_PAGE
    t = json.dumps(m, ensure_ascii=False, indent=2) + '\n'
    if re.search(r'/course(?!-test/)', t):
        raise Refused('the test manifest names /course/')
    if any(json.loads(t).get(k) != TEST_PAGE for k in ('id', 'start_url', 'scope')):
        raise Refused('the test manifest must name /course-test/ as its id, start_url and scope')
    return t


def local_url_problems(text):
    """For a LOCAL build: every mention of a live host, and every full web address not in LOCAL_URLS, as readable lines.
    Addresses with a scheme are looked for in the whole page, comments included; addresses starting // only in the
    code, so a comment such as "//e.g." is not read as one."""
    out = [f'line {text.count(chr(10), 0, x.start()) + 1}: names {x.group(0)!r}' for x in LIVE_HOSTS.finditer(text)]
    found = [x.group(0) for x in URL.finditer(text)] + [x.group(0) for x in URL_NO_SCHEME.finditer(strip_comments(text))]
    for u in found:
        if not any(u == a or u.startswith(a if a.endswith('/') else a + '/') or (not a.endswith('/') and u.startswith(a + '?'))
                   for a in LOCAL_URLS):
            out.append(f'a full web address not in LOCAL_URLS: {u[:80]!r}')
    return out


def ss_problems(js):
    """What is wrong with sailscoring-test.js (Sail Scoring, Stage 1), as readable lines: every browser storage key
    starts with STORE and its STORE is 'test-'; it never names /marks; it makes no request but GET (ssApi) apart from its
    one POST (tokenPost, to the token and revoke endpoints only)."""
    code = strip_js(js)
    out = storage_problems('<script>' + js + '</script>')
    if code.count(SS_STORE) != 1:
        out.append(f'it must contain {SS_STORE!r} exactly once (found {code.count(SS_STORE)})')
    if '/marks' in js:
        out.append('it names /marks: it must never reach race data')
    for m in ('PUT', 'PATCH', 'DELETE'):
        if re.search(r'\b' + m + r'\b', code):
            out.append(f'it names the request method {m}: Stage 1 is read-only')
    if len(re.findall(r'\bmethod\s*:', code)) != 2 or code.count("method:'POST'") != 1 or code.count("method:'GET'") != 1:
        out.append("it must hold exactly two request methods: method:'POST' once (tokenPost) and method:'GET' once (ssApi)")
    if code.count("if(url!==TOKEN&&url!==REVOKE)throw") != 1 or code.count("if(method!=='GET')throw") != 1:
        out.append('tokenPost must refuse any address but the token and revoke endpoints, and ssApi any method but GET')
    return out


def build_page(src, label='', stamp=''):
    """The test page and its PAGE_VERSION. label 'LOCAL' (with stamp, the build time as HHMM) makes the local test site's
    page instead; without it the result is the normal test copy."""
    if label not in ('', 'LOCAL'):
        raise Refused(f'unknown label {label!r}: the only label is LOCAL')
    if label and not re.fullmatch(r'\d{4}', stamp):
        raise Refused(f'a LOCAL build needs the build time as HHMM, not {stamp!r}')
    problems = storage_problems(src)
    if problems:
        raise Refused('the live page uses a browser storage key without STORE:\n  ' + '\n  '.join(problems))
    if label:
        problems = local_url_problems(src)
        if problems:
            raise Refused('a LOCAL build refuses this page:\n  ' + '\n  '.join(problems))
    links = re.findall(r'<link rel="manifest"[^>]*>', src)
    if links and links != ['<link rel="manifest" href="manifest.webmanifest">']:
        raise Refused('the page\'s manifest link must be exactly <link rel="manifest" href="manifest.webmanifest">, '
                      'so the test copy loads its own: ' + ' '.join(links))
    m = re.findall(r"const PAGE_VERSION='([^']+)';", src)
    if len(m) != 1:
        raise Refused(f'expected exactly one PAGE_VERSION, found {len(m)}')
    if SS_FILE in src:
        raise Refused(f'the live page names {SS_FILE}: only the test build may add it')
    version = m[0] + '-test' + (f'-L{stamp}' if label else f'-{SS_LABEL}')
    title_pre, banner_pre = ('LOCAL TEST – ', 'LOCAL TEST – ') if label else ('TEST – ', 'TEST COPY – ')
    t = src
    t = replace_once(t, '<script src="/marks/key.js"></script>', f'<script src="{TEST_BASE}key.js"></script>', 'key.js tag')
    t = replace_once(t, "const MARKS_BASE='/marks/', STORE='';",
                     f"const MARKS_BASE='{TEST_BASE}', STORE='{TEST_STORE}';", 'MARKS_BASE and STORE')
    t = replace_once(t, f"const PAGE_VERSION='{m[0]}';", f"const PAGE_VERSION='{version}';", 'PAGE_VERSION')
    titles = re.findall(r'<title>([^<]*)</title>', t)
    if len(titles) != 1:
        raise Refused(f'expected exactly one <title>, found {len(titles)}')
    t = replace_once(t, f'<title>{titles[0]}</title>', f'<title>{title_pre}{titles[0]}</title>', 'title')
    t = replace_once(t, '<meta charset="utf-8">',
                     '<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">', 'charset meta')
    banner = ('<div id="testBanner" role="note" style="position:sticky;top:0;z-index:9999;background:#B3261E;color:#FFFFFF;'
              f'font:700 14px/1.35 system-ui,sans-serif;text-align:center;padding:6px 10px">{banner_pre}not live data · '
              f'{TEST_BASE} · PAGE_VERSION {version}</div>')
    t = replace_once(t, '<body>', '<body>\n' + banner, 'body tag')
    ss_tag = f'<script src="{SS_FILE}?v={version}"></script>'
    if not label:
        t = replace_once(t, '</body>', ss_tag + '\n</body>', 'closing body tag')
    # the result: no way back to live data, every storage key prefixed, the TEST markings present
    stray = [t[max(0, x.start() - 30):x.start() + 30] for x in re.finditer(r'/marks(?!-test/)', t)]
    if stray:
        raise Refused('the test page still refers to live /marks: ' + '; '.join(repr(s) for s in stray))
    problems = storage_problems(t)
    if problems:
        raise Refused('the test page uses a browser storage key without STORE:\n  ' + '\n  '.join(problems))
    for need in (f"STORE='{TEST_STORE}'", f"MARKS_BASE='{TEST_BASE}'", "ENDPOINT=MARKS_BASE+'marks.php'",
                 'id="testBanner"', f'PAGE_VERSION {version}</div>', f'<title>{title_pre}',
                 '<meta name="robots" content="noindex,nofollow">'):
        if t.count(need) != 1:
            raise Refused(f'the test page must contain {need!r} exactly once (found {t.count(need)})')
    if t.count(SS_FILE) != (0 if label else 1) or (not label and t.count(ss_tag) != 1):
        raise Refused(f'the test page must load {SS_FILE} exactly once, and a LOCAL page never')
    if label:
        problems = local_url_problems(t)
        if problems:
            raise Refused('the LOCAL page:\n  ' + '\n  '.join(problems))
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
    ap.add_argument('--manifest', default=os.path.join(ROOT, 'pages', 'course', 'manifest.webmanifest'))
    ap.add_argument('--assets', default=os.path.join(ROOT, 'pages', 'course', 'assets'))
    ap.add_argument('--ss', default=os.path.join(ROOT, 'pages', 'course', SS_FILE))
    ap.add_argument('--out', default=os.path.join(ROOT, 'build', 'test'))
    ap.add_argument('--label', choices=['LOCAL'], default='', help='LOCAL: for the local test site only, never uploaded')
    a = ap.parse_args()
    try:
        with open(a.page, encoding='utf-8', newline='') as f:
            page, version = build_page(f.read(), a.label, time.strftime('%H%M') if a.label else '')
        with open(a.sw, encoding='utf-8', newline='') as f:
            worker = build_worker(f.read())
        with open(a.marks, 'rb') as f:
            marks = f.read()
        ss = None
        if not a.label:
            with open(a.ss, 'rb') as f:
                ss = f.read()
            problems = ss_problems(ss.decode('utf-8'))
            if problems:
                raise Refused(f'{SS_FILE}:\n  ' + '\n  '.join(problems))
        man = None
        if os.path.exists(a.manifest):
            with open(a.manifest, encoding='utf-8', newline='') as f:
                man = build_manifest(f.read()).encode('utf-8')
            icons = []
            for src, dst in TEST_ICONS:
                p = os.path.join(a.assets, src)
                if not os.path.isfile(p):
                    raise Refused(f'the test icon {src} is missing from {a.assets}')
                with open(p, 'rb') as f:
                    icons.append((dst, f.read(), p))
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
        if man is not None:
            with open(os.path.join(tmp, 'course-test', 'manifest.webmanifest'), 'wb') as f:
                f.write(man)
            for dst, data, _ in icons:
                with open(os.path.join(tmp, 'course-test', dst), 'wb') as f:
                    f.write(data)
        if ss is not None:
            with open(os.path.join(tmp, 'course-test', SS_FILE), 'wb') as f:
                f.write(ss)
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
                    + ('label LOCAL: for the local test site only, never uploaded\n' if a.label else '') +
                    f'course-test/index.html sha256 {sha(pb)}\n'
                    f'course-test/sw.js      sha256 {sha(wb)}\n'
                    f'marks-test/marks.php   sha256 {sha(marks)}\n'
                    + (f'course-test/{SS_FILE} sha256 {sha(ss)} (copied from {source_of(a.ss, commit)})\n' if ss is not None
                       else f'{SS_FILE} left out: a LOCAL build never includes it\n')
                    + (f'manifest built from {source_of(a.manifest, commit)}\n'
                       f'course-test/manifest.webmanifest sha256 {sha(man)}\n'
                       + ''.join(f'course-test/{dst} sha256 {sha(data)} (from {source_of(p, commit)})\n' for dst, data, p in icons)
                       if man is not None else '') +
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
    print(f'{"LOCAL " if a.label else ""}test build {version} from {commit}{" (uncommitted changes in pages/)" if dirty else ""} written to {a.out}')
    print(f'  page built from {page_src}')
    print(f'  worker built from {sw_src}')
    print(f'  marks.php copied from {marks_src}')
    print(f'  course-test/index.html  {sha(pb)}')
    print(f'  course-test/sw.js       {sha(wb)}')
    print(f'  marks-test/marks.php    {sha(marks)}')
    if ss is not None:
        print(f'  course-test/{SS_FILE}  {sha(ss)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
