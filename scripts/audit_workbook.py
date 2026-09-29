#!/usr/bin/env python3
"""Pre-release audit of the Cork Harbour ORC master workbook.

    python scripts/audit_workbook.py workbook.xlsx

Read-only. Prints a report and exits non-zero if any check fails, so it can gate
a commit. Checks, in order:

  1  structure      sheets present, Numbered Legs and ORC row-for-row aligned
  2  completeness   every course x start x finish configuration present
  3  continuity     legs numbered 1..n, each starting where the last ended,
                    first leg from the start option, last leg to the finish option
  4  geometry       every stored distance and bearing recomputed as a WGS84 geodesic
  5  invariant      every VERIFIED passage physically expanded at every occurrence
  6  passages       one authoritative row per directed pair, no empty passages
  7  card           routed sequences match the printed course card text
  8  evidence       every physical chord carries numeric evidence in Evidence Register
  9  marks          every mark referenced by the routing exists with coordinates
"""
import re
import sys
import hashlib
import collections

import pandas as pd

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from geo import vincenty, marks_from_workbook  # noqa: E402

KEY = ['Course', 'Start Option', 'Finish Option']
STARTS = ['Grassy Mid', 'No.8', 'Dosco']
DIST_TOL_NM = 0.001      # stored to 3 dp
BRG_TOL_DEG = 0.06       # stored to 1 dp

fails, notes = [], []


def check(ok, label, detail=''):
    (notes if ok else fails).append(f'{"PASS" if ok else "FAIL"}  {label}' + (f'  {detail}' if detail else ''))
    return ok


def card_marks(text):
    """Rounding marks from one printed round, sides and Finish stripped."""
    out = []
    if not isinstance(text, str):
        return out
    for part in re.split(r'[-\u2013]', text):
        p = re.sub(r'\((P|S)\)', '', part).strip()
        if not p or p.lower() == 'finish':
            continue
        if p.lower().startswith('finish '):
            p = p[7:].strip()
        if p.lower().endswith(' finish'):
            p = p[:-7].strip()
        out.append(p)
    return out


def routed_sequence(nl, course, start, finish):
    g = nl[(nl.Course == course) & (nl['Start Option'] == start)
           & (nl['Finish Option'] == finish)].sort_values('Leg No.')
    seq, prev, prev_to = [], None, None
    for _, r in g.iterrows():
        a, b = [t.strip() for t in r['Original Pair'].split('\u2192')]
        if prev is None or r['Original Pair'] != prev or r.From != prev_to:
            if prev is None:
                seq = [a]
            seq.append(b)
            prev = r['Original Pair']
        prev_to = r.To
    return seq


def main(path):
    print(f'workbook : {path}')
    print(f'sha256   : {hashlib.sha256(open(path, "rb").read()).hexdigest()}\n')
    x = pd.read_excel(path, sheet_name=None)

    need = ['Marks', 'Course Card', 'Required Pairs', 'Passages', 'Navigation Tests',
            'Numbered Legs', 'Evidence Register', 'ORC Distance Bearings', 'Read Me']
    check(all(s in x for s in need), 'sheets present',
          ','.join(s for s in need if s not in x) or 'all')

    nl = x['Numbered Legs'].dropna(how='all').copy()
    ob = x['ORC Distance Bearings'].dropna(how='all').copy()
    for d in (nl, ob):
        d['Course'] = d['Course'].astype(str)
    marks = marks_from_workbook(x['Marks'])

    # 1 structure
    check(len(nl) == len(ob), 'Numbered Legs and ORC row counts match', f'{len(nl)} / {len(ob)}')
    m = nl[KEY + ['Leg No.', 'From', 'To']].merge(
        ob[KEY + ['Leg No.', 'From', 'To']], on=KEY + ['Leg No.'], suffixes=('', '_o'))
    check(len(m) == len(nl) and not ((m.From != m.From_o) | (m.To != m.To_o)).any(),
          'ORC rows describe the same legs')

    # 2 completeness
    courses = sorted(nl.Course.unique(), key=lambda s: int(s) if s.isdigit() else 9999)
    have = set(nl.groupby(KEY).size().index)
    want = {(c, s, f) for c in courses for s in STARTS for f in STARTS}
    check(have == want, 'all configurations present',
          f'{len(have)}/{len(want)}' + (f' missing {sorted(want - have)[:3]}' if want - have else ''))

    # 3 continuity
    numbering, continuity = [], []
    for k, g in nl.groupby(KEY):
        g = g.sort_values('Leg No.')
        if list(g['Leg No.']) != list(range(1, len(g) + 1)):
            numbering.append(k)
        fr, to = list(g.From), list(g.To)
        if fr[0] != k[1] or to[-1] != k[2]:
            continuity.append((k, 'ends'))
        for i in range(1, len(g)):
            if fr[i] != to[i - 1]:
                continuity.append((k, f'leg {i + 1}'))
    check(not numbering, 'leg numbering contiguous', str(numbering[:3]))
    check(not continuity, 'legs join end to end and match the lines', str(continuity[:3]))

    # 4 geometry
    dd = db = 0.0
    worst = None
    for _, r in ob.iterrows():
        if r.From not in marks or r.To not in marks:
            continue
        d, az = vincenty(*marks[r.From], *marks[r.To])
        e_d = abs(d - r['Distance (NM)'])
        e_b = abs((az - r['Bearing \u00b0T'] + 180) % 360 - 180)
        if e_d > dd:
            dd, worst = e_d, (r.From, r.To, r['Distance (NM)'], round(d, 3))
        db = max(db, e_b)
    check(dd <= DIST_TOL_NM and db <= BRG_TOL_DEG, 'stored geometry matches WGS84 geodesics',
          f'max {dd:.4f} NM / {db:.3f} deg' + (f' worst {worst}' if dd > DIST_TOL_NM else ''))

    # 5 invariant  6 passages
    P = x['Passages'].dropna(how='all')
    dup = [k for k, v in collections.Counter(zip(P.From, P.To)).items() if v > 1]
    check(not dup, 'one Passages row per directed pair', str(dup[:3]))
    empty = P[P.Status.astype(str).str.contains('VERIFIED') & P['Full Passage'].isna()]
    check(empty.empty, 'no VERIFIED passage row without a passage',
          str(list(zip(empty.From, empty.To))[:3]))

    ver = {}
    for _, r in P[P.Status.astype(str).str.contains('VERIFIED') & P['Full Passage'].notna()].iterrows():
        ver.setdefault((r.From, r.To), set()).add(tuple(t.strip() for t in r['Full Passage'].split('\u2192')))
    occ = collections.defaultdict(list)
    for k, g in nl.groupby(KEY):
        g = g.sort_values('Leg No.')
        cur = None
        for _, r in g.iterrows():
            if cur and cur[0] == r['Original Pair'] and cur[1][-1] == r.From:
                cur[1].append(r.To)
            else:
                if cur:
                    occ[cur[0]].append(tuple(cur[1]))
                cur = [r['Original Pair'], [r.From, r.To]]
        occ[cur[0]].append(tuple(cur[1]))
    viol = []
    for op, paths in occ.items():
        a, b = [t.strip() for t in op.split('\u2192')]
        if (a, b) in ver:
            viol += [(op, p) for p in paths if p not in ver[(a, b)]]
        elif any(len(p) > 2 for p in paths):
            viol.append((op, 'expanded but no VERIFIED passage row'))
    check(not viol, 'authored passages expanded everywhere', str(viol[:3]))

    # 7 card
    cc = x['Course Card'].copy()
    cc['Course'] = cc['Course'].astype(str)
    mismatch = []
    for _, r in cc.iterrows():
        printed = []
        for col in ['Round One', 'Round Two', 'Round Three']:
            printed += card_marks(r[col])
        star = str(r.get('Card flag')) == '**'
        for st in STARTS:
            got = routed_sequence(nl, r.Course, st, st)[1:-1]
            want_seq = (['Dosco'] + printed) if (star and st == 'Grassy Mid') else printed[:]
            # a card mark that is the line itself is not rounded in that configuration
            if want_seq and want_seq[0] == st:
                want_seq = want_seq[1:]
            if want_seq and want_seq[-1] == st:
                want_seq = want_seq[:-1]
            if got != want_seq:
                mismatch.append((r.Course, st, want_seq, got))
    check(not mismatch, 'routed sequences match the printed card',
          f'{len(mismatch)} configs, first {mismatch[0] if mismatch else ""}')

    # 8 evidence
    chords = set(zip(nl.From, nl.To))
    er = x['Evidence Register']
    er_pairs = set(zip(er.From, er.To))
    missing = chords - er_pairs
    check(not missing, 'every physical chord has an Evidence Register row',
          f'{len(missing)} missing {sorted(missing)[:3]}')
    recovered = er[er.apply(lambda r: (r.From, r.To) in chords, axis=1) &
                   er.Source.astype(str).str.contains('Recovered', case=False)]
    check(recovered.empty, 'no chord left on recovered evidence', f'{len(recovered)} rows')

    # 9 marks
    used = set(nl.From) | set(nl.To)
    check(not (used - set(marks)), 'all routed marks have coordinates', str(sorted(used - set(marks))[:5]))

    print(f'legs {len(nl)}   configurations {nl.groupby(KEY).ngroups}   '
          f'courses {len(courses)}   chords {len(chords)}   marks used {len(used)}\n')
    for line in notes + fails:
        print(line)
    print()
    if fails:
        print(f'{len(fails)} check(s) failed')
        return 1
    print('all checks passed')
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
