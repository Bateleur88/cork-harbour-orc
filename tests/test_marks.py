#!/usr/bin/env python3
"""Safety tests for pages/marks/marks.php, run as real CGI requests through php-cgi.

    python tests/test_marks.py

Needs php-cgi (in the Windows PHP zip; the php-cgi package on Linux). Found through the PHP_CGI
environment variable, or on PATH. marks.php itself is not modified; each test runs it in a
throwaway folder against a day file holding races 1-3, then checks every one of those fixes is
still present and unchanged:

  0  normal     add, delete, GET; device and recorder stored; older fixes have neither;
                a long recorder name cut to 60 characters, not bytes
  1  encode     a fix or course that cannot be JSON-encoded (1e400 -> INF) is refused, file untouched
  2  damaged    a half-written day file is refused, not overwritten
  3  write      a write that fails part-way leaves the day file unchanged, no .tmp left behind
  4  moved      the RO page re-posting a fix to another race keeps its device and recorder
  5  parallel   60 fixes, 10 courses and 30 reads at once: nothing lost, no reader sees a partial day

Exits non-zero if any test fails.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKS_PHP = os.path.join(ROOT, 'pages', 'marks', 'marks.php')
PHPCGI = os.environ.get('PHP_CGI') or shutil.which('php-cgi')
DAY = '2026-09-21'
KEY = 'RCYC_2026'
DEVICE = '55ac7020-9dbc-4c45-a094-364f1bee1890'
WORK = tempfile.mkdtemp(prefix='marks-test-')


def fixture():
    """Races 1-3, four fixes each, none carrying device or recorder (as older fixes don't)."""
    marks = {}
    for race in (1, 2, 3):
        for i, name in enumerate(['Committee boat', 'Start Pin', 'Windward', 'Leeward']):
            mid = f'fixr{race}n{i}'
            marks[mid] = {'id': mid, 'series': 'Autumn League', 'date': DAY, 'race': race, 'name': name,
                          'lat': 51.80 + i / 1000, 'lon': -8.30 - race / 1000, 'acc': 4.0,
                          'time': 1790000000000 + race * 100000 + i, 'received': 1790000000}
    courses = {'1|1': {'data': {'legs': ['Windward', 'Leeward']}, 'updated': 1790000000},
               '2|1': {'data': {'legs': ['A', 'B']}, 'updated': 1790000001}}
    return marks, courses


def setup(name):
    d = os.path.join(WORK, name)
    os.makedirs(os.path.join(d, 'data'))
    shutil.copy(MARKS_PHP, os.path.join(d, 'marks.php'))
    marks, courses = fixture()
    json.dump(marks, open(day_file(d), 'w', encoding='utf-8'))
    json.dump(courses, open(course_file(d), 'w', encoding='utf-8'))
    return d


def day_file(d): return os.path.join(d, 'data', f'marks-{DAY}.json')
def course_file(d): return os.path.join(d, 'data', f'courses-{DAY}.json')
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None
def size(p): return os.path.getsize(p) if os.path.exists(p) else -1
def load(p): return json.load(open(p, encoding='utf-8'))
def leftovers(d): return [f for f in os.listdir(os.path.join(d, 'data')) if f.endswith('.tmp')]


def req(d, method='POST', body=None, query=''):
    raw = body if isinstance(body, bytes) else (json.dumps(body) if body is not None else '').encode()
    env = dict(os.environ, REQUEST_METHOD=method, SCRIPT_FILENAME=os.path.join(d, 'marks.php'),
               REDIRECT_STATUS='1', CONTENT_TYPE='application/json', CONTENT_LENGTH=str(len(raw)),
               QUERY_STRING=query, HTTP_X_RACE_KEY=KEY, GATEWAY_INTERFACE='CGI/1.1')
    p = subprocess.run([PHPCGI], input=raw, env=env, capture_output=True, timeout=60)
    head, _, out = p.stdout.partition(b'\r\n\r\n')
    status = 200
    for line in head.split(b'\r\n'):
        if line.lower().startswith(b'status:'):
            status = int(line.split()[1])
    try:
        return status, json.loads(out)
    except ValueError:
        return status, {'raw': out[:200].decode(errors='replace')}


def fix(mid, race=1, **extra):
    b = {'action': 'add', 'id': mid, 'series': 'Autumn League', 'date': DAY, 'race': race,
         'name': 'Gybe', 'lat': 51.81, 'lon': -8.31, 'acc': 3.5, 'time': 1790099999000}
    b.update(extra)
    return b


def intact(d, changed=()):
    """Every fixture fix still present and unchanged (except ids in `changed`)."""
    want, _ = fixture()
    try:
        have = load(day_file(d))
    except Exception:
        return False, f'day file unreadable ({size(day_file(d))} bytes)'
    lost = [k for k in want if k not in have]
    altered = [k for k in want if k in have and k not in changed and have[k] != want[k]]
    races = sorted({v['race'] for v in have.values()})
    return not lost and not altered, (f'{len(have)} fixes, races {races}' + (f', LOST {len(lost)}' if lost else '')
                                      + (f', ALTERED {altered}' if altered else ''))


results = []


def report(test, ok, detail):
    results.append((test, 'PASS' if ok else 'FAIL', detail))


# ---------------------------------------------------------------- tests
def t0_normal():
    d = setup('t0')
    s = [req(d, body=fix('newfix1', device=DEVICE, recorder='Pat'))[0],
         req(d, body=fix('newfix2', recorder='é' * 70))[0]]           # 140 bytes, 70 characters
    long_name = load(day_file(d))['newfix2']['recorder']
    s.append(req(d, body={'action': 'delete', 'id': 'newfix2', 'date': DAY})[0])
    st, g = req(d, 'GET', query=f'date={DAY}')
    s.append(st)
    got = {m['id']: m for m in g.get('marks', [])}
    n1 = got.get('newfix1', {})
    ok, detail = intact(d)
    good = (ok and s == [200] * 4 and n1.get('device') == DEVICE and n1.get('recorder') == 'Pat'
            and 'newfix2' not in got and len(long_name) == 60
            and all('device' not in m and 'recorder' not in m for k, m in got.items() if k != 'newfix1'))
    report('0 normal add / delete / GET', good,
           f'statuses {s}; long name kept as {len(long_name)} chars; {detail}')


def t1_encode():
    d = setup('t1')
    before = sha(day_file(d))
    # 1e400 decodes to INF: passes the time>0 check, and json_encode cannot write INF
    body = json.dumps(fix('inffix')).replace('1790099999000', '1e400').encode()
    s, j = req(d, body=body)
    ok, detail = intact(d)
    same = sha(day_file(d)) == before
    report('1a failed encode (fix)', ok and same and s == 500 and not leftovers(d),
           f'HTTP {s} {j.get("error", "")!r}; file {"unchanged" if same else "CHANGED"}; {detail}')

    before = sha(course_file(d))
    s, j = req(d, body=b'{"action":"course","date":"%s","key":"3|1","data":{"x":1e400}}' % DAY.encode())
    same = sha(course_file(d)) == before
    report('1b failed encode (course)', same and s == 500,
           f'HTTP {s} {j.get("error", "")!r}; courses file {"unchanged" if same else "CHANGED"}')


def t2_damaged():
    d = setup('t2')
    data = open(day_file(d), 'rb').read()
    open(day_file(d), 'wb').write(data[:len(data) // 2])            # a half-written file
    before = sha(day_file(d))
    s, j = req(d, body=fix('afterdamage'))
    same = sha(day_file(d)) == before
    report('2 damaged day file', same and s == 500,
           f'HTTP {s} {j.get("error", "")!r}; damaged file {"left for repair" if same else "OVERWRITTEN"}')


def t3_write_fails():
    d = setup('t3')
    before = sha(day_file(d))
    os.makedirs(day_file(d) + '.tmp')                               # temp path unusable -> write fails
    s, j = req(d, body=fix('writefail'))
    os.rmdir(day_file(d) + '.tmp')
    ok, detail = intact(d)
    same = sha(day_file(d)) == before
    report('3 write fails part-way', ok and same and s == 500 and not leftovers(d),
           f'HTTP {s} {j.get("error", "")!r}; file {"unchanged" if same else "CHANGED"}; {detail}')


def t4_moved():
    d = setup('t4')
    req(d, body=fix('movefix', race=1, device=DEVICE, recorder='Pat'))
    # what the RO course page sends when moving a fix: same id, new race, no device or recorder
    s, _ = req(d, body={'action': 'add', 'id': 'movefix', 'series': 'Autumn League', 'date': DAY, 'race': 2,
                        'name': 'Gybe', 'lat': 51.81, 'lon': -8.31, 'acc': 3.5, 'time': 1790099999000})
    m = load(day_file(d))['movefix']
    ok, detail = intact(d)
    report('4 moved fix keeps attribution',
           ok and s == 200 and m['race'] == 2 and m.get('device') == DEVICE and m.get('recorder') == 'Pat',
           f'HTTP {s}; race now {m["race"]}; device={m.get("device", "-")[:8]} recorder={m.get("recorder", "-")!r}; {detail}')


def t5_concurrent(run):
    d = setup(f't5-{run}')
    jobs = [('POST', fix(f'par{i:03d}', race=1 + i % 3, device=f'dev-{i % 4}', recorder=f'crew{i % 4}'), '')
            for i in range(60)]
    jobs += [('POST', {'action': 'course', 'date': DAY, 'key': f'{i}|2', 'data': {'legs': [i]}}, '')
             for i in range(1, 11)]
    jobs += [('GET', None, f'date={DAY}') for _ in range(30)]
    with cf.ThreadPoolExecutor(24) as ex:
        res = list(ex.map(lambda j: req(d, *j), jobs))
    posts = [r for j, r in zip(jobs, res) if j[0] == 'POST']
    gets = [r for j, r in zip(jobs, res) if j[0] == 'GET']
    have, courses = load(day_file(d)), load(course_file(d))
    missing = [i for i in range(60) if f'par{i:03d}' not in have]
    partial = sum(1 for s, g in gets if s != 200 or len(g.get('marks', [])) < 12)
    bad = [(s, r.get('error')) for s, r in posts if s != 200]
    ok, detail = intact(d)
    report(f'5 concurrent writes (run {run})',
           ok and not missing and not bad and not partial and len(courses) == 12 and not leftovers(d),
           f'{len(posts) - len(bad)}/{len(posts)} writes OK; fixes missing {len(missing)}; courses {len(courses)}/12; '
           f'reads seeing a partial day {partial}/30; {detail}')


def main():
    if not PHPCGI or not os.path.exists(PHPCGI):
        print('php-cgi not found: install PHP, or set PHP_CGI to the php-cgi executable')
        return 2
    try:
        for t in (t0_normal, t1_encode, t2_damaged, t3_write_fails, t4_moved):
            t()
        for run in (1, 2, 3):
            t5_concurrent(run)
    finally:
        shutil.rmtree(WORK, ignore_errors=True)
    w = max(len(r[0]) for r in results)
    for test, verdict, detail in results:
        print(f'{test:<{w}}  {verdict}  {detail}')
    failed = sum(r[1] != 'PASS' for r in results)
    print(f'\n{failed} test(s) failed' if failed else '\nall tests passed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
