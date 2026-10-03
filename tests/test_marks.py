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
  5  parallel   60 fixes, 10 courses, 9 races' start groups and 30 reads at once: nothing lost, no reader
                sees a partial day
  6  key        a missing key.js, or one still holding the CHANGE_ME placeholder, refuses every request,
                even one sending an empty key; a wrong key is refused
  7  groups     each race's start groups (_starts|race) are kept apart: saving one race's groups leaves the
                other race's, the old day-wide _starts and every course unchanged; malformed keys refused
  8  series     the series name: unset reads as ""; saved (spaces collapsed, 60 characters not bytes), read back,
                cleared; a wrong key is refused 403 on GET and POST; a name over 60 characters or not a string is
                refused 400, a body that is not UTF-8 refused 400 before it is read; a write failing part-way
                is refused 500 by save_json; each refusal leaves series.json unchanged; a fix carrying a long
                "series" (an old page) is accepted and stored without one

Each throwaway folder gets its own key.js with a test key; the real key is never in this repository.
Fixture positions have 7 decimals, as marks.php stores them: PHP before 7.1 writes JSON numbers to 14
significant digits, so a position carrying more digits than marks.php ever writes would change on rewrite.

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
KEY = 'test-key-not-the-real-one'
DEVICE = '55ac7020-9dbc-4c45-a094-364f1bee1890'
WORK = tempfile.mkdtemp(prefix='marks-test-')


def fixture():
    """Races 1-3, four fixes each, none carrying device or recorder (as older fixes don't)."""
    marks = {}
    for race in (1, 2, 3):
        for i, name in enumerate(['Committee boat', 'Start Pin', 'Windward', 'Leeward']):
            mid = f'fixr{race}n{i}'
            marks[mid] = {'id': mid, 'series': 'Autumn League', 'date': DAY, 'race': race, 'name': name,
                          'lat': round(51.80 + i / 1000, 7), 'lon': round(-8.30 - race / 1000, 7), 'acc': 4.0,
                          'time': 1790000000000 + race * 100000 + i, 'received': 1790000000}
    courses = {'1|1': {'data': {'legs': ['Windward', 'Leeward']}, 'updated': 1790000000},
               '2|1': {'data': {'legs': ['A', 'B']}, 'updated': 1790000001}}
    return marks, courses


def setup(name, key=KEY):
    d = os.path.join(WORK, name)
    os.makedirs(os.path.join(d, 'data'))
    shutil.copy(MARKS_PHP, os.path.join(d, 'marks.php'))
    if key is not None:                     # key.js exactly as the pages load it
        open(os.path.join(d, 'key.js'), 'w').write(f"window.RACE_KEY='{key}';\n")
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


def req(d, method='POST', body=None, query='', key=KEY):
    raw = body if isinstance(body, bytes) else (json.dumps(body) if body is not None else '').encode()
    env = dict(os.environ, REQUEST_METHOD=method, SCRIPT_FILENAME=os.path.join(d, 'marks.php'),
               REDIRECT_STATUS='1', CONTENT_TYPE='application/json', CONTENT_LENGTH=str(len(raw)),
               QUERY_STRING=query, HTTP_X_RACE_KEY=key, GATEWAY_INTERFACE='CGI/1.1')
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
    # what an RO course page not yet reloaded sends when moving a fix: same id, new race, a series, no device or recorder
    s, _ = req(d, body={'action': 'add', 'id': 'movefix', 'series': 'Autumn League', 'date': DAY, 'race': 2,
                        'name': 'Gybe', 'lat': 51.81, 'lon': -8.31, 'acc': 3.5, 'time': 1790099999000})
    m = load(day_file(d))['movefix']
    ok, detail = intact(d)
    report('4 moved fix keeps attribution',
           ok and s == 200 and m['race'] == 2 and m.get('device') == DEVICE and m.get('recorder') == 'Pat'
           and 'series' not in m,
           f'HTTP {s}; race now {m["race"]}; device={m.get("device", "-")[:8]} recorder={m.get("recorder", "-")!r}; '
           f'series {"not stored" if "series" not in m else repr(m["series"])}; {detail}')


def t5_concurrent(run):
    d = setup(f't5-{run}')
    jobs = [('POST', fix(f'par{i:03d}', race=1 + i % 3, device=f'dev-{i % 4}', recorder=f'crew{i % 4}'), '')
            for i in range(60)]
    jobs += [('POST', {'action': 'course', 'date': DAY, 'key': f'{i}|2', 'data': {'legs': [i]}}, '')
             for i in range(1, 11)]
    jobs += [('POST', {'action': 'course', 'date': DAY, 'key': f'_starts|{r}', 'data': {'classes': [[f'C{r}']]}}, '')
             for r in range(1, 10)]
    jobs += [('GET', None, f'date={DAY}') for _ in range(30)]
    with cf.ThreadPoolExecutor(24) as ex:
        res = list(ex.map(lambda j: req(d, *j), jobs))
    posts = [r for j, r in zip(jobs, res) if j[0] == 'POST']
    gets = [r for j, r in zip(jobs, res) if j[0] == 'GET']
    have, courses = load(day_file(d)), load(course_file(d))
    missing = [i for i in range(60) if f'par{i:03d}' not in have]
    partial = sum(1 for s, g in gets if s != 200 or len(g.get('marks', [])) < 12)
    bad = [(s, r.get('error')) for s, r in posts if s != 200]
    groups_ok = all(courses.get(f'_starts|{r}', {}).get('data') == {'classes': [[f'C{r}']]} for r in range(1, 10))
    ok, detail = intact(d)
    report(f'5 concurrent writes (run {run})',
           ok and not missing and not bad and not partial and len(courses) == 21 and groups_ok and not leftovers(d),
           f'{len(posts) - len(bad)}/{len(posts)} writes OK; fixes missing {len(missing)}; courses {len(courses)}/21; '
           f'race groups all kept {groups_ok}; '
           f'reads seeing a partial day {partial}/30; {detail}')


def t6_key():
    """No usable key.js must lock everything, including a request that sends an empty key."""
    cases = []
    for label, file_key in (('no key.js', None), ('CHANGE_ME placeholder', 'CHANGE_ME')):
        d = setup('t6-' + label.split()[0], key=file_key)
        before = sha(day_file(d))
        for sent in (KEY, '', 'CHANGE_ME'):
            s_get, _ = req(d, 'GET', query=f'date={DAY}', key=sent)
            s_post, j = req(d, body=fix('keytest'), key=sent)
            cases.append((label, sent or "''", s_get, s_post, j.get('error')))
        cases.append((label, 'file untouched', sha(day_file(d)) == before, None, None))
    d = setup('t6-wrong')
    s_wrong, _ = req(d, 'GET', query=f'date={DAY}', key='wrong-key')
    s_right, _ = req(d, 'GET', query=f'date={DAY}')
    locked = all(c[2] == 500 and c[3] == 500 for c in cases if c[1] != 'file untouched')
    untouched = all(c[2] for c in cases if c[1] == 'file untouched')
    report('6 key configuration', locked and untouched and s_wrong == 403 and s_right == 200,
           f'missing or placeholder key.js: every GET/POST refused 500 ({cases[0][4]!r}) incl. empty key; '
           f'files untouched {untouched}; wrong key {s_wrong}; right key {s_right}')


def t7_race_groups():
    d = setup('t7')
    day_wide = {'classes': [['Class 1 Non Spinnaker', 'Class 2 Non Spinnaker'], ['Class 3 Spinnaker']]}
    r1 = {'classes': [['Class 1 Non Spinnaker', 'Class 2 Non Spinnaker'], ['Class 3 Spinnaker'],
                      ['Class 1 Spinnaker', 'Class 2 Spinnaker']]}
    r2 = {'classes': [['Class 3 Spinnaker'], ['Class 1 Spinnaker', 'Class 2 Spinnaker'],
                      ['Class 1 Non Spinnaker', 'Class 2 Non Spinnaker']]}
    post = lambda k, data: req(d, body={'action': 'course', 'date': DAY, 'key': k, 'data': data})[0]
    s = [post('_starts', day_wide), post('_starts|1', r1), post('_starts|2', r2)]
    c = load(course_file(d))
    _, want = fixture()
    kept = (c.get('_starts', {}).get('data') == day_wide and c.get('_starts|1', {}).get('data') == r1
            and c.get('_starts|2', {}).get('data') == r2 and all(c.get(k) == v for k, v in want.items()))
    before = sha(course_file(d))
    bad = {k: post(k, r1) for k in ('_starts|', '_starts|0', '_starts|10', '_starts|x', '_starts1', 'x_starts|1',
                                     '_starts|1|2', '_starts|1\n')}
    refused = all(v == 400 for v in bad.values()) and sha(course_file(d)) == before
    ok, detail = intact(d)
    report('7 start groups per race', ok and s == [200] * 3 and kept and refused,
           f'statuses {s}; day-wide, race 1, race 2 and courses all kept {kept}; '
           f'malformed keys {sorted(set(bad.values()))}, file {"unchanged" if refused else "CHANGED"}; {detail}')


def series_file(d): return os.path.join(d, 'data', 'series.json')


def t8_series():
    d = setup('t8')
    put = lambda name, key=KEY: req(d, body={'action': 'series', 'name': name}, key=key)
    get = lambda key=KEY: req(d, 'GET', query='type=series', key=key)
    s_unset, g = get()
    unset = g.get('name')
    s = [put('  Autumn \t  League ')[0]]
    collapsed = get()[1].get('name')
    s.append(put('é' * 60)[0])                                       # 60 characters, 120 bytes
    sixty = get()[1].get('name')
    s.append(put('Autumn League')[0])
    s_saved, g = get()
    saved, before = g.get('name'), sha(series_file(d))
    # refusals: each must leave series.json byte-for-byte as it was
    refused = {'61 chars': put('x' * 61), 'not a string': put(5),
               'not UTF-8': req(d, body=b'{"action":"series","name":"Autumn \xff League"}'),
               'wrong key POST': put('Frostbite', key='wrong-key'), 'wrong key GET': get(key='wrong-key')}
    os.makedirs(series_file(d) + '.tmp')                            # temp path unusable -> save_json's fopen fails
    refused['write fails'] = put('Frostbite')
    os.rmdir(series_file(d) + '.tmp')
    want = {'61 chars': (400, 'series name too long'), 'not a string': (400, 'bad series'),
            'not UTF-8': (400, 'bad body'), 'wrong key POST': (403, 'bad key'), 'wrong key GET': (403, 'bad key'),
            'write fails': (500, 'could not write, series.json unchanged')}
    got = {k: (st, j.get('error')) for k, (st, j) in refused.items()}
    kept = sha(series_file(d)) == before and get()[1].get('name') == 'Autumn League' and not leftovers(d)
    s.append(req(d, body=fix('oldpage', series='S' * 500))[0])       # an old RIB page, long series
    stored = load(day_file(d)).get('oldpage', {})
    s.append(put('')[0])
    cleared = get()[1].get('name')
    ok, detail = intact(d)
    report('8 series name', ok and s_unset == 200 and unset == '' and s == [200] * 5 and collapsed == 'Autumn League'
           and sixty == 'é' * 60 and s_saved == 200 and saved == 'Autumn League' and got == want and kept
           and bool(stored) and 'series' not in stored and cleared == '',
           f'unset {unset!r}; statuses {s}; refused {got}; series.json {"unchanged" if kept else "CHANGED"}; '
           f'old-page fix {"stored without series" if stored and "series" not in stored else stored}; {detail}')


def main():
    if not PHPCGI or not os.path.exists(PHPCGI):
        print('php-cgi not found: install PHP, or set PHP_CGI to the php-cgi executable')
        return 2
    print(subprocess.run([PHPCGI, '-v'], capture_output=True, text=True).stdout.splitlines()[0])
    try:
        for t in (t0_normal, t1_encode, t2_damaged, t3_write_fails, t4_moved, t6_key, t7_race_groups, t8_series):
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
