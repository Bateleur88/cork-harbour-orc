# STATUS

Last updated: 27 October 2026. Live: course page PAGE_VERSION 2026-10-06.46e, the .46e release (released 27 October 2026: A127, the line rules rework; A132 to A134 and A138 to A140; A80 course page part), with the .45 service worker and `marks.php`; no race on it yet. Baseline: Phase 1 audit `docs/audit/PHASE1_AUDIT.md` (commit `f30882f`). History of every item is in git (`git log -p STATUS.md`).

## States

NOT STARTED · IN PROGRESS · BUILT AND TESTED (on the pages, not yet in a live race) · CONFIRMED LIVE (seen working in a real race; only Pat sets it). Decisions: DONE (decided and in use) · DECIDED (not yet built) · OPEN (not yet decided) · PARKED (on hold) · INTENDED (planned, may change) · WITHDRAWN (no longer needed) · SUPERSEDED (replaced by a later rule).

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

**Next race:** race-day precautions on .45: open the course page once with signal on each RO device before the race day, so it opens without signal (A65); once a start has gone, don't tap Undo on its start line (A77); check the day's series name reads "Autumn League" and tap Confirm if it shows as carried, before the first course (A8).

**.46e (released, live):** A127, A132, A133, A134, A138, A139, A140 and A80 (course page part); the first race on it next. Nothing is CONFIRMED LIVE until then.

**Next:** A25 (key by header only), A70 (remove Copy legs).

**Then:** A60 (copy a course from any start).

**Then:** A7, A12, A13, A39, A17 to A19, A81, A82 (RIB page icons) (RIB page and server; tested on the water).

**Later, once designed:** A62 with gates; A66, A67, A68; A9; A57; A73 to A77 (layout, wording and line-end fixes); A24 (script tests); A85 to A88. A79 goes with the next workbook release.

**Never** release within 12 hours of a race.

## Open decisions (waiting for Pat)

| Ref | Decision | Recommendation |
|---|---|---|
| A41 | RO-chosen waypoint inside a pair the card already routes: keep "routed via … (RO-chosen)" or say "card route via …" | "card route via …", when taken up. Parked |
| A16 | Align the course-cards overlay with the workbook (Curlane, directed pairs) | None until taken up. Parked |
| A26 | Live host: `X-RO-Key` header pass-through not yet checked | Check when C9 part 2 is built |
| A67, A68 | Design points to settle before building | — |
| C6 | Repository name and what counts as a venue | Parked; ties to the per-venue direction |

---

## 1. 4 October 2026 live-test problems

| Ref | Problem | State | Current note |
|---|---|---|---|
| L1 | Delay between tap and position; stale fixes | CONFIRMED LIVE | RIB page fresh-position rule. The RO page's "Record committee boat here" has no freshness check |
| L2 | Marks recorded in wrong positions | CONFIRMED LIVE | Check recorded marks plot with advisory flags |
| L3 | Recorded marks not visible on the RO page | CONFIRMED LIVE | Check recorded marks: plot, details, list |
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
| A8 | Series name per race day, saved and loaded with the day | BUILT AND TESTED | Released in .45; saved with the race key; sent to Sail Scoring as x-series only; backfilled at release into 27 September, 4, 11 and 18 October; 10 September is not being recreated (decided 23 October 2026), its archived files stay in `E:\CorkHarbourORC_backups\test-data-archive_2026-10-16\` |
| A9 | Laid mark on auto has no start-time limit | DECIDED | Latest fix at or before the race's first start |
| A10 | Laid-mark choice and auto line ends saved with the course | SUPERSEDED (LINE_RULES.md, 26 Oct) | In part: auto line ends (rule 11); the laid-mark choice stays (rule 16) |
| A11 | Magnetic variation by race date (WMM at the course's first leg) | CONFIRMED LIVE | |
| A12 | RIB page offers Races 1 to 3 only | DECIDED | "+ Race" up to 9 on both pages |
| A13 | Which RIB file is uploaded | DECIDED | `pages/record/index.html`; remove `record.html` |
| A15 | Distance method differs (page, workbook, course-cards) | CONFIRMED LIVE | |
| A16 | Overlay omits Curlane; pairs merged | OPEN | Parked (see Open decisions) |
| A27 | A saved course can be reproduced from marks plus saved choices | NOT STARTED | Part met by A10; reproduction not checked |
| A57 | White Bay laid-mark choice became an explicit older fix | DECIDED | Record which device made each course save (`marks.php` already keeps an optional `by`) |

### Regionalisation blockers (Phases 4 and 5, provisional)

| Ref | Item | State | Current note |
|---|---|---|---|
| A17 | RIB page uses absolute `/marks/` paths | NOT STARTED | `/record-test/` path |
| A18 | RIB service worker deletes every `record-` cache on the origin | NOT STARTED | |
| A19 | RIB localStorage keys unprefixed | NOT STARTED | |
| A81 | RIB worker can keep an older page as its offline copy: it installs from `/record/` and accepts any page with the version marker, so a host-cached older page can be saved by a newer worker, or replace a newer copy | NOT STARTED | Fix to match the course page worker (A65); it also waits on reading a copy of the page before answering (`await isPage(res)`), the pattern that stalled the course page's Reload in the A65 test |
| A20 | Snapshot embedded per build; one build and `marks.php` folder per venue | NOT STARTED | |
| A21 | Cork constants in the RO page | NOT STARTED | |
| A22 | No venue, club or course-area identifier in stored files | NOT STARTED | |

### Tests and security

| Ref | Item | State | Current note |
|---|---|---|---|
| A23 | Server tests | BUILT AND TESTED | `marks.php` and backfill tests pass on PHP 8.4, 8.1 and 5.5 |
| A24 | No tests of the page's logic | NOT STARTED | Static source guards only; the browser regression harness is outside git (see README, Tests). To do: script tests on the saved race days, golden outputs from .37, a committed runner |
| A25 | Race key accepted as `?key=` | DECIDED | Stop accepting it, on both sites |
| A26 | Live host checks | OPEN | PHP 5.5.38, Apache, `data/` 403 checked. RO key stays unset until C9 part 2 |
| A28 | `build_test.py` source-commit record | BUILT AND TESTED | Kept |
| A93 | Local test site on the PC: `build_test.py --label LOCAL`, server scripts, reset and a made-up day | BUILT AND TESTED | Used for .44; GPS does not work over http there |

### As-sailed course repair and Sail Scoring hand-off

| Ref | Item | State | Current note |
|---|---|---|---|
| A29 | Picked chips from any fix of the day, saved with the race | CONFIRMED LIVE | WhatsApp names another race's fix by its plain name, by design (A40 clean list); "(moved hh:mm)" marks a later fix of the same mark, by design; positions listed |
| A30 | Line ends from any race's fixes | BUILT AND TESTED | |
| A31 | Course chart from sketch data; Legs block layout | CONFIRMED LIVE | |
| A32 | As-sailed overlay in Check recorded marks | CONFIRMED LIVE | |
| A33 | Refused course save never shown | BUILT AND TESTED | |
| A34 | Loading a day could send a save without an edit | BUILT AND TESTED | Known limit: a record holding only a start time is sent on load with no reason given |
| A35 | Change of day dropped unsent edits | BUILT AND TESTED | Known limit: stale "Still on" message |
| A83 | An edit made after the page is reopened offline gives no sign it is unsent until the day loads from the server | NOT STARTED | The edit is kept on the device and sent once the day loads; until then the save line says nothing |
| A84 | After a change of day stops, its messages stay although Race day has gone back: "Race day is … but … is loaded", "… not loaded (see below)", and the red "Still on" line once the version is confirmed | NOT STARTED | Same cause as A35's known limit; clear or redraw them when the stop is resolved |
| A37 | Copy for Sail Scoring (ORC constructed course JSON) | BUILT AND TESTED | °M to one decimal; no rounding sides, by design. In .38 the series goes as x-series only, not in the name. The AsSailedCourse hand-off (C2) |
| A70 | Remove the "Copy legs for SailScoring" block: Sail Scoring takes only the ORC import (A37) | DECIDED | The on-screen leg table stays |

### Typed and pasted positions, fixed marks, start lines

| Ref | Item | State | Current note |
|---|---|---|---|
| A38 | Typed and pasted positions; RO page queue | BUILT AND TESTED | |
| A39 | RIB page queue blocked by a refused fix | NOT STARTED | Test on the water before relying on it |
| A40 | Fixed marks fold; reversed routes; WhatsApp list in °M | CONFIRMED LIVE | |
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
| A56 | Wind box saved every keystroke, no range check | CONFIRMED LIVE | |
| A58 | One-end start line: the RO estimates the line | SUPERSEDED (LINE_RULES.md, 26 Oct) | In part: the estimate carried within its race (rule 12); the RO's one-end estimate stays (rule 7) |
| A60 | Copy the course from any other start | NOT STARTED | Design points to decide |
| A61 | Straight legs across land or drying ground | NOT STARTED | Parked |
| A62 | Mark with no rounding side holds the WhatsApp text | DECIDED | Built with gates |
| A63 | Finish line set up as the RO works on the day; a RIB-recorded Finish Pin offered, never chosen silently | SUPERSEDED (LINE_RULES.md, 26 Oct) | In part: box 2 and the default finish (rules 4, 6, 14) |
| A64 | Never show or save a course for another day than the Race day box | BUILT AND TESTED | Released in .37 |
| A65 | Course page opens with no signal | BUILT AND TESTED | Service worker, own version only, saved copy keeps Content-Type only; saves and direct fix actions wait for the version check, new fixes and Send never wait; kill switch `pages/course/sw-kill.js`; released in .45 |
| A66 | Server refuses Withdraw while a saved auto choice uses the fix | SUPERSEDED (LINE_RULES.md, 26 Oct) | No saved auto choices (rule 11) |
| A67 | Correct moves only the starts the RO chooses | DECIDED | Design points first |
| A68 | Save each start's auto choice when its start time passes | SUPERSEDED (LINE_RULES.md, 26 Oct) | No auto choices (rule 11) |
| A69 | Remove Start left later starts' line ends behind | CONFIRMED LIVE | Released in .37 |
| A71 | Loading a day opens the start left open on another day | BUILT AND TESTED | Released in .45 |
| A72 | Orange note when a day's series is changed after the day was copied for Sail Scoring | DECIDED | Needs the page to record each copy |
| A73 | Layout and colour: start line section (one line per end, one status line, one next action), Card mark / Laid line labels (say "estimated" when either end is an estimate), messages beside their button, finish line drawn over the estimated start line, sketch start line and labels | IN PROGRESS | Released in .45: the Start line and Finish line rows as sections with one next action, messages inside their boxes, amber for cautions, sketch labels clear of lines, labels and marks. To do: Card mark / Laid line labels; laid marks at their planning position red as chips but not in the Fixed marks list |
| A74 | Save and load lines call pins set at a mark and placed ends "typed position"; a placed fix's detail says "Phone none" | DECIDED | Name them by what the RO did |
| A75 | Favoured end ignores the first mark | DECIDED | Add which end is nearer the first mark, and by how much; whether to switch to distance when the first leg isn't a beat is open |
| A76 | "Record the missing end…" shows with no start time and no ends | DECIDED | Reword or remove |
| A77 | Undo's label; later starts' lines; duplicate list entries; Undo on a started start's estimate removes its line | DECIDED | Partly met by A58: Undo refused while another start uses the estimate. To do: label, duplicate list entries, Undo on a gone start's own estimate. Rule: starts that have gone keep their line; a new start gets its own |
| A78 | A placed line end replaced by placing again can't be withdrawn on its own | BUILT AND TESTED | Withdraw in Check recorded marks for a typed or placed line end that is no start's estimate, or that no start uses; placing an end again withdraws the one it replaces, or says under the list why not (this device only); until it is withdrawn, a replaced end is saved with its start's course and treated as a placed estimate on every device; in .44 the same for finish line ends and a Start Pin a harbour mark replaces; released in .45 |
| A79 | Workbook release items: Grassy Mid as a card start or finish, the workbook's Grassy Mid label, RW_Temblebreedy_Pier spelling | DECIDED | Ask Mark about an explicit stand-in field; check course-cards for the old spelling |
| A80 | Web app manifest for both pages, so Chrome offers a real Install with no badge on the home-screen icon | IN PROGRESS | Course page released in .46e: `manifest.webmanifest` and three icons (192, 512, maskable 512) beside the page; the test copy installs as its own app ("TEST Course", `/course-test/`); passed on the test copy; installs on the phone with no badge and opens offline. RIB page: goes with A82's RIB icons in one release, after Sunday's race. On iPhone an installed icon keeps its own storage, separate from Safari's |
| A82 | Favicons for the RIB page and the course page | IN PROGRESS | Embedded as data URIs (16 and 32 px icons and an apple-touch-icon per page); partly covers A80 (an apple-touch-icon on the course page, no manifest; A80 stays open for the manifest). Course page: released in .45. RIB page: needs checking on the water before it is relied on, and carries the A81 weakness as before |
| A85 | Withdrawn positions shown greyed in All fixes and marks | NOT STARTED | Later |
| A86 | Restore a withdrawn position | NOT STARTED | Needs a `marks.php` action; later |
| A87 | Same-time ties between fixes are ordered differently on different devices | NOT STARTED | Later |
| A88 | Save A78's "replaced end kept / not withdrawn" note with the course, so other devices see it | NOT STARTED | Later |
| A89 | A replaced placed end kept because another start uses it loses its estimate label, so later races' Auto and the "Use it?" prompt can pick it | SUPERSEDED (LINE_RULES.md, 26 Oct) | No Auto (rule 11) |
| A90 | The Chart is blank or only partly drawn on first load (Chrome on PC), also with the service worker bypassed; switching Sketch → Chart draws it | NOT STARTED | Seen on the test copy, not in a quick check of the live page; no errors logged; cause not known |
| A91 | In a line-end list, the Auto option and an explicit entry can read exactly the same, so the RO can't tell which keeps the start on Auto | SUPERSEDED (LINE_RULES.md, 26 Oct) | No Auto option (rule 11) |
| A92 | Saving the day's series (A8) adds nothing to the course history | NOT STARTED | Check whether that is intended |
| A94 | The day's wind in section 1, and each start's wind under its start time | BUILT AND TESTED | Released in .45: a start follows the day's wind until it is used, keeps a wind typed for it, and says where its value came from; `marks.php` keeps the wind in the day record |
| A95 | Start Pin routes: set at a mark (harbour marks only this way), or placed from the committee boat in use or a mark laid in the race | SUPERSEDED (LINE_RULES.md, 26 Oct) | A pin from a laid mark and a pin set at a mark go (rule 4) |
| A96 | The Start Pin list holds this race's fixes only | SUPERSEDED (LINE_RULES.md, 26 Oct) | Carried pins go; pins stay available as choices (rules 12, 15) |
| A97 | Recorded fixes offered after the RO's own choice | BUILT AND TESTED | Released in .45: only when newer ("Newer: …"); the in-use label says where the pin is |
| A98 | A start's saved Auto picks when its start time changes | SUPERSEDED (LINE_RULES.md, 26 Oct) | No saved Auto picks (rule 11) |
| A99 | A helper's "sending…" message didn't follow its fix to "sent." or "not sent" | BUILT AND TESTED | Released in .45 |
| A100 | A start sharing another's finish line was reported as no longer among the day's fixes on another device | BUILT AND TESTED | Released in .45 |
| A101 | The midpoint and a placed Finish boat didn't keep the committee boat end they replaced, so Undo went to Auto | SUPERSEDED (LINE_RULES.md, 26 Oct) | No Auto to go back to (rule 11) |
| A102 | The pin lists offered entries that aren't real marks | BUILT AND TESTED | Released in .45 |
| A103 | "undefined" in the Finish Pin's "on the water" box | BUILT AND TESTED | Released in .45 |
| A104 | A sent item stayed in the "not sent" line near the top of the page | BUILT AND TESTED | Released in .45 |
| A105 | Sketch labels overlapped each other and lines, sat by the wrong mark, or were clipped at the edge | BUILT AND TESTED | Released in .45 |
| A106 | Row messages ("Finish line updated from …", "Undone: …") stayed after the row changed | BUILT AND TESTED | Released in .45: any change in the row clears them |
| A107 | The Start Pin's "from" list offered harbour marks | BUILT AND TESTED | Released in .45 |
| A108 | Auto chose another race's Finish Pin silently | BUILT AND TESTED | Released in .45: never chosen; "No finish set" shown instead |
| A109 | "Square to the last leg" was square to the leg to the boat, not to the line's midpoint | BUILT AND TESTED | Released in .45: worked out for the length typed, in all three finish boxes |
| A110 | The emergency midpoint kept an already placed Finish boat | BUILT AND TESTED | Released in .45: the boat is withdrawn |
| A111 | Change boat… suggestions did nothing with "from" set to a harbour mark | BUILT AND TESTED | Released in .45 |
| A112 | The Start Pin row said "Not recorded" while Auto carried an earlier race's pin | SUPERSEDED (LINE_RULES.md, 26 Oct) | No Auto carrying a pin (rules 11, 12) |
| A115 | After its fixes were moved to another race, a start's rounding list kept them, named with the other race and time | DONE | Decided: kept as now; a start's rounding list keeps pointing at a moved fix, named with its new race. No page change |
| A116 | A set Finish Pin is offered a newer recorded or typed one ("Newer: … Use it") | DONE | Decided: kept as now; a typed Finish Pin is offered the same way as a recorded one (A97). No page change |
| A117 | Box 2's layout: the Suggest buttons on the same line as "from it"; "Set pin and place boat" bigger and bold | BUILT AND TESTED | Released in .45; passed on the test copy |
| A118 | Box 3's "New committee boat fix" list shows no accuracy for a recorded fix | BUILT AND TESTED | Released in .45: "±N m" as the Committee boat lists and All fixes and marks show it; a typed position has none; passed on the test copy |
| A119 | A green "… typed position …: sent." line stays on screen long after it was sent | BUILT AND TESTED | Released in .45: a green "…: sent." line clears after 10 seconds if unchanged; red, amber and not-sent lines never clear this way; passed on the test copy |
| A121 | Box 3's layout as box 2's (A117): the Suggest buttons on its line; "Use the boat and place the pin" bigger and bold on its own line | BUILT AND TESTED | Released in .45 (build .45b); passed on the test copy |
| A122 | Section 4's square-to-wind line measured the mark named Windward from the course's first mark when there was no start line, giving figures such as "132° right of square · move 0 m" | BUILT AND TESTED | Released in .45 (build .45b): "First mark (name) …", from the start line's midpoint to the first mark after the start, whatever its name; with no start line, a note and no figure; the calculation unchanged; passed on the test copy |
| A123 | Start and finish lines with a missing end: "Line not set" beside the Start line heading, and a mark as a line end; section 4's "First mark: set the start line to see how square it is to the wind" in orange | SUPERSEDED (LINE_RULES.md, 26 Oct) | Replaced by the line rules rework (A127) |
| A124 | A committee boat placed from a harbour mark (the route that also sets the Start Pin there) read "1000 m at 090°M from Start Pin No.13": it now reads "0.5 nm at 090°M from No.13", nautical miles to one decimal, the mark named plainly; below 0.1 nm in metres ("80 m at 090°M from No.13") | SUPERSEDED (LINE_RULES.md, 26 Oct) | The harbour mark placement no longer sets a pin (rule 4); the wording is reconsidered in A127 |
| A125 | A Grassy finish on a card course finished on the recorded start line when there was one | BUILT AND TESTED | In .46, not released: a Grassy finish always finishes at Grassy; on Laid line the Finish list stands and there is no fallback to the start line ("Same as the start line" still when the RO picks it); a Grassy card start on Automatic is Grassy, the recorded line not used; a hand-built Grassy start's WhatsApp line reads "Finish at Grassy."; tested in the harness |
| A126 | "Set Start Pin at" on a later start is not taken up when the previous start's Start Pin was chosen by hand and both starts have the same start time: the page keeps the previous start's choice | SUPERSEDED (LINE_RULES.md, 26 Oct) | Nothing carries between starts (rule 12) |
| A127 | Line rules rework (LINE_RULES.md) | BUILT AND TESTED | Released in .46e: every start and finish line end the RO's choice from a list that starts empty; starts saved before read exactly as saved; tested in the harness and on four copies of saved data; passed on the test copy |
| A128 | Sketch labels on the wrong points: a name beside another mark's point, a point with no name, or a name with no point | NOT STARTED | Seen on the test copy, 23 Oct, Race 2 Start 3; the label placer's penalty for sitting nearer another mark is small. Agreed wording for a pin set at a mark: "Start Pin (Dosco)" / "Finish Pin (Dosco)" (now just "Dosco") |
| A129 | The start line note says "pin end favoured by … m" when that end is a harbour mark (Dosco, No.8), not a pin | NOT STARTED | Seen on the test copy in the .46c round |
| A130 | An old start's midpoint estimate reads "Estimate: Dosco used as the line's midpoint" when the midpoint is an old pin record set at Dosco ("Start Pin at Dosco R2 13:10"); the Legs box says it correctly | NOT STARTED | The label uses the sketch's short name for the pin (A128) |
| A131 | After a start line is cleared and rebuilt, the amber placed-boat wording under the Committee boat list may not match the line ("Line not set") | NOT STARTED | Seen on the test copy in the .46c round; the harness rebuild check finds no mismatch; to be watched in the .46d test round |
| A132 | Both placing boxes (committee boat from a harbour mark, pin from the committee boat) take the distance in whole metres, 1 to 5000, and the bearing in whole degrees, 0 to 359, exactly as typed; anything else is refused with the reason under the box and nothing is placed | BUILT AND TESTED | Released in .46e; tested in the harness; passed on the test copy (metres everywhere, no nm). A decimal distance gives its nm conversion only when the result is 1 to 5000 m ("0.5 nm is 926 m"). Every placed end now reads in whole metres, Copy for Sail Scoring too (C13) |
| A133 | A refused Undo says why: which start uses the line and what to change first ("Not undone: Start 6 uses this start line. Change Start 6's start line first."; the race named only when the other start is in a different race). Placed ends told apart in the Line ends line ("Committee boat (est. 926 m from No.13) 15:00") | BUILT AND TESTED | Released in .46e: both halves name the race only for a start in another race; tested in the harness; passed on the test copy. A placed end no line uses stays on record |
| A134 | Race 2 Starts 1 and 3 (saved before the line rules) were saved on the test copy at Step 26 of the .46c round ("Change nothing"): both lines left unset, and Start 3 lost its sent time, wind, Laid line setting, midpoint and placed Finish boat record | BUILT AND TESTED | Released in .46e: a device whose stored day came from a page before .46b (.45b on every live RO device) no longer sends that day's old starts back with empty lines; replayed in the harness; passed on the test copy (a PC and a phone holding stale stored data sent no save, and the old starts read as saved); after the release every RO device read 18 October Race 1 Start 1 as saved (1.48 nm) |
| A135 | On the Chart, the "Start line: estimate" label can sit under a line end's label when the boat and pin are close | NOT STARTED | The line label is not part of the Chart's label placing; separate from the sketch (A128) |
| A136 | In Check recorded marks, placed ends with the same numbers for two starts look like a second start line | NOT STARTED | Low; the pin naming the boat it was placed from may be enough |
| A137 | marks.php keeps a device id and the page version with every course save, history entry and withdrawal, so a save can be traced to the device and page that sent it | NOT STARTED | Raised by A134, where the records could not tell devices apart; a marks.php change (tests on PHP 8.4 and 5.5) |
| A138 | A pin placed from one committee boat, in a line whose committee boat is now another: its label kept "200 m at 190°M from Committee boat …" while the line measured otherwise. It now says it was not placed from the boat now in the line, gives the line as it is, and asks "Do you want to reset the Pin end?" (Yes opens the Place pin box filled, No changes nothing) | BUILT AND TESTED | Released in .46e; Finish Pins too; Copy for Sail Scoring gives the line as it is (C13); tested in the harness; passed on the test copy (start and finish, No, Yes, the reset pin with no warning). Yes button's look: A141; No not kept: A142 |
| A139 | A placed pin names the committee boat it was placed from ("from Committee boat R2 15:45, placed 926 m from No.13"), so two boats at the same time are told apart | BUILT AND TESTED | Released in .46e; tested in the harness; passed on the test copy, records placed before it included |
| A140 | "Place a pin from the committee boat…" straight after the Pins in both Other end lists, before the harbour marks | BUILT AND TESTED | Released in .46e; tested in the harness; passed on the test copy (start and finish lists) |
| A141 | The reset question's Yes button (A138) is plain grey, while No and Undo are blue outlined; make them match | NOT STARTED | Seen in the .46e test round |
| A142 | After No to the reset question (A138), the question comes back whenever the start is drawn again (for example after switching starts), since No is not saved | NOT STARTED | Seen in the .46e test round; works as built; for Pat to decide whether No should be kept |
| A143 | Sail Scoring connection, Stage 1, read-only, test copy only: a "Sail Scoring (test)" panel (Connect with PKCE, Disconnect with revoke) showing the workspace, a series list, its fleets and the races on the Race day; GET only, plus token and revoke | BUILT AND TESTED | In `pages/course/sailscoring-test.js`, added by the test build only; the live page never includes it; passed on the test copy (connect, ORC Ireland workspace, series, fleets, a race day's races with starts and fleets, renewal after more than an hour, Disconnect). Open question for Mark: after Disconnect the account page still lists the app (most likely the grant, which only the account page removes). Later: A144, A145, A146 |
| A144 | After a Sail Scoring sign-in (A143) the page's "Race day is back to today" note stays visible although the panel has restored the saved day; the note must not show when the day has been restored | NOT STARTED | For a later stage; not to be fixed in Stage 1 |
| A145 | The Sail Scoring panel (A143) is absent offline, since the service worker does not keep `sailscoring-test.js` | NOT STARTED | For a later stage; not to be fixed in Stage 1 |
| A146 | The Sail Scoring panel's Disconnect message (A143) should say the connection is ended on this device, and that removing the app from Sail Scoring entirely is done from the Sail Scoring account page | NOT STARTED | For a later stage; not to be fixed in Stage 1 |

Withdrawn: A1, A3, A4, A6 (decisions and review UI; see `docs/experimental/decisions-and-review/`), A14 (Cage position, issue #1), A36, A51, A52, A53, A59 (superseded by A58), A113 (did not recur on the test copy), A114 and A120 (page wording as intended).

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
| C9 | Pin every auto choice; RO-key lock on the as-sailed course | SUPERSEDED (LINE_RULES.md, 26 Oct) | In part: no auto choices to pin (rule 11); the RO-key lock stays |

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
| 2026-10-18 | Race (Autumn League) on .37 | L3, A10, A11, A15, A29, A31, A32, A40, A56, A58, A69 confirmed live; RIB page worked |
