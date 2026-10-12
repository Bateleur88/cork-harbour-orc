#!/usr/bin/env python3
"""Build the course-card snapshot the race officer page bundles.

    python scripts/make_snapshot.py WORKBOOK [--out cardsnap.json]

The page is offline-first, so the snapshot is embedded rather than fetched. It
carries the source filename, hash and date, which the page shows, so a stale
bundle is visible rather than silent. Regenerate it after every workbook release
and rebuild the page.

Structure:
  meta     source, sha256, generated, criterion, attribution
  marks    id -> lat, lon, full name, type, group (the heading the page's Fixed marks list puts it under),
           flag (uncertain position, shown in red), laid (true for a club laid mark: the RIB's fix for the
           day takes precedence), rw (true for a routing waypoint). Every mark with a position in the
           Marks sheet, in sheet order, not only those the card's routes use (STATUS A40)
  pairs    "A|B" -> total nm and the physical segments, so the page never
           recomputes geometry and never invents a route. Where the workbook authors a route one way
           only, its exact reverse is added here, marked rev: true: the same points in reverse order and
           the same distances, each bearing worked out from the positions with Vincenty, as the workbook's
           own are. A pair authored both ways keeps both as authored (STATUS A40)

Refuses, and writes nothing, if a mark name appears twice, if two names are the same once capitals,
spaces and punctuation are ignored, or if a name would be read by the page as a committee boat, pin or
finish.
  courses  number -> printed rounds, sides from the card, condition, printed
           distance, and the mark sequence for each start/finish configuration
"""
import argparse
import hashlib
import json
import re

import pandas as pd

from geo import vincenty

# Marks whose position is not settled. Keep this in step with the Marks sheet.
FLAGS = {
    'Ringabella': 'Two current 2026 RCYC documents give this mark 408 m apart; the Autumn League SI position is used.',
    'Harp': 'Two current 2026 RCYC documents give this mark 83 m apart; the Autumn League SI position is used.',
    'EF4': 'Permanently moored race mark; position from a published RCYC reference only.',
    'Grassy Mid': 'Midpoint standing in for the Grassy Walk line, not a mark.',
}
# Club laid marks are laid afresh each race day. Which marks they are comes from the Marks sheet Type,
# never from a list here; each is flagged, and carries laid: true for the page.
LAID_TYPE = 'Club laid mark'
LAID_FLAG = "Club laid mark: the RIB's fix for the day takes precedence; this position is a planning approximation."


# The Marks sheet Types that are routing waypoints ("Routing waypoint", and "Routing mark" for RW_West_of_Refinery):
# all go under one heading in the page's Fixed marks list (Pat, 12 October 2026)
ROUTING_TYPE = 'Routing'
ROUTING_GROUP = 'Routing waypoints'


class SnapshotError(ValueError):
    """The workbook cannot be made into a snapshot as it stands; nothing is written."""


def group_of(typ):
    """The Fixed marks heading for a Marks sheet Type: the Type up to its first ';' or '(' ("Club laid mark; laid
    afresh…" -> "Club laid mark"), and one heading for every routing waypoint."""
    if typ.startswith(ROUTING_TYPE):
        return ROUTING_GROUP
    return re.split(r'[;(]', typ, maxsplit=1)[0].strip()


def norm(name):
    """A name as the page compares names: lower case, letters and digits only."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


# What the page reads as a line end (isCB, isStartPin, isFinishPin in course_v8.html), and "finish" on its own
LINE_NAME = re.compile(r'committee|pin|finish', re.I)


def check_names(marks):
    """Refuse names the page could confuse: two the same once capitals, spaces and punctuation are ignored (the
    page keeps card marks' ids in lower case and matches names that way), and any it would take for a committee
    boat, a pin or a finish."""
    seen = {}
    for sid in marks:
        k = norm(sid)
        if not k:
            raise SnapshotError(f'mark name {sid!r} has no letters or digits')
        if k in seen:
            raise SnapshotError(f'mark names {seen[k]!r} and {sid!r} are the same once capitals, spaces and '
                                'punctuation are ignored')
        seen[k] = sid
        if LINE_NAME.search(sid):
            raise SnapshotError(f'mark name {sid!r} would be read as a committee boat, pin or finish')


def reversed_routes(pairs, pos):
    """The exact reverse of every route authored one way only: the same points in reverse order, each segment the
    same distance as authored, its bearing from the positions with Vincenty (not the forward bearing + 180), and
    rev: true. A route authored both ways is left as it is."""
    out = {}
    for key, p in pairs.items():
        a, b = key.split('|')
        if f'{b}|{a}' in pairs:
            continue
        pts = [a] + [s['to'] for s in p['segs']]
        nms = [s['nm'] for s in p['segs']]
        back = list(reversed(pts))
        segs = []
        for i in range(len(back) - 1):
            d, brg = vincenty(*pos[back[i]], *pos[back[i + 1]])
            nm = nms[len(nms) - 1 - i]
            if abs(d - nm) > 0.001:
                raise SnapshotError(f'{key}: the reverse of {back[i + 1]} -> {back[i]} measures {d:.4f} nm, '
                                    f'not the {nm} nm stored')
            segs.append({'to': back[i + 1], 'nm': nm, 'brg': round(brg, 1)})
        out[f'{b}|{a}'] = {'nm': p['nm'], 'segs': segs, 'rev': True}
    return out


def build(workbook):
    """The snapshot for one workbook, as a dict. rebuild_page.py embeds it in the course page."""
    sha = hashlib.sha256(open(workbook, 'rb').read()).hexdigest()
    x = pd.read_excel(workbook, sheet_name=None)
    nl = x['Numbered Legs'].copy()
    nl['Course'] = nl['Course'].astype(str)
    ob = x['ORC Distance Bearings'].copy()
    geo = {(r.From, r.To): (round(float(r['Distance (NM)']), 3), round(float(r['Bearing \u00b0T']), 1))
           for _, r in ob.iterrows()}

    marks, pos = {}, {}
    for _, r in x['Marks'].dropna(subset=['Decimal Lat']).iterrows():
        sid = str(r['Mark']).split('/')[0].strip()
        if sid in marks:
            raise SnapshotError(f'mark name {sid!r} appears twice in the Marks sheet')
        pos[sid] = (float(r['Decimal Lat']), float(r['Decimal Lon']))
        marks[sid] = {'lat': round(float(r['Decimal Lat']), 6), 'lon': round(float(r['Decimal Lon']), 6),
                      'full': str(r['Mark']), 'type': str(r['Type']), 'group': group_of(str(r['Type']))}
        if str(r['Type']).startswith(ROUTING_TYPE):
            marks[sid]['rw'] = True
        if str(r['Type']).startswith(LAID_TYPE):
            marks[sid]['laid'] = True
            marks[sid]['flag'] = LAID_FLAG
        elif sid in FLAGS:
            marks[sid]['flag'] = FLAGS[sid]
    check_names(marks)

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
                if pd.isna(v):          # blank: a two-round course has no R3, so fall back to R2
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
    pj.update(reversed_routes(pj, pos))

    snap = {'meta': {'source': re.split(r'[\\/]', workbook)[-1], 'sha256': sha,
                     'generated': pd.Timestamp.today().strftime('%Y-%m-%d'),
                     'criterion': 'Physical legs validated against INFOMAR 2 m LAT grids, minimum 1.5 m at LAT',
                     'attribution': 'Contains Irish Public Sector Data (Geological Survey Ireland & '
                                    'Marine Institute) licensed under CC BY 4.0'},
            'marks': marks, 'pairs': pj, 'courses': courses}
    return snap


def dumps(snap):
    """The snapshot's one text form, used for the file and for the page alike."""
    return json.dumps(snap, separators=(',', ':'), allow_nan=False)   # NaN is not JSON: fail rather than write it


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('workbook')
    ap.add_argument('--out', default='cardsnap.json')
    a = ap.parse_args()
    try:
        snap = build(a.workbook)
    except SnapshotError as e:
        raise SystemExit(f'refused: {e}; nothing written')
    text = dumps(snap)
    with open(a.out, 'w') as fh:
        fh.write(text)
    print(f"{len(snap['marks'])} marks, {len(snap['pairs'])} pairs, {len(snap['courses'])} courses -> {a.out} "
          f"({len(text) // 1024} KB)")


if __name__ == '__main__':
    main()
