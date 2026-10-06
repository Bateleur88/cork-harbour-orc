#!/usr/bin/env python3
"""Tests for scripts/build_test.py, the parallel TEST copy of the race officer page and marks.php.

    python tests/test_build_test.py

Builds from the repository's page into a throwaway folder and checks the result, then feeds the script pages
altered in ways it must refuse and checks that it writes nothing:

  0  build      the test page talks only to /marks-test/, prefixes every browser storage key with "test-", shows
                the red TEST banner with its PAGE_VERSION, "TEST" in the title and noindex; marks.php is copied
                byte for byte; nothing else in the page changed; BUILD.txt names the version and both hashes
  1  live page  the live page itself uses no browser storage key without STORE (so a key added later is caught), and
                the STORE+ key names in its code are exactly STORE_NAMES (a key added or dropped must update the list)
  2  refusals   a storage key without STORE (setItem, getItem, removeItem), any other use of localStorage or
                sessionStorage (bracket access, .clear(), .key(), an alias, window['localStorage'],
                window.localStorage, typeof, passing it as an argument), IndexedDB, document.cookie (also
                document['cookie']), the Cache API, a service worker, a stray "/marks/" path, a missing or doubled
                key.js tag, a missing STORE line, a missing <title>: each is refused, exits non-zero and leaves an
                earlier build in the output folder untouched; a division followed by a call on the same line
                ((a+b)/2;localStorage.setItem('x',1) and var h=x/y;sessionStorage.getItem('z')) does not hide the call
  3  allowed    the same words in comments only, a regex literal holding a quote and "//" before a prefixed call,
                and the two division lines with STORE+ keys, still build

Needs no PHP and no browser. Exits non-zero if any test fails.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'build_test.py')
PAGE = os.path.join(ROOT, 'pages', 'course', 'course_v8.html')
MARKS = os.path.join(ROOT, 'pages', 'marks', 'marks.php')
# every browser storage key name the page writes after STORE ('pv-' is followed by a PAGE_VERSION). ro-name and ro-key
# are the Review name and RO key, kept on the device outside S; the test copy must keep them under 'test-' like the rest
STORE_NAMES = {'pv-', 'race-key', 'course-plot-v1', 'course-series', 'ro-name', 'ro-key'}
failed = []


def report(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + (': ' + detail if detail and not ok else ''))
    if not ok:
        failed.append(name)


def run(page, out):
    return subprocess.run([sys.executable, SCRIPT, '--page', page, '--marks', MARKS, '--out', out],
                          capture_output=True, text=True, encoding='utf-8')


def read(p, mode='r'):
    with open(p, mode, **({} if 'b' in mode else {'encoding': 'utf-8', 'newline': ''})) as f:
        return f.read()


def t0_build(tmp):
    out = os.path.join(tmp, 'out0')
    r = run(PAGE, out)
    report('0 build exits 0', r.returncode == 0, r.stdout + r.stderr)
    if r.returncode:
        return
    live, test = read(PAGE), read(os.path.join(out, 'course-test', 'index.html'))
    v = re.search(r"const PAGE_VERSION='([^']+)';", live).group(1)
    checks = {
        'key.js from /marks-test/': '<script src="/marks-test/key.js"></script>' in test,
        'MARKS_BASE and STORE': "const MARKS_BASE='/marks-test/', STORE='test-';" in test,
        'PAGE_VERSION -test': f"const PAGE_VERSION='{v}-test';" in test,
        'no /marks other than /marks-test/': not re.search(r'/marks(?!-test/)', test),
        'banner with version': f'PAGE_VERSION {v}-test</div>' in test and 'TEST COPY – not live data' in test,
        'TEST title': '<title>TEST – ' in test,
        'noindex': '<meta name="robots" content="noindex,nofollow">' in test,
        'marks.php byte-identical': read(os.path.join(out, 'marks-test', 'marks.php'), 'rb') == read(MARKS, 'rb'),
        'BUILD.txt': f'PAGE_VERSION {v}-test' in read(os.path.join(out, 'BUILD.txt')),
    }
    for k, ok in checks.items():
        report('0 ' + k, ok)
    # nothing else changed: undo the known replacements and compare with the live page
    back = (test.replace('<script src="/marks-test/key.js"></script>', '<script src="/marks/key.js"></script>')
                .replace("const MARKS_BASE='/marks-test/', STORE='test-';", "const MARKS_BASE='/marks/', STORE='';")
                .replace(f"const PAGE_VERSION='{v}-test';", f"const PAGE_VERSION='{v}';")
                .replace('<title>TEST – ', '<title>')
                .replace('<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">', '<meta charset="utf-8">'))
    back = re.sub(r'<body>\n<div id="testBanner"[^\n]*</div>', '<body>', back)
    report('0 nothing else changed', back == live)


def t1_live_page():
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    problems = build_test.storage_problems(read(PAGE))
    report('1 live page: every storage key uses STORE', not problems, '; '.join(problems))
    names = set(re.findall(r"\bSTORE\s*\+\s*'([^']*)'", build_test.strip_comments(read(PAGE))))
    report('1 live page: STORE+ key names are exactly STORE_NAMES', names == STORE_NAMES,
           f'unexpected {sorted(names - STORE_NAMES)}, missing {sorted(STORE_NAMES - names)}')


def t2_refusals(tmp):
    live = read(PAGE)
    out = os.path.join(tmp, 'out2')
    r = run(PAGE, out)                                  # a good build first: a refusal must leave it as it was
    before = read(os.path.join(out, 'course-test', 'index.html'), 'rb') if r.returncode == 0 else None
    script_end = live.rindex('</script>')
    inject = lambda code: live[:script_end] + code + '\n' + live[script_end:]
    cases = {
        'setItem without STORE': inject("try{localStorage.setItem('ro-name','x');}catch(e){}"),
        'getItem without STORE': inject("try{sessionStorage.getItem('undo');}catch(e){}"),
        'removeItem without STORE': inject("try{localStorage.removeItem('ro-key');}catch(e){}"),
        'bracket access': inject("try{localStorage['x']='1';}catch(e){}"),
        'clear()': inject("try{sessionStorage.clear();}catch(e){}"),
        'alias const ls=localStorage': inject("const ls=localStorage;"),
        "window['localStorage']": inject("const s=window['localStorage'];"),
        'window.localStorage': inject("try{window.localStorage.getItem(STORE+'x');}catch(e){}"),
        'typeof localStorage': inject("if(typeof localStorage!=='undefined'){}"),
        'passed as an argument': inject("const keep=s=>s;keep(sessionStorage);"),
        '.key()': inject("try{localStorage.key(0);}catch(e){}"),
        'indexedDB': inject("try{indexedDB.open('x');}catch(e){}"),
        'document.cookie': inject("document.cookie='a=1';"),
        "document['cookie']": inject("const c=document['cookie'];"),
        'Cache API': inject("try{caches.open('x');}catch(e){}"),
        'service worker': inject("try{navigator.serviceWorker.register('sw.js');}catch(e){}"),
        'division then setItem, no STORE': inject("(a+b)/2;localStorage.setItem('x',1)"),
        'division then getItem, no STORE': inject("var h=x/y;sessionStorage.getItem('z')"),
        'stray /marks/ path': inject("const OLD='/marks/marks.php';"),
        'key.js tag missing': live.replace('<script src="/marks/key.js"></script>', ''),
        'key.js tag twice': live.replace('<script src="/marks/key.js"></script>', '<script src="/marks/key.js"></script>' * 2),
        'STORE line missing': live.replace("const MARKS_BASE='/marks/', STORE='';", "const MARKS_BASE='/marks/';"),
        'title missing': re.sub(r'<title>[^<]*</title>', '', live),
    }
    for name, text in cases.items():
        p = os.path.join(tmp, 'bad.html')
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        r = run(p, out)
        after = read(os.path.join(out, 'course-test', 'index.html'), 'rb')
        report('2 refused: ' + name, r.returncode != 0 and 'REFUSED' in r.stdout and after == before,
               f'exit {r.returncode}; {r.stdout.strip()[:160]}; earlier build {"kept" if after == before else "CHANGED"}')


def t3_allowed(tmp):
    """What the check must NOT refuse: the forbidden words in comments only, and a regex literal holding a quote and
    // followed by a prefixed call (the tokenizer must not read the regex as a string or a comment)."""
    live = read(PAGE)
    script_end = live.rindex('</script>')
    inject = lambda code: live[:script_end] + code + '\n' + live[script_end:]
    cases = {
        'words in comments only': inject("/* no document.cookie, indexedDB, caches, serviceWorker or a bare localStorage here */\n"
                                         "// window['localStorage'] and typeof sessionStorage are only mentioned"),
        "regex literal with ' and //": inject("const rx=/a'b\\/\\//;try{localStorage.setItem(STORE+'rx',String(rx));}catch(e){}"),
        'division then setItem with STORE': inject("(a+b)/2;localStorage.setItem(STORE+'x',1)"),
        'division then getItem with STORE': inject("var h=x/y;sessionStorage.getItem(STORE+'z')"),
    }
    for name, text in cases.items():
        p = os.path.join(tmp, 'ok.html')
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        r = run(p, os.path.join(tmp, 'out3'))
        report('3 allowed: ' + name, r.returncode == 0, r.stdout.strip()[:200])


def main():
    with tempfile.TemporaryDirectory() as tmp:
        t0_build(tmp)
        t1_live_page()
        t2_refusals(tmp)
        t3_allowed(tmp)
    print(f'\n{len(failed)} failed' if failed else '\nall passed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
