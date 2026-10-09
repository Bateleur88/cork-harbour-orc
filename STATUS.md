# STATUS

Last updated: 9 October 2026. Baseline: Phase 1 audit of commit `f30882f` (`docs/audit/PHASE1_AUDIT.md`, which stays unchanged as the dated snapshot).

This file tracks progress against the audit findings and the 4 October live-test problems. The audit is the baseline; this file is where progress is recorded.

## States

| State | Meaning |
|---|---|
| NOT STARTED | No work begun, or not built at the baseline commit |
| IN PROGRESS | Work has begun and is not finished |
| BUILT AND TESTED | Built and tested on the pages. Not yet confirmed in a live race |
| CONFIRMED LIVE | Seen working in a real race |

A separate marker is used for decisions: **DECIDED** (decision made, not yet implemented) and **OPEN** (not yet decided). An item no longer needed is **WITHDRAWN**, with the reason, and keeps its reference. A design Pat intends to build is **INTENDED**: it is not yet built and tested, and it may change as a result. It does not become the workflow until it has passed build and test.

## References

Every tracked item has a fixed reference: **L1 to L8** for the 4 October live-test problems, **A1 onwards** for the audit findings, **C1 onwards** for coordination and design decisions. References are never reused or renumbered. New items take the next number in their series. Commits name the item they work on with a trailer such as `Status: L4` or `Status: A3, A7` (see `CLAUDE.md`). The trailer says a commit advances an item, not that the item is complete; the state in this file is what counts. This repository has one GitHub issue, #1 "Cage / C1 position" (opened and closed on 6 October 2026; the A14 cross-check). The P-numbers used for the page-edit phases in Claude Code sessions (P1, P2, P3a, P3b, P4) are separate and are not status references.

## Rules for updating this file

1. Only Pat sets CONFIRMED LIVE.
2. Claude Code may propose a change to a line when it finishes work that affects it. It must show the proposed change and wait for approval. It does not edit the status silently.
3. "Built and tested" means built and tested on the pages. A passing test run is not a live confirmation.
4. Add a dated line to the update log for every change. Do not delete earlier lines.
5. Do not put private correspondence in this file.

---

## 1. 4 October 2026 live-test problems

| Ref | Problem | State | Notes |
|---|---|---|---|
| L1 | Delay between tapping Record and the position received; stale fixes | BUILT AND TESTED | Tap time stored with position time (`4a66559`); only a fresh position is saved (`ce3e7e4`). The freshness rule applies to the RIB page only; the RO page's "Record committee boat here" has no freshness check |
| L2 | Marks recorded in wrong positions | BUILT AND TESTED | "Check recorded marks" plot with advisory flags (`01329fc`) |
| L3 | 16 marks recorded but not visible on the RO page | BUILT AND TESTED | "Check recorded marks": plot, per-fix details, list, All-races chips |
| L4 | Several observations of one named mark as marks moved; deciding which to use | IN PROGRESS | Check recorded marks is where several fixes of one mark are compared. Any recorded fix of the day can be brought into a race's chip bank as a picked chip and added as a row where wanted; the picks are saved with the race (A29, commit `dd86687`). Known gap: a row using another race's fix can still show "Newer fix / Tap to use" (change held by Pat) |
| L5 | Distinguishing races and starts | IN PROGRESS | As-sailed course repair (C8): a start can use another race's fix, by picked chip (A29) or line end (A30), with the race named on the row |
| L6 | No start line generated (Race 1 failed to build) | IN PROGRESS | Committee boat and Start Pin can be chosen from any race's fixes (A30), so a race with no pin of its own can use another race's. Whether a start pin was recorded on the day is unknown |
| L7 | Race 3 clearly wrong; "All races" sketch unusable | IN PROGRESS | Race 3 can be rebuilt from any recorded fix (A29, A30); the as-sailed overlay (A32) shows what the course uses over the recorded lines |
| L8 | Unknown who laid which mark; RIB drivers cannot recall | IN PROGRESS | Recorder name (All fixes list) and lettered phone on every fix; re-record request buttons exist. The decisions process it was tied to is withdrawn (A1) |

---

## 2. Phase 1 audit findings (baseline `f30882f`)

### 2.1 Workflow and invariants

| Ref | Item | State | Notes |
|---|---|---|---|
| A1 | Decisions written by a page | WITHDRAWN | Withdrawn by Pat on 8 October 2026: the review UI (Accept, Do not use, Use as, Undo, review history, Earlier records, the Review name and RO key fields, the C7 warning) was an unnecessary complication and was taken out of the page in PAGE_VERSION 2026-10-06.20 to .24 (commit `dd86687`). The work (.9 to .19) stays in the history under the annotated tag `experiment/decisions-review`; the old row and notes are in `docs/experimental/decisions-and-review/`. `marks.php` keeps the decisions endpoint and the RO key, unused by the page. Replaced by the as-sailed course repair (C8, A29 to A32) |
| A2 | No separate original course: the recorded marks are the original, and the course is always derived from them plus decisions | DECIDED | Decided 7 October 2026. Pat's principle: the recorded marks are the primary source data and are never overwritten (A7). This only works if a saved course can be reproduced from the marks and decisions (A9, A10, A27). The term "original recorded course" and the meaning of "updated course" are to be revisited under C5. Note (8 October 2026): no page writes decisions now (A1 withdrawn); read "plus decisions" as "plus the choices saved with the course" (C8). |
| A3 | Protect the original recorded course | WITHDRAWN | Superseded by the A2 decision on 7 October 2026: there is no separate original course to protect |
| A4 | Saved-course workflow: Draft, then Decisions, then Accepted course | INTENDED | Stated by Pat on 7 October 2026; not decided, and it must pass build and test first. **1 Draft:** the RO sets up Race N, Start N, start time, classes and the intended course (import or chips); working state, replaceable, with at most a short undo window. **2 Decisions:** from "Check recorded marks", each change is its own append-only decision with a reason (for example a moved weather mark used for the second beat; a Start Pin inherited from another race); undo is by revoke. **3 Accepted course:** stored once the course reflects the race as sailed; records the fix ids and decision ids; not replaced. Points to settle: what starts stage 2; whether editing the course after decisions have begun returns it to draft, and what becomes of decisions about marks no longer in it; whether an accepted course can be reopened; whether automatic choices are recorded in the accepted course; a "Draft, not accepted" banner on the leg table. Not built at `f30882f`. Pat to confirm whether the in-progress decisions work covers it. Note (8 October 2026): stage 2 as written depended on A1, withdrawn 8 October 2026; Pat to decide whether A4 is restated or withdrawn. |
| A5 | Leg table produced from the stored course record, not the page's live state | NOT STARTED | At `f30882f` it is computed from the page's live state. Legs are never stored |
| A6 | Check recorded marks lets the RO select marks | OPEN | In the code it is read-only. Selection happens in the line-end pickers, laid-mark picker and course-row taps |
| A7 | Fixes can be deleted (RIB page) or re-posted (RO page move) | OPEN | Pat's stated principle (7 October): recorded marks are primary source data and must never be overwritten; additional information or a flag may be appended. Pat to confirm as a decision. It would affect the RIB delete (no tombstone) and the RO re-post. The RO page's "Fix recorded under the wrong race?" re-post is still in the page and conflicts with C8. |
| A8 | Series name is one value per `data/` folder, not per course | OPEN | Nothing requires it before building |
| A27 | A saved course can be reproduced from the recorded marks and decisions (store the fix ids and choices used with each saved course) | NOT STARTED | Follows from A2. Depends on A9 and A10. The P4 plan keeps the course as hand-edited state with decisions as an audit trail, so it does not meet this on its own. Note (8 October 2026): no page writes decisions now (A1 withdrawn). Picked chips (A29) and line-end choices (`lineSel`) are saved with the course; the laid-mark choice and automatic line ends are not (A10). Pat to decide whether A27 is reworded. |

### 2.2 Items to investigate

| Ref | Item | State | Notes |
|---|---|---|---|
| A9 | Automatic laid-mark choice has no start-time limit (committee boat and Start Pin do) | OPEN | To investigate whether intended. The Finish Pin also has no time limit |
| A10 | Laid-mark choice (`laidSel`) is kept on the phone only, and automatic line ends are re-resolved on each render; neither is saved with the course | OPEN | Affects any race using a laid mark (Curlane, Dutchman, White Bay) or an automatic line end: a stored course can give different legs later. The laid-mark list offers only fixes of that race or an earlier one. Needed for C8 and C9 |
| A11 | `varW()` (magnetic variation) uses today's date, not the race date | DECIDED | Should use the race date. Not yet changed in the code |
| A12 | RIB page offers Races 1 to 3 only; server accepts 1 to 9 | OPEN | Is the limit by design? |
| A13 | RIB source (`record.html`, tracked copy `index.html`): which is uploaded? | OPEN | |
| A33 | A refused course save is never shown | BUILT AND TESTED | Found 9 October 2026: course saves were silent (`postFix` did not read the server's error and `saveCourses` caught every failure and did nothing, `course_v8.html:2114` at `dd86687`). Decided by Pat 9 October 2026: the result shows in Setup (`#saveStatus`) and as a Race view alert; no signal, no race key, 403, no reply (each course save abandoned after 20 s) or any 500 stop the run, which is tried again every 15 s; 400 or 429 mark that record refused while the others are sent, and it is tried again only after it is changed or after a reload (429: the day's limit of 200 courses); "All course changes saved" only when nothing is unsent. Built in PAGE_VERSION 2026-10-06.25: page commit `0db8b42`, guards commit `6ca1ef3`, test build SHA-256 `b84315b9a1e8e84db53c95ee7186e9006da6b3ec09210aab4d2238896d4e5fc5`. All 34 manual tests passed on `/course-test/` on 9 October 2026. Uploaded to the live paths on 9 October 2026; not confirmed live. Open: A36 |
| A34 | Loading a day can send a course save without any edit | BUILT AND TESTED | Found 9 October 2026 (`course_v8.html:1985-1989`, `2009`, `2011` at `dd86687`): loading a day can send course saves without an edit, so loading a day on the live page is not read-only (12-hour rule). Decided by Pat 9 October 2026, option 1: what is saved and when is unchanged, and when a load leads to a save the page says "Saving N course changes held on this device:" with the reason (a course built before this day was loaded; a line end whose fix is gone was cleared; a fix reference updated to the server's copy; edits made while the day was not loaded). Built in PAGE_VERSION 2026-10-06.25 (`0db8b42`, guards `6ca1ef3`, test build `b84315b9a1e8e84db53c95ee7186e9006da6b3ec09210aab4d2238896d4e5fc5`); all 34 manual tests passed on `/course-test/` on 9 October 2026. Uploaded to the live paths on 9 October 2026; not confirmed live. Known limit, decided by Pat 9 October 2026 not to fix in .25: a kept record holding only a start time (no course rows) is sent on loading its day but gets no "a course built before this day was loaded" reason, which is given only to records with course rows or a race's start groups (`course_v8.html:2027-2029` at `0db8b42`). Unchanged by .25: on loading 4 October, a device still on .7 (`2aec398`) keeps the repaired Race 1 line ends: its `checkLineRefs` (`1869-1877`) clears only a chosen fix that `refFix` rejects, and `refFix` accepts a fix of that race or an earlier one with no time test (`1098-1100`), so the Start Pin R1 12:32, recorded after the start, stays; the finish is Start line, with no Finish Pin to clear. This holds while no other Race 1 line end names a fix from a later race. The remaining risk: the first time a .7 device sends Race 1's start groups (after a start-group edit, `488`, `854`, or on loading 4 October from another day, `1797-1798`), it sends them without `picked` (`1890`), dropping the picked R3 14:39 Leeward chip; the Race 1 rows that use that fix stay. Only retiring .7 devices removes that. (Corrected 9 October 2026: the earlier note said a .7 device would clear a Start Pin and Finish Pin taken from Race 2; the repair uses none.) |
| A35 | A change of day deletes the old day's unsent course edits without checking the forced save | BUILT AND TESTED | Found 9 October 2026 (`course_v8.html:1977`, `1979-1987` at `dd86687`): the old day's unsent edits were deleted on a change of day whether or not they had been sent. Decided by Pat 9 October 2026, option (b): a save already running is waited for (stopped after its current record, at most 25 s); the day-change save tries every record, also after a server error; if anything was not sent the change of day stops, the old day stays loaded, the day box goes back and nothing is deleted; records made for a third day stop it too, also when no day was loaded before ("load that day first"); "Change day anyway" only when every record holding it up was refused (400 or 429), failed with a server error (500) or was made for a third day, naming each and saying they are lost from this device and not saved on the server. Built in PAGE_VERSION 2026-10-06.25 (`0db8b42`, guards `6ca1ef3`, test build `b84315b9a1e8e84db53c95ee7186e9006da6b3ec09210aab4d2238896d4e5fc5`); all 34 manual tests passed on `/course-test/` on 9 October 2026. Uploaded to the live paths on 9 October 2026; not confirmed live. Known limit, decided by Pat 9 October 2026 not to fix in .25: a "Still on" message is not cleared or updated when a later save sends the records it names, so it can still say "could not be sent" after they were sent; it clears at the next change-of-day attempt or Clear everything. Not tested by hand: the 25 s wait limit (a running save is abandoned at 20 s first); covered by a static guard only |
| A36 | "All course changes saved" did not appear after a load-led save | OPEN | Seen 9 October 2026 in manual test 26 (PAGE_VERSION 2026-10-06.25 on `/course-test/`): after loading a day whose kept record was then sent and saved, the line did not appear. Not explained from the code: it shows only when no record on the device is unsent (`saveLines`, `saveDone`, `course_v8.html:2166-2178`, `2217-2222` at `0db8b42`), so another record unsent at the time is possible. If it recurs, the first tap of Clear everything (which only arms it) shows any unsent count. No decision recorded |

### 2.3 Data

| Ref | Item | State | Notes |
|---|---|---|---|
| A14 | Cage position | DECIDED | GitHub issue #1 (closed). Workbook keeps eOceanic C1 (51 48.818 N 008 16.990 W). The Navionics reading (51 48.826 N 008 16.970 W, about 27 m away, bearing about 057 T) is a cross-check only. Follow-up: the shared `course-cards` marks file and overlay may hold a different position, about 39 m away (the audit reports this from the `course-cards` RCYC README, `docs/audit/PHASE1_AUDIT.md`); confirm and align |
| A15 | Distance method differs between page (rhumb), workbook (Vincenty) and course-cards library (great-circle) | OPEN | Recorded, no position taken |
| A16 | Overlay omits Curlane; workbook pairs are directed, overlay pairs are merged | OPEN | |

### 2.4 Regionalisation blockers (Phases 4 and 5, provisional)

| Ref | Item | State |
|---|---|---|
| A17 | RIB page uses absolute paths to `/marks/marks.php` and `/marks/key.js` | NOT STARTED |
| A18 | RIB service worker deletes every `record-` cache on the origin | NOT STARTED |
| A19 | RIB localStorage keys are unprefixed | NOT STARTED |
| A20 | Snapshot is embedded in each built RO page; each venue needs its own build and `marks.php` folder | NOT STARTED |
| A21 | Cork constants in the RO page (map centre, `CARD_STARTS`, `CLASSES`, role-name regexes, start and finish rules) | NOT STARTED |
| A22 | No venue, club or course-area identifier in any stored file | NOT STARTED |

### 2.5 Tests and security

| Ref | Item | State | Notes |
|---|---|---|---|
| A23 | Server tests (`test_marks.py`, `test_build_test.py`) | BUILT AND TESTED | All passed on PHP 8.4.26 and PHP 5.5.38 on 7 October 2026 |
| A24 | JavaScript in either page | NOT STARTED | No tests exist (geometry, fix resolution, moved mark, line ends, laid marks, leg table, RIB queue, service worker) |
| A25 | Race key also accepted as a URL parameter (`?key=`) | OPEN | No decision recorded |
| A26 | Live host: PHP version, server software, header pass-through, `data/` deny-all check | OPEN | Checked by Pat on 9 October 2026: PHP 5.5.38 (`X-Powered-By` on a read request); the server software, Apache (the `Server` header of a `marks.php` response); and a request for a non-existent file under `/marks/data/` is refused with 403. Not checked: header pass-through for `X-RO-Key`. The .24 page sends the race key only as the `X-Race-Key` header (`course_v8.html:403`), and its reads succeeded on 9 October. The live `data/` folder accepts the course history write: the first known live course save since the upload (the Race 1 repair of 4 October, made on the PC with PAGE_VERSION 2026-10-06.24 on 9 October 2026) wrote a new `courses-history-2026-10-04.json` (2,934 bytes) beside `courses-2026-10-04.json` (3,306 bytes), both modified 09/10/2026 09:23:57 (FileZilla listing time). The page itself shows no message for a save or a refused one: saves are automatic, can happen on load without an edit (`course_v8.html:1987-1988`, `2009`), and a failure is caught silently (`course_v8.html:2114`), so the result shows only as a `courses-history-*.json` file in `/marks/data/`, another device getting the change, or the count on the first tap of Clear everything |
| A28 | `build_test.py` records "source commit" from the repo HEAD even when `--page` points outside the repo | OPEN | Found 7 October 2026 building the .12 test copy from a page outside the repo: BUILD.txt said "source commit a10394d" with no note that the page was not the committed one (its uncommitted-changes check looks only at the repo's `pages/`). Script unchanged; the test build's MANIFEST.txt records the real source |

### 2.6 As-sailed course repair (built after the audit)

Built after the Phase 1 audit, in place of the withdrawn decisions work (A1, C7). The A references continue.

| Ref | Item | State | Notes |
|---|---|---|---|
| A29 | Picked chips: any recorded fix of the day brought into a race's chip bank and saved with the race | BUILT AND TESTED | Page side in PAGE_VERSION 2026-10-06.20; saved with the race (`picked` in the `_starts|N` record) in .21; committed in `dd86687`. Tested on the shadow copy (`/course-test/`); not confirmed live. `marks.php` stores the field unchanged (`test_marks.py` 17). A save of that record from an older page (the .7 page, live until 9 October 2026) drops the picks; the course history keeps them. Known gap: the Send text names another race's fix as plain "Windward". The comment at `course_v8.html:260` was corrected in PAGE_VERSION 2026-10-06.25 (`0db8b42`). Uploaded to the live paths on 9 October 2026 (PAGE_VERSION 2026-10-06.24). Not confirmed live: no race has used it. Used on the live server on 9 October 2026, on the PC with PAGE_VERSION 2026-10-06.24, for the Race 1 repair of 4 October (the R3 14:39 Leeward as a picked chip in all three starts), the first known live course save since the upload; checked by Pat: the course file and a new course history file were written, and a second device that loaded 4 October shows the repair. |
| A30 | Line ends (committee boat, Start Pin, Finish Pin) chosen from any race's fixes | BUILT AND TESTED | PAGE_VERSION 2026-10-06.20; committed in `dd86687`. Saved in `lineSel` as before; `auto` keeps its own rule and never picks a later race's fix. Tested on the shadow copy; not confirmed live. Uploaded to the live paths on 9 October 2026; not confirmed live (no race has used it). In the live Race 1 repair of 4 October (9 October 2026) the Start Pin chosen is R1 12:32, a Race 1 fix, and the finish is set to Start line, so a line end taken from another race has not yet been used on the live server (corrected 9 October 2026; the earlier note said Start Pin and Finish Pin from Race 2). |
| A31 | Course chart drawn from the sketch's data; the Legs block in the left column from 1100 px | BUILT AND TESTED | Chart in PAGE_VERSION 2026-10-06.22, Legs position in .23; committed in `dd86687`. Tested on the shadow copy; not confirmed live. Uploaded to the live paths on 9 October 2026; not confirmed live (no race has used it). |
| A32 | As-sailed overlay in Check recorded marks: the selected race and start over the recorded lines, unused recorded lines faded | BUILT AND TESTED | PAGE_VERSION 2026-10-06.24; committed in `dd86687`. Tested on the shadow copy; not confirmed live. Uploaded to the live paths on 9 October 2026; not confirmed live (no race has used it). |

---

## 3. Coordination and design decisions

| Ref | Item | State | Notes |
|---|---|---|---|
| C1 | Who owns fix recording and the day-level course record (Decision 1) | OPEN | A call with the Sail Scoring maintainer had not happened as of 7 October 2026 |
| C2 | Course Record format | OPEN | To be agreed with the Sail Scoring maintainer and defined in `course-cards`, not in this repository |
| C3 | Bearing convention for the Course Record (true, with variation) | OPEN | |
| C4 | Line-end convention (starboard/port versus committee boat/pin) | OPEN | No code here works out which end is starboard |
| C5 | Vocabulary: original recorded course, updated course, As Sailed Course versus "Course Record" | OPEN | One vocabulary needed before any export |
| C6 | Repository name and what counts as a venue | OPEN | Depends on Decision 1 |
| C7 | Do not use: effect on the course and outputs | WITHDRAWN | Withdrawn by Pat on 8 October 2026 with A1: Do not use, Use as and the "Legs need updating" warning were taken out of the page in .20 to .24 (commit `dd86687`). Built in `3579dee` and `26f0570`, tested on the shadow copy only, never live. Tag `experiment/decisions-review`; the old row is in `docs/experimental/decisions-and-review/` |
| C8 | The page must work for any race day, not only 4 October 2026 | DECIDED | Decided by Pat 8 October 2026. (1) Any mark (course row, line end, laid mark) can be set from any recorded fix of the day without changing the fix. (2) A saved course records every choice. (3) The default view is small. Met: course rows (A29) and line ends (A30). Not met: laid marks (own or earlier race only, phone-only: A9, A10); automatic choices not pinned (C9); the re-post (A7) changes a fix |
| C9 | Pin every automatic choice in the saved course; an RO-key lock on the as-sailed course | INTENDED | Stated by Pat 8 October 2026; not built, not a feature. (1) Automatic line ends and the laid-mark choice written into the saved course so it rebuilds exactly (A10, A27). (2) The RO key, which today protects only the unused decisions endpoint, may lock the as-sailed course |

---

## 4. Phases

| Phase | State |
|---|---|
| 1. Read-only audit | DONE (7 October 2026, `f30882f`) |
| 2. Settle Decision 1; revise the roadmap | NOT STARTED |
| 3. Decide project identity | NOT STARTED |
| 4. Extract Cork as Venue 1 | NOT STARTED (provisional) |
| 5. DBSC as Venue 2 | NOT STARTED (provisional) |
| 6. Shadow testing | NOT STARTED (provisional) |
| 7. Course Record interoperability | NOT STARTED (provisional) |
| 8. Controlled DBSC trial | NOT STARTED (provisional) |

---

## 5. Live-test log (Pat only)

| Date | Race or event | What was checked | Result |
|---|---|---|---|
| 2026-10-09 | Upload, not a race: RO page PAGE_VERSION 2026-10-06.24 and `marks.php` (318d09b) | Re-downloaded and hashed; the live page loaded the 4 October day; PHP 5.5.38; `/marks/data/` 403; opened and working on a PC and a tablet (Pat); no course saved on live; not a race. | Uploaded. Nothing confirmed live |
| 2026-10-09 | Race 1 repair of 4 October on the live page, not a race | Made on the PC, PAGE_VERSION 2026-10-06.24, as on the test copy: the R3 14:39 Leeward in all three starts (picked chip); Start Pin from Race 2, Finish Pin from Race 2. The first known live course save since the upload. FileZilla listing of `/marks/data/`: `courses-2026-10-04.json` 3,306 bytes and a new `courses-history-2026-10-04.json` 2,934 bytes, both modified 09/10/2026 09:23:57 (FileZilla listing time); a second device that loaded 4 October shows the repair. | Done and checked. Nothing confirmed live |
| 2026-10-09 | Correction to the Race 1 repair row above | The repair uses the Start Pin R1 12:32 (a Race 1 fix, chosen by Pat) and the finish set to Start line, as on the test copy; not "Start Pin from Race 2, Finish Pin from Race 2" | Correction only. Nothing confirmed live |
| 2026-10-09 | Upload, not a race: RO page PAGE_VERSION 2026-10-06.25 (`marks.php` unchanged, 318d09b) | Backups taken first; re-downloaded and hashed; opened on the PC and the tablet (Pat): PAGE_VERSION .25, no page script errors; no day loaded, nothing edited; not a race. | Uploaded. Nothing confirmed live |

First live check: the next race day. Nothing in this file is CONFIRMED LIVE yet.

---

## 6. Update log

- 2026-10-07: file created from the Phase 1 audit, the 4 October problem list and decisions recorded to date.
- 2026-10-07: added fixed references (P1 to P8, A1 onwards, C1 onwards) and the commit trailer convention.
- 2026-10-07: A2 reopened (was DECIDED); A7 note added with Pat's principle that recorded marks are never overwritten.
- 2026-10-07: A2 decided (no separate original course); A3 withdrawn; A4 restated as open; A27 added.
- 2026-10-07: A4 recorded as INTENDED (Draft, Decisions, Accepted); new INTENDED marker added.
- 2026-10-07: 4 October live-test problems renamed P1 to P8 -> L1 to L8 (to avoid clashing with the P-numbered page-edit phases); A1 and A27 notes added.
- 2026-10-07: A14: the Navionics cross-check position added, to match ROADMAP.md; the 39 m figure now cites the audit.
- 2026-10-08: A1 note updated: write path (Accept, Do not use, Undo) committed in 3579dee (PAGE_VERSION 2026-10-06.13); Do not use, Undo and reload read-back tested on the shadow copy from 7 October, the "Legs need updating" warning on 8 October; Accept on scratch only; phase order .14 legPts, .15 Use as for rows, .16 line ends.
- 2026-10-08: C7 added, BUILT AND TESTED: a fix marked do not use stays in the legs with a warning (3579dee); course rows tested on the shadow copy, line ends and the unread-decisions line on scratch only; laid marks, finish ends and other-fix wording untested; leaving the fix out dropped for now; Choose a replacement planned with .15; open points listed.
- 2026-10-08: A28 added: build_test.py records the repo HEAD as "source commit" when --page points outside the repo.
- 2026-10-08: A1 note updated: .14 legPts done (1ef3a7a); Use as for course rows committed as .16 (26f0570), tested on the shadow copy for Leeward, Windward and Gybe, limit, 409 and mid-action failure simulated in scratch; no .15 commit (tested as .15-test); planned .17 Choose a replacement (provisional), .18 line ends.
- 2026-10-08: C7 updated: Use as for course rows built (.16, 26f0570); the whole-race action decided and built; .17 Choose a replacement provisional and kept separate so it can be dropped; per-start tick boxes added to the open points as small and deferred; line-end replacement moved to .18.
- 2026-10-08: A1 and C7 updated: the fix detail and review decisions under the Check recorded marks sketch (`0cd524b`) and the chart tap and review history fold (`4313903`), tested on the shadow copy; the .17 and .18 numbers planned earlier were not used as planned (Choose a replacement shelved, uncommitted; .18 went to the layout step); version numbers are no longer assigned in advance; next: the Information fold, then Add to course; held: the scroll to the decision panel; shelved: Choose a replacement and Fixes from other races.
- 2026-10-08: A1, C7 and L4 corrected: the next planned change is a fix tapped on the Check recorded marks sketch brought into the chip bank of the selected race and start as a separate chip (it adds, does not replace; not Use as); the "Fixes from other races" chip group is reusable for it; Choose a replacement and the scroll to the decision panel are held, not shelved; the page-length folds (key, line notes, Information lines, fix list) are options, not decided.
- 2026-10-08: A1 and C7 WITHDRAWN: the review UI taken out of the page (PAGE_VERSION 2026-10-06.20 to .24, dd86687); history under tag experiment/decisions-review and docs/experimental/decisions-and-review/.
- 2026-10-08: L4 to L8 restated for the as-sailed course repair (L4 stays in progress); A10 restated (laid-mark choice and automatic line ends); A7 note (the re-post conflicts with C8); A14 cites GitHub issue #1.
- 2026-10-08: A4 and A27: notes added (A1 withdrawn; Pat to decide); no change of state or wording.
- 2026-10-08: C8 added (DECIDED, any race day); C9 added (INTENDED, pin automatic choices; RO-key lock).
- 2026-10-08: A29 to A32 added, BUILT AND TESTED on the shadow copy (picked chips, line ends from any race, chart from the same data with the Legs position, as-sailed overlay); not confirmed live.
- 2026-10-08: References corrected: the repository has one GitHub issue (#1).
- 2026-10-09: Uploaded to the live paths by Pat (FileZilla, Binary mode; each file re-downloaded and hashed). First /marks/marks.php: the 318d09b version (23,076 bytes, SHA-256 05b7a38f8827719a4e3d766967b40eca28c0a605feb8a9f561542c1c52d1a0ca) replaced the 4a66559 version (10,487 bytes, a104989efcb6a767aa4fe0c2aaf09f7ffcb389ca46bec112cafcf2ae3b187f04). Then /course/index.html: PAGE_VERSION 2026-10-06.24 (280,789 bytes, 3113744562d739a85d0a7d3f9d6a51c0e8630ae50d754c3ddd42c6c4cf28062b) replaced .7 (2aec398; 257,628 bytes, 157ce311615d4243fe09e5196250cf418bef74c7282c339a04ed7f997c388a10). Backups taken first, outside the repository (release_2026-10-09). Tests re-run beforehand: test_marks.py on PHP 8.4.26 and 5.5.38, test_build_test.py and build_test.py passed. No device may edit courses on the .7 page after the upload.
- 2026-10-09: A26: PHP 5.5.38, the server software (Apache) and the data/ 403 checked; X-RO-Key pass-through unchecked; the course history file not yet written on live. A29 to A32: uploaded to the live paths, not confirmed live; states unchanged. Live-test log: the 9 October upload (not a race).
- 2026-10-09: Race 1 of 4 October repaired on the live page by Pat on the PC (PAGE_VERSION 2026-10-06.24), as on the test copy (the R3 14:39 Leeward in all three starts as a picked chip; Start Pin from Race 2, Finish Pin from Race 2): the first known live course save since the upload. The course history write succeeded (`courses-history-2026-10-04.json` in /marks/data/, 09/10/2026 09:23:57 FileZilla listing time); a second device that loaded 4 October shows the repair. A26: the history question answered, and its wording corrected (a save's result does not show on the page). A29, A30: used on live; states unchanged. Live-test log: the repair (not a race).
- 2026-10-09: A33 and A34 added (OPEN, no decision): a refused course save is never shown; loading a day can send a course save without an edit.
- 2026-10-09: A35 added (DECIDED, option (b), planned for .25): a change of day deletes the old day's unsent course edits without checking the forced save; a running save is waited for (at most 25 s), and "Change day anyway" covers 400, 429 and 500.
- 2026-10-09: A33, A34 and A35 to BUILT AND TESTED: PAGE_VERSION 2026-10-06.25 (page 0db8b42, guards 6ca1ef3, test build b84315b9a1e8e84db53c95ee7186e9006da6b3ec09210aab4d2238896d4e5fc5); all 34 manual tests passed on /course-test/; not confirmed live. A34 and A35: one known limit each, decided not to fix in .25. A36 added (OPEN). A29: the comment at course_v8.html:260 corrected.
- 2026-10-09: Correction: the live Race 1 repair of 4 October uses the Start Pin R1 12:32 (a Race 1 fix, chosen by Pat) and the finish set to Start line, the same as the test copy, not a Start Pin and Finish Pin from Race 2 as the two 9 October repair lines above and the live-test log say. A30's note corrected: no line end from another race has been used on the live server yet. A34's note corrected: a .7 device clears no Race 1 line end on loading 4 October; the picked chip is the remaining risk. Live-test log: correction row added.
- 2026-10-09: PAGE_VERSION 2026-10-06.25 (0db8b42) uploaded to /course/index.html by Pat (FileZilla, Binary mode; 295,269 bytes, SHA-256 2775387969964d825a8e18f20d932370f778d26ae4d79395cc6a0161e9eb9009; re-downloaded, hash matched), replacing .24 (3113744562d739a85d0a7d3f9d6a51c0e8630ae50d754c3ddd42c6c4cf28062b); marks.php unchanged (318d09b). No race within 12 hours; the three backups taken first, outside the repository (release_2026-10-09_25). Opened on the PC and the tablet: .25, no page script errors, no day loaded. A33, A34, A35: uploaded, not confirmed live; states unchanged. Live-test log: the upload (not a race).
