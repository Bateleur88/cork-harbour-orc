# Cork Harbour ORC course routing

A machine-readable, navigationally realistic representation of the 2026 RCYC
Keelboat Racing Course Card, and the race officer tools built on it. Feeds
SailScoring `course-cards` issues #16 to #19.

## Current state

| | |
|---|---|
| Master workbook | `RCYC_Cork_Harbour_ORC_MASTER_v3_16_MARK_TYPES.xlsx` |
| SHA-256 | `3110fe964b2518c555824b8812c8b638a8ebddbfae69a7473ae6b5d94306211c` |
| Courses | 40, all matching the printed 2026 card |
| Configurations | 360 (40 courses x 3 starts x 3 finishes), none missing |
| Physical legs | 3,759, with 3,759 matching ORC geometry rows |
| Directed physical chords | 186 |
| Routing waypoints | 8, plus W2 used as a turning point in 8 passages |
| Marks used | 38 |
| Evidence | every chord carries a numeric INFOMAR result; no chord on recovered evidence |
| Audit | `scripts/audit_workbook.py` passes all 14 checks |

Race officer page: `course_v8.html`, served at `tradboats.ie/course/`, bundling a
snapshot generated from the workbook above.

## The architecture, in one line

    published course -> logical mark pair -> navigation assessment
      -> direct leg OR explicitly authored passage -> numbered physical legs
      -> calculated distance and bearing

This is **not** a route-finding engine. Routing waypoints are reusable building
blocks, not a graph to search. The local knowledge lives in the authored passage;
bathymetry only validates the resulting physical chords.

## Rules that exist because something went wrong

- **The viewer stays dumb.** It displays what the workbook says. It must never
  invent a route, substitute a mark, infer an alias, expand a passage itself, or
  compensate for missing data. When Course 27 Dosco/Dosco was absent it correctly
  showed "No matching Numbered Legs rows found" instead of hiding the defect.
- **Missing bathymetry is not a pass.** Inadequate coverage is recorded as such.
- **Depth does not prove a high-water window.** The ten Curlane chords fail the
  1.5 m LAT criterion. Their use rests on the course-card restriction, and tide
  was never modelled. Keep the bathymetric result and the course condition apart.
- **Some constraints are invisible to bathymetry.** Three pairs are routed via the
  refinery waypoints solely for the SI para 21 jetty exclusion; each direct chord
  passes the depth test.
- **Verified is not immune to corrected inputs.** If a coordinate changes, the
  dependent geometry is recomputed and the evidence retested. EF2 moving 49 m in
  v3.8 invalidated five chords' evidence until v3.9 retested them.
- **Printed card distances are estimates.** They carry through card edits and are
  not recalculated. Never adjust computed geometry to match them.
- **Never rename back:** `RW_Refinery_North` and `RW_West_of_Refinery`, not the
  old `WR_`/`RM_` forms. Never conflate No.7/Corkbeg with Dosco/Corkbeg, or EF1
  with EF4. Never restore the pre-v2.50 E4 coordinate.
- **Never deduplicate** repeated occurrences of a logical pair within a course.
- **Never re-save the workbook through a library.** See `scripts/xlsx_edit.py`.

## Scripts

    scripts/geo.py            Vincenty, UTM 29N, GeoTIFF sampling. No GIS stack needed.
    scripts/audit_workbook.py Read-only pre-release audit. Exits non-zero on failure.
    scripts/test_chords.py    Chord bathymetry against the INFOMAR grids; writes evidence text.
    scripts/make_snapshot.py  Builds the JSON the race officer page bundles.
    scripts/xlsx_edit.py      Surgical cell edits plus a cell-level diff of two workbooks.

Dependencies: `pandas`, `numpy`, `tifffile`, `openpyxl` (diff only).

Rasters are the INFOMAR Inshore Ireland GeoTIFFs, unzipped anywhere, passed as a
directory. Cork Harbour work uses GEO12_04, KRY12_05 and CB12_01 in that priority
order. They are large and are not in the repository.

    Contains Irish Public Sector Data (Geological Survey Ireland & Marine
    Institute) licensed under CC BY 4.0.

## Tests

    tests/test_marks.py       Safety tests for pages/marks/marks.php.

Runs `marks.php` unmodified as real CGI requests against a throwaway day file
holding three races, and checks those races are intact after each case: a fix
or course that cannot be JSON-encoded, a damaged day file, a write failing
part-way, the RO page moving a fix (device and recorder must survive), and 60
fixes, 10 courses and 30 reads arriving at once. Run it before uploading any
change to `marks.php`.

Needs a local PHP install with `php-cgi` (in the Windows PHP zip; the `php-cgi`
package on Linux), found on PATH or through the `PHP_CGI` environment variable.
Tested with PHP 8.4 on Windows; the live host may differ.

## Before any release

1. `python scripts/audit_workbook.py <workbook>` — must pass all 14 checks.
2. `python scripts/xlsx_edit.py` diff, or `cell_diff(before, after)` — confirm the
   changed cells are exactly the ones intended, and nothing else moved.
3. Open the file in Excel itself, not only LibreOffice, and confirm it opens with
   no repair dialog.
4. If any coordinate changed, retest every dependent chord with
   `scripts/test_chords.py` and update its Evidence Register row. Do not carry the
   old numbers forward.
5. Add a Read Me change record: what changed, what did not, and the SHA-256 of the
   workbook it was made from.
6. Regenerate the page snapshot with `scripts/make_snapshot.py` and rebuild the
   page, so the bundled data and the master do not drift.
7. Record the new SHA-256 in this README.

A validation worth repeating whenever the sampling changes: Dosco to
RW_Fort_Davis is 641.3 m, 130/130 samples, minimum 2.875 m LAT. That reproduces a
result recorded long before these scripts existed.

## Open questions

1. **Harp and Ringabella.** The 2026 General SIs (§22.3, March) and the 2026
   Autumn League SIs (para 36, September) publish Ringabella 408 m apart and Harp
   83 m apart. The workbook follows the later document. RCYC has not been asked to
   resolve it.
2. **Laid marks.** White Bay, Curlane and Dutchman are club laid marks, laid afresh
   each race day: the stored position is a planning approximation and the RIB's fix
   for the day is authoritative; the mark-logging page records it. Harp, Ringabella,
   Dosco and EF4 are permanently moored; only their published coordinates are in
   question. The Marks sheet Type says which is which, and `make_snapshot.py` reads it.
3. **EF2 and Cage.** Carried on the club's word. The Port publishes no positions
   and refers mariners to BA 1765, 1773 and 1777.
4. **No.6 to Cage** has a 29.9 m unsurveyed run near Cage. Deliberately retained at
   DIRECT – VERIFIED; do not downgrade it on coverage grounds without new evidence.
5. **Twenty-three chords pass under 2.0 m at LAT,** mostly around Cage. Passing,
   but the criterion is doing real work there.
6. **Mark's 204.** Navigation Tests holds 204 distinct directed pairs, 58 of which
   are not physical chords. Probably the population behind his figure; unconfirmed.

## Workbook sheets

`Read Me` change records · `Marks` positions, type, source, accuracy ·
`Course Card` the printed card as data · `Required Pairs` the 177 logical pairs ·
`Passages` one authoritative row per directed pair · `Navigation Tests` the
development test log · `Numbered Legs` the physical legs, the routing authority ·
`ORC Distance Bearings` geodesic geometry for those legs · `Evidence Register`
numeric evidence per chord. `Course Legs`, `ORC Export`, `Issues Audit` and
`Resolution Priority` are stale v2.76-era sheets kept for history; do not read
them as current.

## Licence

The licence is split by what the material is:

- **Scripts and page code** (`scripts/`, and the race officer and mark-logging
  pages): MIT, copyright 2026 Pat Tanner. See `LICENSE`.
- **INFOMAR bathymetry**: Irish Public Sector Data (Geological Survey Ireland &
  Marine Institute), licensed under CC BY 4.0. It is not redistributed here; the
  scripts read rasters you download yourself.
- **RCYC course card and Sailing Instruction content**: the club's. It is
  reproduced in the workbook as data for scoring purposes and is not covered by
  the MIT licence.
