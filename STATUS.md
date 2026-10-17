# STATUS

Last updated: 16 October 2026. Live: course page PAGE_VERSION 2026-10-06.37 (released 15 October 2026). Built and tested, not released: .38 (A8, A71). Baseline: Phase 1 audit `docs/audit/PHASE1_AUDIT.md` (commit `f30882f`). History of every item is in git (`git log -p STATUS.md`).

## States

NOT STARTED · IN PROGRESS · BUILT AND TESTED (on the pages, not yet in a live race) · CONFIRMED LIVE (seen working in a real race; only Pat sets it). Decisions: DONE (decided and in use) · DECIDED (not yet built) · OPEN (not yet decided) · PARKED (on hold) · INTENDED (planned, may change) · WITHDRAWN (no longer needed).

## Rules for updating this file

1. One line per note: the current position only. Replace the note; never append to it.
2. No dates of past steps, test step numbers, commit lists, byte counts or hashes. Git holds those.
3. No future release numbers in a row. The release order lives only in the Next block.
4. L, A and C references only. Anything found in testing gets an A-number when it is recorded, or it is not tracked.
5. Claude Code proposes changes and waits for Pat's approval; it does not edit silently.
6. Only Pat sets CONFIRMED LIVE.
7. No private correspondence.

References are never reused or renumbered. Commits name them with a trailer such as `Status: A58`.

---

## Next

**Sunday 18 October 2026:** first live race on .37. Race-day precautions: don't reload the course page with poor signal; once a start has gone, don't tap Undo on its start line; don't tap Remove Start in a race that has a course; check the series name reads "Autumn League" before the first course. After the race Pat decides what moves to CONFIRMED LIVE.

**.38 (built and tested, not released):** A8, A71. Released after Sunday's race, with the series backfill for 27 September, 4, 11 and 18 October.

**Next:** A65 (race-day safety), A25 (key by header only), A70 (remove Copy legs).

**Then:** A63 (finish line), A60 (copy a course from any start).

**Then:** A7, A12, A13, A39, A17 to A19, A81 (RIB page and server; tested on the water).

**Later, once designed:** A62 with gates; A66, A67, A68; A9; A57; A73 to A78 (layout, wording and line-end fixes); A24 (script tests). A79 goes with the next workbook release.

**Never** release within 12 hours of a race.

## Open decisions (waiting for Pat)

| Ref | Decision | Recommendation |
|---|---|---|
| A41 | RO-chosen waypoint inside a pair the card already routes: keep "routed via … (RO-chosen)" or say "card route via …" | "card route via …", when taken up. Parked |
| A16 | Align the course-cards overlay with the workbook (Curlane, directed pairs) | None until taken up. Parked |
| A26 | Live host: `X-RO-Key` header pass-through not yet checked | Check when C9 part 2 is built |
| A67, A68 | Design points to settle before building | — |
| C6 | Repository name and what counts as a venue | Parked; ties to the per-venue direction |
| A80 | Home-screen icon (manifest) for the course page. On iPhone an icon avoids Safari clearing the copy after about a week, but keeps its own storage, separate from Safari's | None until taken up |

---

## 1. 4 October 2026 live-test problems

| Ref | Problem | State | Current note |
|---|---|---|---|
| L1 | Delay between tap and position; stale fixes | CONFIRMED LIVE | RIB page fresh-position rule. The RO page's "Record committee boat here" has no freshness check |
| L2 | Marks recorded in wrong positions | CONFIRMED LIVE | Check recorded marks plot with advisory flags |
| L3 | Recorded marks not visible on the RO page | BUILT AND TESTED | Check recorded marks: plot, details, list |
| L4 | Several fixes of one mark; choosing which | IN PROGRESS | Any fix of the day can be picked into a race (A29). Known gap: "Newer fix / Tap to use" on rows using an earlier race's fix (held by Pat) |
| L5 | Distinguishing races and starts | IN PROGRESS | A start can use another race's fix (A29, A30) |
| L6 | No start line generated | IN PROGRESS | Line ends from any race (A30); one-end start line (A58) |
| L7 | Race 3 wrong; All-races sketch unusable | IN PROGRESS | Rebuild from any fix (A29, A30); as-sailed overlay (A32) |
| L8 | Unknown who laid which mark | IN PROGRESS | Recorder name and phone letter on every fix; re-record buttons |

## 2. Audit findings and later work

### Workflow and data

| Ref | Item | State | Current note |
|---|---|---|---|
| A2 | No separate original course: recorded marks are the original; the course is derived from them plus saved choices | DECIDED | Nothing to build |
| A5 | Leg table from the stored course, not live page state | NOT STARTED | Later stage |
| A7 | Recorded fixes are never deleted or rewritten | DECIDED | RIB Delete becomes Withdraw; "wrong race" move makes a new linked record |
| A8 | Series name per race day, saved and loaded with the day | BUILT AND TESTED | In .38, not released; saved with the race key; sent to Sail Scoring as x-series only; backfill runs at release; then recreate 10 September in the August / September series |
| A9 | Laid mark on auto has no start-time limit | DECIDED | Latest fix at or before the race's first start |
| A10 | Laid-mark choice and auto line ends saved with the course | BUILT AND TESTED | |
| A11 | Magnetic variation by race date (WMM at map centre) | BUILT AND TESTED | |
| A12 | RIB page offers Races 1 to 3 only | DECIDED | "+ Race" up to 9 on both pages |
| A13 | Which RIB file is uploaded | DECIDED | `pages/record/index.html`; remove `record.html` |
| A15 | Distance method differs (page, workbook, course-cards) | BUILT AND TESTED | |
| A16 | Overlay omits Curlane; pairs merged | OPEN | Parked (see Open decisions) |
| A27 | A saved course can be reproduced from marks plus saved choices | NOT STARTED | Part met by A10; reproduction not checked |
| A57 | White Bay laid-mark choice became an explicit older fix | DECIDED | Record which device made each course save (`marks.php` already keeps an optional `by`) |

### Regionalisation blockers (Phases 4 and 5, provisional)

| Ref | Item | State | Current note |
|---|---|---|---|
| A17 | RIB page uses absolute `/marks/` paths | NOT STARTED | `/record-test/` path |
| A18 | RIB service worker deletes every `record-` cache on the origin | NOT STARTED | |
| A19 | RIB localStorage keys unprefixed | NOT STARTED | |
| A81 | RIB worker can keep an older page as its offline copy: it installs from `/record/` and accepts any page with the version marker, so a host-cached older page can be saved by a newer worker, or replace a newer copy | NOT STARTED | Fix to match the course page worker (A65) once its design is agreed |
| A20 | Snapshot embedded per build; one build and `marks.php` folder per venue | NOT STARTED | |
| A21 | Cork constants in the RO page | NOT STARTED | |
| A22 | No venue, club or course-area identifier in stored files | NOT STARTED | |

### Tests and security

| Ref | Item | State | Current note |
|---|---|---|---|
| A23 | Server tests | BUILT AND TESTED | `marks.php` and backfill tests pass on PHP 8.4 and 5.5 |
| A24 | No tests of the page's logic | NOT STARTED | Static source guards only; the browser regression harness is outside git. To do: script tests on the saved race days, golden outputs from .37, a committed runner |
| A25 | Race key accepted as `?key=` | DECIDED | Stop accepting it, on both sites |
| A26 | Live host checks | OPEN | PHP 5.5.38, Apache, `data/` 403 checked. RO key stays unset until C9 part 2 |
| A28 | `build_test.py` source-commit record | BUILT AND TESTED | Kept |

### As-sailed course repair and Sail Scoring hand-off

| Ref | Item | State | Current note |
|---|---|---|---|
| A29 | Picked chips from any fix of the day, saved with the race | BUILT AND TESTED | WhatsApp names another race's fix by its plain name, by design (A40 clean list); "(moved hh:mm)" marks a later fix of the same mark, by design; positions listed |
| A30 | Line ends from any race's fixes | BUILT AND TESTED | |
| A31 | Course chart from sketch data; Legs block layout | BUILT AND TESTED | |
| A32 | As-sailed overlay in Check recorded marks | BUILT AND TESTED | |
| A33 | Refused course save never shown | BUILT AND TESTED | |
| A34 | Loading a day could send a save without an edit | BUILT AND TESTED | Known limit: a record holding only a start time is sent on load with no reason given |
| A35 | Change of day dropped unsent edits | BUILT AND TESTED | Known limit: stale "Still on" message |
| A37 | Copy for Sail Scoring (ORC constructed course JSON) | BUILT AND TESTED | °M to one decimal; no rounding sides, by design. In .38 the series goes as x-series only, not in the name. The AsSailedCourse hand-off (C2) |
| A70 | Remove the "Copy legs for SailScoring" block: Sail Scoring takes only the ORC import (A37) | DECIDED | The on-screen leg table stays |

### Typed and pasted positions, fixed marks, start lines

| Ref | Item | State | Current note |
|---|---|---|---|
| A38 | Typed and pasted positions; RO page queue | BUILT AND TESTED | |
| A39 | RIB page queue blocked by a refused fix | NOT STARTED | Test on the water before relying on it |
| A40 | Fixed marks fold; reversed routes; WhatsApp list in °M | BUILT AND TESTED | |
| A41 | RO-chosen routing waypoint inside a pair the card already routes is labelled "routed via … (RO-chosen)" | OPEN | Parked (see Open decisions) |
| A43 | RO's course message reader (aliases) | NOT STARTED | Later stage |
| A44 | Changing day drops pasted positions with no warning | NOT STARTED | Later stage |
| A45 | Far positions (over 8 nm) in the plots | BUILT AND TESTED | |
| A46 | Withdraw and correct a typed position | BUILT AND TESTED | |
| A47 | Pasted positions saved to the race record on request | BUILT AND TESTED | |
| A48 | Stale "All course changes saved" after change of day | BUILT AND TESTED | |
| A49 | Typed position timed by the computer clock | BUILT AND TESTED | |
| A50 | Plain chips beside a laid mark's chip | BUILT AND TESTED | |
| A54 | Start line length and bearing without wind | BUILT AND TESTED | |
| A55 | Scale bar, label overlap, far-away warning colour | BUILT AND TESTED | Label nudging moved to A73 |
| A56 | Wind box saved every keystroke, no range check | BUILT AND TESTED | |
| A58 | One-end start line: the RO estimates the line | BUILT AND TESTED | Released in .37 |
| A60 | Copy the course from any other start | NOT STARTED | Design points to decide |
| A61 | Straight legs across land or drying ground | NOT STARTED | Parked |
| A62 | Mark with no rounding side holds the WhatsApp text | DECIDED | Built with gates |
| A63 | Finish line built like the start line; recorded Finish Pin as default | DECIDED | |
| A64 | Never show or save a course for another day than the Race day box | BUILT AND TESTED | Released in .37 |
| A65 | Course page opens with no signal | DECIDED | |
| A66 | Server refuses Withdraw while a saved auto choice uses the fix | DECIDED | |
| A67 | Correct moves only the starts the RO chooses | DECIDED | Design points first |
| A68 | Save each start's auto choice when its start time passes | DECIDED | Design points first |
| A69 | Remove Start left later starts' line ends behind | BUILT AND TESTED | Released in .37; the Remove Start precaution stays until CONFIRMED LIVE |
| A71 | Loading a day opens the start left open on another day | BUILT AND TESTED | In .38, not released |
| A72 | Orange note when a day's series is changed after the day was copied for Sail Scoring | DECIDED | Needs the page to record each copy |
| A73 | Layout and colour: start line section (one line per end, one status line, one next action), Card mark / Laid line labels (say "estimated" when either end is an estimate), messages beside their button, finish line drawn over the estimated start line, sketch start line and labels | DECIDED | Colour rule: red only for what holds Send back or could lose data; laid marks at their planning position shown red as chips but not in the Fixed marks list, to be made consistent |
| A74 | Save and load lines call pins set at a mark and placed ends "typed position"; a placed fix's detail says "Phone none" | DECIDED | Name them by what the RO did |
| A75 | Favoured end ignores the first mark | DECIDED | Add which end is nearer the first mark, and by how much; whether to switch to distance when the first leg isn't a beat is open |
| A76 | "Record the missing end…" shows with no start time and no ends | DECIDED | Reword or remove |
| A77 | Undo's label; later starts' lines; duplicate list entries; Undo on a started start's estimate removes its line | DECIDED | Partly met by A58: Undo refused while another start uses the estimate. To do: label, duplicate list entries, Undo on a gone start's own estimate. Rule: starts that have gone keep their line; a new start gets its own |
| A78 | A placed line end replaced by placing again can't be withdrawn on its own | DECIDED | Add a way to withdraw a placed end no start uses |
| A79 | Workbook release items: Grassy Mid as a card start or finish, the workbook's Grassy Mid label, RW_Temblebreedy_Pier spelling | DECIDED | Ask Mark about an explicit stand-in field; check course-cards for the old spelling |
| A80 | Home-screen icon (manifest) for the course page | OPEN | Option only, kept separate from A65; see Open decisions |
| A82 | Favicons for the RIB page and the course page | IN PROGRESS | Embedded as data URIs (16 and 32 px icons and an apple-touch-icon per page); partly covers A80 (an apple-touch-icon on the course page, no manifest; A80 stays open for the manifest). Course page: to be tested with A65 on the test copy. RIB page: needs checking on the water before it is relied on, and carries the A81 weakness as before |

Withdrawn: A1, A3, A4, A6 (decisions and review UI; see `docs/experimental/decisions-and-review/`), A14 (Cage position, issue #1), A36, A51, A52, A53, A59 (superseded by A58).

## 3. Coordination and design decisions

| Ref | Item | State | Current note |
|---|---|---|---|
| C1 | Who owns fix recording and the day-level course record | DONE | Settled with Sail Scoring #667: this page records fixes and builds the AsSailedCourse; Sail Scoring imports it |
| C2 | Course Record format | DONE | ORC constructed course JSON (Sail Scoring #667), sent by Copy for Sail Scoring (A37) |
| C3 | Bearing convention | DONE | Degrees magnetic to one decimal, variation by race date (A11) |
| C4 | Line-end convention | DONE | Start line repairs in .37 (A58) |
| C5 | Vocabulary | DONE | AsSailedCourse in use |
| C6 | Repository name and what counts as a venue | PARKED | Ties to the per-venue direction |
| C7 | Do not use | WITHDRAWN | See `docs/experimental/decisions-and-review/` |
| C8 | Page works for any race day | DECIDED | Not met until A7: the RO page's "wrong race" move still re-posts the fix |
| C9 | Pin every auto choice; RO-key lock on the as-sailed course | INTENDED | Part 1 built (A10); part 2 later stage, and may also require the RO key to change a day's series |

## 4. Phases

| Phase | State |
|---|---|
| 1. Read-only audit | DONE (7 October 2026) |
| 2. Settle Decision 1; revise the roadmap | IN PROGRESS: Decision 1 settled (#667); roadmap being rewritten |
| 3. Decide project identity | NOT STARTED |
| 4. Extract Cork as Venue 1 | NOT STARTED (provisional) |
| 5. DBSC as Venue 2 | NOT STARTED (provisional) |
| 6. Shadow testing | NOT STARTED (provisional) |
| 7. Course Record interoperability | IN PROGRESS: format settled (#667), export built (A37) |
| 8. Controlled DBSC trial | NOT STARTED (provisional) |

## 5. Live log (Pat only)

| Date | Event | Result |
|---|---|---|
| 2026-10-09 | .24 and `marks.php` uploaded; 4 October Race 1 repaired on live | First live course save |
| 2026-10-09 | .25 uploaded | Checks passed on PC and tablet |
| 2026-10-10 | .26 uploaded | Checks passed on PC and tablet |
| 2026-10-11 | Race (Autumn League) | L1, L2 confirmed live |
| 2026-10-12 | .29 uploaded | Checks passed on PC and tablet |
| 2026-10-14 | .36 and `marks.php` released | Checks passed on PC and tablet |
| 2026-10-15 | .37 released | Checks passed on PC, tablet, phone and laptop |
| 2026-10-16 | Test files removed from live | Kept days unchanged |
