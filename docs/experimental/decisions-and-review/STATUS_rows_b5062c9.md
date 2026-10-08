# STATUS rows at b5062c9

Quoted word for word from `STATUS.md` at commit `b5062c9` (tag `experiment/decisions-review`). Each block gives its line numbers in that file. Nothing here describes the current page.

The table header the rows sit under (STATUS.md line 51 for A1 to A27, line 106 for C7):

~~~~text
| Ref | Item | State | Notes |
|---|---|---|---|
~~~~

## STATUS.md line 53: A1 Decisions written by a page

~~~~text
| A1 | Decisions written by a page | IN PROGRESS | Server side is built and tested (append-only, RO key). Page write path committed in `3579dee` (PAGE_VERSION 2026-10-06.13): Accept, Do not use and Undo from the fix detail in Check recorded marks, with the "Legs need updating" warning (C7). Tested on the shadow copy (`/course-test/`, `/marks-test/`): the write path (Do not use, Undo, read back after a reload) first on 7 October 2026 with the .12 test build, the .13 warning on 8 October 2026; Accept was tested on scratch only. `.14` legPts done in `1ef3a7a` (no behaviour change, scratch only). Use as for course rows committed in `26f0570` (PAGE_VERSION 2026-10-06.16): tested on the shadow copy on 8 October 2026 for Leeward, Windward and Gybe, with Undo per start and for all, reload as a new phone and the wrong-race line; the daily limit, a 409 and a failure part-way through an action simulated in scratch only. There was no .15 commit: that work was tested as `.15-test` and committed as .16. Check recorded marks: the tapped fix's detail and review decisions sit directly under the sketch, and a tap in the sketch, the list or the chart scrolls the detail into view. The review history shows the records in force, with the undone, replaced and Undo records folded into a closed "Earlier records (N)" that keeps its open state. Committed in `0cd524b` and `4313903`, tested on the shadow copy on 8 October 2026. Version numbers are no longer assigned in advance; each commit takes the next free one. Next planned change: tapping a fix on the Check recorded marks sketch (All races) brings that fix into the chip bank of the selected race and start as a separate chip, which the RO then taps to add it as a row where wanted; it adds and does not replace, and nothing is marked do not use (Use as, `26f0570`, replaces a mark in every row of every start of the race and is the wrong tool for that). The "Fixes from other races" chip group (scratch only, never built) is reusable for it. Options, not decided: folding the key, the line notes, the Information lines and the fix list under the sketch, to shorten the page. Held: Choose a replacement (built as a provisional change and uploaded as .17-test, never committed) and scrolling to the decision panel instead of the detail. Line ends (Use as for line ends) later. Not on the live paths. The live RO page (version .7) and the live `marks.php` have no decisions |
~~~~

## STATUS.md line 56: A4 Saved-course workflow: Draft, then Decisions, then Accepted course

~~~~text
| A4 | Saved-course workflow: Draft, then Decisions, then Accepted course | INTENDED | Stated by Pat on 7 October 2026; not decided, and it must pass build and test first. **1 Draft:** the RO sets up Race N, Start N, start time, classes and the intended course (import or chips); working state, replaceable, with at most a short undo window. **2 Decisions:** from "Check recorded marks", each change is its own append-only decision with a reason (for example a moved weather mark used for the second beat; a Start Pin inherited from another race); undo is by revoke. **3 Accepted course:** stored once the course reflects the race as sailed; records the fix ids and decision ids; not replaced. Points to settle: what starts stage 2; whether editing the course after decisions have begun returns it to draft, and what becomes of decisions about marks no longer in it; whether an accepted course can be reopened; whether automatic choices are recorded in the accepted course; a "Draft, not accepted" banner on the leg table. Not built at `f30882f`. Pat to confirm whether the in-progress decisions work covers it |
~~~~

## STATUS.md line 61: A27 A saved course can be reproduced from the recorded marks and decisions

~~~~text
| A27 | A saved course can be reproduced from the recorded marks and decisions (store the fix ids and choices used with each saved course) | NOT STARTED | Follows from A2. Depends on A9 and A10. The P4 plan keeps the course as hand-edited state with decisions as an audit trail, so it does not meet this on its own |
~~~~

## STATUS.md line 114: C7 Do not use: effect on the course and outputs

~~~~text
| C7 | Do not use: effect on the course and outputs | BUILT AND TESTED | Decided by Pat 8 October 2026, replacing the display-only rule. A fix marked do not use STAYS in the legs: the legs, total, sketch, SailScoring table and Send text keep their numbers. Where the selected start still uses it (course rows, a laid mark following it, or a committee boat, Start Pin or finish end, automatic, chosen or inherited), a warning with the legs ("Legs need updating") names the fix, who and when, the rows and line ends, and whether the race has another fix of that mark type, and says to change them with the course chips or line-end choices for now; the SailScoring note (not copied) carries one line; Check recorded marks flags it for every start. While the day's decisions cannot be read, a line with the legs says so. Built in `3579dee`. Tested on the shadow copy on 8 October 2026 for course rows only (Race 1 11:03 Leeward: Start 1 rows 2, 4, 6; Start 2 rows 2, 4; Start 3 row 3), with the SailScoring note line, Undo and reload. Tested on scratch only, not on the server (8 October 2026): the committee boat case (Race 1 10:42, picked automatically, Starts 1 to 3), the Start Pin case (Race 1 12:32, chosen by the RO, Start 1) and the line shown when the decisions cannot be read. Not tested anywhere: a laid mark following the fix, a finish end, and a race with another fix of the same mark type. Not confirmed live; A1 stays in progress. Leaving the fix out of the legs was dropped for now. Use as for course rows built in `26f0570` (`.16`): it replaces only the rows that use a fix marked do not use, in every start of the selected race, with a preview, Undo and a line naming the race when another race holds the flagged fix; tested on the shadow copy for Leeward, Windward and Gybe. "Choose a replacement" (stored as a Use as) was built as a provisional change and uploaded to the shadow copy as .17-test; it is held, not committed, and is not on the current test page. Open: output behaviour once Use as exists (whether the SailScoring table or Send text should refuse or warn while a start still uses a do-not-use fix); line-end replacement (Use as for line ends); laid marks (a laid mark following a do-not-use fix has no review role and its choice is phone-only, A10); the box's defaults (Check recorded marks still shows the page's automatic lines, which ignore the review); Use as for some starts of a race only (per-start tick boxes): small, deferred. |
~~~~

## STATUS.md lines 152 to 153: Update log: A1 and C7

~~~~text
- 2026-10-08: A1 note updated: write path (Accept, Do not use, Undo) committed in 3579dee (PAGE_VERSION 2026-10-06.13); Do not use, Undo and reload read-back tested on the shadow copy from 7 October, the "Legs need updating" warning on 8 October; Accept on scratch only; phase order .14 legPts, .15 Use as for rows, .16 line ends.
- 2026-10-08: C7 added, BUILT AND TESTED: a fix marked do not use stays in the legs with a warning (3579dee); course rows tested on the shadow copy, line ends and the unread-decisions line on scratch only; laid marks, finish ends and other-fix wording untested; leaving the fix out dropped for now; Choose a replacement planned with .15; open points listed.
~~~~

## STATUS.md lines 155 to 158: Update log: A1, C7 and L4

~~~~text
- 2026-10-08: A1 note updated: .14 legPts done (1ef3a7a); Use as for course rows committed as .16 (26f0570), tested on the shadow copy for Leeward, Windward and Gybe, limit, 409 and mid-action failure simulated in scratch; no .15 commit (tested as .15-test); planned .17 Choose a replacement (provisional), .18 line ends.
- 2026-10-08: C7 updated: Use as for course rows built (.16, 26f0570); the whole-race action decided and built; .17 Choose a replacement provisional and kept separate so it can be dropped; per-start tick boxes added to the open points as small and deferred; line-end replacement moved to .18.
- 2026-10-08: A1 and C7 updated: the fix detail and review decisions under the Check recorded marks sketch (`0cd524b`) and the chart tap and review history fold (`4313903`), tested on the shadow copy; the .17 and .18 numbers planned earlier were not used as planned (Choose a replacement shelved, uncommitted; .18 went to the layout step); version numbers are no longer assigned in advance; next: the Information fold, then Add to course; held: the scroll to the decision panel; shelved: Choose a replacement and Fixes from other races.
- 2026-10-08: A1, C7 and L4 corrected: the next planned change is a fix tapped on the Check recorded marks sketch brought into the chip bank of the selected race and start as a separate chip (it adds, does not replace; not Use as); the "Fixes from other races" chip group is reusable for it; Choose a replacement and the scroll to the decision panel are held, not shelved; the page-length folds (key, line notes, Information lines, fix list) are options, not decided.
~~~~
