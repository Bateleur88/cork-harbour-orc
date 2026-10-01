#!/usr/bin/env python3
"""Embed a fresh course-card snapshot in the race officer page.

    python scripts/rebuild_page.py WORKBOOK [--page pages/course/course_v8.html] [--dry-run]

The page is offline-first, so the snapshot from make_snapshot.py is embedded as
one line, `const CARD={...};`, rather than fetched. This replaces exactly that
line, and nothing else except PAGE_VERSION, which moves on so phones holding an
old copy reload: to today's date and .1, or the next number if already today.

Before writing it prints what changed in the snapshot, field by field, so a
release can be checked (after a workbook-only change, expect just meta.source
and meta.sha256). If the snapshot is already current the page is left alone.
--dry-run prints the changes and writes nothing.

Every run that is not --dry-run also writes index.html next to the page, a
byte-identical copy that is uploaded as /course/index.html. It is written from
the same bytes as the page, in the same step, even when the snapshot is already
current, so a copy left stale by an interrupted run is put right by the next.

Refuses, and writes nothing, if the page does not have exactly one CARD line
and one PAGE_VERSION, or if the result would not read back as the snapshot.
"""
import argparse
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_snapshot import build, dumps  # noqa: E402

CARD = 'const CARD='
VERSION = re.compile(r"const PAGE_VERSION='(\d{4}-\d{2}-\d{2})\.(\d+)';")


def changes(old, new, path=''):
    """Every leaf that differs between two snapshots, as (path, old, new)."""
    if isinstance(old, dict) and isinstance(new, dict):
        out = []
        for k in sorted(set(old) | set(new), key=str):
            if k not in old:
                out.append((f'{path}/{k}', None, new[k]))
            elif k not in new:
                out.append((f'{path}/{k}', old[k], None))
            else:
                out += changes(old[k], new[k], f'{path}/{k}')
        return out
    return [] if old == new else [(path, old, new)]


def write_both(page, copy, data):
    """Write the page and its upload copy from the same bytes. Both are written in full to .tmp files before
    either is renamed into place, then both are read back and must match."""
    try:
        for p in (page, copy):
            with open(p + '.tmp', 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        for p in (page, copy):
            os.replace(p + '.tmp', p)
    finally:
        for p in (page, copy):
            if os.path.exists(p + '.tmp'):
                os.remove(p + '.tmp')
    for p in (page, copy):
        if open(p, 'rb').read() != data:
            sys.exit(f'{p}: does not read back as written')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('workbook')
    ap.add_argument('--page', default=os.path.join('pages', 'course', 'course_v8.html'))
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    copy = os.path.join(os.path.dirname(a.page), 'index.html')
    if os.path.basename(a.page) == 'index.html':
        sys.exit(f'{a.page}: --page must be the source page, not its index.html copy; nothing written')

    page = open(a.page, encoding='utf-8', newline='').read()      # keep the page's own line endings
    lines = page.split('\n')
    at = [i for i, line in enumerate(lines) if line.startswith(CARD)]
    if len(at) != 1:
        sys.exit(f'{a.page}: expected one line starting {CARD!r}, found {len(at)}; nothing written')
    if len(VERSION.findall(page)) != 1:
        sys.exit(f'{a.page}: expected one PAGE_VERSION; nothing written')
    line = lines[at[0]]
    eol = '\r' if line.endswith('\r') else ''
    old = json.loads(line[len(CARD):].rstrip('\r').rstrip(';'))

    snap = build(a.workbook)
    diff = changes(old, snap)
    if [p for p, _, _ in diff] in ([], ['/meta/generated']):
        print(f'{a.page}: snapshot already current for {snap["meta"]["source"]}; page unchanged')
        if a.dry_run:
            print('dry run: nothing written')
            return 0
        write_both(a.page, copy, open(a.page, 'rb').read())
        print(f'{copy}: written, byte-identical to {a.page}')
        return 0
    print(f'snapshot changes ({len(diff)}):')
    for p, o, n in diff[:40]:
        print(f'  {p}: {json.dumps(o, ensure_ascii=False)[:70]} -> {json.dumps(n, ensure_ascii=False)[:70]}')
    if len(diff) > 40:
        print(f'  ... and {len(diff) - 40} more')

    day, n = VERSION.search(page).groups()
    today = datetime.date.today().isoformat()
    version = f'{today}.{int(n) + 1 if day == today else 1}'
    lines[at[0]] = CARD + dumps(snap) + ';' + eol
    out = VERSION.sub(f"const PAGE_VERSION='{version}';", '\n'.join(lines), count=1)

    back = json.loads([x for x in out.split('\n') if x.startswith(CARD)][0][len(CARD):].rstrip('\r').rstrip(';'))
    if back != snap:
        sys.exit('the rebuilt page does not read back as the snapshot; nothing written')
    if a.dry_run:
        print(f'dry run: would set PAGE_VERSION {day}.{n} -> {version}; nothing written')
        return 0
    write_both(a.page, copy, out.encode('utf-8'))
    print(f'{a.page}: embedded {snap["meta"]["source"]} ({snap["meta"]["sha256"][:12]}), '
          f'PAGE_VERSION {day}.{n} -> {version}')
    print(f'{copy}: written, byte-identical to {a.page}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
