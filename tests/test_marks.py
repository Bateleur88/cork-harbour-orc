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
  9  tap        the tap time (when Record was tapped) is stored and returned by GET; a fix without one (an old
                page) has none; a bad tap (a string, negative, zero, INF, a boolean, more than a day from the
                position's time) is dropped and the fix still accepted; moving a fix keeps its tap
 10  RO key     decision writes need the RO key from data/ro-key.php, in the X-RO-Key header only: missing file,
                CHANGE_ME, too short, bad characters, no <?php, two return lines are all "RO key not set"; a wrong
                header, or the right key only as ?ro_key=, is refused; a wrong race key is refused first; the
                commented example layout works; the RO key never appears in a response; course and series writes
                still need only the race key
 11  history    a course save keeps the replaced version in courses-history-DAY.json: the first version of the day
                plus the last 5; an identical save writes nothing (both files byte-identical); "by" is stored with a
                version (cut to 40 characters; not text, or with < >, dropped) and moves into the history with
                replaced_by; a new course has no history; GET ?type=coursehistory returns it (wrong key 403); the
                courses file holds no history
 12  hist cap   20 courses x 7 versions of ~45 KB: the history file stays within 5 MB, every course keeps its first
                version, the oldest non-first versions went first
 13  hist fails a damaged history file, or a history write failing, refuses the course save (500) and leaves both
                files unchanged; a course write failing after the history was written does not add the same version
                twice on the retry
 14  hist conc  20 saves of one course at once: all accepted, the history stays within first + last 5, starts with
                the original version, holds no version twice in a row, and no .tmp is left
 15  decisions  use-as (course rows and a line end), accept, do-not-use (reason required, race/start optional),
                revoke (copies race/start/role of what it undoes): stored with the server's time and the series; a
                retry of the same id writes nothing, the same id with other content is refused 409; 30 malformed
                records are each refused 400 and write nothing; the 2001st record of a day is refused 429;
                GET ?type=decisions returns them in order (wrong key 403)
 16  old pages  every request exactly as the current RIB and RO pages send them (fix add with tap, device and
                recorder; delete; a committee boat fix; a typed mark; a moved fix; a course save; a race's start
                groups; the series; the three GETs, with the source file and line of each) is accepted and stored as
                before, and creates no decisions file

Each throwaway folder gets its own key.js with a race key, and data/ro-key.php with an RO key, both generated at run
time; no real key is ever in this repository.
Fixture positions have 7 decimals, as marks.php stores them: PHP before 7.1 writes JSON numbers to 14
significant digits, so a position carrying more digits than marks.php ever writes would change on rewrite.

Exits non-zero if any test fails.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKS_PHP = os.path.join(ROOT, 'pages', 'marks', 'marks.php')
PHPCGI = os.environ.get('PHP_CGI') or shutil.which('php-cgi')
DAY = '2026-09-21'
KEY = 'test' + secrets.token_hex(8)          # dummy race key, made at run time
RO = secrets.token_hex(12)                   # dummy RO key (24 characters), made at run time
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


def req(d, method='POST', body=None, query='', key=KEY, ro=None, raw_out=None):
    raw = body if isinstance(body, bytes) else (json.dumps(body) if body is not None else '').encode()
    env = dict(os.environ, REQUEST_METHOD=method, SCRIPT_FILENAME=os.path.join(d, 'marks.php'),
               REDIRECT_STATUS='1', CONTENT_TYPE='application/json', CONTENT_LENGTH=str(len(raw)),
               QUERY_STRING=query, HTTP_X_RACE_KEY=key, GATEWAY_INTERFACE='CGI/1.1')
    if ro is not None:
        env['HTTP_X_RO_KEY'] = ro
    p = subprocess.run([PHPCGI], input=raw, env=env, capture_output=True, timeout=60)
    if raw_out is not None:
        raw_out.append(p.stdout)
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


def t9_tap():
    d = setup('t9')
    t = 1790099999000
    s = [req(d, body=fix('tapfix', device=DEVICE, recorder='Pat', tap=t + 2000))[0],
         req(d, body=fix('notap', device=DEVICE))[0]]                  # an old RIB page: no tap
    st, g = req(d, 'GET', query=f'date={DAY}')
    got = {m['id']: m for m in g.get('marks', [])}
    stored, returned = load(day_file(d)).get('tapfix', {}).get('tap'), got.get('tapfix', {}).get('tap')
    # each bad tap: the fix is accepted, stored without a tap
    bad = {'string': '1790100001000', 'negative': -5, 'zero': 0, 'boolean': True, 'null': None,
           'two days off': t + 2 * 86400000}
    dropped = {}
    for label, v in bad.items():
        mid = 'bad' + ''.join(c for c in label if c.isalnum())
        s_bad, _ = req(d, body=fix(mid, tap=v))
        dropped[label] = (s_bad, 'tap' in load(day_file(d)).get(mid, {'tap': 'MISSING FIX'}))
    raw = json.dumps(fix('badinf', tap=1)).replace('"tap": 1', '"tap": 1e400').encode()   # decodes to INF
    s_inf, _ = req(d, body=raw)
    dropped['INF'] = (s_inf, 'tap' in load(day_file(d)).get('badinf', {'tap': 'MISSING FIX'}))
    # the RO page moving the fix re-posts it without a tap: the tap stays
    s_move, _ = req(d, body={'action': 'add', 'id': 'tapfix', 'date': DAY, 'race': 2, 'name': 'Gybe',
                             'lat': 51.81, 'lon': -8.31, 'acc': 3.5, 'time': t})
    moved = load(day_file(d))['tapfix']
    ok, detail = intact(d)
    good = (ok and s == [200, 200] and st == 200 and stored == t + 2000 and returned == t + 2000
            and 'tap' not in got.get('notap', {'tap': 1}) and all(v == (200, False) for v in dropped.values())
            and s_move == 200 and moved['race'] == 2 and moved.get('tap') == t + 2000)
    report('9 tap time', good,
           f'statuses {s}; stored {stored!r}, GET {returned!r}; old page no tap {"tap" not in got.get("notap", {})}; '
           f'bad taps (status, kept?) {dropped}; after move race {moved["race"]} tap {moved.get("tap")!r}; {detail}')

# ---------------------------------------------------------------- RO key, course history, decisions
def history_file(d): return os.path.join(d, 'data', f'courses-history-{DAY}.json')
def decisions_file(d): return os.path.join(d, 'data', f'decisions-{DAY}.json')
def ro_file(d): return os.path.join(d, 'data', 'ro-key.php')


def put_ro(d, text):
    open(ro_file(d), 'w', encoding='utf-8', newline='').write(text)


def dec(rid, **f):
    """A decision request; the record is an accept of the Race 1 Windward unless fields say otherwise."""
    rec = {'id': rid, 'ref': 's:fixr1n2', 'action': 'accept', 'race': 1, 'start': 0, 'role': 'windward',
           'who': 'Test Scorer', 'client_when': 1791200000000}
    rec.update(f)
    for k in [k for k, v in rec.items() if v is None]:
        del rec[k]
    return {'action': 'decision', 'date': DAY, 'record': rec}


def course(k, data, by=None):
    b = {'action': 'course', 'date': DAY, 'key': k, 'data': data}
    if by is not None:
        b['by'] = by
    return b


def t10_ro_key():
    d = setup('t10')
    good = f"<?php\nreturn '{RO}';\n"
    files = {'no ro-key.php': None, 'CHANGE_ME': "<?php\nreturn 'CHANGE_ME';\n",
             'too short (15)': "<?php\nreturn 'abcdefghijklmno';\n", 'bad characters': "<?php\nreturn 'abcdefghijklmnop!';\n",
             'no <?php': f"return '{RO}';\n", 'two return lines': f"<?php\nreturn '{RO}';\nreturn '{RO}';\n"}
    outs, rows = [], []
    for label, text in files.items():
        if os.path.exists(ro_file(d)):
            os.remove(ro_file(d))
        if text is not None:
            put_ro(d, text)
        s, j = req(d, body=dec('rokey0001'), ro=RO, raw_out=outs)
        rows.append((label, s, j.get('error', '')))
    unset_ok = all(s == 403 and 'RO key not set' in e for _, s, e in rows) and not os.path.exists(decisions_file(d))
    put_ro(d, good)
    s_wrong, j_wrong = req(d, body=dec('rokey0002'), ro='x' * 24, raw_out=outs)
    s_query, _ = req(d, body=dec('rokey0003'), query=f'ro_key={RO}', raw_out=outs)      # the URL is never read
    s_race, j_race = req(d, body=dec('rokey0004'), ro=RO, key='wrong-race-key', raw_out=outs)
    none_written = not os.path.exists(decisions_file(d))
    s_ok, _ = req(d, body=dec('rokey0005'), ro=RO, raw_out=outs)
    put_ro(d, "<?php\n/* RO key for marks.php decision writes: 16-64 letters, digits, - or _ */\n"
              f"return '{RO}';\n?>\n")
    s_commented, _ = req(d, body=dec('rokey0006'), ro=RO, raw_out=outs)
    s_course, _ = req(d, body=course('3|1', {'legs': ['x']}))                             # race key only
    s_series, _ = req(d, body={'action': 'series', 'name': 'Autumn League'})
    leaked = any(RO.encode() in o for o in outs)
    stored = load(decisions_file(d)) if os.path.exists(decisions_file(d)) else {}
    report('10 RO key', unset_ok and s_wrong == 403 and j_wrong.get('error') == 'bad RO key' and s_query == 403
           and s_race == 403 and j_race.get('error') == 'bad key' and none_written and s_ok == 200
           and s_commented == 200 and sorted(stored) == ['rokey0005', 'rokey0006'] and s_course == 200
           and s_series == 200 and not leaked,
           f'unset cases {[(l, s) for l, s, _ in rows]} ({rows[0][2]!r}); wrong RO {s_wrong}; ?ro_key= only {s_query}; '
           f'wrong race key {s_race} {j_race.get("error")!r}; right {s_ok}; commented layout {s_commented}; '
           f'course {s_course} and series {s_series} on the race key; RO key in a response {leaked}')


def t11_history():
    d = setup('t11')
    original = load(course_file(d))['1|1']['data']
    s1, _ = req(d, body=course('1|1', {'legs': ['v1']}))
    h1 = load(history_file(d))['1|1']
    before = (sha(course_file(d)), sha(history_file(d)))
    s_same, j_same = req(d, body=course('1|1', {'legs': ['v1']}))
    unchanged = (sha(course_file(d)), sha(history_file(d))) == before and j_same.get('unchanged') is True
    for v in range(2, 9):
        req(d, body=course('1|1', {'legs': [f'v{v}']}))
    h = load(history_file(d))['1|1']
    want = [original] + [{'legs': [f'v{v}']} for v in range(3, 8)]          # first of the day + last 5 replaced
    kept = [e['data'] for e in h] == want and all(isinstance(e.get('replaced'), int) for e in h)
    # who saved a version
    req(d, body=course('1|1', {'legs': ['by1']}, by='  Test   Scorer  '))
    by_course = load(course_file(d))['1|1'].get('by')
    req(d, body=course('1|1', {'legs': ['by2']}, by='Other Scorer'))
    last = load(history_file(d))['1|1'][-1]
    req(d, body=course('1|1', {'legs': ['by3']}, by='x' * 45))
    cut = load(course_file(d))['1|1'].get('by')
    req(d, body=course('1|1', {'legs': ['by4']}, by=12345))
    dropped_num = 'by' not in load(course_file(d))['1|1']
    req(d, body=course('1|1', {'legs': ['by5']}, by='<b>me</b>'))
    dropped_tag = 'by' not in load(course_file(d))['1|1']
    req(d, body=course('4|1', {'legs': ['new']}))
    new_has_none = '4|1' not in load(history_file(d))
    s_get, g = req(d, 'GET', query=f'type=coursehistory&date={DAY}')
    s_bad, _ = req(d, 'GET', query=f'type=coursehistory&date={DAY}', key='wrong')
    no_hist_in_courses = all(k.count('|') == 1 and 'history' not in k for k in load(course_file(d)))
    report('11 course history', s1 == 200 and h1 and h1[0]['data'] == original and s_same == 200 and unchanged and kept
           and by_course == 'Test Scorer' and last.get('by') == 'Test Scorer' and last.get('replaced_by') == 'Other Scorer'
           and cut == 'x' * 40 and dropped_num and dropped_tag and new_has_none and s_get == 200
           and g.get('history', {}).get('1|1') == load(history_file(d))['1|1'] and s_bad == 403 and no_hist_in_courses,
           f'first kept {h1 and h1[0]["data"] == original}; identical save wrote nothing {unchanged}; '
           f'first + last 5 {kept} ({len(h)} versions); by {by_course!r} -> history by {last.get("by")!r} '
           f'replaced_by {last.get("replaced_by")!r}; 45 chars cut to {len(cut or "")}; number dropped {dropped_num}; '
           f'tags dropped {dropped_tag}; new course no history {new_has_none}; GET {s_get}, wrong key {s_bad}')


def t12_history_cap():
    d = setup('t12')
    jobs = [course(f'{k}|0', {'v': v, 'pad': 'x' * 45000}) for v in range(7) for k in range(1, 21)]
    st = [req(d, body=b)[0] for b in jobs]
    h = load(history_file(d))
    firsts = all(h[f'{k}|0'][0]['data']['v'] == 0 for k in range(1, 21))
    total = sum(len(v) for v in h.values())
    fits = size(history_file(d)) <= 5242880
    report('12 history cap', all(x == 200 for x in st) and fits and firsts and total < 20 * 6 and not leftovers(d),
           f'{sum(x == 200 for x in st)}/{len(st)} saves OK; history {size(history_file(d))} bytes (cap 5242880); '
           f'every first version kept {firsts}; {total} versions kept of {20 * 6} without the cap')


def t13_history_fails():
    d = setup('t13')
    req(d, body=course('1|1', {'legs': ['a']}))                                            # history now exists
    open(history_file(d), 'w').write('{"1|1": [{"data": ')                                 # damaged
    before = (sha(course_file(d)), sha(history_file(d)))
    s_dmg, j_dmg = req(d, body=course('1|1', {'legs': ['b']}))
    dmg_ok = s_dmg == 500 and (sha(course_file(d)), sha(history_file(d))) == before
    os.remove(history_file(d))
    os.makedirs(history_file(d) + '.tmp')                                                   # history write fails
    before = sha(course_file(d))
    s_wf, _ = req(d, body=course('1|1', {'legs': ['c']}))
    os.rmdir(history_file(d) + '.tmp')
    wf_ok = s_wf == 500 and sha(course_file(d)) == before and not os.path.exists(history_file(d))
    os.makedirs(course_file(d) + '.tmp')                                                    # course write fails after history
    s_cf, _ = req(d, body=course('1|1', {'legs': ['d']}))
    os.rmdir(course_file(d) + '.tmp')
    n1 = len(load(history_file(d))['1|1'])
    s_retry, _ = req(d, body=course('1|1', {'legs': ['d']}))
    n2 = len(load(history_file(d))['1|1'])
    report('13 history write fails', dmg_ok and wf_ok and s_cf == 500 and s_retry == 200 and n1 == n2 == 1
           and load(course_file(d))['1|1']['data'] == {'legs': ['d']} and not leftovers(d),
           f'damaged history: {s_dmg} {j_dmg.get("error", "")!r}, both files unchanged {dmg_ok}; failed history write: '
           f'{s_wf}, course unchanged {wf_ok}; course write failing after history {s_cf}, retry {s_retry}, '
           f'versions {n1} -> {n2} (not doubled)')


def t14_history_concurrent():
    d = setup('t14')
    original = load(course_file(d))['1|1']['data']
    jobs = [('POST', course('1|1', {'legs': [f'p{i}']}), '') for i in range(20)]
    with cf.ThreadPoolExecutor(10) as ex:
        res = list(ex.map(lambda j: req(d, *j), jobs))
    h = load(history_file(d))['1|1']
    datas = [json.dumps(e['data']) for e in h]
    report('14 history, saves at once', all(s == 200 for s, _ in res) and h[0]['data'] == original and len(h) <= 6
           and all(a != b for a, b in zip(datas, datas[1:])) and load(course_file(d))['1|1']['data'] != original
           and not leftovers(d),
           f'{sum(s == 200 for s, _ in res)}/20 OK; {len(h)} versions, first is the original {h[0]["data"] == original}; '
           f'none twice in a row {all(a != b for a, b in zip(datas, datas[1:]))}')


def t15_decisions():
    d = setup('t15')
    put_ro(d, f"<?php\nreturn '{RO}';\n")
    req(d, body={'action': 'series', 'name': 'Autumn League'})
    rows = [{'row': 1, 'ref': 's:fixr1n3'}, {'row': 3, 'ref': 's:fixr1n3'}]
    good = [dec('dec00001', action='use-as', role='leeward', ref='s:fixr3n3', **{'from': rows}),
            dec('dec00002', action='use-as', role='pin', ref='s:fixr1n1', **{'from': 'auto'}),
            dec('dec00003'),
            dec('dec00004', action='do-not-use', ref='s:fixr1n3', race=None, start=None, role=None, note='moved after the wind shift'),
            dec('dec00005', action='do-not-use', ref='s:fixr2n3', role=None, note='checked: wrong mark'),
            dec('dec00006', action='revoke', ref='s:fixr3n3', revokes='dec00001', race=None, start=None, role=None)]
    st = [req(d, body=b, ro=RO)[0] for b in good]
    all_ = load(decisions_file(d))
    rv = all_.get('dec00006', {})
    shaped = (list(all_) == [b['record']['id'] for b in good] and all(isinstance(r.get('when'), int) for r in all_.values())
              and all(r.get('series') == 'Autumn League' for r in all_.values())
              and rv.get('race') == 1 and rv.get('start') == 0 and rv.get('role') == 'leeward'
              and 'race' not in all_['dec00004'] and all_['dec00005'].get('race') == 1)
    before = sha(decisions_file(d))
    s_dup, j_dup = req(d, body=good[2], ro=RO)
    s_rv_dup, _ = req(d, body=good[5], ro=RO)
    s_409, _ = req(d, body=dec('dec00003', role='leeward'), ro=RO)
    retry_ok = s_dup == 200 and j_dup.get('duplicate') is True and s_rv_dup == 200 and s_409 == 409 and sha(decisions_file(d)) == before
    bad = {
        'not a record': {'action': 'decision', 'date': DAY, 'record': ['x']},
        'no record': {'action': 'decision', 'date': DAY},
        'bad action': dec('bad00001', action='delete'),
        'unknown field': dec('bad00002', colour='red'),
        'short id': dec('short'),
        'local ref': dec('bad00003', ref='l:1|windward|1'),
        'no such fix': dec('bad00004', ref='s:nosuchfix'),
        'race 0': dec('bad00005', race=0),
        'race as text': dec('bad00006', race='1'),
        'start 10': dec('bad00007', start=10),
        'bad role': dec('bad00008', role='offset'),
        'use-as without from': dec('bad00009', action='use-as', role='leeward'),
        'from row -1': dec('bad00010', action='use-as', role='leeward', **{'from': [{'row': -1, 'ref': 's:fixr1n3'}]}),
        'from row extra key': dec('bad00011', action='use-as', role='leeward', **{'from': [{'row': 1, 'ref': 's:fixr1n3', 'x': 1}]}),
        'from empty list': dec('bad00012', action='use-as', role='leeward', **{'from': []}),
        'line from as list': dec('bad00013', action='use-as', role='pin', **{'from': rows}),
        'accept with from': dec('bad00014', **{'from': 'auto'}),
        'do-not-use without note': dec('bad00015', action='do-not-use', role=None),
        'do-not-use blank note': dec('bad00016', action='do-not-use', role=None, note='   '),
        'do-not-use with role': dec('bad00017', action='do-not-use', note='x'),
        'revoke unknown id': dec('bad00018', action='revoke', revokes='nosuch0001', race=None, start=None, role=None),
        'revoke a revoke': dec('bad00019', action='revoke', revokes='dec00006', ref='s:fixr3n3', race=None, start=None, role=None),
        'revoke twice': dec('bad00020', action='revoke', revokes='dec00001', ref='s:fixr3n3', race=None, start=None, role=None),
        'revoke other fix': dec('bad00021', action='revoke', revokes='dec00003', ref='s:fixr3n3', race=None, start=None, role=None),
        'revoke itself': dec('bad00022', action='revoke', revokes='bad00022', race=None, start=None, role=None),
        'no who': dec('bad00023', who=None),
        'who 41 characters': dec('bad00024', who='x' * 41),
        'who with <': dec('bad00025', who='<script>'),
        'note 201 characters': dec('bad00026', note='x' * 201),
        'note with a control character': dec('bad00027', note='a\x07b'),
        'note with <': dec('bad00029', note='less than <5 m'),
        'client_when as text': dec('bad00028', client_when='today'),
    }
    refused, errors = {}, {}
    for label, b in bad.items():
        s, j = req(d, body=b, ro=RO)
        refused[label] = s
        errors[label] = j.get('error')
    angle_text = errors['who with <'] == 'bad decision: who' and errors['note with <'] == 'bad decision: note'
    none_written = sha(decisions_file(d)) == before
    s_get, g = req(d, 'GET', query=f'type=decisions&date={DAY}')
    s_get_bad, _ = req(d, 'GET', query=f'type=decisions&date={DAY}', key='wrong')
    order = [r['id'] for r in g.get('decisions', [])] == [b['record']['id'] for b in good]
    # the cap: a day already holding 2000 records refuses the next
    full = {f'cap{i:05d}': {'id': f'cap{i:05d}', 'ref': 's:fixr1n2', 'action': 'accept', 'race': 1, 'start': 0,
                            'role': 'windward', 'who': 'x', 'when': 1, 'series': ''} for i in range(2000)}
    json.dump(full, open(decisions_file(d), 'w'))
    s_cap, _ = req(d, body=dec('cap99999'), ro=RO)
    report('15 decisions', all(x == 200 for x in st) and shaped and retry_ok and all(v == 400 for v in refused.values())
           and angle_text and none_written and s_get == 200 and order and s_get_bad == 403 and s_cap == 429,
           f'valid {st}; stored with server time, series, revoke copies race/start/role, do-not-use race optional {shaped}; '
           f'retry {s_dup} {j_dup.get("duplicate")}, same id other content {s_409}, file unchanged {retry_ok}; '
           f'malformed refused 400: {sum(v == 400 for v in refused.values())}/{len(refused)}'
           + (f' (NOT 400: {[(k, v) for k, v in refused.items() if v != 400]})' if any(v != 400 for v in refused.values()) else '')
           + f'; < in who / note: {errors["who with <"]!r} / {errors["note with <"]!r}; nothing written {none_written}; GET {s_get} in order {order}, wrong key {s_get_bad}; 2001st {s_cap}')


def t16_old_pages():
    """Every request exactly as the current pages send it (the same fields, in the same order). Sources:
    pages/record/record.html   line 219  fix add       {action,id,date,race,name,lat,lon,acc,time,tap,device,recorder}
                               line 224  fix delete    {action,id,date}
    pages/course/course_v8.html
                               line 1783 GET ?date=
                               line 1820 GET ?type=courses&date=
                               line 1858 moved fix     {action,id,date,race,name,lat,lon,acc,time}  (moveFix)
                               line 1924 course save   {action,date,key,data}, data from recordFor (lines 1894-1903):
                                         {entries:[{ref,side}],startTime,finish,lineSel,wind:{twd,tws},card}, or for
                                         _starts|race {classes}
                               line 2004 series        {action,name}
                               line 2006 GET ?type=series
                               line 2030 committee boat fix, sent from the outbox  {action,id,date,race,name,lat,lon,acc,time}
                               line 2088 typed mark, sent from the outbox          {action,id,date,race,name,lat,lon,acc:0,time}
    Line numbers are those of commit d7abc2f."""
    d = setup('t16')
    t = 1791200000000
    reqs = [
        ('RIB add (record.html 219)', {'action': 'add', 'id': 'ribfix0001', 'date': DAY, 'race': 2, 'name': 'Leeward',
                                       'lat': 51.82, 'lon': -8.28, 'acc': 4.2, 'time': t, 'tap': t + 2000,
                                       'device': DEVICE, 'recorder': 'Crew'}),
        ('RIB delete (record.html 224)', {'action': 'delete', 'id': 'ribfix0001', 'date': DAY}),
        ('RIB add, no recorder (record.html 219)', {'action': 'add', 'id': 'ribfix0002', 'date': DAY, 'race': 1,
                                                    'name': 'Gybe', 'lat': 51.8, 'lon': -8.3, 'acc': 3.1, 'time': t,
                                                    'tap': t + 1000, 'device': DEVICE, 'recorder': ''}),
        ('RO committee boat (course_v8 2030)', {'action': 'add', 'id': 'cbfix00001', 'date': DAY, 'race': 1,
                                                'name': 'Committee boat', 'lat': 51.81, 'lon': -8.3, 'acc': 6.5,
                                                'time': t}),
        ('RO typed mark (course_v8 2088)', {'action': 'add', 'id': 'typed00001', 'date': DAY, 'race': 1,
                                            'name': 'Offset', 'lat': 51.81, 'lon': -8.29, 'acc': 0, 'time': t}),
        ('RO moved fix (course_v8 1858)', {'action': 'add', 'id': 'ribfix0002', 'date': DAY, 'race': 3, 'name': 'Gybe',
                                           'lat': 51.8, 'lon': -8.3, 'acc': 3.1, 'time': t}),
        ('RO course save (course_v8 1924)', {'action': 'course', 'date': DAY, 'key': '1|1', 'data': {
            'entries': [{'ref': 's:fixr1n2', 'side': ''}, {'ref': 's:fixr1n3', 'side': 'P'}], 'startTime': '11:11',
            'finish': 'start', 'lineSel': {'pin': 's:fixr1n1'}, 'wind': {'twd': '250', 'tws': '12'}, 'card': None}}),
        ('RO start groups (course_v8 1924)', {'action': 'course', 'date': DAY, 'key': '_starts|1',
                                              'data': {'classes': [['Class 1 Spinnaker'], ['Class 2 Spinnaker']]}}),
        ('RO series (course_v8 2004)', {'action': 'series', 'name': 'Autumn League'}),
    ]
    st = {label: req(d, body=b)[0] for label, b in reqs}
    gets = {q: req(d, 'GET', query=q)[0] for q in (f'date={DAY}', f'type=courses&date={DAY}', 'type=series')}
    have = load(day_file(d))
    moved = have.get('ribfix0002', {})
    cs = load(course_file(d))
    stored_ok = ('ribfix0001' not in have and moved.get('race') == 3 and moved.get('device') == DEVICE
                 and moved.get('tap') == t + 1000 and have.get('typed00001', {}).get('acc') == 0
                 and have.get('cbfix00001', {}).get('name') == 'Committee boat'
                 and cs['1|1']['data']['startTime'] == '11:11' and cs['_starts|1']['data']['classes'][1] == ['Class 2 Spinnaker']
                 and 'by' not in cs['1|1'])
    ok, detail = intact(d)
    report('16 old pages unchanged', ok and all(v == 200 for v in st.values()) and all(v == 200 for v in gets.values())
           and stored_ok and not os.path.exists(decisions_file(d)),
           f'POSTs {st}; GETs {gets}; stored as before {stored_ok}; no decisions file '
           f'{not os.path.exists(decisions_file(d))}; {detail}')


def main():
    if not PHPCGI or not os.path.exists(PHPCGI):
        print('php-cgi not found: install PHP, or set PHP_CGI to the php-cgi executable')
        return 2
    print(subprocess.run([PHPCGI, '-v'], capture_output=True, text=True).stdout.splitlines()[0])
    try:
        for t in (t0_normal, t1_encode, t2_damaged, t3_write_fails, t4_moved, t6_key, t7_race_groups, t8_series, t9_tap,
                  t10_ro_key, t11_history, t12_history_cap, t13_history_fails, t14_history_concurrent, t15_decisions,
                  t16_old_pages):
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
