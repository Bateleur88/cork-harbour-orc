#!/usr/bin/env python3
"""One-off backfill (STATUS A8): write a race day's series as its "_day" record, through marks.php.

    python scripts/backfill_day_series.py --url https://<host>/marks-test/marks.php --backup-dir <folder>
        [--key-js <path to key.js>] [--series "Autumn League"] [--dates 2026-09-27,2026-10-04,2026-10-11] [--dry-run]

Prepared for the days raced before the series name became per day (PAGE_VERSION 2026-10-06.38): by default "Autumn
League" into 27 September, 4, 11 and 18 October 2026 (Pat, 16 October 2026). A listed day not raced (18 October if the
race is cancelled) is refused, named with the reason, and the other days are still written.
Every write is an ordinary course save of the "_day" key ({"action":"course","key":"_day","data":{"series":...}}), so
marks.php's lock and course history apply exactly as for a save from the RO page. Nothing else is written; series.json
is not touched.

In order, and nothing is written unless every step before it passed:
  1. Backup. For each day: GET its courses, course history and fixes, written to a new folder under --backup-dir
     (backfill_<series>_<time>), each as the object marks.php returns (courses-DAY.json and courses-history-DAY.json
     hold exactly what the day's files hold), with a SHA-256 list (backup.sha256.csv).
  2. Backup check. Each file is read back from disk and must match its SHA-256 and parse to what the server returned;
     the courses are fetched a second time and must be unchanged (nothing else was saving).
  3. Refusals, per day: a day whose courses already hold a _day series is refused and left alone; so is a day with no
     courses and no fixes (not raced, e.g. a cancelled race). The run carries on: the others are written.
  4. Write, then check: each day's courses must now hold _day with the series and every other record exactly as in
     the backup, and its course history must be unchanged.
--dry-run stops after step 3. The race key is read from --key-js (the key.js the pages load) or typed at the prompt;
it is never printed or written anywhere. Exit status: 0 all days written (or, with --dry-run, all would be); 3 a day
was refused; 1 anything failed (stops at once; days already written stay written, the backup is the way back).
Rollback: restore the day's courses-DAY.json from the backup folder to the data folder (the _day record has no earlier
version, so the course history has nothing to restore).
"""
import argparse
import datetime
import getpass
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_DATES = ['2026-09-27', '2026-10-04', '2026-10-11', '2026-10-18']


class Stop(Exception):
    pass


def race_key(path):
    if not path:
        k = getpass.getpass('Race key (not shown): ')
    else:
        m = re.search(r"RACE_KEY\s*=\s*'([^'\\]{6,})'", open(path, encoding='utf-8').read())
        if not m or m.group(1) == 'CHANGE_ME':
            raise Stop(f'{path}: no usable race key in it')
        k = m.group(1)
    if not k:
        raise Stop('no race key')
    return k


def call(url, key, query=None, body=None):
    u = url + ('?' + urllib.parse.urlencode(query) if query else '')
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(u, data=data, method='POST' if data is not None else 'GET',
                                 headers={'X-Race-Key': key, 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            status = r.status
    except urllib.error.HTTPError as e:
        raw, status = e.read(), e.code
    except OSError as e:
        raise Stop(f'cannot reach {url}: {e}')
    try:
        j = json.loads(raw.decode('utf-8'))
    except ValueError:
        raise Stop(f'{u}: HTTP {status}, not JSON: {raw[:120]!r}')
    if status != 200 or not j.get('ok'):
        raise Stop(f'{u}: HTTP {status}: {j.get("error", j)}')
    return j


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1).encode('utf-8')


def day_series(courses):
    d = courses.get('_day')
    s = d.get('data', {}).get('series') if isinstance(d, dict) and isinstance(d.get('data'), dict) else None
    return s if isinstance(s, str) and s.strip() else ''


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--url', required=True, help='marks.php, e.g. https://<host>/marks-test/marks.php')
    ap.add_argument('--backup-dir', required=True, help='folder outside the repository for the backup')
    ap.add_argument('--key-js', help='the key.js the pages load (else the key is asked for)')
    ap.add_argument('--series', default='Autumn League')
    ap.add_argument('--dates', default=','.join(DEFAULT_DATES), help='comma-separated YYYY-MM-DD')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args(argv)
    try:
        dates = [d.strip() for d in a.dates.split(',') if d.strip()]
        if not dates or not all(re.fullmatch(r'\d{4}-\d{2}-\d{2}', d) for d in dates) or len(set(dates)) != len(dates):
            raise Stop(f'bad --dates {a.dates!r}')
        series = re.sub(r'\s+', ' ', a.series).strip()
        if not series or len(series) > 60 or re.search(r'[\x00-\x1f\x7f<>]', series):
            raise Stop(f'bad --series {a.series!r}: 1 to 60 characters, no < or >')
        key = race_key(a.key_js)
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        root = os.path.abspath(a.backup_dir)
        nc = lambda p: os.path.normcase(os.path.realpath(p))
        if nc(root) == nc(here) or nc(root).startswith(nc(here) + os.sep):
            raise Stop('the backup folder must be outside the repository')
        out = os.path.join(root, 'backfill_' + re.sub(r'[^A-Za-z0-9]+', '-', series) + '_' +
                           datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
        os.makedirs(out)                          # a new folder: refuses one that exists

        # 1. backup
        got, rows = {}, []
        for d in dates:
            c = call(a.url, key, {'type': 'courses', 'date': d})['courses']
            h = call(a.url, key, {'type': 'coursehistory', 'date': d})['history']
            m = call(a.url, key, {'date': d})['marks']
            got[d] = {'courses': c, 'history': h, 'marks': m}
            for name, obj in ((f'courses-{d}.json', c), (f'courses-history-{d}.json', h), (f'marks-{d}.api.json', m)):
                b = dump(obj)
                with open(os.path.join(out, name), 'wb') as f:
                    f.write(b)
                rows.append((name, hashlib.sha256(b).hexdigest(), len(b)))
        with open(os.path.join(out, 'backup.sha256.csv'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('file,sha256,bytes\n' + ''.join(f'{n},{s},{z}\n' for n, s, z in rows))
        print(f'Backup: {len(rows)} files in {out}')

        # 2. backup check
        for n, s, z in rows:
            b = open(os.path.join(out, n), 'rb').read()
            d = n[-15:-5] if not n.endswith('.api.json') else n[6:16]
            want = got[d]['courses' if n.startswith('courses-2') else 'history' if n.startswith('courses-history') else 'marks']
            if hashlib.sha256(b).hexdigest() != s or len(b) != z or json.loads(b.decode('utf-8')) != want:
                raise Stop(f'backup check failed for {n}')
        for d in dates:
            if call(a.url, key, {'type': 'courses', 'date': d})['courses'] != got[d]['courses']:
                raise Stop(f'{d}: the courses changed while the backup was taken; nothing written')
        print('Backup checked: every file matches its SHA-256 and the server; the courses did not change meanwhile.')

        # 3. refusals
        todo, refused = [], []
        for d in dates:
            c, m = got[d]['courses'], got[d]['marks']
            if day_series(c):
                refused.append((d, f'already has the series {day_series(c)!r}: left alone'))
            elif not [k for k in c if k != '_day'] and not m:
                refused.append((d, 'no courses and no fixes on this day (not raced): left alone'))
            else:
                todo.append(d)
        for d, why in refused:
            print(f'REFUSED {d}: {why}')
        if a.dry_run:
            print('Dry run: would write ' + (', '.join(todo) or 'nothing') + '. Nothing written.')
            return 3 if refused else 0

        # 4. write, then check
        for d in todo:
            call(a.url, key, body={'action': 'course', 'date': d, 'key': '_day', 'data': {'series': series}})
            c = call(a.url, key, {'type': 'courses', 'date': d})['courses']
            h = call(a.url, key, {'type': 'coursehistory', 'date': d})['history']
            rest = {k: v for k, v in c.items() if k != '_day'}
            if day_series(c) != series or rest != got[d]['courses'] or h != got[d]['history']:
                raise Stop(f'{d}: written, but the check after it failed: restore courses-{d}.json from {out}')
            print(f'Written {d}: _day series {series!r}; every other record and the course history unchanged.')
        return 3 if refused else 0
    except Stop as e:
        print('STOPPED: ' + str(e), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
