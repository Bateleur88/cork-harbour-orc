# Cork Harbour ORC course routing

A machine-readable, navigationally realistic representation of the 2026 RCYC
Keelboat Racing Course Card, and the race officer tools built on it. Feeds
SailScoring `course-cards` issues #16 to #19.

## Current state

| | |
|---|---|
| Master workbook | `RCYC_Cork_Harbour_ORC_MASTER_v3_20_DUPLICATES_REMOVED.xlsx` |
| SHA-256 | `9fdaaf5b50ab9f6df3e6df047dc1b8a7f68361cc1298fb75356822d4190097aa` |
| Courses | 40, all matching the printed 2026 card |
| Configurations | 360 (40 courses x 3 starts x 3 finishes), none missing |
| Physical legs | 3,759, with 3,759 matching ORC geometry rows |
| Directed physical chords | 186 |
| Routing waypoints | 8, plus W2 used as a turning point in 9 passages |
| Marks used | 38 (by the card's routes) |
| Marks in the page's snapshot | 63, every mark with a position in the Marks sheet |
| Routes in the page's snapshot | 262: the 177 authored, plus the exact reverse of each of the 85 authored one way only |
| Evidence | every chord carries a numeric INFOMAR result; no chord on recovered evidence |
| Audit | `scripts/audit_workbook.py` passes all 16 checks |

The race officer page (`pages/course/course_v8.html`) bundles a snapshot generated
from the workbook above. See [The pages](#the-pages).

## Start here for reviewers

1. **Install.** Python 3 (developed on 3.12) with `pandas`, `numpy`, `tifffile` and
   `openpyxl`:

       pip install pandas numpy tifffile openpyxl

2. **Audit the workbook.** Read-only; prints a report and exits non-zero on any
   failure. Expect 16 PASS lines and the counts in the table above:

       python scripts/audit_workbook.py RCYC_Cork_Harbour_ORC_MASTER_v3_20_DUPLICATES_REMOVED.xlsx

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
  search for or build a route. Every route it uses comes from the snapshot: the
  workbook's authored routes and, where the workbook authors a route one way only,
  its exact reverse, added by `make_snapshot.py` and marked reversed, never worked
  out by the page. Where the snapshot has no route between two points of a course,
  the leg is measured straight and never refused; where it touches a Course Card
  mark it is labelled "not depth-checked". A routing waypoint the RO chooses for a
  course is the RO's choice: the legs either side are measured straight, say
  "routed via <RW> (RO-chosen)", and are labelled "not depth-checked" unless the
  workbook tested that exact chord. When Course 27 Dosco/Dosco was absent it correctly
  showed "No matching Numbered Legs rows found" instead of hiding the defect.
  **Two stated exceptions**, both of position only, both keeping the card's route
  and labelling the measured hop "not depth-checked": a recorded start or finish
  line stands where the card's start (or Grassy Mid finish) is (see The pages);
  and a club laid mark (Curlane, Dutchman, White Bay) takes
  its *position* from the day's RIB fix, because its stored coordinate is only a
  planning approximation. The mark is never substituted, only its position; only
  a fix whose name matches the mark's name, ignoring case, spaces and punctuation,
  is used automatically; the card's route to it
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

Three files in `pages/`, working together through the web server.

### RIB page (`pages/record/index.html`, served as `/record/`)

The RIB crew records each mark as it is laid, with the phone's GPS: pick the date
and race (Races 1 to 3), tap a name (quick picks include the laid marks Curlane,
Dutchman and White Bay) and record. Each fix carries a random id for the phone, an
optional "Who's recording?" name, the position's own time and the moment Record
was tapped. Fixes queue on the phone and upload to `marks.php` when there is
signal, so nothing is lost offline. A WhatsApp message headed "Laid marks – date"
is the backup. (`pages/record/record.html` is an identical copy of the same page.)
The ORC IRL watermark behind the page is embedded in it as a data URI, so it is
there offline; `pages/record/assets/orc-irl-watermark.png` is its source and is not
uploaded. The favicon, the ORC IRL sails with an orange (#FF6600) R badge, is
embedded in the page as data URIs, so it is there offline; its sources are in
`pages/record/assets/` and are not uploaded.

*A fresh position only.* Android Chrome can hand over the phone's last known
position first, with its own old time, even when asked not to. So a position more
than 5 s older than the tap (`FRESH_MS`) is ignored while the page keeps
listening; a fresh one at ±5 m or better is saved at once, otherwise the most
accurate fresh one after 10 s; with none by 20 s (`GIVE_UP_MS`) nothing is saved
and a red panel asks the driver to stay at the mark and tap Record again. "HOLD
STILL at the mark…" shows while waiting, "Saved ✓" only once a fresh position is
stored on the phone. *Clock risk:* a phone whose clock is more than 5 s out would
refuse every fix; set it to automatic time.

*Opening with no signal.* A service worker (`pages/record/sw.js`, served as
`/record/sw.js`, controlling `/record/` only) keeps a copy of the page and
`key.js`. Opening always tries the network first and uses the saved copy only if
the network fails, gives a server error, or takes over 3 seconds; only a response
containing the `PAGE_VERSION` marker replaces the copy. Each `PAGE_VERSION`
registers its own worker and cache (`record-<version>`), and the new worker
deletes the older ones. **Dock rule:** a phone must open
`https://<site>/record/` once with signal before it can open it without; bookmark
it with the trailing slash. Safari on iPhone may drop the copy after about a week
without a visit.

### Server (`pages/marks/marks.php`, served as `/marks/marks.php`)

Stores each day's fixes (`marks-YYYY-MM-DD.json`) and courses
(`courses-YYYY-MM-DD.json`) in `/marks/data/`, behind the race key in `key.js`.
Writes go to a temporary file renamed into place, under a lock; a damaged day file
is refused rather than overwritten. `marks.php` writes an `.htaccess` that denies
web access to `data/` (Apache or LiteSpeed only: check that a request for a file
there is refused with 403).

- *Courses* are keyed `race|start`; each race's start groups and picked chips are
  `_starts|race`; the day's series name and wind are `_day`, saved like a course (a
  save that sends only one of them keeps the other). `GET
  ?type=seriesbefore&date=` returns the series of the latest earlier day that has
  one. The older single series file, `series.json`, is still served for pages from
  before series names were per day.
- *Course history.* Before a course save replaces a version, the replaced version
  goes to `courses-history-YYYY-MM-DD.json`: per record, the first version of the
  day plus the last 5 replaced, each at most 50 KB, the file capped at 5 MB. If
  the history cannot be written the save is refused, so no version is lost. A
  damaged history file blocks that day's saves until it is put back from a backup
  or removed. Read with `GET ?type=coursehistory&date=`.
- *Typed positions* (accuracy 0, no phone) can be withdrawn (`withdraw`, with a
  reason) or corrected (`correct`, a new position with the old one withdrawn and
  linked), never deleted. Withdraw is refused while a saved course row or chosen
  line end uses the position; the course page moves rows to a corrected one. A RIB fix can still be deleted by the RIB page, and the
  course page's "Fix recorded under the wrong race?" re-posts a fix under a new
  race.
- *RO key and decisions endpoint (unused).* `marks.php` still accepts append-only
  review decisions, written only with an RO key taken from the `X-RO-Key` header
  and read from `/marks/data/ro-key.php` (template `pages/marks/ro-key.example.php`).
  No page uses it. A course save may carry
  `by` (who saved it); the course page does not send it.
- The race key is also accepted as `?key=` in the address; neither page sends it.

### Course page (`pages/course/course_v8.html`, served as `/course/`)

The race officer's page, in two views: **Setup** (sections 1 to 3: marks, import,
building the course) and **Race** (what is needed after the gun: the course and
total, legs, plot, wind shift, Send and the committee boat button). The course
card snapshot and an ORC IRL watermark are embedded. The favicon, the same ORC IRL
sails with a green (#2E8E47) C badge, is embedded as data URIs too, so it is there
offline; its sources are in `pages/course/assets/` and are not uploaded. From 1100 px
wide the page is
two columns (legs and course on the left; sketch or chart, Check recorded marks,
wind shift and Send on the right).

**The day.** *Race day* and **Get latest marks** load a day's fixes and courses
from the server, then refresh every 30 seconds. Every edit, fix and send belongs
to the day loaded. While the Race day box shows a different day from the one
loaded, the course is hidden and edits and sends are held ("Race day is X but Y is
loaded: tap Get latest marks"). A newly loaded day opens Start 1 of its race, or
its first start with a course. Reopened on the day it had loaded, the page shows
the copy on the device at once and refreshes in the background when there is
signal; reopened with Race day set to today and another day loaded before, it
says so and holds until the RO chooses.

**Series name** ("Series Name for Message heading", in Setup) belongs to the day
and heads the WhatsApp text. A day with none of its own shows the latest earlier
day's in orange, "carried from dd/mm/yyyy: check", with **Confirm**; the day's
first course save asks "Use it?" once (Use it or Change). Changing one day's
series changes no other day.

**Building a course.** Start groups (classes per start), **+ Start** and
**Remove Start**; a start time per start. Marks are added by tapping chips:
recorded fixes of the race, **Fixed marks** (every positioned mark in the Marks
sheet, labelled "Course Card", plus laid marks and routing waypoints), a card
course from **Import a harbour course**, a typed position (**Add a mark by typing
its position**, which asks for the time on the water) or a pasted WhatsApp
message (**Read marks from a WhatsApp message**). Each mark row has a rounding
side (P or S); routing waypoints have none. A pasted position stays on the device
only, shown in red with **Save to the race record**. A card mark's own name is
refused in the typing and pasting boxes. **Add to Race N chips** in Check recorded
marks brings any RIB fix of the day into a race as a picked chip.

**Line ends.** The Committee boat lists offer every recorded committee boat fix
of the day; the Start Pin list offers this race's fixes only, with **Auto** and
**None**. On Auto a start line end takes the latest fix of its race or an earlier
one at or before the start time; a fix after the start is shown as a candidate,
never used by default, and a Start Pin carried from an earlier race says so
("carried from Race N"). When a course is saved, Auto's choice is saved with it, so
the course rebuilds the same on every device. A start's saved Auto choices are
picked again when its start time changes, until the start is used: its course has
been sent, or, on the race day, its start time has passed. After a choice of the
RO's own (a fix chosen, a pin set or an end placed) a recorded fix is offered only
when it is newer ("Newer: … Use it"), never taken by itself. A start's line-end
choices are saved only once its start time is complete.

**Start line.** The Start line row has a **Committee boat** section, a **Start
Pin** section, then the line. With a start time each section has its helper, open
by itself while its end is missing and otherwise behind **Change boat…** or
**Change pin…**:
- the Start Pin **at a mark** (Option 1: a mark of the course, a harbour mark, or an
  earlier race's Start Pin, set at its position), or **placed by distance and
  bearing** (Option 2) from the committee boat in use or a mark laid in this race,
  never from a harbour mark;
- the committee boat placed by distance and bearing (°M) from the Start Pin or
  another mark. Placed from a harbour mark, that mark becomes the Start Pin, set at
  it, in the same placement; a different pin in use is switched out, and Undo puts
  it back;
- greyed suggestions (200 m, **Square to wind** or **Square to first mark**, which
  end the committee boat is at), worked from the end in use or from a harbour mark
  chosen under "from", used only if typed in;
- the **Grassy start** (the Grassy Walk line, measured from Grassy Mid), and, with
  one end found, that end **as the line midpoint**, drawn as a 200 m line square to
  the first leg.

A placed end is saved as a typed position timed at the start time and flagged as
an estimate on the page, the leg table, the sketch, the chart and Copy for Sail
Scoring (`"x-estimate"`), never in the WhatsApp text. An estimate carries forward
within its own race only; a later race is offered it. **Undo** withdraws what the
helper placed, and is refused while another start uses it. Placing an end again
withdraws the one it replaces; a replaced end not yet withdrawn (another start uses
it, or there was no signal) is labelled ", replaced" and never offered by "Use it?"
or Auto. A placed or typed line end that is no longer an estimate, or that was
replaced by placing again, can be withdrawn from **Check recorded marks**.
**Remove Start** moves
every later start's records down with it, withdraws the removed start's own placed
ends, and is refused while another start uses them.

**Finish line.** The **Finish type** list offers **Same as the start line**,
**Committee boat & Finish Pin**, and the finish line of another start ("Shared from
another start", which follows that start's changes). A start saved with "At the
last mark" keeps it, shown as "(saved before .44)" only on that start. With
Committee boat & Finish Pin and no finish set, the row says **No finish set** in
amber, as does the leg table's last leg, and Copy for Sail Scoring is INCOMPLETE;
Send is not held back. A Finish Pin a RIB recorded for the race is offered ("Use
it"), never chosen by itself, and no other race's Finish Pin is ever used. The
finish is set in one of three boxes, closed to their titles, one open at a time:
1. **Committee boat remains, place new Finish Pin**: the pin by distance and
   bearing from the committee boat in use;
2. **Choose Finish mark and position Committee boat**: the Finish Pin at a mark
   (any mark; the last mark finishes at the last mark), and the committee boat
   placed from it; below it, for emergencies only, the mark as the finish line's
   midpoint with no committee boat;
3. **Move Committee boat and Finish Pin**: a new recorded committee boat fix, then
   the Finish Pin placed from it.

Each box suggests a bearing **square to the last leg** (from the last mark to the
line's midpoint, for the length typed or 200 m) and which end the placed end goes,
used only if typed in; the likely Finish Pin end is marked as a suggestion until
the RO taps a side. A finish line more than 30° off square to the last leg is said
in amber. Placed finish ends are estimates, as start line ends are; **Undo**
withdraws them and puts back the committee boat end they replaced. A course saved
before the Finish Pin stopped using Auto keeps the pin Auto chose then, in amber:
"Finish Pin chosen by Auto in an earlier version: … – check it". **Change
finish…** reopens the boxes.

**Laid marks** (Curlane, Dutchman, White Bay) take their position from the latest
RIB fix, saved typed position or pasted position of the race or an earlier one
whose name matches, ignoring case, spaces and punctuation; with none, the card's
planning position, flagged until laid. A near miss is suggested, never applied.
The Position box lets the RO pin any fix or the card position; that choice, and
auto's choice, are saved with the course. Harp, Ringabella, Dosco and EF4 are
permanently moored and always use the workbook position.

**Legs.** Between two card marks the card's own route is used, passages included,
reversed from the snapshot where the workbook authors it one way only. Otherwise
the leg is straight, labelled "not depth-checked" where it touches a Course Card
mark. A recorded start line keeps the card's route from the card's start point
and measures only the first hop from the line, labelled; the finish likewise. For
a card course the card's Finish decides: Grassy Mid stands for the Grassy Walk
line; No.8 or Dosco is the mark itself. A No.8 or Dosco card start is a committee
boat line near the mark, never the mark. Distances and bearings use Vincenty on
WGS84, as the workbook does. Magnetic variation comes from the embedded World
Magnetic Model at the course's first leg (noon UTC on the race date), as Sail
Scoring computes it; with no measured leg, the map centre, said beside the wind
arrow.

**Wind.** The day's wind (direction 0 to 360 °M, large, and speed) is set in
section 1, under Race day; while it is empty an amber line asks for it. Each start
shows its own wind under its start time: it follows the day's wind until the start
is used, keeps a wind typed for it (clearing the box makes it follow again), and
says where its value came from ("from the day's wind", "set for this start",
"kept: course sent at hh:mm"). A start's wind gives TWA per leg, how far its line
is off square and which end is favoured. Without wind the line's length and
bearing still show.

**Check recorded marks** (closed by default, in both views): a sketch or map of
every fix of the race (or all races), with the recorded lines, the as-sailed
course of the selected start drawn over them, and advisory flags that never block
(old position, pin near a mark, line far off square, mark far from the same mark
in another race, pin order, no committee boat). Tapping a fix shows its detail;
typed positions there can be withdrawn or corrected. Typed or pasted positions more
than 8 nm from the map centre are listed, not drawn.

**Saving.** Course changes save automatically a second after each change and
every 15 seconds while any is unsent, once the device has loaded that day. The
line under Get latest marks says what happened: saved, waiting (no signal, no
key, no reply in 20 s, server error: retried every 15 s), or a record refused. A
load that leads to a save says why. Changing day first sends the old day's unsent
changes; if any cannot be sent the change of day stops ("Still on …"), and
"Change day anyway" is offered only when nothing more can be done.

**Send** (section 6):
- **WhatsApp**, **Share** and **Copy text**: a clean course list for competitors
  (series and date heading, race and start, the numbered marks with sides, each
  leg in °M with distance and TWA, the total and the positions). No route notes,
  estimates or labels.
- A course with a missing mark, a leg not measured, a leg under 50 m or a position
  over 8 nm away shows a red line above the buttons, and each asks "Send anyway?".
- **Copy legs for SailScoring**: one line per physical leg, distance in nm and
  bearing in °M.
- **Copy for Sail Scoring**: the start as one JSON document in Sail Scoring's ORC
  constructed course format (`docs/constructed-course-format.md`): legs from the
  same calculation as the leg table, distance to 0.01 nm, course in °M to one
  decimal, wind on every leg or none, the anchor where the first leg starts, the
  series as `"x-series"`. The name is the date, race and start, followed by any
  INCOMPLETE or STAND-IN warning. A start with no start time is not exported.
  Rounding sides are never sent.

**Clear everything** (foot of Setup, tap twice) clears this device as a reload
would; nothing is sent, and the first tap warns about anything unsent.

**Offline.** A service worker (`pages/course/sw.js`, served as `/course/sw.js`,
controlling `/course/` only) keeps a copy of the page and `key.js`. Opening always
tries the network first and uses the saved copy only if the network fails, gives a
server error or takes over 3 seconds (10 seconds when the page is reloading to a
newer version it found). The worker keeps only a page of its own version, so an
older page cached by the host never becomes the saved copy. Its cache is named
after its folder and version, and a new worker deletes only its own folder's older
copies, never the RIB page's or the test copy's. A device must open the page once
with signal before it can open it without.

Until the page has confirmed its version with the server since it was opened,
course saves (the day's series among them) and withdraw, correct, move to another
race, Undo's and Remove Start's withdrawals wait; new fixes and Send never wait.
The save line reads "Waiting: checking the page version", and a change of day
that cannot check stops with "Still on ‹day›: waiting to check the page version".
A newer page on the server reloads the page by itself, at most once a minute and
twice in all; after that a red line and **Reload** show under Get latest marks,
and nothing held is sent until the page reloads. The Google Fonts stylesheet
never holds the page: text shows at once in the fallback font. Safari on iPhone
may drop the saved copy after about a week without a visit, so open the page with
signal before each race day.

## Sites

- **tradboats.ie**: RCYC's live install, `/record/`, `/course/` and `/marks/`,
  with the test copy beside it (`/course-test/`, `/marks-test/`).
- **orc-ireland.org**: a separate install with its own race key and data, same
  layout; installed from a package by its own administrator
  (`docs/INSTALL_ORC-IRELAND.md`).

## Scripts

    scripts/geo.py            Vincenty, UTM 29N, GeoTIFF sampling. No GIS stack needed.
    scripts/audit_workbook.py Read-only pre-release audit. Exits non-zero on failure.
    scripts/test_chords.py    Chord bathymetry against the INFOMAR grids; writes evidence text.
    scripts/make_snapshot.py  Builds the JSON the race officer page bundles; refuses a duplicate mark name, two names
                              the same once capitals, spaces and punctuation are ignored, or a name read as a
                              committee boat, pin or finish.
    scripts/rebuild_page.py   Embeds that snapshot in the race officer page and bumps PAGE_VERSION.
    scripts/xlsx_edit.py      Surgical workbook edits, and a cell-level diff of two workbooks.
    scripts/build_test.py     Builds the parallel test copy of the RO page and marks.php (see Test copy), or with
                              --label LOCAL the local test site's copy (see Local test site).
    scripts/backfill_day_series.py  One-off: writes a series name into chosen past days, through marks.php,
                              after backing them up.

Command lines:

    python scripts/audit_workbook.py WORKBOOK
    python scripts/test_chords.py WORKBOOK RASTER_DIR [--chords "A>B,C>D"] [--rasters GEO12_04,KRY12_05,CB12_01]
                                  [--spacing 5.0] [--criterion 1.5] [--out chord_evidence.csv] [--date "30 Sep 2026"]
    python scripts/make_snapshot.py WORKBOOK [--out cardsnap.json]
    python scripts/rebuild_page.py WORKBOOK [--page pages/course/course_v8.html] [--dry-run]
    python scripts/build_test.py [--page ...] [--marks ...] [--out build/test] [--label LOCAL]
    python scripts/backfill_day_series.py --url URL --backup-dir DIR [--key-js PATH] [--series NAME] [--dates ...] [--dry-run]

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

    python scripts/test_chords.py RCYC_Cork_Harbour_ORC_MASTER_v3_20_DUPLICATES_REMOVED.xlsx E:\Infomar --rasters GEO12_04,KRY12_05,CB12_01

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

    tests/test_marks.py       marks.php, run unmodified as real CGI requests on throwaway data
    tests/test_build_test.py  build_test.py, plus static checks of the course page's source
    tests/test_backfill.py    backfill_day_series.py against a local marks.php

`test_marks.py` checks that every request the pages send is accepted, that bad
input and failed writes leave the data intact, and the course history, typed
position withdraw and correct, the day's series, the RO key and the decisions
endpoint. It needs `php-cgi` on PATH or in `PHP_CGI`; run it on PHP 8.4, PHP 8.1
(which the live host may move to) and PHP 5.5 (as the live host) before any change
to `marks.php`. `test_build_test.py`
builds a test copy into a throwaway folder and checks it talks only to
`/marks-test/` with `test-` storage keys, and that the build refuses pages it
must; it also holds static guards over the course page's source. None of these
runs the page's JavaScript.

**Browser regression harness.** Kept outside the repository, in
`E:\CorkHarbourORC_backups\harness`, because it reads copies of real data. It drives
the page in headless Edge against `marks.php` on PHP 5.5:
- `regress.py` and `compare.py`: every start of every day in a throwaway copy of
  the live or test data, read by the released page and by the new one, and
  compared (points, legs, totals, Copy for Sail Scoring, the saved record, the
  WhatsApp text);
- `madeup*.py`: a made-up day built by the page itself through the real
  `marks.php` on throwaway data, one check per line, then read back by the
  previous version;
- `legacy*.py`: chosen saved starts on a data copy read as before;
- `guards*.py`: each release's edits to the static guards, applied to the test
  file before it and checked to reproduce the committed one.

## Deploying the pages

    pages/course/course_v8.html  ->  /course/index.html
    pages/course/sw.js           ->  /course/sw.js       (upload before the page)
    pages/record/sw.js           ->  /record/sw.js       (upload before the page)
    pages/record/index.html      ->  /record/index.html
    pages/marks/marks.php        ->  /marks/marks.php
    key.js                       ->  /marks/key.js       (made from pages/marks/key.example.js; never in the repository)

The course page is uploaded exactly as committed. `rebuild_page.py` also writes
`pages/course/index.html`, a byte-identical copy, when a workbook release changes
the snapshot.

The race key is kept out of this public repository. Copy
`pages/marks/key.example.js` to `key.js`, set the key and upload it next to
`marks.php`: both pages load it and `marks.php` reads it. Without a usable `key.js`
`marks.php` refuses every request. Each phone remembers the last key it saw.

**If a page's service worker misbehaves,** upload that page's kill switch in place
of its `sw.js`: `pages/record/sw-kill.js` as `/record/sw.js`, or
`pages/course/sw-kill.js` as `/course/sw.js` (or `/course-test/sw.js` for the test
copy). Do not just delete `sw.js`: a missing file leaves the installed worker
running. Each device picks up the kill switch the next time it opens the page with
signal; it deletes that folder's saved copies and unregisters itself. Put the real
`sw.js` back once fixed.

## Test copy

A copy of the course page and `marks.php` that runs beside the live ones on the
same site, on its own data, so the live pages and data are never touched. The RIB
page has no test copy: its service worker would remove the live page's offline
copy.

    python scripts/build_test.py        ->  build/test/   (ignored by git)
    build/test/course-test/sw.js        ->  /course-test/sw.js      (upload before the page)
    build/test/course-test/index.html   ->  /course-test/index.html
    build/test/marks-test/marks.php     ->  /marks-test/marks.php

`BUILD.txt` names where each built file came from. The test page differs from the
live one only in its `key.js` path and `MARKS_BASE` (`/marks-test/`), `STORE`
(`test-`, so it never shares browser storage with the live page), `-test` on
`PAGE_VERSION`, "TEST" in the title, `noindex`, and a red banner.
The test worker differs from the live one only in its `key.js` path
(`/marks-test/key.js`); its saved copies are named for `/course-test/`, so the test
and live copies never touch each other's.

First install: create `/course-test/` and `/marks-test/`, upload the two files, and
place `/marks-test/key.js` by hand with a test race key different from the live
one. Opening `/course-test/` creates `/marks-test/data/`; check it is refused
(403). Copy into it, by FTP, the live days the test needs. That data holds real
recorder names and phone ids: keep any download of it outside the repository.

Each test build: back up `/marks-test/data/` and the current `/course-test/index.html`
and `/course-test/sw.js` first; upload `sw.js`, then the page (and `marks.php` if
it changed); check its `PAGE_VERSION` by view-source in a private window. To roll a
test build back, restore the page, `sw.js` and the data folder; if the restored
page has no service worker, upload `pages/course/sw-kill.js` as `/course-test/sw.js`
instead.

## Local test site

A copy of the test site on this PC, for testing on the tablet and phone over the
local network before the test copy. Its folder, `E:\CorkHarbourORC_local`, is
outside the repository: `site/` is served (`/course-test/` and `/marks-test/`,
with a made-up race key and a copy of the test data), `seed/` holds the data to
reset to, and `stage/` the last build.

    build-local.ps1     python scripts/build_test.py --label LOCAL into stage/, then the worker, page and
                        marks.php copied into site/, each checked against BUILD.txt (refused if built in the
                        same minute as the page served)
    start.ps1           PHP 5.5's server on port 8765 with router.php (which refuses /marks-test/data with 403);
                        prints RUNNING and the PAGE_VERSION served
    stop.ps1            stops the php.exe on port 8765 and checks the port is closed
    reset-data.ps1      puts the data back to the seed, checked file by file by SHA-256
    add-day-*.ps1       writes a made-up test day (positions in Cork Harbour) into the local data only,
                        with the server stopped

The local build differs from the test copy only in `-L<HHMM>` on its
`PAGE_VERSION` and "LOCAL TEST" in its title and banner, and the build refuses a
page that names a live host or an address outside the allowed list. Run the
server in a visible terminal and stop it when testing ends. GPS does not work over
http, so new fixes, opening offline, and Copy and Share on the devices are tested
on the test copy. Norton's behavioural protection can stop `php -S` after a few
seconds: the PHP folder and the local site's folder need exclusions.

## Releasing to a live site

1. **Timing.** Nothing goes to the live paths within 12 hours of a race.
2. **Tests.** `tests/test_build_test.py` passes; if `marks.php` changed,
   `tests/test_marks.py` passes on PHP 8.4, PHP 8.1 and PHP 5.5. The build has passed on the
   test copy: a script regression on copies of the live and test data (every
   start's legs, totals, outputs and saves against the released page), and the
   manual steps for what needs a person's eyes.
3. **Nothing unsent.** No RIB phone has fixes waiting and no RO device has course
   changes waiting.
4. **Backups**, outside the repository, in a dated folder: the live
   `/course/index.html`, `/course/sw.js`, `/marks/marks.php`, and the whole
   `/marks/data/` folder.
   Check the data folder's file count against FileZilla's and keep a SHA-256 list
   of every file:

       Get-ChildItem <folder> -File | Get-FileHash | Select-Object Hash, Path | Export-Csv <folder>.sha256.csv -NoTypeInformation

   These backups hold real recorder names and phone ids: never share them.
5. **Upload** in FileZilla, Binary mode: `marks.php` first if it changed, then
   `/course/sw.js`, then the page. Download each back and compare its SHA-256 with
   the file uploaded.
6. **Check** in a private window by view-source: the new `PAGE_VERSION`,
   `MARKS_BASE='/marks/'` and `STORE=''`, and no test banner. Load a raced day and
   check its totals are unchanged.
7. **Every device.** On each RO device (PC, tablet, phone, laptop) close every
   `/course/` tab and reopen it with signal; confirm it runs the new release
   before it is used again, by view-source or by wording only the new release
   shows. An older page can drop choices a newer one saved.

The detailed steps for each release are written to `build/release/` (not in git).

**Rollback.** Upload the backed-up page and `sw.js` (and `marks.php`, if it was
replaced) and restore the whole `/marks/data/` backup: an older page may not read
what a newer one saved. If the page rolled back to has no service worker, upload
`pages/course/sw-kill.js` as `/course/sw.js` instead, so every device drops the
newer page's saved copy. Anything saved after the backup is lost and must be
entered again. Then repeat step 7 for the older page.

## Before any workbook release

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
   data and the master do not drift. It prints what changed in the snapshot first:
   after a change to the workbook alone, expect only `meta.source` and
   `meta.sha256`. `--dry-run` shows the changes without writing. The page is then
   released as above.
7. Record the new workbook SHA-256 in the Current state table.

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
