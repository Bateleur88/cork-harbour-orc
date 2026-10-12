# Project History

## Cork Harbour ORC Course Data, Race-Day Recording and Course Plotting

This history was reconstructed by Pat Tanner from his records,
correspondence and the repository. Events before 29 September 2026, and
those involving external systems, cannot be verified from this repository.

This document records how `cork-harbour-orc` developed, why its
principal components exist, and how the project has interacted with
`sailscoring/course-cards` and `sailscoring/sailscoring`.

It is a technical project history, not a statement of ownership over
ideas or a roadmap for the upstream projects. The work developed
iteratively from practical requirements encountered while preparing and
running the RCYC Autumn League 2026 ORC scoring trial.

## 1. Origin: accurate course geometry for ORC scoring

The project began with a practical ORC scoring requirement in Cork
Harbour.

ORC Constructed Course scoring requires a useful representation of the
course actually sailed: in particular the distance, bearing and wind
conditions for its component legs. An initial leg/bearing spreadsheet
was developed to provide this information for Cork Harbour courses.

That work immediately exposed a local-navigation problem: the straight
line between two racing marks is not necessarily the route a yacht can
actually sail. Land, shoals, harbour geometry and other navigational
constraints can require a physical passage to contain one or more
intermediate turning points.

The original spreadsheet therefore contained practical passage
information rather than treating every mark-to-mark leg as a simple
geodesic chord.

## 2. Early review with `course-cards`

The spreadsheet was shared with Mark McLoughlin, maintainer of Sail
Scoring and `sailscoring/course-cards`. Review of the Cork Harbour data
exposed several issues in the more general course-card model.

The resulting `course-cards` issues included:

-   [#14](https://github.com/sailscoring/course-cards/issues/14) ---
    mark identity and the need not to silently guess that differently
    named marks are the same physical object.
-   [#15](https://github.com/sailscoring/course-cards/issues/15) ---
    marks used across different clubs and the case for
    harbour-level/shared mark data.
-   [#16](https://github.com/sailscoring/course-cards/issues/16) ---
    `courseLegs` returning straight-line distances and bearings through
    water the fleet cannot actually sail.

Issue #16 was particularly important. The Cork Harbour passage table
provided a working example showing that realistic course geometry could
be represented using racing marks, a relatively small set of routing
waypoints, and authored passages between them.

This established an important distinction which has remained central to
the project:

> **The marks may be correct while the straight line between them is not
> the sailed passage.**

## 3. Development of the Course Data Workbook

The original leg/bearing spreadsheet developed into a broader Course
Data Workbook.

The objective was no longer merely to hold calculated leg figures. The
workbook increasingly recorded and checked the underlying information
needed to make those figures defensible, including:

-   racing-mark identities and coordinates;
-   sources and provenance for positions;
-   routing waypoints and authored passages;
-   local navigational constraints;
-   depth/bathymetric validation; and
-   differences between published, approximate and otherwise derived
    positions.

As this work was forwarded to Mark, he updated #16 and opened three
further `course-cards` issues:

-   [#17](https://github.com/sailscoring/course-cards/issues/17) ---
    improving Cork Harbour mark positions from the supplied data;
-   [#18](https://github.com/sailscoring/course-cards/issues/18) ---
    representing course/leg conditions such as tidal or depth
    restrictions;
-   [#19](https://github.com/sailscoring/course-cards/issues/19) ---
    recording provenance and positional accuracy at an appropriate
    level.

The depth work was especially useful in demonstrating why these concerns
are connected. A route can only be described as depth-validated to the
degree justified by the accuracy of its endpoint and waypoint positions.

The work also showed the advantage of attaching a restriction to the
physical leg or passage which causes it, rather than only to a numbered
published course. A leg-level restriction can then follow that passage
into any course in which it is used.

## 4. RCYC Autumn League 2026: the need to record laid marks

A separate practical requirement arose while preparing the RCYC Autumn
League 2026 ORC scoring trial.

Fixed racing marks could use known or published positions. Laid racing
marks could not: their actual position on the day was required if the
resulting course geometry was to represent the course actually sailed.

This led to the **RIB Recording Page**.

Its original purpose was narrow and operational:

1.  a RIB crew lays or attends a racing mark;
2.  the device records an accurate GPS position;
3.  that race-day position is returned to the race/scoring workflow; and
4.  the position can be used in constructing the ORC course.

The RIB recorder was therefore created to solve an ORC scoring-data
problem, not as an attempt to create a general race-management
application.

## 5. From recorded positions to the Race Officer Course Plot

The first intended transfer method was simple: recorded mark positions
could be sent by plain-text WhatsApp and entered into Sail Scoring as
waypoints.

Once the RIB Recording Page was functioning, however, there was an
obvious opportunity to make better use of the same information.

The project already had:

-   published/fixed mark positions;
-   actual race-day positions for laid marks;
-   the selected course;
-   Cork Harbour passage/routing information; and
-   the geometry required to calculate ORC legs.

Rather than sending isolated coordinates without first seeing the course
they produced, these inputs were combined into a **Race Officer Course
Plot**.

The Course Plot could therefore show the physical race-day course and
calculate the leg information required for ORC scoring.

Its original intended output remained a handoff to Sail Scoring: a
packaged WhatsApp message containing information such as:

-   Series name;
-   Race name;
-   relevant race-day coordinates; and
-   ORC leg data.

The Course Plot was therefore initially an intermediate
operational/validation step between race-day observations and Sail
Scoring, rather than a replacement for Sail Scoring.

The RIB and committee-boat observations were also retained on the server in JSON format rather than existing only transiently in the browser. Each fix kept its date, race, mark name, position, GPS accuracy, position time and server-received time; device and recorder fields were added by 29 September. The Course Plot reads the JSON data for the requested date and creates the Race Day Course Record from those stored observations. It can also request earlier dates, allowing historical race-day data to be displayed and reconstructed from the retained record.

This established an early separation between the persistent **race-day observation archive** and the **Race Day Course Record** constructed from it.

## 6. 25 September 2026: feedback from Mark

On 25 September, Mark reviewed the work and gave feedback.


## 7. 27 September 2026: first operational use

The RIB Recording Page and Race Officer Course Plot were successfully used operationally on the first day of racing in the RCYC Autumn League on 27 September 2026.

The working flow was:

1. RIB and committee-boat positions were recorded;
2. those observations were retained on the server;
3. the Course Plot loaded the requested race-day data;
4. the Race Officer could construct and inspect the physical course;
5. usable ORC leg distances and bearings were calculated; and
6. the resulting leg data was transferred into Sail Scoring by hand. The dedicated `Copy legs for SailScoring` block was added later, on 30 September (commit [`98f9713`](https://github.com/Bateleur88/cork-harbour-orc/commit/98f9713f062b9b09abae33b8eca5aaffbb98a074)).

The resulting course data was therefore used in the actual Sail Scoring workflow for the Autumn League ORC trial. This established that the end-to-end workflow — race-day position capture, persistence, course reconstruction, ORC leg calculation and transfer to Sail Scoring — was operational rather than merely a prototype.

## Regional deployment concept — week beginning 28 September 2026

Once the usefulness of the combined RIB Recording Page and Race Officer Course Plot had been demonstrated, thinking moved beyond a single RCYC deployment. During the week beginning 28 September, Pat raised with the person hosting the ORC Ireland site whether the ORC-Ireland server could accommodate a regional file structure for separate deployments using the same methodology and workflows.

The concept was not one central operational dataset for every club. Instead, each sailing area or organisation would have its own deployment and venue-specific data while reusing the same underlying approach. For example:

- **RCYC / Cork Harbour** — Cork Harbour marks, courses, routing/local-navigation data and historical race-day JSON;
- **DBSC / Dublin Bay** — a separate Dublin Bay dataset and race-day archive using the same recording and Course Plot workflow; and
- **HYC / Howth** — a separate Howth dataset and race-day archive using the same methodology.

The principle was therefore **common methodology and workflow, separate regional data**. This was an early indication that the combined pages could become a reusable regional Race Officer system rather than remaining solely an RCYC Autumn League tool.

This regional/server concept was already under discussion before the question of overlap was raised with Mark. It should therefore not be described as having arisen in response to the later `course-days` design. Retrospectively, however, it fits naturally with the later distinction between venue-specific operational tools/data, reusable course representations, and Sail Scoring's durable scoring record.

## 8. 4 October 2026: variable wind exposes race-day fix problems

The system was used again on 4 October. Variable wind resulted in marks being moved during the racing and exposed several issues which had not been obvious during the first operational use.

These included:

- delays between the user's recording action and the position ultimately recorded or received;
- marks being recorded in incorrect positions;
- multiple observations for the same named mark as marks were moved;
- the need to distinguish observations belonging to different races; and
- the need to decide which observation should be used when reconstructing a particular race.

The persistent JSON observation archive proved important here. Rather than replacing one coordinate with another, the system could retain separate observations with race, time, accuracy, device and recorder information. The Course Plot could then read the requested day's observations and resolve them in the context of the selected race.

The Course Plot already resolved fixes in the context of each race from 1 October (commit [`8d36c09`](https://github.com/Bateleur88/cork-harbour-orc/commit/8d36c0943e4e94d3cdbd4e656c95dd46d37a67f8): the automatic choice never picks a fix recorded after the start). After the 4 October use exposed the problems above, the pages gained on 5 October the tap time stored beside the position time ([`4a66559`](https://github.com/Bateleur88/cork-harbour-orc/commit/4a66559f3b61159f229409ca20d03f256e541b86)), a rule that saves only a fresh GPS position ([`ce3e7e4`](https://github.com/Bateleur88/cork-harbour-orc/commit/ce3e7e4c567dc028fc2b45d260b2a6bc76767ea8)) and the Check recorded marks box, a read-only plot of the day's fixes ([`01329fc`](https://github.com/Bateleur88/cork-harbour-orc/commit/01329fc48edcbba5c9c2e2f138ba3ea85b902477)). The archive also preserved the source data for later historical inspection rather than leaving only the final pasted leg table.

The 4 October field use showed why position time, receipt time, accuracy, source and several fixes for one mark matter when a course is reconstructed after marks have moved.

## 9. Operational features grew naturally from the Course Plot

Once the page contained actual course geometry, further Race Officer
functions became natural extensions.

Adding wind direction, for example, made it possible to assess:

-   start-line squareness;
-   the relationship between the course axis and the observed wind; and
-   whether a weather mark remained appropriately positioned after a
    wind change.

These functions grew from information already available to the Course
Plot. They mark the point at which the project began to provide useful
**race-operation decision support**, in addition to preparing data for
scoring.

## 10. 29 September--1 October: the project is organised on GitHub

On 29 September, the Cork Harbour work was organised into the
`Bateleur88/cork-harbour-orc` GitHub repository and shared with Mark.

The purpose was to put the accumulated "Cork Course Card" work into a
logical sequence and make it open to comment, criticism and suggestions.

Pat disclosed the use of AI assistance in development to Mark at this
stage.

On 1 October, Mark reviewed the work and gave feedback.

Organising the work on GitHub moved the collaboration from exchanges of
individual spreadsheets and outputs toward an inspectable repository with
its supporting data.

## 11. 30 September to 5 October: from a pasted leg table toward a richer handoff

Further testing exposed limitations in transferring only a bare table of
leg distances and bearings.

By early October Pat was considering a richer handoff than a bare leg table,
which could include:

-   named mark positions;
-   the ordered sequence of marks;
-   calculated chord distances and true bearings;
-   magnetic/true bearing reference and variation information;
-   authored routing waypoints where a direct chord is not navigable;
-   provenance/version information; and
-   a known geographical anchor for locating an otherwise free-floating
    chain of leg vectors.

(Compare the course record proposed in section 14.)

Pat's Course Plot already used both a committee boat position and a pin
position and derived course geometry from the line, rather than
treating the start as one abstract point.

This period also contributed to work around explicit magnetic/true
bearings in Sail Scoring, tracked in
[sailscoring/sailscoring#660](https://github.com/sailscoring/sailscoring/issues/660).

## 12. 5 October: Cork Harbour as an integration test

By the evening of 5 October, Cork Harbour course data was being
exercised against the live Sail Scoring workflow.

That testing exposed further practical issues, including:

-   [sailscoring/sailscoring#663](https://github.com/sailscoring/sailscoring/issues/663)
    --- previously imported marks whose positions had subsequently
    changed; and
-   [sailscoring/sailscoring#664](https://github.com/sailscoring/sailscoring/issues/664)
    --- a starting-mark name which was not recognised.

These tests reinforced two themes already encountered in the earlier
Course Data Workbook work:

1.  **identity and position are different things** --- the same mark can
    acquire corrected or race-day positions without ceasing to be the
    same object; and
2.  **names alone are not a sufficiently robust identity mechanism**
    where different systems or users may describe the same object
    differently.

At this point the Cork Harbour workflow was functioning not only as a
local solution but also as a practical integration test for developing
Sail Scoring course functionality.

## 13. 6 October 2026: feedback and the duplication concern

On the morning of 6 October, Pat raised the concern directly with Mark
that the two projects appeared to be duplicating some functionality and
suggested discussing the overlap.

Mark reviewed the work and gave feedback.

## 14. `course-days.md`

Mark's public Sail Scoring design document is:

[`docs/design/course-days.md`](https://github.com/sailscoring/sailscoring/blob/main/docs/design/course-days.md)

The developing design document formalises many of the problems encountered during the Cork
Harbour work, including race-day fixes, course recording, start/finish
representation, provenance and the production of a final Course Record.

It also makes the intended product boundary explicit:

> **Sail Scoring keeps the record of what was sailed. It does not help
> run the race.**

This is consistent with the distinction that had emerged through the
practical work:

-   Sail Scoring needs a reliable record of the course actually sailed
    in order to score it;
-   Race Officers may also need tools which help them decide what course
    to set, where to lay or move marks, whether a line is square, and
    how to operate the race;
-   shared representations of marks, courses, passages and routing
    should be reusable rather than independently reinvented.

The design document remains an upstream Sail Scoring design document and
should be treated as such; this repository does not define Sail
Scoring's roadmap.

### What the public design document proposes (status: proposed, October 2026)

The following summarises the public design document
[`docs/design/course-days.md`](https://github.com/sailscoring/sailscoring/blob/main/docs/design/course-days.md)
as published. It is marked as proposed; none of it is recorded here as
agreed or implemented.

-   **The line between scoring and race management.** The document places
    within Sail Scoring anything a score or published result relies on,
    together with the evidence needed to check or dispute it. Things meant
    to influence events on the water are placed outside it.
-   **Under that line**, recording fixes for marks, the committee boat and
    the pin, and checking those fixes, count as evidence for the record.
    Advice to the water, such as re-laying a mark or squaring the line,
    falls outside it.
-   **Recording fixes.** Its roadmap includes fixes on the day's marks,
    each keeping its own position time and accuracy, with rules for which
    fix applies to a start and the scorer able to pin a particular fix.
-   **Checking the day's fixes.** A view plotting one race's fixes, or all
    of a day's, without editing them, with advisory flags that never block
    anything.
-   **A race-officer role.** A role able to read and manage the day's
    courses, with a phone layout for use on the committee boat.
-   **RIB links with no account.** Per-day links for each RIB that can
    expire and be revoked, opening a narrow offline page that saves only
    fresh positions.
-   **Competitor tracks.** A later step, needing a privacy decision first,
    using tracks as evidence which cannot alter a score on its own.
-   **The course record as the handover.** A documented, versioned course
    record format, kept in `course-cards`, as the handover from a course
    day to a scored start, describing one start's race details, marks and
    the fixes they came from, lines, mark sequence, legs and provenance. A
    bare leg table would be a record containing only legs.

## 15. The three-project relationship

By October 2026, the work can usefully be understood as three related
but distinct areas.

### `cork-harbour-orc`

This repository grew from the operational requirements of the RCYC ORC
trial. It contains Cork Harbour-specific data/validation and the
practical tools developed to capture race-day information, visualise the
course and assist the Race Officer.

Its operational side answers questions such as:

> **What should the race team do, and what does the course look like on
> the water?**

### `sailscoring/course-cards`

`course-cards` is the natural home for reusable representations of
course-card knowledge which are not specific to one application's UI:
marks, course definitions and increasingly the shared concepts needed to
represent real navigable passages.

The Cork Harbour work has provided real-world cases against which those
abstractions can be tested.

### `sailscoring/sailscoring`

Sail Scoring owns the scoring workflow and the durable representation of
what was actually sailed.

Its side of the boundary answers:

> **What course was actually sailed, what evidence supports that record,
> and how should it be scored?**

## 16. An iterative field-driven development process

The project has not followed a predetermined product specification. Its
development has repeatedly followed the same pattern:

1.  encounter a real racing/scoring requirement;
2.  build the minimum practical solution;
3.  test it with real Cork Harbour data and race operations;
4.  discover assumptions which do not survive real-world use;
5.  improve the local solution;
6.  share generalisable findings upstream;
7.  test the resulting model again.

This process produced a progression from:

**leg/bearing spreadsheet → Course Data Workbook → RIB Recording Page →
Race Officer Course Plot → richer course handoff**

while, in parallel, relevant general problems were being discussed and
addressed in `course-cards` and Sail Scoring.

The resulting overlap is therefore not accidental duplication between
independently conceived products. It arose because the projects were
progressively addressing different parts of the same real-world
course-recording and scoring workflow.

## 17. Position at 6 October 2026

As of 6 October 2026:

-   the existing Cork Harbour tools remain working operational tools and
    should not be removed merely because equivalent or overlapping
    functionality is proposed upstream;
-   generic course-data concepts should, where appropriate, be shared
    through `course-cards` rather than maintained as incompatible
    parallel models;
-   the Course Days/Course Record work proposed in Sail Scoring's public
    design document `course-days.md` (status: proposed, not agreed or
    implemented) provides a natural destination for the durable scoring
    record;
-   the Cork Harbour project has a distinct continuing role in local
    navigation, validation, course visualisation and Race Officer
    operational decision support; and
-   a documented, versioned Course Record, as proposed in the same public
    design document, provides a promising future boundary between
    race-operation tools and scoring systems.

The next development roadmap should be derived from this history while
respecting the independent maintenance and contribution processes of
both upstream Sail Scoring repositories.

## 18. Intended operational workflow (stated 7 October 2026)

This section records the intended workflow as stated on 7 October 2026. It is not a statement of what the code currently does.

1. **Laid Mark Record page.** The RIB records the physical laid marks on the day, ideally in the correct Race 1, 2, 3 sequence. Mark roles include Committee Boat, Windward, Leeward, Start Pin, Gybe and Finish Pin. Each fix is saved on the server in JSON format. Several marks with the same name can be saved; the timestamp is what distinguishes them, which allows for marks repositioned because of wind changes.

2. **Course Plot page.** This is the Race Officer's tool page. It starts by assigning a Series Name to the course. Tapping Get Latest Marks reads the exact as-recorded marks from the saved JSON file. It never edits that source data.

3. **Derived course.** The page builds an initial course plot from the mark names and recorded times, using the start time entered for each race and the classes starting. No separate original course is saved (decided 7 October 2026): the recorded marks are the original, and any course must be reproducible from them plus the rules and decisions.

4. **Race Officer tools.** Entering wind direction, and optionally wind speed, provides the initial tools, such as line squareness and whether the windward mark is a true beat.

5. **Check recorded marks.** Where automatic detection has produced an inaccurate as-sailed course plot, the Race Officer selects which of the recorded marks are used.

6. **Saved course.** The revised course is saved to the server as a complete course in its own record, derived from the recorded marks plus the accept, use-as and not-to-be-used decisions. The intended way of storing it is described under "Intended saved-course workflow" below.

7. **Handoff to Sail Scoring.** The saved course is what the Course Plot page hands to Sail Scoring as the As Sailed Course, for use in the scoring sequence.

### Intended saved-course workflow (to be built and tested)

This is the intended workflow, stated on 7 October 2026. It is not decided, and it becomes the workflow only after it has been built and has passed testing.

1. **Draft.** The Race Officer sets up the course: Race N, Start N, start time, classes starting, and the intended course by card import or by tapping chips. This is working state that can be replaced; only a short undo window is needed.
2. **Decisions.** This stage begins when the Race Officer starts "Check recorded marks". The Race Officer checks that the plotted course is what was created and is not distorted by a bad mark position or an unrecognised start line, and selects, for example, a moved weather mark for the second leg. Each edit records its own decision with its reason, such as "Weather Mark fix 2 used for 2nd beat due to wind shift". Decisions are append-only.
3. **Accepted course.** When the course reflects the race as sailed, it becomes the accepted course, stored as a complete record that names the fixes and decisions it came from. It is not replaced.

### Invariants

- The recorded marks are never edited or overwritten; new information or a flag may be added.
- A saved course is reproducible from the recorded marks plus decisions.
- Decisions are append-only.
- A saved course is always derived, never hand-edited.
- What is handed to scoring is the saved course.

### Terminology

This project's names are updated course and As Sailed Course; "original recorded course" was retired on 7 October 2026. The earlier term "Race Day Course Record" in this history refers to the course the Course Plot builds from stored observations. "Course Record" with capitals refers to the versioned format proposed in Sail Scoring's `course-days.md`. Use one vocabulary before any export to that format.

## 19. 7 and 8 October 2026: from a decisions layer to as-sailed course repair

On 7 October 2026 a read-only Phase 1 audit (`docs/audit/PHASE1_AUDIT.md`, at commit `f30882f`) compared the code with the workflow in section 18. Among other things, it found that fixes can still be deleted or re-posted, that automatic line ends and the laid-mark choice are re-resolved on each render, and that no page wrote decisions. The same day Pat decided there is no separate original course: the recorded marks are the primary source data and are never overwritten.

From 6 to 8 October a decisions write path was built on the RO page (PAGE_VERSION 2026-10-06.9 to .19): a Review name and RO key (`73e8633`), decisions shown in Check recorded marks (`56b7750`, `f30882f`), Accept, Do not use and Undo with a legs warning (`3579dee`), Use as for course rows (`26f0570`), and the fix detail and review history under the sketch (`0cd524b`, `4313903`). The server side came in `d6d24a8`. It was tested on the parallel test copy and in scratch only.

On 8 October Pat took the review decisions out of the page as an unnecessary complication. In their place the page repairs the as-sailed course directly from the recorded fixes, which stay untouched. Any recorded fix of the day can become a chip of a race and a course row, and the picks are saved with the race. Line ends can be chosen from any race's fixes. The chart draws what the sketch draws. Check recorded marks shows the as-sailed course over the recorded lines (PAGE_VERSION .20 to .24, commit `dd86687`). The principle recorded with it: the page must work for any race day; any mark can be set from any recorded fix without changing the fix; a saved course should record every choice; the default view is small. `marks.php` keeps the decisions endpoint and the RO key, unused. The earlier commits stay in the history under the tag `experiment/decisions-review` (`docs/experimental/decisions-and-review/`).

This section supersedes these points of section 18: step 6 ("derived from the recorded marks plus the accept, use-as and not-to-be-used decisions"), the Decisions stage of the intended saved-course workflow, and the invariants that a saved course is reproducible from the recorded marks plus decisions and is always derived, never hand-edited. Section 18 stays as the record of what was stated on 7 October.

Not verified: none of this has been used in a live race. The laid-mark choice and automatic line ends are still not saved with the course.

## 20. 9 October 2026: the RO page and marks.php uploaded

On 9 October 2026 Pat uploaded `marks.php` (the version at `318d09b`) and then the RO page at PAGE_VERSION 2026-10-06.24 (commit `dd86687`, unchanged at `318d09b`) to the live paths by hand, after taking dated backups and re-running the tests on PHP 8.4.26 and 5.5.38. Each file was re-downloaded and its SHA-256 checked. The live page loaded the 4 October day, and was opened and working on a PC and a tablet (Pat). The page replaced PAGE_VERSION 2026-10-06.7 (`2aec398`), which had been uploaded as a renamed copy of `course_v8.html` by Pat's recollection; the live file's bytes are identical to `course_v8.html` at `2aec398`. `marks.php` replaced the version from `4a66559`. The live host runs PHP 5.5.38 on Apache, and a request for `/marks/data/`, and for a non-existent file under it, is refused with 403.

Not verified: no race has used the new page. No course has been saved on the live server since the upload, so the course history has not yet been written there. The live course records for 4 October are still those the .7 page saved; the as-sailed repair of Race 1 exists only on the test copy.

Later on 9 October 2026 Pat redid the Race 1 repair of 4 October on the live page, on the PC with PAGE_VERSION 2026-10-06.24, as on the test copy: the R3 14:39 Leeward in all three starts, the Start Pin from Race 2 and the Finish Pin from Race 2. It was the first known live course save since the upload, and the course history write succeeded: the FileZilla listing of `/marks/data/` showed `courses-2026-10-04.json` (3,306 bytes) and a new `courses-history-2026-10-04.json` (2,934 bytes), both modified 09/10/2026 09:23:57 (FileZilla listing time), and a second device that loaded 4 October showed the repair. The previous paragraph's statements that no course had been saved on live, that the history file had not been written and that the 4 October records were the .7 page's describe the state before this repair.

Correction (9 October 2026): the live Race 1 repair uses the Start Pin R1 12:32, a Race 1 fix chosen by Pat, and the finish set to Start line, the same as the test copy. The paragraph above wrongly says the Start Pin and Finish Pin were taken from Race 2.

## 21. 9 October 2026: course saves made visible (PAGE_VERSION 2026-10-06.25)

Reading the page after the Race 1 repair showed that course saves were silent: a refused save was caught and never shown, loading a day could send saves without an edit, and a change of day deleted the old day's unsent edits without checking that they had been sent (`STATUS.md` A33, A34, A35). PAGE_VERSION 2026-10-06.25 (commit `0db8b42`, static guards `6ca1ef3`) shows every save result in Setup and in the Race view, says when a load leads to a save, and stops a change of day while anything is unsent, with "Change day anyway" only for records the server refused or failed, or records made for a third day. All 34 manual tests passed on the test copy. Later the same day Pat uploaded it as `/course/index.html` after taking dated backups; `marks.php` was not changed. It was opened on the PC and the tablet with no page script errors; no day was loaded for the check.

Not verified: no race has used .25, and no course has been saved with it on the live server. Known limits are recorded in `STATUS.md` A34, A35 and A36.

## 22. 10 October 2026: a constructed-course hand-off to Sail Scoring (PAGE_VERSION 2026-10-06.26)

On 10 October 2026 two sample documents in Sail Scoring's ORC constructed course format, made from the 27 September Race 1 course, were pasted into Sail Scoring's Add start dialog and accepted (`docs/orc-constructed-course-tests/`). For each leg the format carries its distance, magnetic course and wind, and an anchor where the first leg starts: the known geographical anchor that section 11 lists among the richer hand-off contents. It is Sail Scoring's format, not the Course Record of section 14 (`STATUS.md` A37; C5 and ROADMAP Phase 7 apply to the Course Record only).

The same day the Course Plot gained "Copy for Sail Scoring" (page commit `3ece041`, static guards `c06c18b`), beside the "Copy legs for SailScoring" block, which is unchanged. It copies the selected race and start with the leg table's own figures, and names in the document any leg left out or measured from a stand-in. On the test copy with the 27 September day, Race 1 Start 1 matched the complete sample in every field apart from the anchor (about 0.6 m off, because the sample's positions were rounded) and the new series field. The page's own output was then accepted by Sail Scoring (six legs, 4.54 nm).

Later on 10 October 2026 Pat uploaded it as `/course/index.html` after taking dated backups and re-running the tests; `marks.php` was not changed. Re-downloaded, the hash matched. It was opened on the PC and the tablet, showing PAGE_VERSION .26 and the new block, with no page script errors in the PC's console; no day was loaded for the check.

Not verified: no race has used .26, and "Copy for Sail Scoring" has not yet been used on the live page. The sample showed that Sail Scoring uses the document's name as the race title, so warnings in the name are a stopgap until a note field exists.

## 23. 11 and 12 October 2026: typed and pasted positions, and the queue (PAGE_VERSION 2026-10-06.29)

On Sunday 11 October 2026 the Race Officer's courses were built on the day from fixed marks, not numbered card courses: "White Sail: E4 (P), 10 (P), E4 (P), 10 (P), Finish" and "Spinnaker (all classes): 3 (P), 12 (P), 3 (P), 12 (P), 3 (P), 12 (P), Finish", starting in the vicinity of No.8. The RIBs recorded one Start Pin and one Finish Pin and no committee boat. The Course Plot offered no way to bring E4, No.10, No.3 or No.12 into a race's chips, so no course could be built on the day and there was nothing to copy for Sail Scoring. After the race a position copied from the course card was refused by both "Read marks from a WhatsApp message" and "Add a mark by typing its position", because the card writes minutes with a prime (′) and the page accepted only a plain apostrophe. A course built later from positions pasted in the backup format existed on one device only, and after Clear everything its saved rows would have been hidden with no warning.

Reading the code showed four related faults on the RO page: the minutes mark; pasted positions kept on the device only and given ids a later server fix could take over; a fix the server refuses staying first in the device's queue and blocking every later fix, with a message about the committee boat whatever the fix was; and a course row whose mark could not be found left out of the course and its legs with no warning, so the remaining marks were quietly joined. The RIB page's queue has the same blocking fault; it is the proven offline code used on the water and was left unchanged (`STATUS.md` A39).

PAGE_VERSION 2026-10-06.27 to .29 (commits `49af982`, `7674d71`, `b870d91`, `0cb5563`; `STATUS.md` A38) changed only the RO page. The minutes mark may be ', ′ or ’. A card row pasted into the reader is named by its short name (E4, No.10). Pasted positions are labelled "pasted position · this device only", get an id no server fix can have, and the reader says they stay on the device. The queue sends each fix with a 20 s limit; no signal, no reply, a key problem or a server error stop it with every fix kept in order; a refusal or a full day moves that fix to a "Not sent" list on the device, with Send again and Remove from this device, and the queue carries on; every message says what the fix is and what happened to it, including the message under Get latest marks. A typed or pasted position more than 8 nm from the map centre (51.82 N, 8.27 W; every mark in the workbook is within 7 nm of it) is flagged, never refused. Check recorded marks and the line under Get latest marks count recorded fixes apart from typed and pasted positions. Clear everything also warns about "Not sent" fixes and pasted positions. A course row whose mark cannot be found is shown as "Mark missing", its legs are not measured, and the leg table, the WhatsApp text and Copy for Sail Scoring say so. Copy for Sail Scoring's name now gives the race name first, then the warnings in short form, one count of the legs not measured with the reasons ("Race 1, Start 5 - INCOMPLETE - 3 legs not measured (mark missing: No.12; start line not recorded)"); the full warnings stay beside the button.

Pat made these decisions while testing: in a combined warning each leg is counted once and the reasons are listed together; a row saved from a pasted position may match a pasted position with the same race and name on another device, but never a fix on the server; and .29 is released without a warning when the race day is changed on a device holding pasted positions, which loses them (`STATUS.md` A44). Typed positions are still saved on the server as recorded fixes, labelled as typed (`STATUS.md` A2, A7).

Pat tested 2026-10-06.27-test and then the .29 retest on the test copy on 12 October 2026, with the 11 October day, on a PC and an Android tablet: every item on the test sheet passed. The 11 October rows saved from pasted positions on the day, hidden on .26, showed as "Mark missing". The 27 September Race 1 Start 1 output and all three 4 October Race 1 starts were identical to .26. Later on 12 October 2026 Pat uploaded .29 as `/course/index.html` after taking dated backups and re-running the tests; `marks.php` was not changed. Re-downloaded, the hash matched. It was opened on the PC and the tablet, showing PAGE_VERSION .29, with no page script errors; no day was loaded for the check.

Not verified: no race has used .29. The fixed marks themselves, the course message reader, routing waypoints and one-end lines, which 11 October also called for, are later steps (`STATUS.md`, A40 to A43 when approved).

## 24. 12 October 2026: fixed marks, step 2 (PAGE_VERSION 2026-10-06.30-test)

After the 11 October race (section 23), step 2 of the fixed-mark work gave the Course Plot every mark in the workbook (`STATUS.md` A40), with far typed or pasted positions kept out of the plots (A45). Pat decided the following on 12 October 2026, reviewing two proposals.

**The workbook (v3.20).** The Marks sheet listed C2A and C1A twice: the second rows (71 and 72, "Owenboy River Approach") were removed and the first (29 and 32) kept; the sentence "reference mark only - not used in current 2026 course routing" went with them and was not copied anywhere. Neither mark is used by any card route, card course or other sheet. Nothing else changed: v3.20 (`RCYC_Cork_Harbour_ORC_MASTER_v3_20_DUPLICATES_REMOVED.xlsx`, SHA-256 `9fdaaf5b50ab9f6df3e6df047dc1b8a7f68361cc1298fb75356822d4190097aa`) was made from v3.19 with `xlsx_edit.py`, which now renumbers an empty one-line row instead of refusing the sheet; `cell_diff` showed only the new Read Me record, the audit passed all 16 checks with the counts unchanged, and Pat opened it in Excel with no repair dialog. There is no Aliases column.

**The snapshot.** `make_snapshot.py` now carries every mark with a position in the Marks sheet (63: the fixed marks, the 8 routing waypoints, Grassy Mid and the laid marks Curlane, Dutchman and White Bay), each with the heading it goes under. Position Source, Source URL and Verification / Use stay in the workbook only. The build refuses a mark name that appears twice, two names that are the same once capitals, spaces and punctuation are ignored, and a name the page would read as a committee boat, pin or finish.

**Reversed routes.** A route that works one way also works in reverse. Of the workbook's 177 authored routes, 92 are authored both ways (each pair the exact mirror of the other, and each kept as authored) and 85 one way only. For each of the 85 the snapshot build adds the exact reverse, marked reversed: the same points in reverse order and the same distances, each bearing worked out from the positions with Vincenty, as the workbook's own are, not the forward bearing plus 180° (they differ by at most 0.04°). The page never reverses or builds a route itself. The eight passages that turn at W2 are reversed like the rest, with no side for W2, as the forward routes have none. The three Curlane high-water routes (Curlane to No.10, No.12 and No.5) are reversed too: the restriction is published on the course card and is the RO's responsibility. In the leg table a reversed route reads "card route reversed, via <RW>", or "card route reversed" when direct. No card course, no leg of 27 September or 4 October, and no saved course in the test data used a pair authored one way in the other direction, so no existing figure changes.

**The Fixed marks list.** A "Fixed marks" fold in section 3, closed by default, with one button per mark under headings from the workbook Type: the Course Card headings first in sheet order (Starboard lateral, Port lateral, Fixed light, Permanently moored race mark, North cardinal, Start/finish modelling point), then "Club laid mark", then one "Routing waypoints" heading for all eight (RW_West_of_Refinery's Type is "Routing mark"). One tap adds the mark to the race being built and a course row with no side at the end of the course; a second rounding is tapped from its chip. A mark is added to the device only when tapped (or imported, or named by a saved row), never every mark at once, because the magnetic variation is worked out from the marks loaded.

**Labels.** Fixed marks and Grassy Mid read "Course Card" on chips and rows ("E4 · Course Card"), with the side button; Grassy Mid keeps its card warning ("Midpoint standing in for the Grassy Walk line, not a mark"). Laid marks read "laid mark" and follow the existing RIB-fix rules unchanged (A9, A10). Marks of an imported card course get the same treatment, with figures unchanged. The line "position from the course card, not a fix recorded today", naming the course's Course Card marks, appears in exactly two places: the leg table and the note above the SailScoring leg table. Card marks never count as recorded fixes. A saved row naming a card mark is rebuilt from the embedded card on every device; a name not in the card shows "Mark missing".

**Routing waypoints chosen by the RO.** Routing waypoints exist only to keep boats off the shore and shallows, and to give the correct as-sailed length for ORC legs. A tapped one goes to the end of the course; its row reads "routing waypoint" and has no side button, but ↑, ↓ and ✕ (other rows keep ↑ and ✕), so the RO moves it to its place in the sequence or removes it, and the leg then runs between the marks either side. Moving a waypoint's position is not part of this step. In the leg table a leg through RO-chosen waypoints is one leg made of its physical legs, as a card passage shows, reading "routed via <RW> (RO-chosen)"; the SailScoring lines and Copy for Sail Scoring give one entry per physical leg. A physical leg that is exactly a chord the workbook tested takes the workbook's distance and bearing and carries no label; any other is measured straight and labelled "not depth-checked". Check recorded marks neither lists nor counts routing waypoints; the as-sailed course is drawn through them with a small waypoint dot.

**Straight legs and "not depth-checked".** Where the snapshot has no route between two points of a course (counting the reversed routes), the leg is measured straight, never refused, and labelled exactly "not depth-checked" when it touches a Course Card mark: on 11 October's courses, E4 to No.10 (1.89 nm, 347°M) and No.3 to No.12 (1.87 nm, 351°M), and the legs to and from a recorded start or finish line. Legs between laid or recorded marks carry no label: deep-water laid courses are assumed safe. Legs to or from an RO-chosen waypoint follow the tested-chord rule above.

**Check recorded marks.** The Course Card marks the RO has put in a course of the race shown are drawn (hollow, dashed, in the sea colour), listed as "Course Card" and counted under "other marks"; they are never checked as fixes. A typed or pasted position more than 8 nm from the map centre (51.82 N, 8.27 W) is left out of the zoom of both views and not drawn, named in a line under the view ("1 position more than 8 nm away is not drawn: FarT (614 nm), see the list below"), and stays in the list with its warning and in the count to check (A45). In the course sketch and chart a leg to or from it is drawn to the edge of the frame with an arrow and "FarT, 614 nm, off the plot"; the leg table, the WhatsApp text and Copy for Sail Scoring keep the real figures. Recorded fixes are always drawn, however far away.

**The WhatsApp text.** For every course it is now a clean course list for competitors: the heading, the race and start, the course line, the numbered marks, each leg (mark to mark, bearing °M and °T, distance, TWA), the total and the positions. Left out: the start line line (length, bearing, off square, favoured end), the windward mark squaring line, the wind line, every route note ("card route", "card route reversed", "routed via"), routing waypoints (not in the mark list, the legs or the positions; a leg through one reads mark to mark with its whole distance), the card-position line and the "not depth-checked" labels. All of these stay on the page. The A38 warnings in the text (mark missing, legs not measured) are unchanged.

**Deferred.** Aliases (other names for a mark, such as "10" for No.10 or "Chicago Knoll" for E1) are deferred to the RO's course message reader (A43), with the approved and refused names kept for that step. Reading a pasted line that names a card mark as that card mark was dropped: "Read marks from a WhatsApp message" works exactly as on .29. Withdrawing a wrong typed position is a later step (A46).

Built as PAGE_VERSION 2026-10-06.30 (`9759ab1`) and first tested on a local copy of the page (no server, no day loaded) by Claude Code.

**Pat's test of 2026-10-06.30-test (12 October 2026).** On `/course-test/`, with the test copies of 27 September, 4, 11 and 13 October, Pat tested and passed: the Fixed marks list and its labels; the White Sail and Spinnaker figures and "not depth-checked" labels (11 and 13 October); the side buttons; Course Card marks in Check recorded marks; Curlane as a laid mark; the reversed route No.14 to E2 ("card route reversed, via RW_Fort_Davis", 2.58 nm, the SailScoring lines the exact mirror); RW_Fort_Davis chosen by the RO between E2 and No.14 (one leg of 2 physical legs, no label, figures identical to the card route); the untested chord via RW_Fort_Davis_South ("not depth-checked"); Grassy Mid with its warning; FarT off the plot and in the list; the clean WhatsApp text with no routing waypoint; a reload and the tablet; the paste box as on .29; the 27 September and 4 October regression; and every stored key of the test page beginning "test-". Two tests could not be run because no real data exists for them: a recorded fix more than 8 nm away (the 8 nm rule applies to typed and pasted positions only, A38), and a saved row naming a card mark not in the card.

**Five fixes decided by Pat after that test (PAGE_VERSION 2026-10-06.31).**

1. A Course Card mark tapped in one race is not carried into a later race's chips ("from Race 1"): the RO taps it from the Fixed marks list in that race. Recorded fixes and typed positions are carried as before. Laid marks and routing waypoints, card marks too, were also carried in .30 and still are: reported to Pat for a decision, not changed.
2. Under All races in Check recorded marks, every race with anything drawn has its switch, including a race whose only items are Course Card marks. In .30, 13 October (Course Card marks in Races 1 and 2, no fixes) showed no switches, and 11 October only R1.
3. The paste box ("Read marks from a WhatsApp message") and the typing box ("Add a mark by typing its position") refuse a name that is a card mark's own name (a fixed mark, Grassy Mid or a routing waypoint), comparing names as the page does for laid marks, ignoring capitals, spaces and punctuation, with no aliases (A43). The refusal stores nothing and reads "E4 is on the course card: tap it under Fixed marks. If the buoy has moved, give it a different name, such as E4 moved." Laid marks are not refused and behave as before. No typed position in the test data, and no recorded fix, has a card mark's name (11 October's typed positions are T1, T2, FarT, A1 to A4, NR1, M1 and Q1); the refusal applies only to new entries, so stored data is unchanged and shown as before.
4. A routing waypoint with nothing on one side (the first row with no start line, or the last row with no finish point) shows on its row "routing waypoint must sit between two marks: move it with ↑" (or "↓" when it is first); no leg is measured to or from it; it is left out of the WhatsApp text completely; and Copy for Sail Scoring says INCOMPLETE until it is moved. With a start line or finish point, a waypoint in the first or last row sits between the line and a mark, as before.
5. The laid-mark notice "Course x → y nm" includes any detour through an RO-chosen routing waypoint, as every other figure does.

**The WhatsApp heading's date (checked, not changed).** The heading's date is the page's `S.date`, which is set only when a loaded day has at least one fix (or from a pasted message's heading), and is never cleared when another day is loaded; only Clear everything clears it. So a day with no fixes (13 October in the test data) keeps whatever date the device last had: none on a cleared device ("*Autumn League*", as Pat saw), but the previous day's date on a device that loaded another day first (Claude Code's test browser, having loaded 11 October, showed "*Autumn League – Sun 11 Oct 2026*" for 13 October). PAGE_VERSION 2026-10-06.29 has the same code. Left for Pat to decide.

**Open question for step 3 (A41).** A routing waypoint chosen by the RO inside a pair the card already routes changes the leg's label from "card route via …" to "routed via … (RO-chosen)", though the route is identical: with RW_Temblebreedy_Pier and RW_Rams_Head placed before E4 in card course 11, the first leg reads "routed via RW_Temblebreedy_Pier → RW_Rams_Head (RO-chosen)" with the card's own figures (1.17 nm, 105°M). Not decided.

PAGE_VERSION 2026-10-06.31 was tested by Claude Code against the test data on `/course-test/`, running the built test page on the test site's own address without uploading it: all 28 saved courses of 27 September, 4, 11 and 13 October were identical to .30 in every figure and every output (leg table, SailScoring lines and note, WhatsApp text, Copy for Sail Scoring); 13 and 11 October showed the R1 and R2 switches; Race 2 showed no Course Card chip from Race 1; the refusals stored nothing. Fixes 4 and 5 were tested on a local copy with no day loaded, with real marks and waypoints. Pat's retest of .31 is to follow. Not verified: no race has used it, and it has not been uploaded to the live paths.

------------------------------------------------------------------------

## Related repositories and issues

-   `Bateleur88/cork-harbour-orc`
-   `sailscoring/course-cards`
-   `sailscoring/sailscoring`
-   `course-cards` issues #14, #15, #16, #17, #18 and #19
-   `sailscoring` issues #660, #663 and #664
-   Sail Scoring `docs/design/course-days.md`
-   Sail Scoring `CONTRIBUTING.md`
