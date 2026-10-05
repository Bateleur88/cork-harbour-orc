# Cork Harbour ORC course routing

A machine-readable, navigationally realistic representation of the 2026 RCYC
Keelboat Racing Course Card, and the race officer tools built on it. Feeds
SailScoring `course-cards` issues #16 to #19.

## Current state

| | |
|---|---|
| Master workbook | `RCYC_Cork_Harbour_ORC_MASTER_v3_19_CAGE_CORROBORATED.xlsx` |
| SHA-256 | `ff0ae3ee4cbd4216caaa0e5608848a6c8ca7ba82a3d41612bfd0069b9a735220` |
| Courses | 40, all matching the printed 2026 card |
| Configurations | 360 (40 courses x 3 starts x 3 finishes), none missing |
| Physical legs | 3,759, with 3,759 matching ORC geometry rows |
| Directed physical chords | 186 |
| Routing waypoints | 8, plus W2 used as a turning point in 9 passages |
| Marks used | 38 |
| Evidence | every chord carries a numeric INFOMAR result; no chord on recovered evidence |
| Audit | `scripts/audit_workbook.py` passes all 16 checks |

Race officer page: `course_v8.html`, served at `tradboats.ie/course/`, bundling a
snapshot generated from the workbook above. See [The pages](#the-pages).

## Start here for reviewers

1. **Install.** Python 3 (developed on 3.12) with `pandas`, `numpy`, `tifffile` and
   `openpyxl`:

       pip install pandas numpy tifffile openpyxl

2. **Audit the workbook.** Read-only; prints a report and exits non-zero on any
   failure. Expect 16 PASS lines and the counts in the table above:

       python scripts/audit_workbook.py RCYC_Cork_Harbour_ORC_MASTER_v3_19_CAGE_CORROBORATED.xlsx

3. **Check the file is the one described.** The audit prints its SHA-256; it should
   match the table above.
4. **Read the Read Me chain.** The workbook's `Read Me` sheet opens with the design
   (rows 1–6: problem, design, stages, the role of bathymetry), then has one change
   record per release in order. From v3.5 onwards each record states what changed,
   what did not, and the SHA-256 of the workbook it was made from, so the chain can
   be followed back version by version. Earlier versions of the workbook are in
   this repository's history (`git log -- '*.xlsx'`).
5. **Then** the rules below, the sheets at the end, and the open questions.

Checking the bathymetry itself needs the INFOMAR rasters, which are not in the
repository; see `scripts/test_chords.py` under Scripts.

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
  **Two stated exceptions**, both of position only, both keeping the card's route
  and labelling the measured hop "not depth-checked": a recorded start or finish
  line stands where the card's start (or Grassy Mid finish) is (see The pages);
  and a club laid mark (Curlane, Dutchman, White Bay) takes
  its *position* from the day's RIB fix, because its stored coordinate is only a
  planning approximation. The mark is never substituted, only its position; only
  a fix with exactly the mark's name is used automatically; the card's route to it
  is kept, with the last segment measured to the fix and labelled not
  depth-checked; and every change of position is shown with its effect on the
  course, never applied silently.
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

## The pages

Three files in `pages/`, working together through the web server (see Deploying
the pages for where each goes).

**RIB page** (`pages/record/record.html`, served as `/record/`). The RIB crew
records each mark as it is laid, with the phone's GPS: pick the date and
race, tap a name (quick picks include the laid marks Curlane, Dutchman and White
Bay) and record. Fixes are queued on the phone and upload to `marks.php` when there
is signal, so nothing is lost offline. Each fix carries a random id for the phone
and an optional "Who's recording?" name. A WhatsApp message is the backup, headed
"Laid marks – date": the series name is set on the RO page, not here.
The ORC IRL watermark behind the page is embedded in it as a data URI, so it is
there offline; `pages/record/assets/orc-irl-watermark.png` is its source and is
not uploaded.

*A fresh position only.* Android Chrome can hand over the phone's last known
position first, with its own old time, even when asked not to (`maximumAge:0`): on
4 Oct 2026 half the fixes carried a position 24 s to 12.5 minutes old. So every
position is checked against the moment Record was tapped, and one more than 5 s
older (`FRESH_MS`) is ignored while the page keeps listening. A fresh position at
±5 m or better is saved at once, otherwise the most accurate fresh one after 10 s;
with none by 20 s (`GIVE_UP_MS`) nothing is saved and a red panel asks the driver to
stay at the mark and tap Record again. Cancel, the screen locking or the page being
left also stop the fix with nothing saved and the mark name kept. A large panel says
"HOLD STILL at the mark…" with a countdown while waiting, and "Saved ✓" (green, one
buzz on Android) only once a fresh position is stored on the phone; sending is shown
separately, as before. The fix keeps the position's own time (`time`) and the tap
(`tap`), so the age of a position can be measured exactly.
*Clock risk:* the check compares GPS time with the phone's clock. A phone whose
clock is more than 5 s out would refuse every fix; if that happens, set the phone to
automatic time, or raise `FRESH_MS`. The tap time shows any offset afterwards.
*Possible later check:* a position taken while the RIB is still moving towards the
mark is fresh but not at the mark. A later version could also require two fresh
positions a few metres apart, or a low speed, before saving.

*Opening with no signal.* A service worker (`pages/record/sw.js`, served as
`/record/sw.js`, controlling `/record/` and nothing else on the site) keeps a copy
of the page and `key.js`. Opening the page always tries the network first. The
saved copy is used only if the network fails, answers with a server error (5xx), or
has not answered within 3 seconds; an answer that arrives later still refreshes the
copy for next time. The saved page is replaced only by a response that contains
the `PAGE_VERSION` marker, so a maintenance or error page that comes back as 200 is
shown but never saved over the good copy. `marks.php`, the page's version check,
Google Fonts and every other request go to the network untouched. Each
`PAGE_VERSION` registers its own worker (`sw.js?v=<version>`) with its own cache,
`record-<version>`, and the new worker deletes the older caches when it takes over,
so `sw.js` itself needs no change for a release.
**Dock rule:** a new phone must open `https://tradboats.ie/record/` once with
signal before it can open it without; until then a cold start offline shows
Chrome's own offline page. Bookmark it with the trailing slash: `/record` without
it is outside the worker's scope. On iPhones, Safari may clear the copy after about
a week without a visit, so open the page with signal before each race day.

**Server** (`pages/marks/marks.php`, served as `/marks/marks.php`). Stores the day's
fixes and the RO's built courses as JSON in `/marks/data/`, behind the race key in
`key.js`. It also keeps the series name, one for the whole series and set from the
RO page, in `/marks/data/series.json`; fixes no longer carry a series, and a
`series` sent by a phone that has not reloaded is ignored, never refused. Each fix from
the RIB page also stores `tap`, when Record was tapped (ms, the phone's clock), beside
`time`, the position's own time, so the age of a position can be measured exactly; a
fix from an older page has none, a malformed `tap` is dropped rather than refused, and
moving a fix keeps it. Writes go
to a temporary file renamed into place, so a failed write cannot empty a day; a
damaged day file is refused rather than overwritten.
`tests/test_marks.py` checks all of this.

**Race officer page** (`pages/course/course_v8.html`, served as `/course/`).
Offline-first: the course card snapshot from the workbook is embedded in the page.
The same ORC IRL watermark as the RIB page, embedded, sits behind it, with the
footer "© Pat Tanner ORC Ireland".

- *Series name*: at the top of Setup, set by the RO and saved on the server, so
  every RO device shows the same name; it heads the WhatsApp course message. It is
  never taken from the RIBs' fixes or from a pasted WhatsApp backup. Unset, the
  field is empty with a red border and says so. An edit made without signal is
  kept on the phone and saved when there is signal.
- *Import a harbour course* (section 2) is folded away, closed each time the page
  opens; its heading names the card in use (e.g. `RCYC_Cork_Harbour_ORC_MASTER_v3_19,
  40 courses`) and, once a course is imported, that course, with ⚠ when it is flagged.
  Whether it is open is not saved.
- *Check recorded marks* (end of section 1, closed by default): a read-only plot of
  every fix loaded for the race selected, or for all races, for the RO or scorer to
  spot one out of place. It is one element shown in both views (at the bottom of Race
  view). Its closed line counts fixes: "2 fixes to check" is two fixes with at least
  one flag each, however many flags they have; a note about the race as a whole (no
  committee boat of its own) is counted apart as a race note. Shape and colour give the race;
  a typed position (±0, no phone) is hollow, an estimate; a fix carried in from an
  earlier race (such as Race 1's committee boat) is dashed. With *All races* ticked
  each fix has a short label (`R2 L 13:21`: race, mark initial, time; CB, SP and FP
  for the committee boat, start pin and finish pin, with a key under the sketch), a
  thin line in each race's colour joins its latest Windward and Leeward, and chips
  (R1, R2, R3…) switch races on and off in the sketch, chart and list; the closed
  line still counts every race, and the choice is not saved. A switched-off race's
  committee boat stays, dashed, while a race shown carries it forward, and a selected
  fix of a switched-off race is deselected. Tapping a fix gives its
  name, race, time, accuracy, phone (lettered A, B… by first fix of the day),
  recorder, position, and how old the position was when saved: the fix id starts
  with the phone's clock, so id time minus the fix's time, falling back to when the
  server received it. The checks, with their thresholds as named constants at the
  top of that code and tuned to one day's fixes (4 Oct 2026), are advice only and
  never block anything: a position 20 s to 5 min old (check) or over 5 min (likely
  wrong, the only one in the warning colour); a Start or Finish Pin within 60 m of a
  mark of its race; a start line more than 45° off square to the leg to the race's
  first mark; a mark more than 500 m from the nearest fix of its name in another
  race (line ends left out); a Start Pin later than its race's Finish Pin, or a
  Finish Pin later than the next race's first start; a race with no committee boat
  of its own. Each has a WhatsApp, Share or Copy button with a short message asking
  for the mark to be recorded again. Sketch by default; Chart needs signal.
- *Setup view*: get the day's marks (then refreshed every 30 seconds), import a card
  course or tap marks in rounding order, record the committee boat and pin, set
  the wind. Until a line is recorded, the card's own start (e.g. Grassy Mid) stands
  in for it, and the page says so. A course built before the day's marks could be
  loaded, at the dock say, is kept when they load.
- *Race view*: what is needed after the gun. A header with race and start pickers,
  the course and its total; an alert strip for anything that changes during a race
  (a laid mark re-pointed, a mark moved, two phones disagreeing, the refresh
  stopped); the legs table and plot; wind and the wind-shift box; the send buttons;
  and the committee-boat button. The view never switches by itself.
- *Legs*: between two card marks the card's own route is used, passages included,
  with distances and bearings from the workbook; the page never searches for a
  route. With a recorded start line, the leg from it keeps the card's route from
  the card's start point, and only the first hop (line → first waypoint, or → the
  first mark on a direct leg) is measured from the line, labelled "from the
  recorded line, not depth-checked"; the finish leg to a recorded line likewise.
  A committee boat for a Grassy Walk start sits within a few hundred metres of
  Grassy Mid, so that water is effectively the validated water; the page warns
  when the line's midpoint is more than 500 m from the card's start point.
- *Starts and finishes of a card course are deliberately not mirror images* — do
  not "fix" one into the other:
  - **Finish:** the card's Finish decides. Grassy Mid stands for the Grassy Walk
    line: the recorded start line, or Grassy Mid standing in until it is recorded.
    **No.8 or Dosco is the mark itself:** boats finish as they round or pass it and
    the committee boat positions itself to time them, so a recorded line is not
    used for the finish. The workbook ends such a route at the mark (a final
    rounding of Dosco becomes the finish; there is no zero-length leg).
  - **Start:** a recorded committee boat and pin always win. The Autumn League SI
    2026 has committee boat starts in the area of Cage (C1), No.8 or Dosco, so a
    No.8 or Dosco card start is a committee boat line near that mark, never the
    mark itself. The card start only picks the workbook configuration and stands
    in when nothing is recorded.
  - The Finish selector in section 3 (start line, committee boat and Finish Pin, or
    at the last mark) is for hand-built courses only; for a card course it is
    replaced by a statement of the card's finish.
- *Laid marks* (Curlane, Dutchman, White Bay, from the Marks sheet Type): the
  latest RIB fix of the day with exactly the mark's name is used; with none, the
  card position, flagged as a planning position until laid. A near miss such as
  "Curlane Bank" is suggested, never applied (Curlane Bank is also a name of No.8
  and No.10). The RO can pin any fix, or the card position. See the exception to
  the dumb-viewer rule above. Harp, Ringabella, Dosco and EF4 are permanently
  moored, not laid: they always use the workbook position, and only their published
  coordinates are in question. The Marks sheet Type says which is which.
- *Outputs* (section 6): a WhatsApp message of the course, legs and positions; and
  the **leg table for SailScoring**, below.

**Wide screens.** Under 700 CSS px (phones) the page is one 560 px column, as it
always was. From 700 px it is one 760 px column with larger sketches. From 1100 px
(tablet landscape, PC) it is two columns, up to 1400 px in all, centred (the "Check
recorded marks" sketch is drawn on a larger canvas there, up to 85% of the screen
height, so its labels have more room), so the scorer
can check the recorded marks and the legs together: in Setup, sections 1 to 3 on the
left and section 4, "Check recorded marks", wind shift and send on the right; in Race
view, the legs table on the left and the sketch with "Check recorded marks" on the
right, and wind, wind shift and send below. The columns depend on element order in
the page, not on wrapper elements (see the comment above the media queries): moving
an element into or out of the Setup container, or reordering the column's elements,
moves it between columns. The watermark stays centred on the screen.

**SailScoring leg table.** The course as sailed, for entering into SailScoring:
one line per physical leg, in sailing order, from the start to the first mark
through to the last mark to the finish. A card passage is split into the legs
actually sailed. Each line is the distance in nautical miles to two decimals, a
space, and the bearing as three digits, and nothing else. The bearings are given in
degrees **magnetic**; that SailScoring expects magnetic rather than true is an
assumption, pending confirmation with Mark:

    0.24 105
    0.23 123
    0.86 183

A note above the block, not part of what is copied, says whether the first and
last legs are measured from the recorded committee boat and pin (or finish pin) or
from the card's stand-in start and finish, and that the bearings given are magnetic
(see the assumption above). Because
each physical leg is rounded separately, the lines can add to a few hundredths
more or less than the legs table's total.

## Scripts

    scripts/geo.py            Vincenty, UTM 29N, GeoTIFF sampling. No GIS stack needed.
    scripts/audit_workbook.py Read-only pre-release audit. Exits non-zero on failure.
    scripts/test_chords.py    Chord bathymetry against the INFOMAR grids; writes evidence text.
    scripts/make_snapshot.py  Builds the JSON the race officer page bundles.
    scripts/rebuild_page.py   Embeds that snapshot in the race officer page and bumps PAGE_VERSION.
    scripts/xlsx_edit.py      Surgical workbook edits, and a cell-level diff of two workbooks.

Command lines:

    python scripts/audit_workbook.py WORKBOOK
    python scripts/test_chords.py WORKBOOK RASTER_DIR [--chords "A>B,C>D"] [--rasters GEO12_04,KRY12_05,CB12_01]
                                  [--spacing 5.0] [--criterion 1.5] [--out chord_evidence.csv] [--date "30 Sep 2026"]
    python scripts/make_snapshot.py WORKBOOK [--out cardsnap.json]
    python scripts/rebuild_page.py WORKBOOK [--page pages/course/course_v8.html] [--dry-run]

Dependencies: `pandas`, `numpy`, `tifffile`, `openpyxl` (diff only).

**`test_chords.py`** tests every chord in the workbook, or those named with
`--chords`, sampling each every 5 m on the UTM 29N grid against the rasters under
RASTER_DIR, and writes a CSV whose `evidence` column is the text for the Evidence
Register. Chord lengths it reports are grid lengths, about 0.5 m per 1.3 km
shorter than the geodesic distances in ORC Distance Bearings.

**Always pass `--rasters`.** Where grids overlap, the first listed wins. Without
`--rasters` the order is alphabetical by filename, which puts CB12_01 first and
also includes every other GeoTIFF under RASTER_DIR, so the evidence would differ
from the register's. Cork Harbour work uses GEO12_04, then KRY12_05, then CB12_01:

    python scripts/test_chords.py RCYC_Cork_Harbour_ORC_MASTER_v3_19_CAGE_CORROBORATED.xlsx E:\Infomar --rasters GEO12_04,KRY12_05,CB12_01

**`xlsx_edit.py`** has no command line: it is used from Python. `Workbook(path)`
opens a workbook; `set_cell`, `append_readme`, `remove_sheet` and `delete_rows`
edit its sheet XML in place; `save(out)` copies every other part byte for byte.
`cell_diff(before, after)` lists every differing cell. `remove_sheet` and
`delete_rows` refuse, rather than guess, when anything in the workbook could depend
on what they remove. To compare two workbooks:

    python -c "import sys; sys.path.insert(0, 'scripts'); from xlsx_edit import cell_diff; [print(d) for d in cell_diff('OLD.xlsx', 'NEW.xlsx')]"

`cell_diff` compares cells by position, so after `delete_rows` every later row of
that sheet shows as changed: compare such a sheet record by record instead.

Rasters are the INFOMAR Inshore Ireland GeoTIFFs. Here they live in `E:\Infomar`,
one unzipped folder per dataset (e.g.
`E:\Infomar\BY_GEO12_04_CorkHarbour_2m_U29N_LAT_TIFF_Inshore_Ireland\`); any
layout below the directory passed as RASTER_DIR works. They are large (GEO18_02
alone is over 5 GB) and are not in the repository.

    Contains Irish Public Sector Data (Geological Survey Ireland & Marine
    Institute) licensed under CC BY 4.0.

## Tests

    tests/test_marks.py       Safety tests for pages/marks/marks.php.

Runs `marks.php` unmodified as real CGI requests against a throwaway day file
holding three races, and checks those races are intact after each case: a fix
or course that cannot be JSON-encoded, a damaged day file, a write failing
part-way, the RO page moving a fix (device, recorder and tap must survive), the tap
time (stored, returned, a bad one dropped while the fix is kept), the series
name (saved, read back and cleared; a wrong key, a bad name or a failed write leaves
`series.json` unchanged), and 60 fixes, 10 courses and 30 reads arriving at once.
Run it before uploading any change to `marks.php`.

Needs a local PHP install with `php-cgi` (in the Windows PHP zip; the `php-cgi`
package on Linux), found on PATH or through the `PHP_CGI` environment variable.
Tested with PHP 8.4 on Windows; the live host may differ.

## Deploying the pages

    pages/course/index.html      ->  /course/index.html  (generated: see below)
    pages/record/sw.js           ->  /record/sw.js       (upload before the page)
    pages/record/record.html     ->  /record/index.html
    pages/marks/marks.php        ->  /marks/marks.php
    pages/marks/key.js           ->  /marks/key.js      (not in the repository)

`pages/course/index.html` is not in the repository: `rebuild_page.py` writes it on
every run as a byte-identical copy of `course_v8.html`, which stays the source. Upload
that file as `/course/index.html`; never edit it by hand.

The race key is kept out of this public repository. Copy `pages/marks/key.example.js`
to `key.js`, set the key, and upload it next to `marks.php`: both pages load it and
`marks.php` reads it, so the key is changed in one place. Without a usable `key.js`,
`marks.php` refuses every request. Each phone remembers the last key it saw, so a
`key.js` that fails to load mid-race does not stop uploads.

**If the RIB page's service worker misbehaves,** upload `pages/record/sw-kill.js`
**as `/record/sw.js`**, replacing the real one. Do not just delete `sw.js`: a
missing file leaves the installed worker running. Each phone picks up the kill
switch the next time it opens `/record/` with signal (reload once if the page
looked wrong): it deletes the saved copies and unregisters itself, and the page
loads from the network as before. While the kill switch is in place the page still
registers it on each open, and it removes itself again at once. Put the real
`sw.js` back once it is fixed. `sw-kill.js` itself is never uploaded under its own
name.

`marks.php` keeps its data in `/marks/data/` and writes an `.htaccess` there that
denies web access. That only works on Apache or LiteSpeed; check it on the live server.

## Before any release

1. `python scripts/audit_workbook.py <workbook>` — must pass all 16 checks.
2. `cell_diff(before, after)` from `scripts/xlsx_edit.py` (the one-line command is
   under Scripts) — confirm the changed cells are exactly the ones intended, and
   nothing else moved.
3. Open the file in Excel itself, not only LibreOffice, and confirm it opens with
   no repair dialog.
4. If any coordinate changed, retest every dependent chord with
   `scripts/test_chords.py` and update its Evidence Register row. Do not carry the
   old numbers forward.
5. Add a Read Me change record: what changed, what did not, and the SHA-256 of the
   workbook it was made from.
6. `python scripts/rebuild_page.py <workbook>` — embeds a fresh snapshot in
   `pages/course/course_v8.html` and moves its `PAGE_VERSION` on, so the bundled
   data and the master do not drift, and writes `pages/course/index.html` as a
   byte-identical copy; upload that file as `/course/index.html`. It prints what
   changed in the snapshot first: after a change to the workbook alone, expect only
   `meta.source` and `meta.sha256`. `--dry-run` shows the changes without writing.
7. Record the new SHA-256 in this README.

A validation worth repeating whenever the sampling changes: Dosco to
RW_Fort_Davis is 641.3 m, 130/130 samples, minimum 2.875 m LAT. That reproduces a
result recorded long before these scripts existed.

## Open questions

1. **Harp and Ringabella.** The 2026 General SIs (§22.3, March) and the 2026
   Autumn League SIs (para 36, September) publish Ringabella 408 m apart and Harp
   83 m apart. The workbook follows the later document. RCYC has not been asked to
   resolve it.
2. **EF2.** The club-supplied position, adopted in v3.8 because a Navionics reading
   corroborated it: 15 m south, on an identical longitude. The Port publishes no
   position for this buoy and refers mariners to BA 1765, 1773 and 1777.
3. **No.6 to Cage** has a 29.9 m unsurveyed run near Cage. Deliberately retained at
   DIRECT – VERIFIED; do not downgrade it on coverage grounds without new evidence.
4. **Twenty-three chords pass under 2.0 m at LAT,** mostly around Cage. Passing,
   but the criterion is doing real work there.
5. **Mark's 204.** Navigation Tests holds 204 distinct directed pairs, 61 of which
   are not physical chords. Probably the population behind his figure; unconfirmed.

## Workbook sheets

`Read Me` change records · `Marks` positions, type, source, accuracy ·
`Course Card` the printed card as data · `Required Pairs` the 177 logical pairs ·
`Passages` one authoritative row per directed pair · `Navigation Tests` the
development test log · `Bathymetry Sources` the six INFOMAR grids used, with CRS,
pixel size, no-data value and extent · `Navigation Model` the routing rules: the
1.5 m chart-datum threshold, land and drying areas prohibited, inadequate coverage
for review, and the western routing boundary · `Numbered Legs` the physical legs,
the routing authority · `ORC Distance Bearings` geodesic geometry for those legs ·
`Evidence Register` numeric evidence per chord. The stale v2.76-era sheets
`Course Legs`, `ORC Export`, `Issues Audit` and `Resolution Priority` were removed
in v3.17; they remain in the repository history.

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
