#!/usr/bin/env python3
"""Tests for scripts/backfill_day_series.py (STATUS A8), against marks.php run through php-cgi on made-up test data.

    python tests/test_backfill.py        (PHP_CGI names php-cgi, as for tests/test_marks.py)

A local server on 127.0.0.1 serves a throwaway copy of pages/marks/marks.php with its own key.js and data folder:
  27 September  two courses and fixes, no _day                  -> written
  4 October     a course, fixes and course history, no _day     -> written; the history unchanged
  11 October    already has the _day series "August / September" -> refused, left byte for byte
  18 October    no courses file and no fixes (not raced)        -> refused, no file made
Checks: --dry-run writes nothing; the backup folder holds every day's courses, history and fixes with a SHA-256 list
that matches; each written day holds _day {"series": "Autumn League"} with every other record unchanged; series.json
is untouched; the race key is never printed; a second run refuses every day and writes nothing; a backup folder inside
the repository and a wrong key are refused before anything is written. Exits non-zero if any test fails.
"""
import hashlib
import http.server
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHPCGI = os.environ.get('PHP_CGI') or shutil.which('php-cgi')
SCRIPT = os.path.join(ROOT, 'scripts', 'backfill_day_series.py')
KEY = 'test' + secrets.token_hex(8)
results = []


def report(name, ok, detail=''):
    results.append((name, ok, detail))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None


def serve(work):
    class H(http.server.BaseHTTPRequestHandler):
        def _php(self, method, body=b''):
            q = self.path.split('?', 1)[1] if '?' in self.path else ''
            env = dict(os.environ, REQUEST_METHOD=method, SCRIPT_FILENAME=os.path.join(work, 'marks.php'), REDIRECT_STATUS='1',
                       QUERY_STRING=q, HTTP_X_RACE_KEY=self.headers.get('X-Race-Key', ''), GATEWAY_INTERFACE='CGI/1.1',
                       CONTENT_TYPE='application/json', CONTENT_LENGTH=str(len(body)))
            p = subprocess.run([PHPCGI], input=body, env=env, capture_output=True, timeout=60)
            head, _, out = p.stdout.partition(b'\r\n\r\n')
            code = 200
            for line in head.split(b'\r\n'):
                if line.lower().startswith(b'status:'):
                    code = int(line.split()[1])
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(out)))
            self.end_headers()
            self.wfile.write(out)

        def do_GET(self):
            self._php('GET')

        def do_POST(self):
            n = int(self.headers.get('Content-Length') or 0)
            self._php('POST', self.rfile.read(n))

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def run(args):
    p = subprocess.run([sys.executable, SCRIPT] + args, capture_output=True, text=True, encoding='utf-8', timeout=300)
    return p.returncode, p.stdout + p.stderr


def main():
    if not PHPCGI or not os.path.exists(PHPCGI):
        print('php-cgi not found: set PHP_CGI to the php-cgi executable')
        return 2
    print(subprocess.run([PHPCGI, '-v'], capture_output=True, text=True).stdout.splitlines()[0])
    tmp = tempfile.mkdtemp(prefix='backfill-test-')
    try:
        work, data, bk = os.path.join(tmp, 'site'), os.path.join(tmp, 'site', 'data'), os.path.join(tmp, 'backups')
        os.makedirs(data)
        os.makedirs(bk)
        shutil.copy(os.path.join(ROOT, 'pages', 'marks', 'marks.php'), work)
        kj = os.path.join(tmp, 'key.js')
        for p in (os.path.join(work, 'key.js'), kj):
            open(p, 'w').write(f"window.RACE_KEY='{KEY}';\n")
        fixm = lambda d: {f'f{d[-2:]}{i}': {'id': f'f{d[-2:]}{i}', 'date': d, 'race': 1, 'name': n, 'lat': 51.8 + i / 1000,
                                             'lon': -8.3, 'acc': 4.0, 'time': 1790000000000 + i, 'received': 1790000000}
                          for i, n in enumerate(['Committee boat', 'Start Pin', 'E4'])}
        files = {
            'courses-2026-09-27.json': {'1|0': {'data': {'entries': [{'ref': 's:f270', 'side': ''}], 'startTime': '10:55'}, 'updated': 1790000100},
                                        '_starts|1': {'data': {'classes': [['Class 1 Spinnaker']]}, 'updated': 1790000101}},
            'marks-2026-09-27.json': fixm('2026-09-27'),
            'courses-2026-10-04.json': {'1|0': {'data': {'entries': [], 'startTime': '11:00'}, 'updated': 1790000200}},
            'courses-history-2026-10-04.json': {'1|0': [{'data': {'entries': []}, 'updated': 1790000150, 'replaced': 1790000200}]},
            'marks-2026-10-04.json': fixm('2026-10-04'),
            'courses-2026-10-11.json': {'_day': {'data': {'series': 'August / September'}, 'updated': 1790000300},
                                        '1|0': {'data': {'entries': []}, 'updated': 1790000301}},
            'marks-2026-10-11.json': fixm('2026-10-11'),
            'series.json': {'name': 'Autumn League', 'updated': 1790000000},
        }
        for n, obj in files.items():
            json.dump(obj, open(os.path.join(data, n), 'w', encoding='utf-8'))
        before = {n: sha(os.path.join(data, n)) for n in os.listdir(data)}
        srv = serve(work)
        url = f'http://127.0.0.1:{srv.server_address[1]}/marks.php'
        dates = '2026-09-27,2026-10-04,2026-10-11,2026-10-18'
        base = ['--url', url, '--backup-dir', bk, '--key-js', kj, '--dates', dates]

        code, out = run(base + ['--dry-run'])
        after = {n: sha(os.path.join(data, n)) for n in os.listdir(data) if n != '.htaccess'}
        report('dry run writes nothing and names what it would write', code == 3 and after == before
               and 'would write 2026-09-27, 2026-10-04.' in out and 'REFUSED 2026-10-11' in out and 'REFUSED 2026-10-18' in out,
               f'exit {code}; {out.strip()[-300:]}')

        code, out = run(['--url', url, '--backup-dir', os.path.join(ROOT, 'build'), '--key-js', kj, '--dates', dates])
        report('a backup folder inside the repository is refused', code == 1 and 'outside the repository' in out, out.strip()[-200:])
        wrong = os.path.join(tmp, 'wrong.js')
        open(wrong, 'w').write("window.RACE_KEY='wrongkey123';\n")
        n0 = len(os.listdir(bk))
        code, out = run(['--url', url, '--backup-dir', bk, '--key-js', wrong, '--dates', dates])
        after = {n: sha(os.path.join(data, n)) for n in os.listdir(data) if n != '.htaccess'}
        report('a wrong key stops before anything is written', code == 1 and 'bad key' in out and after == before, out.strip()[-200:])
        shutil.rmtree(os.path.join(bk, sorted(os.listdir(bk))[-1])) if len(os.listdir(bk)) > n0 else None

        code, out = run(base)
        c = {d: json.load(open(os.path.join(data, f'courses-{d}.json'), encoding='utf-8')) for d in ('2026-09-27', '2026-10-04')}
        written = all(c[d].get('_day', {}).get('data') == {'series': 'Autumn League'}
                      and {k: v for k, v in c[d].items() if k != '_day'} == files[f'courses-{d}.json'] for d in c)
        kept = all(sha(os.path.join(data, n)) == before[n] for n in before if n not in ('courses-2026-09-27.json', 'courses-2026-10-04.json'))
        no18 = not os.path.exists(os.path.join(data, 'courses-2026-10-18.json'))
        hist27 = not os.path.exists(os.path.join(data, 'courses-history-2026-09-27.json'))
        report('27 September and 4 October written; every other record, 11 October, series.json and the history unchanged',
               code == 3 and written and kept and no18 and hist27 and 'Written 2026-09-27' in out and 'Written 2026-10-04' in out,
               f'exit {code}; written {written}; others kept {kept}; no 18 October file {no18}; no history made {hist27}')
        report('11 October (already has a series) and 18 October (not raced) refused', "REFUSED 2026-10-11: already has the series 'August / September'" in out
               and 'REFUSED 2026-10-18: no courses and no fixes' in out, out.strip()[-400:])
        report('the race key is never printed', KEY not in out)

        folder = [os.path.join(bk, f) for f in os.listdir(bk)]
        ok_bk, detail = len(folder) == 2, f'{len(folder)} backup folders (dry run and the run)'
        if ok_bk:
            last = sorted(folder)[-1]
            rows = open(os.path.join(last, 'backup.sha256.csv'), encoding='utf-8').read().splitlines()[1:]
            ok_bk = len(rows) == 12 and all(sha(os.path.join(last, r.split(',')[0])) == r.split(',')[1] for r in rows)
            b27 = json.load(open(os.path.join(last, 'courses-2026-09-27.json'), encoding='utf-8'))
            ok_bk = ok_bk and b27 == files['courses-2026-09-27.json'] and 'Backup checked' in out
            detail = f'{len(rows)} files listed, hashes match {ok_bk}'
        report('the backup holds every day\'s courses, history and fixes, checked against its SHA-256 list', ok_bk, detail)

        snap = {n: sha(os.path.join(data, n)) for n in os.listdir(data)}
        code, out = run(base)
        report('a second run refuses every day and writes nothing', code == 3 and out.count('REFUSED') == 4
               and {n: sha(os.path.join(data, n)) for n in os.listdir(data)} == snap, f'exit {code}')
        srv.shutdown()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    w = max(len(r[0]) for r in results)
    for n, ok, d in results:
        print(f'{n:<{w}}  {"PASS" if ok else "FAIL"}  {d if not ok else ""}')
    failed = sum(not r[1] for r in results)
    print(f'\n{failed} test(s) failed' if failed else '\nall tests passed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
