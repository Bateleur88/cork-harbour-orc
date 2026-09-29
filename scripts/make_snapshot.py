#!/usr/bin/env python3
"""Build the course-card snapshot the race officer page bundles.

    python scripts/make_snapshot.py WORKBOOK [--out cardsnap.json]

The page is offline-first, so the snapshot is embedded rather than fetched. It
carries the source filename, hash and date, which the page shows, so a stale
bundle is visible rather than silent. Regenerate it after every workbook release
and rebuild the page.

Structure:
  meta     source, sha256, generated, criterion, attribution
  marks    id -> lat, lon, full name, type, flag (uncertain position, shown in red)
  pairs    "A|B" -> total nm and the physical segments, so the page never
           recomputes geometry and never invents a route
  courses  number -> printed rounds, sides from the card, condition, printed
           distance, and the mark sequence for each start/finish configuration
"""
import argparse
import hashlib
import json
import re

import pandas as pd

# Marks whose position is not settled. Keep this in step with the Marks sheet.
FLAGS = {
    'Ringabella': 'Two current 2026 RCYC documents give this mark 408 m apart; the Autumn League SI position is used.',
    'Harp': 'Two current 2026 RCYC documents give this mark 83 m apart; the Autumn League SI position is used.',
    'White Bay': 'Laid mark, position approximate.',
    'Curlane': 'Laid mark, position approximate.',
    'Dutchman': 'Laid mark, position approximate.',
    'EF4': 'Laid or movable race mark, position approximate.',
    'E4': 'Position from a single secondary source.',
    'Dosco': 'Position from a Navionics chart reading; the SI position is 11 m away.',
    'Grassy Mid': 'Midpoint standing in for the Grassy Walk line, not a mark.',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('workbook')
    ap.add_argument('--out', default='cardsnap.json')
    a = ap.parse_args()

    sha = hashlib.sha256(open(a.workbook, 'rb').read()).hexdigest()
    x = pd.read_excel(a.workbook, sheet_name=None)
    nl = x['Numbered Legs'].copy()
    nl['Course'] = nl['Course'].astype(str)
    ob = x['ORC Distance Bearings'].copy()
    geo = {(r.From, r.To): (round(float(r['Distance (NM)']), 3), round(float(r['Bearing \u00b0T']), 1))
           for _, r in ob.iterrows()}

    used = set(nl.From) | set(nl.To)
    marks, seen = {}, set()
    for _, r in x['Marks'].dropna(subset=['Decimal Lat']).iterrows():
        sid = str(r['Mark']).split('/')[0].strip()
        if sid not in used or sid in seen:
            continue
        seen.add(sid)
        marks[sid] = {'lat': round(float(r['Decimal Lat']), 6), 'lon': round(float(r['Decimal Lon']), 6),
                      'full': str(r['Mark']), 'type': str(r['Type'])}
        if sid in FLAGS:
            marks[sid]['flag'] = FLAGS[sid]

    pairs, courses = {}, {}
    cc = x['Course Card'].copy()
    cc['Course'] = cc['Course'].astype(str)
    for c, g in nl.groupby('Course'):
        cfg = {}
        for (st, fi), gg in g.groupby(['Start Option', 'Finish Option']):
            gg = gg.sort_values('Leg No.')
            seq, prev, prev_to, path = [], None, None, []
            for _, r in gg.iterrows():
                p0, p1 = [t.strip() for t in r['Original Pair'].split('\u2192')]
                if prev is None or r['Original Pair'] != prev or r.From != prev_to:
                    if path:
                        pairs.setdefault('|'.join(path[0]), path[1])
                    if prev is None:
                        seq = [p0]
                    seq.append(p1)
                    prev = r['Original Pair']
                    path = [(p0, p1), [r.From, r.To]]
                else:
                    path[1].append(r.To)
                prev_to = r.To
            if path:
                pairs.setdefault('|'.join(path[0]), path[1])
            cfg[f'{st}|{fi}'] = seq
        row = cc[cc.Course == c]
        rounds = [str(row[col].iloc[0]).strip() for col in ['Round One', 'Round Two', 'Round Three']
                  if len(row) and isinstance(row[col].iloc[0], str) and row[col].iloc[0].strip()]
        d = {'label': ' \u00b7 '.join(rounds), 'rounds': rounds, 'cfg': cfg}
        if len(row):
            card = []
            for text in rounds:
                for part in text.split('\u2013'):
                    p = part.strip()
                    if not p or p.lower().startswith('finish'):
                        continue
                    m = re.match(r'^(.*?)\s*\(([PS])\)$', p)
                    card.append({'m': m.group(1).strip(), 's': m.group(2)} if m else {'m': p, 's': ''})
            d['card'] = card
            flag = row['Card flag'].iloc[0]
            if isinstance(flag, str) and flag.strip():
                d['flag'] = flag.strip()
            note = row['Notes'].iloc[0]
            if isinstance(note, str) and note.strip():
                d['note'] = note.strip()
            for col in ['Cum NM R3', 'Cum NM R2', 'Cum NM R1']:
                v = row[col].iloc[0]
                if isinstance(v, str) and v.strip() and not v.strip().replace('.', '').isdigit():
                    d.setdefault('cond', v.strip())
                    continue
                try:
                    d['printed'] = float(v)
                    break
                except (TypeError, ValueError):
                    pass
        courses[c] = d

    pj = {}
    for key, path in pairs.items():
        segs = [{'to': path[i + 1], 'nm': geo[(path[i], path[i + 1])][0],
                 'brg': geo[(path[i], path[i + 1])][1]} for i in range(len(path) - 1)]
        pj[key] = {'nm': round(sum(s['nm'] for s in segs), 3), 'segs': segs}

    snap = {'meta': {'source': a.workbook.rsplit('/', 1)[-1], 'sha256': sha,
                     'generated': pd.Timestamp.today().strftime('%Y-%m-%d'),
                     'criterion': 'Physical legs validated against INFOMAR 2 m LAT grids, minimum 1.5 m at LAT',
                     'attribution': 'Contains Irish Public Sector Data (Geological Survey Ireland & '
                                    'Marine Institute) licensed under CC BY 4.0'},
            'marks': marks, 'pairs': pj, 'courses': courses}
    with open(a.out, 'w') as fh:
        json.dump(snap, fh, separators=(',', ':'))
    print(f"{len(marks)} marks, {len(pj)} pairs, {len(courses)} courses -> {a.out} "
          f"({len(json.dumps(snap, separators=(',', ':'))) // 1024} KB)")


if __name__ == '__main__':
    main()
