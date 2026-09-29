#!/usr/bin/env python3
"""Test physical chords against the INFOMAR 2 m LAT grids.

    python scripts/test_chords.py WORKBOOK RASTER_DIR [--chords "A>B,C>D"] [--spacing 5.0] [--out results.csv]

With no --chords it sweeps every directed physical chord in Numbered Legs.
Prints one line per chord and writes a CSV plus the evidence sentence that
should go into Evidence Register.

Validation: run it on Dosco>RW_Fort_Davis first. The recorded historical test is
641.3 m, 130/130 samples, minimum 2.875 m LAT. If this pipeline reproduces that,
it is measuring what the earlier testing measured.

Rasters are the Inshore Ireland GeoTIFFs, unzipped, any layout below RASTER_DIR.
Priority is the order given by --rasters, else alphabetical by filename.

  Contains Irish Public Sector Data (Geological Survey Ireland & Marine
  Institute) licensed under CC BY 4.0.
"""
import argparse
import csv
import glob
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import Raster, chord_result, marks_from_workbook  # noqa: E402


def evidence_sentence(r, tested_on):
    src = '; '.join(f'{k} ({v})' for k, v in sorted(r['sources'].items(), key=lambda kv: -kv[1]))
    s = (f"INFOMAR 2 m LAT grids {src}; {r['spacing_m']} m spacing along the "
         f"{r['length_m']:,.1f} m chord; {r['covered']}/{r['samples']} samples covered "
         f"({100 * r['covered'] / r['samples']:.1f}%); ")
    if r['min_depth_m'] is None:
        s += 'no coverage. '
    elif r['below_criterion']:
        s += (f"minimum depth {r['min_depth_m']:.3f} m LAT; {r['below_criterion']} samples below "
              f"{r['criterion_m']} m. FAILS the normal criterion; any use of this chord rests on a "
              f"course-level condition, not on bathymetry, and tidal height was not modelled. ")
    else:
        s += (f"minimum depth {r['min_depth_m']:.3f} m LAT at {r['min_at_fraction']:.2f} of the chord; "
              f"0 samples below {r['criterion_m']} m. ")
    if r['max_gap_samples']:
        s += f"Largest unsurveyed run {r['max_gap_samples']} samples ({r['max_gap_m']} m). "
    return s + (f"Tested {tested_on}; criterion >={r['criterion_m']} m at LAT; "
                f"nearest-neighbour sampling in UTM 29N.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('workbook')
    ap.add_argument('raster_dir')
    ap.add_argument('--chords', help='comma separated A>B pairs; default every chord in the workbook')
    ap.add_argument('--spacing', type=float, default=5.0)
    ap.add_argument('--criterion', type=float, default=1.5)
    ap.add_argument('--rasters', help='comma separated filename fragments, in priority order')
    ap.add_argument('--out', default='chord_evidence.csv')
    ap.add_argument('--date', default=pd.Timestamp.today().strftime('%d %b %Y'))
    a = ap.parse_args()

    tifs = sorted(glob.glob(os.path.join(a.raster_dir, '**', '*.tif'), recursive=True))
    if a.rasters:
        order = [f.strip() for f in a.rasters.split(',')]
        tifs = [t for frag in order for t in tifs if frag in os.path.basename(t)]
    if not tifs:
        sys.exit(f'no GeoTIFFs under {a.raster_dir}')
    rasters = [(os.path.basename(t).split('_U29N')[0].replace('BY_', ''), Raster(t)) for t in tifs]
    print('rasters, in priority order: ' + ', '.join(n for n, _ in rasters))

    x = pd.read_excel(a.workbook, sheet_name=None)
    marks = marks_from_workbook(x['Marks'])
    if a.chords:
        pairs = [tuple(p.split('>')) for p in a.chords.split(',')]
    else:
        nl = x['Numbered Legs']
        pairs = sorted(set(zip(nl.From, nl.To)))

    rows = []
    for f, t in pairs:
        if f not in marks or t not in marks:
            print(f'{f} -> {t}: unknown mark, skipped')
            continue
        r = chord_result(rasters, f, t, marks, spacing=a.spacing, criterion=a.criterion)
        r['evidence'] = evidence_sentence(r, a.date)
        rows.append(r)
        print(f"{f:>22} -> {t:<22} {r['verdict']:<26} "
              f"{r['length_m']:>8.1f} m  {r['covered']}/{r['samples']}  "
              f"min {r['min_depth_m'] if r['min_depth_m'] is not None else '-'}")

    cols = ['from', 'to', 'verdict', 'length_m', 'samples', 'covered', 'min_depth_m',
            'below_criterion', 'min_at_fraction', 'max_gap_samples', 'max_gap_m',
            'spacing_m', 'criterion_m', 'sources', 'evidence']
    with open(a.out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            r['sources'] = '; '.join(f'{k} ({v})' for k, v in sorted(r['sources'].items()))
            w.writerow(r)
    bad = [r for r in rows if r['verdict'] != 'PASS']
    print(f"\n{len(rows)} chords, {len(rows) - len(bad)} pass, {len(bad)} not clean -> {a.out}")
    for r in bad:
        print(f"  {r['verdict']:<26} {r['from']} -> {r['to']}")


if __name__ == '__main__':
    main()
