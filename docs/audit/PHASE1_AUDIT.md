# Phase 1 audit: architecture and regional readiness

Read-only audit of `cork-harbour-orc` at commit `f30882f` (main, 7 October 2026). No code, data or workbook was
changed. This file is the only file created.

## How to read this report

Every statement carries one tag:

- **[V …]** verified, with the file and line numbers (or commit) that show it. Line numbers are for the files at
  `f30882f`. `course_v8.html` line numbers count the embedded snapshot as one line (line 797).
- **[D …]** documented only: stated in a document, not confirmed in code or tests.
- **[NE]** not established: it cannot be settled from the code, tests or documents. Each one has a question in §11.

Sources read, in the order the brief gives:

| Source | Version read |
|---|---|
| `README.md`, `PROJECT_HISTORY.md` | this repository at `f30882f` |
| Draft roadmap | a local draft kept outside the repository (draft 5, 7 Oct 2026). Called "ROADMAP" below. Its email summaries are not reproduced here. |
| Draft workflow passage | a local draft kept outside the repository |
| `docs/design/course-days.md` | `sailscoring/sailscoring` at `665f7b9` (status: proposed, October 2026). Called "course-days" below. |
| `docs/format.md`, `README.md` | `sailscoring/course-cards` at `7de4a2c` (format version 2). Called "format.md" and "cc-README" below. |
| RCYC data set | `course-cards` `data/rcyc/keelboat-2026/` at `7de4a2c`: `README.md`, `marks.json`, `keelboat.json`, `routing.json`. There is no `data/rcyc/README.md`; the README is one level down. |

What was run (each writes only to a temporary folder, or nowhere):

- `tests/test_marks.py` on PHP 8.4.26 and PHP 5.5.38 (`php-cgi` for each PHP version): all tests passed on both.
- `tests/test_build_test.py`: all passed.
- `scripts/audit_workbook.py` on the v3.19 workbook: 16 PASS, SHA-256 `ff0ae3ee…a735220`, as the README states.
- `PYTHONDONTWRITEBYTECODE=1` was set for all three, so no `__pycache__` was written. `git status` was the same
  before and after.

Not read: `pages/marks/key.js` (it exists locally and is gitignored), any `data/` folder, and the live JSON copies in the local backups folder.

---

## 1. Architecture as built

### 1.1 Components

| Component | File | Served as | What it is |
|---|---|---|---|
| RIB page | `pages/record/record.html` (a byte-identical tracked copy is `pages/record/index.html`) | `/record/` | A single HTML file with inline JS. Records GPS fixes and queues them for upload. [V record.html:1-356; `cmp` of the two files] |
| RIB service worker | `pages/record/sw.js`; kill switch `sw-kill.js` | `/record/sw.js` | Keeps a copy of the page and `/marks/key.js` for offline start. [V sw.js:1-43; sw-kill.js:1-10] |
| Server | `pages/marks/marks.php` | `/marks/marks.php` | A single PHP file storing fixes, courses, course history, decisions and the series name as JSON files. [V marks.php:1-395] |
| Race key template | `pages/marks/key.example.js` | `/marks/key.js` (the real file is not committed) | `window.RACE_KEY='…'`. [V key.example.js:5; .gitignore] |
| RO key template | `pages/marks/ro-key.example.php` | `/marks/data/ro-key.php` (placed by hand) | `return '…';` [V ro-key.example.php:10] |
| RO page ("Course Plot") | `pages/course/course_v8.html`; `pages/course/index.html` is generated and gitignored | `/course/` | A single HTML file with inline JS and the course-card snapshot embedded as one line, `const CARD={…}`. [V course_v8.html:797; .gitignore] |
| Master workbook | `RCYC_Cork_Harbour_ORC_MASTER_v3_19_CAGE_CORROBORATED.xlsx` | not served | The source of the snapshot. [V make_snapshot.py:40-135] |
| Scripts | `scripts/*.py` | not served | Audit, chord depth tests, snapshot, page rebuild, workbook edits, test-copy build. [V each file's docstring] |
| Tests | `tests/test_marks.py`, `tests/test_build_test.py` | not served | Server safety tests through `php-cgi`; tests of the test-copy builder. [V] |

### 1.2 Data flow: RIB page → server → Course Plot → leg table

1. **Recording.** Tapping Record starts `watchPosition`. Positions older than `FRESH_MS` (5 s) before the tap are
   ignored. A position at 5 m or better is saved at once; otherwise the best fresh one is saved after 10 s. With
   nothing fresh by 20 s, nothing is saved. [V record.html:279-321]
2. The fix is pushed to the phone's state `S.marks` (localStorage `laid-mark-log-v4`). It carries a client id
   `uid()` (base-36 `Date.now()` plus random), date, race, name, lat, lon, acc, `time` (the position's own
   timestamp), `tap`, recorder and `sent:false`. [V record.html:166, 200, 297-299]
3. **Upload queue.** `sync()` posts every unsent fix as `{action:'add', …, device}` with the `X-Race-Key` header,
   then sends queued deletes. It runs every 15 s, on `online`, and when the page becomes visible. [V record.html:211-242]
4. **Server.** `marks.php` checks the race key [V marks.php:196-198]. It validates the fix [V :349-372] and writes it
   into `data/marks-DATE.json`, keyed by fix id, with `received` (server time), under a lock, through a temporary
   file and a rename [V :91-114, 377-395].
5. **Course Plot read.** "Get latest marks" calls `GET ?date=`. Each fix is loaded into the page's `S.marks` with
   `sid` (server id), `tms` (position time), `rcv` (received) and a per-race-and-name `fix` number in time order
   [V course_v8.html:2046-2088]. It then calls `GET ?type=courses` [V :2089-2092], checks line references
   [V :2093] and starts `GET ?type=decisions` without waiting for it [V :2099]. While the day is today and the last
   load succeeded, it refreshes every 30 s [V :2110].
6. **Building a course.** The RO either imports a card course [V :845-877] or taps "bank" chips, one per fix or
   card mark, in rounding order [V :924-940]. Line ends (committee boat, Start Pin, finish committee boat, Finish
   Pin) are chosen automatically or by the RO [V :1129-1186]. Laid card marks take a RIB fix by name [V :583-632].
7. **Course save.** Every `commit()` schedules `saveCourses()` 800 ms later, and the save also runs every 15 s
   [V :1047, 2183, 2341]. One record per `race|start`, plus `_starts|race` for start groups, is posted as
   `{action:'course', date, key, data, by?}` [V :2168-2204]. On the server the previous version moves into the
   history file first [V marks.php:267-308].
8. **Legs and outputs.** `buildLegs()` computes the legs from the page's current state `S`, not from the
   server's course file or history. It produces the legs table, the SailScoring leg table, the WhatsApp text and
   the plot [V course_v8.html:1329-1404]. Legs are never stored on the server: `recordFor()` has no legs field
   [V :2168-2177].
9. **Decisions** are read and shown only. No page writes a decision. The RO key is stored on the device and
   never sent [V :427-430, 1655-1659; a search of both pages finds no request carrying `X-RO-Key` and no
   `action:'decision'`].

### 1.3 Storage layout and file naming

All files are in `data/` next to `marks.php` (`dirname(__FILE__).'/data'`) [V marks.php:200].

| File | Shape (from the code that writes it) | Written by |
|---|---|---|
| `marks-YYYY-MM-DD.json` | Object keyed by fix id. Each value: `id, date, race (1-9), name (≤80), lat, lon (7 dp), acc (1 dp), time (ms), received (s)`, optional `device, recorder (≤60 chars), tap`. Legacy fixes may carry `series`. | `action:'add'` and `'delete'` [V marks.php:346-395] |
| `courses-YYYY-MM-DD.json` | Object keyed `race\|start` (regex `\d{1,2}\|\d{1,2}`) or `_starts\|race` or `_starts`. Each value: `{data, updated, by?}`, with `data` ≤ 50,000 bytes encoded and at most 200 keys a day. | `action:'course'` [V :266-308] |
| `courses-history-YYYY-MM-DD.json` | Object keyed like the courses file. Each value is a list of `{data, updated, replaced, by?, replaced_by?}`. | Same request, before the course is replaced [V :284-301] |
| `decisions-YYYY-MM-DD.json` | Object keyed by record id, in insertion order. Each record holds the validated fields plus `series` and `when` (server time). | `action:'decision'` [V :310-344] |
| `series.json` | `{name (≤60), updated}`. One per `data/` folder, with no date. | `action:'series'` [V :250-260] |
| `ro-key.php` | Exactly one `return '…';` holding 16-64 characters from `[A-Za-z0-9_-]`, read as text | placed by hand [V :51-59] |
| `.htaccess` | Deny-all, Apache 2.2 and 2.4 syntax, written only if absent | marks.php [V :203-206] |
| `.write.lock`, `*.tmp` | Lock file; temporary file before a rename | marks.php [V :91-114] |

The course record `data` written by the RO page has this shape [V course_v8.html:2168-2177]:
`{entries:[{ref:'s:<server id>'|'l:<local id>', side:''|'P'|'S'}], startTime:'HH:MM', finish:'start'|'finishpin'|'last', lineSel:{cb|pin|fcb|fpin: ref|'auto'|'none'}, wind:{twd (°M, as typed), tws}, card:{c, s, f, ls?, lf?, lfs?}|null}`.
A `_starts|race` record holds `{classes:[[…],…]}`.

The laid-mark choice `S.laidSel`, the acknowledgements `S.laidAck` and `S.laidNo` are kept on the phone only. They
are not in `recordFor()` [V :557, 2168-2177].

### 1.4 Authentication

| Key | Where it is set | Where it is checked | Scope |
|---|---|---|---|
| Race key | `key.js` next to `marks.php`, read by regex; empty, under 6 characters or `CHANGE_ME` refuses every request with 500 [V marks.php:35-41, 196] | Header `X-Race-Key`, **or the URL parameter `?key=`** [V :197], with a constant-time compare [V :77-83, 198] | Every GET and POST: fixes, deletes, courses, history, series, decisions read |
| RO key | `data/ro-key.php`, read as text and never run [V :51-59] | Header `X-RO-Key` only [V :314-315] | `action:'decision'` writes only [V :311-316] |

- Both pages load `/marks/key.js` with a `<script>` tag and keep the last key seen in localStorage (`race-key`; on
  the RO page `STORE+'race-key'`). [V record.html:10, 145-146; course_v8.html:391-392]
- `keyFetch` re-reads `key.js` once on a 403. [V record.html:157-164; course_v8.html:403-410]
- The RO page stores the RO key in localStorage `STORE+'ro-key'` and never sends it. [V course_v8.html:431, 2306-2307; no sender found]
- The race key is effectively public to anyone who can load a page, because `key.js` is a public script.
  [D README.md:186; course-days.md:261-263] The code agrees: `key.js` is served as a script. [V record.html:10]

### 1.5 Build pipeline

1. The workbook is edited only through `scripts/xlsx_edit.py`, which edits sheet XML in place.
   [V xlsx_edit.py:1-22; D README.md:92, 466-476]
2. `audit_workbook.py WORKBOOK` runs read-only checks. Today: 16 PASS, with the SHA-256 the README gives.
   [V run today; README.md:11-20]
3. `make_snapshot.build()` reads the sheets `Marks`, `Numbered Legs`, `ORC Distance Bearings` and `Course Card`
   and produces `{meta, marks, pairs, courses}`. Pair bearings come from the column `Bearing °T`, so they are
   **true** bearings. [V make_snapshot.py:43-48, 125-127]
4. `rebuild_page.py WORKBOOK` replaces the single `const CARD=` line and bumps `PAGE_VERSION`. It refuses unless
   there is exactly one of each and the result reads back as the snapshot. It then writes `course_v8.html` and a
   byte-identical `index.html`. [V rebuild_page.py:191-283]
5. The embedded snapshot today names v3.19, SHA `ff0ae3ee…`, generated 2026-10-01, and holds 38 marks, 177 pairs
   and 40 courses with nine start/finish configurations. [V course_v8.html:797, decoded]

### 1.6 Test and release tooling

- `tests/test_marks.py` (§10) and `tests/test_build_test.py` (§10).
- `scripts/build_test.py` builds `/course-test/` and `/marks-test/` copies. It changes the `MARKS_BASE`, `STORE`,
  `PAGE_VERSION` and title lines, adds a banner and `noindex`, copies `marks.php` unchanged, and refuses a page
  whose storage keys lack `STORE`. [V build_test.py:1-28]
- `scripts/test_chords.py` tests chord depth against the INFOMAR rasters, which are not in the repository.
  [V test_chords.py:1-18]
- Release steps: README.md:620-639 (workbook) and README.md:604-618 (live backup and rollback). The release steps
  themselves are [D] only: no script enforces their order.

---

## 2. Claim verification

### 2.1 ROADMAP §1a, "Documented as implemented" (and "Field-proven")

| # | Claim (ROADMAP line) | Status | Evidence |
|---|---|---|---|
| F1 | RIB offline queue and service worker tested on the water (55) | **documented only** for the field test | The code exists [V record.html:209-242; sw.js:17-43]. The on-water test cites a "position paper", which is not in the repository [NE]. |
| F2 | End-to-end use on 27 Sep 2026, with the leg table transferred by hand (56) | **documented only** | PROJECT_HISTORY.md:174-185. The repository's first page commit is `e370fb8`, later than 27 Sep: the first commit, `ee9e7f9`, is described in PROJECT_HISTORY.md:238 as 29 Sep. The code used on 27 Sep is [NE]. |
| F3 | Geometry is derived from a committee boat position and a pin position (57) | **verified** | `mkLine(cb,pin)` with the midpoint [V course_v8.html:1127, 1186]; legs from the midpoint [V :1343-1344]. |
| 1 | Several observations of a mark are retained, not overwritten; each keeps its position time, and the tap time since `4a66559` (62) | **verified, with exceptions** | Each fix gets a new client id [V record.html:200, 297] and the server stores by id [V marks.php:387]. Tap time is stored [V marks.php:370-372], commit `4a66559` dated 2026-10-05. Exceptions: fixes can be deleted or re-posted (rewritten). See §3, invariant 1. |
| 2 | Automatic fix choice never picks a fix recorded after the start (`8d36c09`) (63) | **verified for start-line ends; contradicted for laid marks** | Committee boat and Start Pin: the latest fix at or before the start [V course_v8.html:1178-1184]; inheritance across starts [V :1161-1169]; commit `8d36c09` (2026-10-01) is titled for line ends. Laid card marks: `laidState` takes the latest exact-name fix of race ≤ current, **with no start-time test** [V :602-605]. Finish Pin: "latest", no time limit [V :1176-1177; D README.md:284-285]. Windward and Leeward course rows are tapped by the RO, not chosen automatically [V :940]. |
| 3 | A dedicated "Copy legs for SailScoring" block (`98f9713`, 30 Sep) (64) | **verified** | Commit `98f9713` dated 2026-09-30, "Course page: leg table for SailScoring". Current code: course_v8.html:353-358, 1358, 1405-1419, 2426-2428. |
| 4 | Fresh position only: >5 s older than the tap ignored; ≤5 m saved at once, else best after 10 s; nothing after 20 s (`ce3e7e4`) (65) | **verified** | record.html:279-321. Commit `ce3e7e4` (2026-10-05). The rule applies to the RIB page only: the RO page's "Record committee boat here" has no freshness check and sends no tap [V course_v8.html:2318-2340]. |
| 5 | Race and start structure, with course history per race and start: first of the day plus the last 5, size-capped (66) | **verified** | Course keys `race\|start` [V marks.php:270]; history [V :284-301]; `HISTORY_KEEP` 5, cap 5 MB [V :44-45, 117-127]; tests t11 to t14 pass. No page reads the history [V: no `coursehistory` in either page]. |
| 6 | Append-only decisions file (use as, do not use, accept, revoke), written only with the RO key, read with the race key (67) | **verified (server); no page writes decisions** | marks.php:143-194, 310-344, 224-229; test t15 passes. The RO page only reads [V course_v8.html:1655-1678]. The decisions layer has no single commit in the roadmap; server `d6d24a8`, read layer `56b7750`, glyphs `f30882f`. |
| 7 | "Check recorded marks" (`01329fc`): read-only plot, computed lines, candidates never joined by default, advisory flags (68) | **verified** | Commit `01329fc` (2026-10-05). Read-only: course_v8.html:281, 1471-1476. Flags and thresholds: :1477-1480, 1518-1554. Lines and candidates: :1580-1640 (candidates never joined: :1602-1612). The flags listed in the roadmap all appear in `fxChecks`. |
| 8 | Server-side tests on PHP 8.4 and PHP 5.5; `test_build_test.py`; no browser-workflow tests (69) | **verified** | Run today: all passed on PHP 8.4.26 and 5.5.38; `test_build_test.py` all passed. No browser or JS test exists in the repository [V `git ls-files`]. |

### 2.2 ROADMAP §1b, intended workflow (steps)

| Step | Claim (ROADMAP 109-115) | Status | Evidence |
|---|---|---|---|
| 1 | RIB page records the laid marks, ideally in race order; roles include CB, Windward, Leeward, Start Pin, Gybe, Finish Pin; every fix saved as JSON; several fixes with the same name kept, told apart by time | **verified** | Race buttons 1-3 [V record.html:90]. Preset chips: `Committee boat, Start Pin, Windward, Leeward, Offset, Gybe, Finish Pin, A-D, Curlane, Dutchman, White Bay` [V :167-168]. Stored as JSON [V marks.php:377-392]. Same-name fixes are separate ids; the list labels "moved (fix n)" in time order [V record.html:205-206, 249]. The roles are free-text names, not a typed field (§6). |
| 2a | The Course Plot starts by assigning a Series Name to the course | **contradicted in part** | The field is first in Setup [V course_v8.html:236]. The series is one value for the whole `data/` folder, not per course [V marks.php:250-260]. Course records carry no series [V course_v8.html:2168-2177]. Nothing requires it before building. Decisions are stamped with the series at write time [V marks.php:337-338]. |
| 2b | Get Latest Marks reads the exact as-recorded marks and never edits that source data | **verified for Get Latest Marks; contradicted for the page as a whole** | `pull()` is GET only [V course_v8.html:2053]. The same page can rewrite a fix's race on the server ("Fix recorded under the wrong race?") [V :2112-2147], and can add fixes (committee boat, typed) [V :2330, 2388]. |
| 3 | The page builds a first course from mark names and recorded times, using each race's start time and classes, and saves it as the original recorded course | **contradicted** | The course is built by RO taps or a card import [V :845-877, 940]. Automatic parts: start-line ends by time [V :1172-1185]; laid marks by name [V :599-615]. Classes set the number of starts and the labels; no leg calculation in `buildLegs` reads them [V :1329-1404]. There is no designated "original": every edit is autosaved as the current `race\|start` version [V :1047, 2183-2204]. The first version saved that day is kept in history as `list[0]` once replaced [V marks.php:289-296]. |
| 4 | Wind direction and optional speed give line squareness and whether the windward mark is a true beat | **verified** | `analysis()`: line length, bearing, off-square angle, favoured end [V course_v8.html:1257-1272]; windward mark angle from square, measured from the start-line midpoint [V :1273-1283]. Wind is entered in °M and converted with `varW()` [V :321-322, 1331-1333]. A wind-shift box gives mark moves [V :1293-1328]. |
| 5 | Check recorded marks: where automatic detection gives a wrong plot, the RO selects which recorded marks are used | **contradicted as located; partly present elsewhere** | "Check recorded marks" is read-only and selects nothing [V :281, 1472-1474]. Selection happens in section 3: the line-end pickers [V :1235-1250, 2353-2357], the laid-mark position picker [V :625-632, 2359], course-row taps and "newer fix" [V :2393-2404]. Decisions recording a selection are read and shown only; no page writes them [V §1.2 step 9]. |
| 6 | The updated course is saved as its own complete record, derived from the original plus accept / use-as / not-to-be-used decisions; it never overwrites the original | **not built; contradicted** | There is one course record per `race\|start`, replaced on each save [V marks.php:302-305]. Decisions do not change any course, line, leg or output [V course_v8.html:1576-1577, 1655-1659]. No record references decisions [V :2168-2177]. |
| 7 | The updated course is what is handed to Sail Scoring as the As Sailed Course | **contradicted** | The leg table is built from the page's current state `S` [V :1329-1358]. That state is the RO's current course, including unsent local edits. No updated course exists (step 6). |

### 2.3 ROADMAP §1b, invariants

| Invariant (ROADMAP 121-126; workflow insert 21-25) | Status | Evidence (details in §3) |
|---|---|---|
| Source observations are never edited or overwritten; new fixes are added | **contradicted** | Delete [V record.html:224, 331-334; marks.php:388-390]; re-post overwrite [V marks.php:383-387; course_v8.html:2132] |
| The original recorded course is never overwritten | **contradicted** (the current version is replaced); first-saved version retained in history | marks.php:302-305, 289-296 |
| Decisions are append-only | **verified** at the API | marks.php:310-344; no update or delete action |
| The updated course is always derived, never hand-edited | **not established**: no updated course exists | §2.2 step 6 |
| What is handed to scoring is the updated course | **contradicted** | §2.2 step 7 |

### 2.4 ROADMAP §1b, "Phase 1 checks against this workflow" (ROADMAP 128-134)

- *Is the leg table produced from the updated course, or from the original if there is none?* Neither. It comes
  from the page's live state [V course_v8.html:1329-1358].
- *Is the workflow the same for a start with no decisions?* Yes: decisions never enter the calculation, so the
  output does not depend on them [V :1655-1659].
- *Terminology.* The code's own terms are "course", "course record" (`recordFor`), "version", "history" and
  "review decisions" [V course_v8.html:2164-2177; marks.php:22-33]. The terms "original recorded course", "updated
  course" and "As Sailed Course" do not occur in the code or the README [V by search].

---

## 3. Invariants: can any code path violate them?

### Invariant 1: observations are never edited

| Path | Effect | Evidence |
|---|---|---|
| RIB page ✕ on a sent fix | Queues `{action:'delete'}`; the server `unset`s the fix, with no tombstone or history | [V record.html:331-334, 222-226; marks.php:388-390] |
| RO page "Move" (fix under the wrong race) | Re-posts `action:'add'` with the same id and a new race. The server replaces the record. `device`, `recorder` and `tap` are kept [V marks.php:383-386]. `received` is reset to the server time [V :361]. `acc` is sent as `m.acc‖0` and `time` as `m.tms‖Date.now()`, so a fix without them gets new values | [V course_v8.html:2130-2132] |
| Any client with the race key | Can post `add` with an existing id and any content, or `delete` any id. A retry overwrites ("same id twice … just overwrites") | [V marks.php:387] |
| Manual file restore | The README tells the operator to restore a day file from a dated copy in some cases | [D README.md:613-616] |

New fixes from the RIB page always get new ids, so a recorded-then-moved mark adds a fix and replaces none.
[V record.html:297]

### Invariant 2: the original recorded course is never overwritten

- **The current version is overwritten** on every changed save: `$c[$k] = $rec` [V marks.php:302-305]. Saves are
  automatic, 800 ms after any edit [V course_v8.html:2183].
- **The replaced version is kept first.** If the history cannot be written, the course save is refused (500)
  [V marks.php:284-299; tests t13 pass].
- **Removing a start** saves an empty record for the race's last start number, if the server had one
  [V course_v8.html:1043].

### Invariant 3: decisions are append-only

- There is no update or delete action. A second record with the same id and different content gets 409; an
  identical retry gets 200 and writes nothing [V marks.php:320-326]. A revoke is a new record [V :330-336].
- There is a cap of 2000 records a day [V :327]. A decision must name a fix currently on the server [V :328-329].
  Deleting that fix later leaves the decision naming a missing fix; the page flags this [V course_v8.html:1791-1792].
- A damaged decisions file blocks writes (`load_json` refuses) [V marks.php:96-103]. `GET ?type=decisions`
  silently returns an empty list for an unreadable file [V :224-229].

### Invariant 4: the updated course is derived, never hand-edited

- No updated course exists [§2.2 step 6]. The single course record is built by hand by design: taps, reorder,
  delete, side, line-end picks [V course_v8.html:2393-2404, 2353-2356].

### Invariant 5: what is handed to scoring is the updated course

- The leg table is produced from `S` [V :1329-1358, 1405-1419]. It is not produced from a stored record.

### Course-history cap: the three questions

**Is the original always retained?**

- `list[0]` is never dropped by the keep rule: `array_merge(array($list[0]), array_slice($list, -5))` [V marks.php:296].
- `list[0]` is never dropped by the size cap: the loop starts at `$i = 1` [V :120]. When only first versions
  remain, the cap stops and the file may exceed 5 MB [V :124].
- Test t12 confirms every first version is kept [V tests/test_marks.py:487-497; run today: 116 of 120 versions
  kept, all firsts kept].
- What `list[0]` is: the first version of that key **saved to the courses file and then replaced** on that day,
  while that history file existed [V marks.php:288-296]. With autosave this is the first state the page saved,
  which may be a partly built course [V course_v8.html:2183]. It is not a version the RO designated.
- `list[0]` is lost if the history file is removed. The README gives that as one way to unblock a damaged history
  file [D README.md:170-173]. It is also absent for courses saved before `d6d24a8`, when there was no history
  [V commit d6d24a8 adds it].
- A course saved once and never replaced has no history entry. Its only copy is the courses file.

**Could the cap drop an "updated course"?**

- The current version is in the courses file, not the history, so neither the cap nor `HISTORY_KEEP` touches it
  [V marks.php:302-305].
- Replaced versions other than the first are dropped: beyond the last 5 per key [V :296], and oldest-first across
  all keys when the file exceeds 5 MB [V :117-127]. Any intermediate version can therefore be dropped, including
  one that was the RO's corrected course before a later save.

**Does the updated course record which original and which decisions it came from?**

- No. The record holds `entries, startTime, finish, lineSel, wind, card`, plus the server's `updated` and `by`
  [V course_v8.html:2168-2177; marks.php:302-303].
- It holds no version id, no reference to a history entry and no decision ids.
- Line ends stored as `'auto'` and laid marks (whose choice is not stored at all, §1.3) are resolved again each time
  the page renders. A stored course can therefore give different legs later if fixes are added, moved or deleted
  [V course_v8.html:1155-1185, 599-615].

---

## 4. Cork / RCYC-specific dependencies

Kind: **data** means a value that could live in a venue data set. **code** means a rule embedded in logic.
**deploy** means a path or host setting.

| File:line | What it is | Kind |
|---|---|---|
| record.html:167-168 | Quick-pick chips include the club laid marks `Curlane`, `Dutchman`, `White Bay` (exact names, so the RO page matches them) | data (in code) |
| record.html:90; course_v8.html:2118 | Races 1-3 only on the RIB page and in the "move fix" list (server accepts 1-9 [marks.php:356]) | code constant |
| record.html:142, 10; sw.js:12 | Absolute paths `/marks/marks.php`, `/marks/key.js` | deploy |
| record.html:166, 175, 146 | Unprefixed localStorage keys `laid-mark-log-v4`, `rib-device-id`, `rib-recorder`, `race-key` | deploy |
| sw.js:10, 25 | Cache names `record-<version>`; a new worker deletes every `record-` cache on the origin | deploy |
| record.html:279 | `FRESH_MS 5000, GOOD_ACC_M 5, SETTLE_MS 10000, GIVE_UP_MS 20000` (README ties them to 4 Oct 2026) | code constants |
| course_v8.html:373 | `MARKS_BASE='/marks/'`, `STORE=''` (changed by `build_test.py` for the test copy) | deploy |
| course_v8.html:526 | `CLASSES`: six RCYC class names (Class 1-3 Spinnaker / Non Spinnaker) | data (in code) |
| course_v8.html:586-598 | Near-miss name rule (substring when ≥4 chars, or Levenshtein ≤2); the comment cites "Curlane Bank" | code (generic algorithm, Cork reason) |
| course_v8.html:720, 2017 | Map initial view `51.82, -8.27`, zoom 13 | data (in code) |
| course_v8.html:797 | Embedded snapshot of the v3.19 workbook: 38 marks, 177 pairs, 40 courses | data (embedded) |
| course_v8.html:798 | `CARD_STARTS=['Grassy Mid','No.8','Dosco']` (start and finish options, and the snapshot's `cfg` keys) | data (in code) |
| course_v8.html:839 | Card `**` rule text: Dosco inserted as Mark 1 for the Grassy Walk line | code text (Cork card rule) |
| course_v8.html:852-858 | Card sides matched in order; a first printed mark equal to the start is skipped | code |
| course_v8.html:961, 1198, 1383 | Mark type string `'Start/finish modelling point'` decides "mark itself" against "line near the mark" | code keyed to workbook vocabulary |
| course_v8.html:1011 | `cardShort()` expects the workbook name pattern `…_vN_N_…` | code |
| course_v8.html:1108 | `BOAT_M=10` (boat length for line bias) | code constant |
| course_v8.html:1109-1117 | `varW()`: magnetic variation fitted to Irish WMM values (Dublin 1.55°W, Cork 1.88°W), from the mean longitude of loaded marks and **today's date** | code (Irish constants) |
| course_v8.html:1118-1125, 1584, 1661 | Role detection by English name: `/committee/i`, `/pin/i` without `/finish/i`, `/finish/i` with `/pin/i`, `/windward/i`, `/leeward/i`, `/gybe/i`, `/offset/i` | code |
| course_v8.html:1138 | `ACC_CHECK 15`, `ACC_POOR 30` m | code constants |
| course_v8.html:1189-1205, 1340-1344 | Cork start and finish rules: Grassy Mid stands for the Grassy Walk line; a No.8 or Dosco finish is the mark itself; No.8 or Dosco starts are committee-boat lines (comment cites "Autumn League SI 2026", "Cage (C1)") | code (Cork rule) |
| course_v8.html:1347-1350 | Warning when the recorded start line is >500 m from the card start point | code constant |
| course_v8.html:470, 1289 | Beat ≤50°, run ≥140°; fix accuracy >10 m flagged | code constants |
| course_v8.html:1474, 1477-1480 | `FIX_AGE_CHECK_S 20`, `FIX_AGE_BAD_S 300`, `PIN_NEAR_M 60`, `LINE_SQUARE_DEG 45`, `SAME_NAME_M 500`, "tuned to one day's fixes (4 Oct 2026)" | code constants |
| course_v8.html:1500 | Race colours for races 1-3 only | code |
| course_v8.html:2329 | Committee boat fix name literal `'Committee boat'` | code |
| course_v8.html:364; record.html:118 | Footer "© 2026 Pat Tanner ORC Ireland"; ORC IRL watermark | data (branding) |
| make_snapshot.py:28-33 | `FLAGS` text for Ringabella, Harp, EF4, Grassy Mid | data (in code) |
| make_snapshot.py:36-37 | `LAID_TYPE='Club laid mark'` and its flag text (laid marks come from the Marks sheet Type, not a list) | code keyed to workbook vocabulary |
| make_snapshot.py:131-133 | INFOMAR criterion and attribution strings in `meta` | data (in code) |
| make_snapshot.py:44-110 | Workbook sheet and column names (`Numbered Legs`, `ORC Distance Bearings`, `Bearing °T`, `Start Option`, `Original Pair`, `Round One…Three`, `Cum NM R1-3`, `Card flag`) | code keyed to workbook schema |
| audit_workbook.py:32, 179 | `STARTS=['Grassy Mid','No.8','Dosco']`; the `**` Dosco rule | code |
| geo.py:53-56 | Projection fixed to UTM zone 29N (central meridian -9°) | code constant |
| test_chords.py:70; README.md:459-464 | INFOMAR raster name parsing (`_U29N`); raster priority GEO12_04, KRY12_05, CB12_01 | code / data |
| marks.php:250-260 | One series name per `data/` folder | code (keyed to a single series) |
| README.md:22, 142, 583-595 | Host `tradboats.ie` | deploy (documented) |

`marks.php` contains no Cork or RCYC name, position or rule [V marks.php:1-395, by reading].

---

## 5. Generic components

This section lists what the code shows. Whether each part works at another venue is not shown by any test.

| Component | Venue-neutral? | Evidence |
|---|---|---|
| `marks.php` storage, locking, atomic writes, history, decisions, keys | Yes: no venue content; data folder relative to the script | [V marks.php:1-395]. A second copy in another folder keeps separate data; `/marks-test/` relies on this [D README.md:556-571] |
| RIB fresh-position rule, upload queue, client fix ids, delete queue, WhatsApp backup | Yes, apart from the preset list, the race count and the absolute paths in §4 | [V record.html:200-242, 279-321, 256-262] |
| RIB service worker | Yes, apart from the `/marks/key.js` path and the origin-wide `record-` cache cleanup | [V sw.js:10-43] |
| RO page: line-end resolution (`endPick`/`autoEnd`), inheritance between starts, line-end pickers | Yes, given English role names | [V course_v8.html:1129-1250] |
| RO page: laid-mark resolution | Data-driven: laid marks are those with `laid:true` in the snapshot | [V course_v8.html:590-615; make_snapshot.py:59-61] |
| RO page: card routing (`legGeom`) | Data-driven from `CARD.pairs`; the page never searches for a route | [V course_v8.html:635-661] |
| RO page: hand-built courses with no card | Code path exists: a leg between non-card marks is a rhumb line [V :640, 659-660]; finish selector [V :318, 1229] | Untested [NE] |
| Check recorded marks (`fxChecks`, `fxResolve`), review layer (`decResolve`, `decFlags`) | Yes, apart from the constants and name regexes in §4 | [V :1477-1907] |
| Wind analysis and wind-shift box | Yes, apart from `varW()` and `BOAT_M` | [V :1257-1328] |
| `rebuild_page.py`, `xlsx_edit.py`, `build_test.py` | Yes: no venue content | [V by reading] |
| `geo.vincenty` | Yes | [V geo.py:20-50] |
| `geo.utm29`, `test_chords.py` | Fixed to UTM 29N | [V geo.py:53-56] |
| `make_snapshot.py`, `audit_workbook.py` | Generic over the workbook schema, with Cork lists in `FLAGS` and `STARTS` | [V §4] |

---

## 6. Alignment with course-cards and course-days

### 6.1 Mapping table

| This project | course-cards (format.md v2) | course-days "course record v1" (course-days.md:155-167) |
|---|---|---|
| Snapshot `marks[id]`: `lat, lon, full, type, flag, laid` [V make_snapshot.py:57-63] | Marks file `marks[]`: `id, name, shape, color, position{lat,lng}` or `placement`, `source`; file `notes` [format.md:37-104] | `marks`: id, name, kind, position, and the fix it came from (time, accuracy, source) |
| Snapshot `courses[n]`: `rounds, card[{m, s:'P'\|'S'}], cfg{'start\|finish': [ids]}, printed, cond, flag, note` [V make_snapshot.py:89-121] | Card `courses[]`: `id, windDirectionDeg, distanceNm, marks[{mark, side:'port'\|'starboard', passing}]`, starting and ending at `startLine` [format.md:229-261] | `sequence`: mark ids with side and rounding or passing; which fix each rounding used |
| Snapshot `pairs['A\|B']`: directed; `nm`, `segs[{to, nm, brg (°T)}]` [V make_snapshot.py:123-127] | Overlay: `waypoints, passages{from,to,via}, direct, assumed{…toleranceM}`, undirected [format.md:322-409] | `legs`: routed-via waypoints |
| Fix: `id, date, race, name, lat, lon, acc, time, received, device?, recorder?, tap?` [V marks.php:359-372] | Race positions per race: `marks{id: {lat,lng}}` or line `ends` [format.md:268-301] | `marks…fix` (time, accuracy, source) |
| Course record: `entries[{ref, side}], startTime, finish, lineSel, wind{twd °M, tws}, card` + `updated, by` [V course_v8.html:2168-2177] | Called course: a sequence handed to the library per race; nothing stored [format.md:313-320] | `race` (date, course area, race number, start number, classes, start time); `lines`; `provenance` |
| Start groups `_starts\|race`: `{classes}` [V :2169-2170] | none | `race.classes` |
| Decisions: `id, ref, action, race?, start?, role?, from?, revokes?, who, note?, client_when?, series, when` [V marks.php:143-194, 337-339] | none | none (course-days.md:64-65 mentions pinning a fix; there are no decision records) |
| Leg table text: `"0.24 105"` per physical leg, NM 2 dp and °M [V course_v8.html:1358] | Library output: `{from, to, distanceNm, bearingDeg (true)}` [cc-README:52-57] | `legs`: from, to, distance (0.01 NM), true bearing, wind, current, via; "a bare leg table is a record with only legs" (course-days.md:171) |

### 6.2 Fields on one side only

- **Here only:**
  - mark `type`, `flag` and `laid` (course-days has "kind" [course-days.md:55-58]; format.md has none);
  - printed-card `cond`, `printed` and `**` `flag`;
  - per-segment precomputed `nm`/`brg` from the workbook;
  - fix `device`, `recorder`, `received` and `race`;
  - course `finish` mode, `lineSel` (`auto`/`none`/ref) and `card{c,s,f,ls,lf,lfs}`;
  - history entries; decisions; `series.json`.
- **course-cards only:**
  - mark `shape`, `color`, `source` (per mark), `placement`; file `notes`, `club`, `formatVersion`;
  - `passing`; `windDirectionDeg`; `startLine.ends`; `finish.via`; `assumed` with `toleranceM`.
  - The workbook's Marks sheet has source and accuracy columns [D README.md:663]. `make_snapshot.py` does not
    carry them [V make_snapshot.py:57-58].
- **course-days only:**
  - course area; reference (variation, model, position, date); per-leg wind and current; provenance (app, URL,
    version, generated-at);
  - fix `source` as a typed field.
  - Here the source is implied: a typed fix has `acc` 0 and no device [V course_v8.html:1514, 2388]; a committee
    boat fix from the RO page has no device [V :2330].

### 6.3 Specific checks

**True versus magnetic bearings.**

- Workbook and snapshot bearings are true [V make_snapshot.py:47].
- The legs table shows both °M and °T [V course_v8.html:1368].
- The SailScoring leg table is °M only: `magOf(brgT)` adds `varW()` [V :1117, 1358].
- `varW()` uses an Irish-fitted formula and **the current date**, not the race date [V :1111-1116]. Re-rendering a
  past day's course uses today's variation.
- Wind is entered in °M [V :321]. The README records "magnetic" as an assumption pending confirmation
  [D README.md:418-420].
- course-cards and the course record store true [cc-README:55-57; course-days.md:158].

**Starboard/port versus committee boat and pin.**

- This project uses `cb`, `pin`, `fcb` and `fpin` [V course_v8.html:1136-1137; marks.php:161].
- format.md names the ends `starboard`/`port`, looking towards the first mark, "not committee boat and pin"
  [format.md:186-191]. The course record uses "committee boat + pin" [course-days.md:161].
- No code here works out which end is starboard [V: none found].
- The midpoint here is the arithmetic mean of lat/lon [V course_v8.html:1127]. format.md uses the geodesic
  midpoint [format.md:210].

**Mark identity.**

- **Card marks:** referenced by the workbook short id, which is also the display name [V make_snapshot.py:53].
  These ids equal the course-cards RCYC ids for every card mark: Harp, Ringabella, Dosco, No.3-No.20, E1, E2, E4,
  W1, W2, W4, EF2, EF4, Cage, Dutchman, Curlane, White Bay. The 8 `RW_*` routing ids equal the overlay waypoint
  ids [V snapshot decode; course-cards `marks.json`, `routing.json` at `7de4a2c`].
- **Differences:** `Grassy Mid` here, against `SL` with `SL@grassy-walk` there. Starts at No.8 and Dosco here are
  `cfg` options; there they are `SL@no8` and `SL@dosco` with `as`. `East Mark` is there only.
- **RIB fixes:** free-text names. Laid card marks match a fix by normalized exact name (lower case,
  non-alphanumerics removed) [V course_v8.html:589, 603]. Line-end roles and W/L match by regex [V §4].
- **Course rows:** reference a specific fix by id (`s:<server id>`) [V :2166, 2173]. Decisions reference fixes by
  server id [V marks.php:154].

**Venue identity.**

- No venue, club, course area or data-set identifier exists in any stored file [V §1.3].
- The snapshot names only its source workbook file and hash [V make_snapshot.py:129].
- A venue is implied by the server folder and by the page that embeds a given snapshot [V course_v8.html:373, 797].

**Per-rounding moved marks.**

- Course rows are per rounding and each holds a fix reference [V course_v8.html:2173].
- "Use moved position" during the race replaces the fix only for that rounding and the later ones. Before the
  start it replaces every rounding [V :2396-2400]. This matches the course-days rule [course-days.md:85-86] for
  ordinary marks.
- **Laid card marks** have one position per race and name, shared by all their roundings [V :600, 614-615].
- Line ends have one fix per start [V :1155-1171].

**Wind.**

- One wind (`twd` °M, optional `tws`) per race and start, stored in the course record [V course_v8.html:2175, 2414].
- TWA is shown per leg [V :1363]. Wind is not in the leg table [V :1358].
- course-cards `windDirectionDeg` is the true wind a card course was laid out for, not recorded wind
  [format.md:235-240]. The snapshot carries no such field; whether the workbook has one is [NE].
- course-days legs carry recorded wind per leg [course-days.md:164].

### 6.4 Incompatibilities (as found; no position taken)

1. **Distance method.** The page measures non-card hops by rhumb line [V course_v8.html:451-460]. Card legs use
   the workbook's Vincenty geodesics [V geo.py:20; make_snapshot.py:47]. The course-cards library uses great-circle
   distance [cc-README:55-57].
2. **Field names and values.** `lat/lon` here against `lat/lng` there. `P`/`S` here against `port`/`starboard`.
3. **Pair direction.** Workbook pairs are directed. The overlay merges each pair with its reverse and refuses a pair
   routed differently each way (RCYC README, "The routing overlay").
4. **Curlane.** The snapshot carries the Curlane pairs. The overlay leaves Curlane out (RCYC README, "The routing
   overlay").
5. **Laid-mark rule.** course-days describes the laid-mark rule as the newest exact-name fix "recorded before the
   start" [course-days.md:80-81]. The code applies no start-time limit to laid marks [V course_v8.html:602-605].
6. **Cage position.** The overlay assumes Cage at the club's position, 39 m from the workbook's C1 (RCYC README).
   The snapshot uses the workbook position [V course_v8.html:797 via make_snapshot.py:57].

---

## 7. Overlaps with Sail Scoring's proposed responsibilities (course-days steps 3-6)

This section is a neutral correspondence. It makes no recommendation.

| course-days step | Proposed there | Existing function here |
|---|---|---|
| 3 · Workspace course days (course-days.md:196-219) | Day = date + course area; day's marks, schedule, courses; `manage-courses` permission | Day files by date [V marks.php:236, 274]. Schedule: races, starts, classes, start times [V course_v8.html:2168-2177]. Courses per `race\|start`. No course area. Course writes need only the race key [V marks.php:196-198]. |
| 4 · Fixes and time-bound positions (221-231) | Fixes on day marks, resolution rules, pinning, per-rounding choice; typed or pasted fixes incl. WhatsApp; read-only "check the day's fixes"; wide layout | Fixes with position time, tap, accuracy [V marks.php:359-372]. Resolution: line ends [V course_v8.html:1155-1185], laid marks [V :599-615]. Pinning: `lineSel`, `laidSel` [V :2353-2359]. Per-rounding [V :2396-2400]. Paste [V :483-508] and typed fixes [V :2381-2391]. Check recorded marks [V :1471-1907]. Wide layout [V :193-220]. |
| 5 · Race-officer role, phone layout (233-239) | `race-officer` role; "Record committee boat here"; schedule; build course; leg table with total, accuracy warnings, not-depth-checked labels | No accounts or roles; RO name and RO key on the device [V :427-446]. "Record committee boat here" [V :2318-2340]. Legs table with total [V :1395-1397]. Accuracy warnings [V :1138-1139, 1289]. "not depth-checked" labels [V :641, 1342]. |
| 6 · RIB links with no account (241-263) | Per-RIB links, hashed, expiring, revocable, quarantine; narrow offline page, SW scoped to one route, queue, client fix id; fresh-position rules; hold still; clock refusal explained; re-record requests to the RIB link; WhatsApp backup; RO view refresh and alerts | Shared race key; no per-RIB link, expiry, revocation or quarantine [V marks.php:196-198]. Offline page with a worker scoped to `/record/` [V sw.js:9-11]. Queue and client id [V record.html:200, 215-229]. Fresh rule and "HOLD STILL" [V :279-321]. Clock refusal: the message says only "Only an old GPS position came in" [V :294]; the clock cause is in the README [D README.md:123-125]. Re-record requests go out as WhatsApp/Share/Copy text from the RO page, not to a RIB link [V course_v8.html:1516, 1557-1559]. WhatsApp backup [V record.html:106-115, 256-264]. 30 s refresh and Race-view alerts [V course_v8.html:1077-1106, 2110]. |

course-days places some functions outside Sail Scoring [course-days.md:126-140]. Three of them exist here: mark-move
advice after a wind shift [V course_v8.html:1293-1328], line squaring and bias [V :1257-1272], and a WhatsApp course
message [V :1400-1403]. course-days step 1 (course record import) and step 2 (two-ended lines) are Sail Scoring
and course-cards work. The two-ended line already exists here, by committee boat and pin [V :1127].

---

## 8. Transitional components

| Component | Where | What it produces |
|---|---|---|
| SailScoring leg table | course_v8.html:353-358, 1358, 1405-1419, 2426-2428 | One line per physical leg, "NM(2 dp) bearing(°M 3 digits)", with an uncopied note above |
| RO WhatsApp / Share / Copy course message | course_v8.html:346-352, 1400-1403, 1420-1426 | Series and date heading, race, start and time, card abbreviation, numbered marks, legs with °M and °T, total, line and wind analysis, positions in DDM |
| Wind-shift message | course_v8.html:1325-1327, 341-344 | "Mark moves" text |
| Re-record request messages | course_v8.html:1516, 1557-1559 | Text asking a RIB to record again |
| RIB WhatsApp backup with optional CSV "for scoring" | record.html:106-115, 256-264 | "Laid marks – date", race, fixes; CSV `race,mark,fix,lat,lon,acc_m,time` |
| RO paste reader (input side of the same text) | course_v8.html:483-508, 2367-2375 | Reads the RIB WhatsApp text or CSV into local fixes. These are not sent to the server; they are cleared on a day change [V :2075] |

No structured export of a course (JSON or otherwise) exists [V: no such output in either page].

---

## 9. Hosting constraints

**PHP and server assumptions**

- `marks.php` says it is "Written to run on old and new PHP alike (5.3 upwards)" [V marks.php:13]. It has fallbacks
  for `hash_equals` (<5.6) and `http_response_code` [V :71-72, 77-83]. `fsync` is used only if present (PHP 8.1+)
  [V :111].
- Tests pass on PHP 8.4.26 and 5.5.38 [V run today].
- The README says the live host runs PHP 5.5 ("like the live host") [D README.md:504-505]. It also says "Tested with
  PHP 8.4 on Windows; the live host may differ" [D README.md:509]. The live version and server software are [NE].
- **Apache or LiteSpeed is assumed** for the `.htaccess` deny-all [V marks.php:203-206; D README.md:553-554]. On
  other servers `data/` (fixes, courses, decisions, `ro-key.php`) is not protected by this mechanism. Whether it
  works on the live host is [D README.md:554: "check it on the live server"] / [NE].
- `ro-key.php` prints nothing if fetched, because it is PHP [V ro-key.example.php; marks.php:48-50]. That depends on
  PHP handling `.php` files in `data/` [NE].
- Custom request headers `X-Race-Key` and `X-RO-Key` must reach PHP as `HTTP_X_…` [V marks.php:197, 314]. Whether
  the host passes them is [NE]. The race key also works as `?key=` [V :197].
- `flock` on `.write.lock` and `rename()` over an existing file must work on the host filesystem [V :91-114].

**File permissions**

- `data/` is created with `mkdir(…, 0755, true)` and must be writable by PHP, else 500 [V marks.php:201-202].
- Files are created by `fopen`/`file_put_contents` with the process umask [V :105-114, 204].
- `key.js` must be readable by PHP and also served publicly [V :36-37; record.html:10].

**What would block a second regional deployment on the same server**

1. **The RIB page has absolute paths** to `/marks/marks.php` and `/marks/key.js` [V record.html:10, 142; sw.js:12].
   It has no `MARKS_BASE` constant.
2. **The RIB service worker deletes every `record-` cache on the origin** when it activates [V sw.js:25]. The README
   gives this as the reason the RIB page has no test copy [D README.md:559-561]. Two RIB deployments on one origin
   would delete each other's offline copy.
3. **RIB localStorage keys are unprefixed** [V record.html:146, 166, 175]. Two RIB deployments on one origin would
   share the queue, device id and race key.
4. **The RO page's base path and storage prefix are constants** (`MARKS_BASE`, `STORE`) [V course_v8.html:373].
   `build_test.py` shows they can be changed by text substitution for one extra copy [V build_test.py:11-16].
5. **The snapshot is embedded per page** [V course_v8.html:797]. A second venue needs its own built page.
   `rebuild_page.py` takes `--page` [V rebuild_page.py:233].
6. **Separate data needs a separate `marks.php` folder.** Data, `series.json`, `key.js` and `ro-key.php` are
   resolved next to the script [V marks.php:36, 52, 200].
7. Cork constants in the RO page: map centre, `CARD_STARTS`, `CLASSES`, `varW` (§4).
8. The planned move to orc-ireland.org is [D ROADMAP.md:335 only]; the repository has no reference to it [V by
   search] [NE].

---

## 10. Tests

### 10.1 What each test covers

**`tests/test_marks.py`** runs `marks.php` unmodified through `php-cgi` in a temporary folder
[V test_marks.py:1-71, 73-108]. All tests passed on PHP 8.4.26 and PHP 5.5.38 today.

| Test | Covers |
|---|---|
| t0 | add, delete, GET; device and recorder; recorder cut to 60 characters |
| t1 | an unencodable fix or course refused, file unchanged |
| t2 | a damaged day file is refused, not overwritten |
| t3 | a write failing part-way leaves the file unchanged |
| t4 | a re-posted (moved) fix keeps device and recorder |
| t5 | 60 fixes, 10 courses, groups and 30 reads concurrently, ×3 |
| t6 | race key missing, placeholder or wrong |
| t7 | per-race start groups |
| t8 | series name |
| t9 | tap time |
| t10 | RO key cases |
| t11 | history: first + last 5, identical save, `by` |
| t12 | history 5 MB cap; firsts kept |
| t13 | history write failures |
| t14 | concurrent saves of one course |
| t15 | decisions validation, retry, 409, cap, revoke |
| t16 | requests shaped as the current pages send them |

Each line is [V test_marks.py docstring :12-62, functions :169-677]. The source line labels inside t16 (for example
"RO moved fix (course_v8 1858)") no longer match the page: that request is now at course_v8.html:2132
[V test_marks.py, run output].

**`tests/test_build_test.py`** builds a test copy into a temporary folder and checks paths, `test-` storage keys,
banner, title, `noindex`, byte-identical `marks.php` and the exact set of `STORE` key names. It also checks that
the builder refuses unsafe pages [V test_build_test.py:1-28]. All passed today.

**`scripts/audit_workbook.py`** is a release gate for the workbook, not a unit test. It includes check 4,
"stored geometry matches WGS84 geodesics" [V audit_workbook.py:12; run today].

### 10.2 What is not covered

- **No JavaScript in either page is tested** [V `git ls-files`]. That includes the geometry (`rhumb`, `dest`,
  `varW`, `magOf`), `legGeom`, line-end resolution, laid-mark resolution, `fxChecks`, `fxResolve`, `decResolve`,
  `decFlags`, the leg-table and WhatsApp builders, the course save and merge (`saveCourses`, `applyServerCourses`),
  and the RIB fresh-position rule and queue.
- The service worker is not tested.
- `geo.py`, `make_snapshot.py` and `rebuild_page.py` have no tests. `rebuild_page.py` checks its own output when it
  runs [V rebuild_page.py:273-275].

### 10.3 Roadmap priority tests (ROADMAP §10) with no coverage

| Priority test | Coverage |
|---|---|
| Geometry (A and B give a known distance and true bearing) | None for the page's `rhumb()` or `varW()`. The workbook's stored geometry is checked against Vincenty by the audit (a data check). |
| Fix resolution (fixes at 11:55, 12:02, 12:09 with a 12:05 start) | None |
| Moved mark (historical Race 1 reconstruction unchanged) | None |
| Browser workflow (offline, queue, reconnect, delayed fix, moved mark, review, selection) | None. Server-side pieces only: request shapes (t16), concurrency (t5), re-post (t4). |
| Equivalence after extraction | None |

---

## 11. Questions for you

1. Which PHP version and web server (Apache, LiteSpeed, other) run on the live host? Has the `data/` deny-all been
   checked there (README.md:554)?
2. Does the live host pass the `X-Race-Key` and `X-RO-Key` headers through to PHP? Does any client still use
   `?key=`?
3. Is the live `marks.php` the repository version at `d6d24a8` or later? Is the live `/course/` page
   `PAGE_VERSION 2026-10-06.11`?
4. What exactly is planned for orc-ireland.org: host, paths, PHP version, one origin or several? There is no
   reference in the repository.
5. Is a second deployment intended on the same origin as `/record/`? This matters for the service-worker cache
   cleanup and the unprefixed RIB storage keys (§9).
6. Where are the on-water tests of the offline queue recorded? The roadmap cites a "position paper" that is not in
   the repository.
7. Which code ran on 27 Sep 2026? The repository's page commits start later.
8. Is the "original recorded course" meant to be the first autosaved version of the day (what the history keeps as
   `list[0]`), or a version the RO marks deliberately?
9. Is the absence of a start-time limit on the automatic choice for laid marks (course_v8.html:602-605) intended?
   course-days describes Pat's rule as "recorded before the start".
10. Is it intended that the laid-mark position choice (`laidSel`) is kept on the phone only and not saved with the
    course?
11. Is it intended that `varW()` uses today's date rather than the race date when a past day is re-rendered?
12. Have any decisions been written on the live server? No page sends the RO key, so by what means? Live data was
    not read.
13. Is the RO / Scorer decisions write work held anywhere other than this repository (another branch, a local
    copy)? `git status` shows no modified tracked files.
14. Does the workbook record a wind heading per course, as course-cards `windDirectionDeg` does? `make_snapshot.py`
    reads none.
15. Should the six RCYC class names (course_v8.html:526) be treated as series data or club data? This is a
    classification question, not a change.
16. Is the RIB page limited to Races 1-3 by design? The server allows 1-9.
17. Has the Sail Scoring side confirmed magnetic bearings for the pasted leg table (README.md:418-420)? The
    `sailscoring` issue threads were not read.
18. The roadmap's 4 October issues (for example "16 marks recorded but not visible") cannot be reproduced without
    the live day files. Should a sanitised copy be provided for Phase 1 follow-up, or is that out of scope?
19. Is `pages/record/index.html` (tracked, identical to `record.html`) still uploaded, or only `record.html` as
    `/record/index.html` (README.md:528)?
