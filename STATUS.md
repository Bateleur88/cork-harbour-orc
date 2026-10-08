# STATUS

Last updated: 7 October 2026. Baseline: Phase 1 audit of commit `f30882f` (`docs/audit/PHASE1_AUDIT.md`, which stays unchanged as the dated snapshot).

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

Every tracked item has a fixed reference: **L1 to L8** for the 4 October live-test problems, **A1 onwards** for the audit findings, **C1 onwards** for coordination and design decisions. References are never reused or renumbered. New items take the next number in their series. Commits name the item they work on with a trailer such as `Status: L4` or `Status: A3, A7` (see `CLAUDE.md`). The trailer says a commit advances an item, not that the item is complete; the state in this file is what counts. This repository does not use GitHub issues. The P-numbers used for the page-edit phases in Claude Code sessions (P1, P2, P3a, P3b, P4) are separate and are not status references.

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
| L4 | Several observations of one named mark as marks moved; deciding which to use | IN PROGRESS | Part of the RO / Scorer decisions work |
| L5 | Distinguishing races and starts | IN PROGRESS | RO / Scorer decisions process |
| L6 | No start line generated (Race 1 failed to build) | IN PROGRESS | RO / Scorer decisions process. Whether a start pin was recorded on the day is unknown |
| L7 | Race 3 clearly wrong; "All races" sketch unusable | IN PROGRESS | RO / Scorer decisions process |
| L8 | Unknown who laid which mark; RIB drivers cannot recall | IN PROGRESS | RO / Scorer decisions process. Recorder name and lettered phone are on every fix; re-record request buttons exist |

---

## 2. Phase 1 audit findings (baseline `f30882f`)

### 2.1 Workflow and invariants

| Ref | Item | State | Notes |
|---|---|---|---|
| A1 | Decisions written by a page | IN PROGRESS | Server side is built and tested (append-only, RO key). Page write path committed in `3579dee` (PAGE_VERSION 2026-10-06.13): Accept, Do not use and Undo from the fix detail in Check recorded marks, with the "Legs need updating" warning (C7). Tested on the shadow copy (`/course-test/`, `/marks-test/`): the write path (Do not use, Undo, read back after a reload) first on 7 October 2026 with the .12 test build, the .13 warning on 8 October 2026; Accept was tested on scratch only. `.14` legPts done in `1ef3a7a` (no behaviour change, scratch only). Use as for course rows committed in `26f0570` (PAGE_VERSION 2026-10-06.16): tested on the shadow copy on 8 October 2026 for Leeward, Windward and Gybe, with Undo per start and for all, reload as a new phone and the wrong-race line; the daily limit, a 409 and a failure part-way through an action simulated in scratch only. There was no .15 commit: that work was tested as `.15-test` and committed as .16. Planned order: .17 Choose a replacement (provisional), .18 line ends. Not on the live paths. The live RO page (version .7) and the live `marks.php` have no decisions |
| A2 | No separate original course: the recorded marks are the original, and the course is always derived from them plus decisions | DECIDED | Decided 7 October 2026. Pat's principle: the recorded marks are the primary source data and are never overwritten (A7). This only works if a saved course can be reproduced from the marks and decisions (A9, A10, A27). The term "original recorded course" and the meaning of "updated course" are to be revisited under C5 |
| A3 | Protect the original recorded course | WITHDRAWN | Superseded by the A2 decision on 7 October 2026: there is no separate original course to protect |
| A4 | Saved-course workflow: Draft, then Decisions, then Accepted course | INTENDED | Stated by Pat on 7 October 2026; not decided, and it must pass build and test first. **1 Draft:** the RO sets up Race N, Start N, start time, classes and the intended course (import or chips); working state, replaceable, with at most a short undo window. **2 Decisions:** from "Check recorded marks", each change is its own append-only decision with a reason (for example a moved weather mark used for the second beat; a Start Pin inherited from another race); undo is by revoke. **3 Accepted course:** stored once the course reflects the race as sailed; records the fix ids and decision ids; not replaced. Points to settle: what starts stage 2; whether editing the course after decisions have begun returns it to draft, and what becomes of decisions about marks no longer in it; whether an accepted course can be reopened; whether automatic choices are recorded in the accepted course; a "Draft, not accepted" banner on the leg table. Not built at `f30882f`. Pat to confirm whether the in-progress decisions work covers it |
| A5 | Leg table produced from the stored course record, not the page's live state | NOT STARTED | At `f30882f` it is computed from the page's live state. Legs are never stored |
| A6 | Check recorded marks lets the RO select marks | OPEN | In the code it is read-only. Selection happens in the line-end pickers, laid-mark picker and course-row taps |
| A7 | Fixes can be deleted (RIB page) or re-posted (RO page move) | OPEN | Pat's stated principle (7 October): recorded marks are primary source data and must never be overwritten; additional information or a flag may be appended. Pat to confirm as a decision. It would affect the RIB delete (no tombstone) and the RO re-post |
| A8 | Series name is one value per `data/` folder, not per course | OPEN | Nothing requires it before building |
| A27 | A saved course can be reproduced from the recorded marks and decisions (store the fix ids and choices used with each saved course) | NOT STARTED | Follows from A2. Depends on A9 and A10. The P4 plan keeps the course as hand-edited state with decisions as an audit trail, so it does not meet this on its own |

### 2.2 Items to investigate

| Ref | Item | State | Notes |
|---|---|---|---|
| A9 | Automatic laid-mark choice has no start-time limit (committee boat and Start Pin do) | OPEN | To investigate whether intended. The Finish Pin also has no time limit |
| A10 | Laid-mark choice (`laidSel`) is kept on the phone only, not saved with the course | OPEN | To investigate. A stored course can give different legs later because `auto` line ends and laid marks are re-resolved on each render |
| A11 | `varW()` (magnetic variation) uses today's date, not the race date | DECIDED | Should use the race date. Not yet changed in the code |
| A12 | RIB page offers Races 1 to 3 only; server accepts 1 to 9 | OPEN | Is the limit by design? |
| A13 | RIB source (`record.html`, tracked copy `index.html`): which is uploaded? | OPEN | |

### 2.3 Data

| Ref | Item | State | Notes |
|---|---|---|---|
| A14 | Cage position | DECIDED | Workbook keeps eOceanic C1 (51 48.818 N 008 16.990 W). The Navionics reading (51 48.826 N 008 16.970 W, about 27 m away, bearing about 057 T) is a cross-check only. Follow-up: the shared `course-cards` marks file and overlay may hold a different position, about 39 m away (the audit reports this from the `course-cards` RCYC README, `docs/audit/PHASE1_AUDIT.md`); confirm and align |
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
| A26 | Live host: PHP version, server software, header pass-through, `data/` deny-all check | OPEN | Not yet checked |
| A28 | `build_test.py` records "source commit" from the repo HEAD even when `--page` points outside the repo | OPEN | Found 7 October 2026 building the .12 test copy from a page outside the repo: BUILD.txt said "source commit a10394d" with no note that the page was not the committed one (its uncommitted-changes check looks only at the repo's `pages/`). Script unchanged; the test build's MANIFEST.txt records the real source |

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
| C7 | Do not use: effect on the course and outputs | BUILT AND TESTED | Decided by Pat 8 October 2026, replacing the display-only rule. A fix marked do not use STAYS in the legs: the legs, total, sketch, SailScoring table and Send text keep their numbers. Where the selected start still uses it (course rows, a laid mark following it, or a committee boat, Start Pin or finish end, automatic, chosen or inherited), a warning with the legs ("Legs need updating") names the fix, who and when, the rows and line ends, and whether the race has another fix of that mark type, and says to change them with the course chips or line-end choices for now; the SailScoring note (not copied) carries one line; Check recorded marks flags it for every start. While the day's decisions cannot be read, a line with the legs says so. Built in `3579dee`. Tested on the shadow copy on 8 October 2026 for course rows only (Race 1 11:03 Leeward: Start 1 rows 2, 4, 6; Start 2 rows 2, 4; Start 3 row 3), with the SailScoring note line, Undo and reload. Tested on scratch only, not on the server (8 October 2026): the committee boat case (Race 1 10:42, picked automatically, Starts 1 to 3), the Start Pin case (Race 1 12:32, chosen by the RO, Start 1) and the line shown when the decisions cannot be read. Not tested anywhere: a laid mark following the fix, a finish end, and a race with another fix of the same mark type. Not confirmed live; A1 stays in progress. Leaving the fix out of the legs was dropped for now. Use as for course rows built in `26f0570` (`.16`): it replaces only the rows that use a fix marked do not use, in every start of the selected race, with a preview, Undo and a line naming the race when another race holds the flagged fix; tested on the shadow copy for Leeward, Windward and Gybe. "Choose a replacement" (stored as a Use as) is planned in `.17`; it is provisional and kept in its own code and commit, so it can be dropped or reverted without touching `.16`. Open: output behaviour once Use as exists (whether the SailScoring table or Send text should refuse or warn while a start still uses a do-not-use fix); line-end replacement (Use as for line ends, `.18`); laid marks (a laid mark following a do-not-use fix has no review role and its choice is phone-only, A10); the box's defaults (Check recorded marks still shows the page's automatic lines, which ignore the review); Use as for some starts of a race only (per-start tick boxes): small, deferred. |

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
| | | | |

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
