# Project History

## Cork Harbour ORC Course Data, Race-Day Recording and Course Plotting

This history was reconstructed by Pat Tanner from his records and the
repository. Events before 29 September 2026, and those involving external
systems, cannot be verified from this repository. It is a technical history of
how `cork-harbour-orc` developed and how it has worked with
`sailscoring/course-cards` and `sailscoring/sailscoring`; it is not a statement of
ownership over ideas or a roadmap for those projects.

## 1. Origin: accurate course geometry for ORC scoring

ORC Constructed Course scoring needs the distance, bearing and wind for each leg
of the course actually sailed. A leg and bearing spreadsheet for Cork Harbour
courses immediately exposed a local-navigation problem: the straight line between
two racing marks is not necessarily a route a yacht can sail. Land, shoals and
harbour geometry can require a passage with intermediate turning points, so the
spreadsheet held practical passages rather than simple chords.

## 2. Early review with `course-cards`

The spreadsheet was shared with Mark McLoughlin, maintainer of Sail Scoring and
`course-cards`. Review of the Cork Harbour data led to `course-cards` issues
[#14](https://github.com/sailscoring/course-cards/issues/14) (do not silently
treat differently named marks as the same object),
[#15](https://github.com/sailscoring/course-cards/issues/15) (marks shared across
clubs) and [#16](https://github.com/sailscoring/course-cards/issues/16)
(straight-line legs through water the fleet cannot sail). The Cork passage table
showed that realistic geometry can be represented with racing marks, a small set
of routing waypoints and authored passages between them. One idea has stayed
central since: **the marks may be correct while the straight line between them is
not the sailed passage.**

## 3. The Course Data Workbook

The spreadsheet grew into a Course Data Workbook recording what makes the figures
defensible: mark identities and coordinates, their sources, routing waypoints and
passages, local constraints, bathymetric validation, and the difference between
published and approximate positions. Mark opened three further issues:
[#17](https://github.com/sailscoring/course-cards/issues/17) (Cork mark
positions), [#18](https://github.com/sailscoring/course-cards/issues/18) (tidal
and depth restrictions on legs) and
[#19](https://github.com/sailscoring/course-cards/issues/19) (provenance and
accuracy). The depth work showed that a route is only as well validated as the
positions of its ends, and that a restriction belongs on the physical leg that
causes it, so it follows that leg into any course.

## 4. The RIB recording page

Preparing the RCYC Autumn League 2026 ORC trial raised a separate need. Fixed
marks have known positions; laid marks do not, and their position on the day is
needed to describe the course sailed. The RIB recording page was built for that
narrow purpose: a RIB crew records each laid mark's GPS position, which goes back
to the scoring workflow. It solved a scoring-data problem; it was not meant as a
race-management application.

## 5. From recorded positions to the course page

The first plan was to send recorded positions by WhatsApp and enter them into
Sail Scoring as waypoints. Once fixes were recorded, the fixed positions, the
day's laid-mark positions, the chosen course and the passage data could be put
together, so the Race Officer Course Plot (the course page) was built to show the
day's course and calculate its ORC legs before handing them on. Fixes were kept on
the server as JSON, each with date, race, name, position, accuracy and times, so
any earlier day can be loaded and rebuilt. The stored observations and the course
built from them were separate from the start.

## 6. First operational use, and regional thinking

Mark reviewed the work on 25 September. On 27 September 2026, the first day of
the Autumn League, the RIB page and course page were used for real: positions
recorded and kept on the server, the course built and checked, ORC legs
calculated and entered into Sail Scoring by hand. A "Copy legs for SailScoring"
block followed on 30 September. The end-to-end workflow worked in practice.

In the week beginning 28 September Pat asked the host of the ORC Ireland site
whether it could take separate deployments for different areas: RCYC/Cork
Harbour, DBSC/Dublin Bay, HYC/Howth, each with its own data but the same method.
The principle, common method and workflow with separate regional data, came
before Sail Scoring's later course-days design and was not a response to it.

## 7. GitHub, integration tests and the duplication concern

On 29 September the work was organised into the `Bateleur88/cork-harbour-orc`
repository and shared with Mark, with AI assistance disclosed. Mark reviewed it
on 1 October. Pat was by then considering a richer hand-off than a bare leg table:
named positions, the mark sequence, bearings with their reference and variation,
routing waypoints, provenance, and a known geographical anchor so the chain of
legs could be located. This fed into explicit magnetic and true bearings in Sail
Scoring ([sailscoring#660](https://github.com/sailscoring/sailscoring/issues/660)).
On 5 October, Cork data run through Sail Scoring exposed imported marks whose
positions had changed
([#663](https://github.com/sailscoring/sailscoring/issues/663)) and an
unrecognised starting-mark name
([#664](https://github.com/sailscoring/sailscoring/issues/664)): identity and
position are different things, and names alone are not a robust identity. On 6
October Pat raised with Mark that the two projects seemed to be duplicating
functionality.

## 8. 4 October: moved marks expose fix problems

On 4 October variable wind meant marks were moved during racing. That exposed
delays between tapping Record and the position stored, marks recorded in the
wrong place, several fixes for one mark, and the difficulty of telling races
apart and choosing which fix a race used. Keeping every fix rather than
overwriting proved its worth. By 5 October the RIB page saved only a fresh
position and recorded the tap time, and the course page gained Check recorded
marks, a read-only plot of the day's fixes with advisory flags. Once the page had
real geometry, wind-based tools followed naturally (line squareness, whether the
windward mark is still a beat): the start of race-operation decision support as
well as scoring data.

## 9. `course-days.md` and three projects

Mark's public design document
[`docs/design/course-days.md`](https://github.com/sailscoring/sailscoring/blob/main/docs/design/course-days.md)
(proposed, October 2026) formalised many of the same problems: race-day fixes,
start and finish lines, provenance and a versioned "Course Record" as the
hand-over to scoring, with the line "Sail Scoring keeps the record of what was
sailed. It does not help run the race." By then the work fell into three areas:
this repository (Cork data and validation, and the tools that capture race-day
positions and help the Race Officer), `course-cards` (shared representations of
marks, courses and passages) and Sail Scoring (scoring and the durable record).
The overlap was not accidental duplication: the projects had been working on
different parts of the same real workflow. Pat's position on 6 October was that
the Cork tools stay in use, shared concepts belong in `course-cards`, and a
documented hand-over format is the natural boundary.

The project has followed the same pattern throughout: meet a real requirement,
build the least that solves it, use it with real races, find the assumptions that
fail, fix them, and share what generalises.

## 10. 7–8 October: the audit, and from decisions to as-sailed repair

On 7 October a read-only audit (`docs/audit/PHASE1_AUDIT.md`) compared the code
with the intended workflow: a RIB page recording fixes, a course page that never
edits them, a course built from them, and a saved course handed to Sail Scoring.
Pat decided the same day that there is no separate original course: the recorded
marks are the original and are never overwritten. A staged Draft, Decisions,
Accepted workflow was described but never decided.

A review-decisions layer (Accept, Do not use, Use as, with an RO key) was built
over 6 to 8 October and then taken out of the page as an unnecessary
complication. In its place the course page repairs the as-sailed course directly:
any recorded fix of the day can be picked into a race and used for a course row
or a line end, without changing the fix, and the choices are saved with the
course. The withdrawn work is kept under the tag `experiment/decisions-review`.

## 11. 9 October: first live upload, and visible saves

On 9 October Pat uploaded `marks.php` and the course page to tradboats.ie after
taking backups, and repaired 4 October's Race 1 on the live page: the first live
course save, with its course history written. Reading the page afterwards showed
that course saves were silent: a refused save was never shown, loading a day
could send saves without an edit, and changing day could drop unsent edits. The
next release, the same day, showed every save result, said why a load led to a
save, and stopped a change of day while anything was unsent.

## 12. 10 October: Copy for Sail Scoring

Sail Scoring accepted sample documents of the 27 September Race 1 in its ORC
constructed course format, which carries each leg's distance, magnetic course and
wind, and an anchor where the first leg starts. The course page gained Copy for
Sail Scoring, producing that document from the leg table's own figures and naming
any leg left out or measured from a stand-in. Its output was accepted by Sail
Scoring the same day and released.

## 13. 11–12 October: a course built from fixed marks

On 11 October the Race Officer set courses from fixed marks rather than card
courses, and the RIBs recorded one Start Pin, one Finish Pin and no committee
boat. The page could not bring fixed marks into a race, a position copied from the
card was refused because of its minutes symbol, and a course built from pasted
positions existed on one device only. The releases that followed accepted the
card's minutes symbol, labelled pasted positions as device-only, stopped a refused
fix blocking the course page's queue, and showed a missing mark instead of hiding
it. The RIB page's queue has the same blocking fault but was left alone as proven
offline code.

## 14. 12–13 October: fixed marks and a run of fixes

Over the next releases the course page gained every positioned mark in the
workbook as Fixed marks, with one-way card routes completed by their exact reverse
in the snapshot build, routing waypoints the RO can place, and a clean WhatsApp
course list for competitors. Far-away typed positions were kept out of the plots.
Typed positions could be withdrawn or corrected on the server, never deleted, and
pasted positions saved to the race record. A course with a missing mark was held
back from competitors. Magnetic variation moved to the World Magnetic Model for
the race date, as Sail Scoring uses. Each release was tested by Pat on the test
copy.

## 15. 13–14 October: choices saved with the course, and one-end start lines

Testing showed that a saved course could still change later: the laid-mark choice
was kept on one phone and automatic line ends were re-resolved on every load. The
page now saves auto's choices with the course and offers a newer fix rather than
taking it. Distances and bearings moved to Vincenty, as the workbook uses, and
variation to the exact point and time Sail Scoring uses. The wind box stopped
saving every keystroke. Recreating 11 October's Race 1, which had only a Start
Pin, showed the page could not give a start line from one end, so the release was
held until the RO could estimate the missing end by distance and bearing, or use
the known end as the line's midpoint. It went live on 14 October with a new
`marks.php`, and the live 11 October courses were rebuilt with it. A sweep of
straight legs crossing drying ground and a design for gates were recorded for
later.

## 16. 14–15 October: start line setup

The next release dealt only with start lines: the Grassy start on any start, a
Start Pin set at a harbour mark, the missing end placed from either direction with
suggestions, the midpoint drawn as a line, and estimates carried forward only
within their race. Pat's testing found that the page could show and save one
day's course under another day after a crash and reopen, so the page now holds
everything until the loaded day matches the Race day box. An analysis of how a
start that has gone could still be changed led to Undo being refused while another
start uses an estimate, placed ends taking their own start's time, Remove Start
moving every record of later starts and withdrawing the removed start's own
placed ends, and line ends saved only once a start time is complete. The Grassy
start was reworded as a real start line rather than a stand-in. It was released
on 15 October, with race-day precautions for the first race on it, Sunday 18
October.

## 17. 16 October: cleanup, a second site, and the series per day

On 16 October Pat removed the test files from the live data folder, archived in
full first: a decided exception to never deleting recorded data, since they were
tests, not races. An install package and guide were prepared for orc-ireland.org,
a separate install with its own key and data (`docs/INSTALL_ORC-IRELAND.md`).
Preparing it showed that `marks.php` still accepts the race key in the address,
where it can reach server logs. Recreating 10 September in a different series
showed that the series name was one setting for every day, so editing an old day
changed it for all. The series became part of each race day, saved and loaded
with it, with a script to write it into the days already raced. A loaded day now
opens its first start with a course rather than the start left open on another
day. Both were built and tested on the test copy the same day.

## 18. The hand-off settled with Sail Scoring (#667)

Discussion with Sail Scoring's maintainer settled the question that had stood
since the audit: who records fixes and builds the race-day course, and in what
format it reaches scoring. This project records the fixes and builds the
AsSailedCourse; Sail Scoring imports it in its ORC constructed course format,
produced by Copy for Sail Scoring, and does the scoring. The proposed "Course
Record" format no longer applies, and the bearing and line-end conventions follow
what the page already sends.

## 19. Documentation cleanup

By mid-October the status, roadmap, README, history and guidance files had grown
long, repetitive and in places contradictory, and each round of manual testing
took an hour and a half or more. On 16 October 2026 the facts were re-established
from the code and the git log, and the files were rewritten so that each has one
job and each fact lives in one place: `STATUS.md` for where things stand,
`README.md` for how the system works, `ROADMAP.md` for direction, this file for
how it got here, and `CLAUDE.md` for how Claude Code works here. Regression
testing moves to scripts, leaving manual steps for what needs a person's eyes.

## 20. 16–17 October: opening with no signal

On the water the course page has to open where there is no signal, so .39 gave it
a service worker that keeps a copy of the page and the race key and uses it only
when the network fails or is slow. Its saved copies are named for its own folder
and version, so it never touches the RIB page's or the test copy's, and it keeps
only a page of its own version, because the host can serve an older page from its
cache. Saves and withdrawals wait until the page has confirmed its version with
the server, so an old copy can never overwrite what a newer page saved; new fixes
and Send never wait. Testing on the test copy found the worker holding the page
while it read a copy of it, which stalled Reload, and it was changed to hand the
page over at once. A kill switch was kept ready, and both pages gained embedded
icons.

## 21. 18–19 October: withdrawing replaced line ends

After the race of 18 October, a wrongly placed start line end stayed in its list
and was offered back through "Use it?". .40 let the RO withdraw a placed or typed
line end from Check recorded marks once nothing uses it, and made placing an end
again withdraw the one it replaces, saying under the list when it cannot. .41 kept
a replaced end that could not yet be withdrawn with its start's course, so every
device treats it as a replaced estimate: never offered back, never taken by Auto,
and still able to be withdrawn.

## 22. 19–22 October: the finish line, tested on the PC

The finish line was built like the start line in three rounds (.42 to .44). To
test faster than uploading to the test copy each time, a local test site was set
up on the PC, with a build labelled LOCAL, a made-up race day and scripts to reset
it, so the tablet and phone could test over the home network; a browser harness
drove the same made-up day and compared every saved day against the released page.
Each round on the tablet changed the design: the finish became three ways that
follow how the RO works on the day (the boat stays, a mark and the boat placed
from it, or the boat has moved), no finish is shown as "No finish set" rather than
guessed from another race, and the suggested bearings were made square to the leg
to the line's midpoint. The same rounds settled the Start Pin's routes (a harbour
mark only ever as the pin itself), moved the wind to the day with each start
keeping its own once used, and turned every fault found into a tracked item. Both
test files passed on the local site on 22 October, with one Undo result that could
not be reproduced, carried to the test copy.

## Related repositories and issues

-   `Bateleur88/cork-harbour-orc`
-   `sailscoring/course-cards`: issues #14 to #19
-   `sailscoring/sailscoring`: issues #660, #663, #664 and #667;
    `docs/design/course-days.md`
