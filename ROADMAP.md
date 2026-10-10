# ROADMAP

Status: PUBLIC DRAFT, 7 October 2026, revised 8 October 2026; Phase 7 note added 10 October 2026. Redacted from a private working draft: private correspondence is not summarised here. For discussion only; nothing here is agreed with anyone outside this project. The Phase 1 audit is complete (`docs/audit/PHASE1_AUDIT.md`). Nothing is a commitment until Decision 1 has been settled with the Sail Scoring maintainer.

Sources for this revision, all read on 7 October 2026:

- `Bateleur88/cork-harbour-orc`: README and `PROJECT_HISTORY.md` (reconstructed by Pat from his records; events before 29 September 2026 and those involving external systems cannot be verified from the repository)
- `sailscoring/sailscoring`: `CONTRIBUTING.md`, `CLAUDE.md`, README, `docs/design/course-days.md` (status: proposed, October 2026)
- `sailscoring/course-cards`: README and `docs/format.md` (format version 2)
- `docs/audit/PHASE1_AUDIT.md`: the Phase 1 read-only audit of `cork-harbour-orc` at commit `f30882f` (7 October 2026). Its findings supersede any earlier statement here about the code.

Statements about the current implementation come from the READMEs and `PROJECT_HISTORY.md`. The Phase 1 audit (`docs/audit/PHASE1_AUDIT.md`) has since verified or corrected them against the code.

**Scope of this roadmap.** It is this project's roadmap only. As `PROJECT_HISTORY.md` puts it, this repository does not define Sail Scoring's roadmap, and the upstream maintenance and contribution processes of `sailscoring/sailscoring` and `sailscoring/course-cards` must be respected. Everything in Mark McLoughlin's `course-days.md` is a proposal (status: proposed, October 2026), not an agreed or implemented plan.

**Terminology.** "Course Record" in this document means Mark's proposed versioned format. `PROJECT_HISTORY.md` uses "Race Day Course Record" for what the Course Plot builds from stored observations. Keep the two names distinct to avoid confusion.

---

## 1. Purpose

The project began as a way to produce sufficiently accurate constructed-course information for ORC scoring in the RCYC Autumn League 2026. It has grown into a race-operations methodology:

```
RIB / Committee Boat
  -> GPS observations
  -> persistent race-day evidence
  -> RO review / resolution
  -> Course Plot
  -> actual sailed-course geometry
  -> course history / audit trail
  -> scoring handoff
```

Much of this is not specific to Cork or to ORC. The next phase is mostly **separation, formalisation and interoperability**, not new construction.

**Direction:** keep one codebase and one methodology, with separate regional deployments and data (the "common methodology and workflow, separate regional data" principle in `PROJECT_HISTORY.md`). Separate the common application from local Cork knowledge, make Cork "Venue 1", prove reuse with a second venue (DBSC), and interoperate with Sail Scoring through the shared formats that Mark McLoughlin maintains in `course-cards`.

```
FIELD-PROVEN CORK SYSTEM
  -> common application + local venue knowledge (a course-cards data set + local config)
       -> Cork Venue | Dublin Venue
  -> common resolved course
  -> Course Record (to be defined in course-cards)
  -> Sail Scoring
```

---

## 1a. Current status (as of 7 October 2026)

This separates what is field-proven from what is documented but not re-tested live, so that "preserve Cork behaviour" (guardrails 1 and 11) does not lock in behaviour that is wrong. The Phase 1 audit has since confirmed or corrected these lines where it says so.

### Field-proven, as stated by Pat (preserve)
- RIB recorder offline queue and service-worker behaviour: stated by Pat as tested operationally on the water. `PROJECT_HISTORY.md` does not record which race day, and the repository log shows the service worker was added on 3 October (commit `981026f`), so the race day is not established.
- The end-to-end workflow was used on the first day of the RCYC Autumn League on 27 September 2026: positions recorded, retained on the server, Course Plot built the course, ORC leg distances and bearings were calculated and transferred into Sail Scoring by hand (`PROJECT_HISTORY.md` section 7).
- The Course Plot derives geometry from a committee boat position and a pin position, not a single abstract start point (section 11).

### Documented as implemented; live status since 4 October unconfirmed
Commit references are from `PROJECT_HISTORY.md`; the others are README-only.

- Multiple observations of a mark retained rather than overwritten. Each fix keeps the position's own time and, since 5 October, the tap time (commit `4a66559`), so its age is measurable.
- Automatic fix choice never picks a fix recorded after the start (1 October, commit `8d36c09`). **Corrected by the audit:** this holds for committee boat and Start Pin only. Laid card marks take the latest exact-name fix of the race with no start-time test, and the Finish Pin takes the latest with no time limit.
- A dedicated "Copy legs for SailScoring" block (30 September, commit `98f9713`).
- RIB page accepts only a fresh position: a position more than 5 s older than the tap is ignored; at 5 m accuracy or better it saves at once, otherwise the best fresh one is saved after 10 s; nothing is saved after 20 s. This responds to the 4 October finding that half the fixes were 24 s to 12.5 minutes old (5 October, commit `ce3e7e4`).
- Race + start structure, with course history kept per race and start (first version of the day plus the last 5 replaced versions, size-capped).
- Append-only decisions file (use as, do not use, accept, revoke), written only with a separate RO key, read with the race key. **Corrected by the audit:** verified on the server (test t15), but no page writes decisions yet; the RO page only reads and displays them. **Since 8 October 2026:** a page write path was built (PAGE_VERSION .13 to .19) and taken out again (.20); no page reads or writes decisions. The endpoint and RO key stay in `marks.php`, unused (tag `experiment/decisions-review`).
- RO page "Check recorded marks" (5 October, commit `01329fc`): a read-only plot of every fix, with computed start lines, finish lines and the leg between the latest Windward and Leeward, candidates shown but never joined by default, and advisory flags that never block (stale position, pin close to a mark, line far from square, mark far from the same mark in another race, pin ordering, no committee boat).
- Server-side tests: `tests/test_marks.py` (runs `marks.php` as real CGI requests, on PHP 8.4 and PHP 5.5) and `tests/test_build_test.py`. There are no browser-workflow tests.

### Open issues logged after the live test of Sunday 4 October 2026 (Autumn League)
Variable wind meant marks were moved during racing. `PROJECT_HISTORY.md` section 8 records the underlying problems: delays between the recording action and the position ultimately received, marks recorded in wrong positions, several observations for one named mark, the need to tell races apart, and the need to decide which observation to use for a race. The items below were logged separately.

- 16 marks recorded but not visible on the RO page; the automatic system did not show what had been recorded.
- No start line generated, so Race 1 failed to build (intended: about one third of the way up the first leeward-windward leg).
- Race 1 no start line; Race 2 moderately believable; Race 3 clearly wrong.
- The "All races" check sketch was unusable.
- Unknown from the day's data: whether a start pin was recorded, and who laid which mark. RIB drivers may not remember where marks were laid.

Where the README and `PROJECT_HISTORY.md` say each problem is addressed. On 7 October Pat reported problems 1 to 3 completed and problem 4 in progress. "Completed" here means built and tested on the pages; none has yet been confirmed in a live race. He also reported that the start line fix and problems 5 to 8 are part of the work in progress covered by the RO / Scorer decisions process.

| 4 October problem | Addressed by (per README / history) | Status (Pat, 7 Oct) |
|---|---|---|
| Delay between tapping Record and the position received; stale fixes (half were 24 s to 12.5 min old) | Tap time stored beside position time (`4a66559`); only a fresh position is saved (`ce3e7e4`) | Completed |
| Marks recorded in wrong positions | "Check recorded marks" plot with advisory flags (`01329fc`) | Completed |
| 16 marks recorded but not visible on the RO page | "Check recorded marks": plot, per-fix details, list, All-races chips | Completed |
| Several observations of one named mark as marks moved; deciding which to use | Observations retained, never overwritten; every fix plotted, latest joined; automatic choice never picks a fix after the start (`8d36c09`); append-only decisions (use as, do not use, accept, revoke) | In progress (the decisions layer has no commit cited; tested in `test_marks.py`; ties to the RO validation step in section 1a) |
| Distinguishing races and starts | Race + start structure; per-race and per-start lines; carried-forward marks labelled | In progress (RO / Scorer decisions process) |
| No start line generated (Race 1 failed to build) | Start line joins the latest committee boat and the latest Start Pin at or before the start time; later fixes shown as candidates; no line if no start time is set | In progress (RO / Scorer decisions process); whether a pin was recorded on the day is unknown |
| Race 3 clearly wrong; "All races" sketch unusable | All-races view with race chips and labelled fixes | In progress (RO / Scorer decisions process) |
| Unknown who laid which mark; RIB drivers cannot recall | Recorder name and lettered phone on every fix; re-record request buttons | In progress (RO / Scorer decisions process) |

Since 8 October 2026 the RO / Scorer decisions process is replaced by the as-sailed course repair; current state in `STATUS.md` L4 to L8.

### Phase 1 audit findings (7 October 2026, commit `f30882f`)
- Server tests pass on PHP 8.4.26 and PHP 5.5.38; the workbook audit passes 16 of 16 with the SHA-256 the README gives. No JavaScript in either page is tested.
- **Intended workflow versus built:** see the table in section 1b. In short, the course is not derived and stored as described (see the design decisions); the leg table comes from the page's live state, and legs are never stored.
- **Stored courses can change later:** automatic line ends (`auto`) and laid-mark choices are re-resolved each time the page renders, and the laid-mark choice is kept on the phone only, so a saved course can give different legs if fixes are later added, moved or deleted.
- **Fixes can be edited:** a fix can be deleted from the RIB page, and re-posted (rewritten) from the RO page's "Fix recorded under the wrong race?" move.
- `varW()` (magnetic variation) uses an Irish-fitted formula and today's date, not the race date.

### In progress
- RO page as-sailed course repair per race (replacing the RO / Scorer decisions process, withdrawn 8 October 2026): any recorded fix of the day can be used for a course row (picked chips) or a line end, without changing the fix, and those choices are saved with the course (`STATUS.md` C8).
- Tap-to-use applies to the selected start only, because starts within a race can have different layouts.
- Work on the RIB and RO pages is done through Claude Code, using prompts written in chat.

### Relationship to this roadmap
- The RO page work is the practical start of observations -> choices -> course -> history, and continues independently of the roadmap phases.
- The Phase 1 audit makes no code changes and should run alongside it.
- Proven offline behaviour and unproven course-building behaviour should be tracked separately when Cork is extracted as Venue 1.

---

## 1b. Intended workflow (as stated by Pat, 7 October 2026)

This is the intended operational workflow. The Phase 1 audit has checked the code against it (results below). Terms are Pat's.

1. **Laid Mark Record page** (RIB). Records the physical laid marks on the day, ideally in the correct Race 1, 2, 3 sequence. Mark roles include Committee Boat (CB), Windward, Leeward, Start Pin, Gybe and Finish Pin. Every fix is saved on the server as JSON. Several marks with the same name can be saved; the timestamp tells them apart, which allows for marks repositioned after wind changes.
2. **Course Plot page** (the RO's tool page). It starts by assigning a **Series Name** to the course. **Get Latest Marks** then reads the exact "as recorded" marks from the saved JSON. It never edits that source data.
3. **Derived course.** The page builds a first course plot from mark names and recorded times, using the start time and starting classes entered for each race. (Decided 7 October 2026: no separate original course is saved. The recorded marks are the original, and any course must be reproducible from them plus the rules and decisions.)
4. **RO tools.** Entering wind direction, and optionally wind speed, gives initial tools such as line squareness and whether the windward mark is a true beat.
5. **Check recorded marks.** Where automatic detection has produced an inaccurate "as sailed" plot, the RO selects which of the recorded marks are used.
6. **Saved course.** The revised course is saved to the server as a complete course in its own record, built from the recorded marks plus the RO's choices (course rows, picked chips, line ends; `STATUS.md` C8). The intended storage workflow (Draft, Decisions, Accepted) is described below and is not yet decided (`STATUS.md` A4).
7. **Handoff.** The saved course is what the Course Plot hands to Sail Scoring as the **As Sailed Course** for the scoring sequence (today by the leg-table paste; see section 12).

### Data layers and invariants

| Layer | Written by | Changes after saving? |
|---|---|---|
| Observations (fixes) | RIB recorder | Never edited; new fixes are added |
| Choices (course rows, picked chips, line ends, laid marks) | RO / Scorer | Saved with the course; laid-mark choice and automatic line ends not yet (`STATUS.md` A10) |
| Saved course (working term: updated course) | Course Plot, from the recorded marks plus the choices saved with it | Intended: Draft, Decisions, Accepted (below; `STATUS.md` A4); must be reproducible (A27) |

Invariants: the recorded marks (observations) are never edited or overwritten (guardrail 17); the as-sailed course is built from them, using any recorded fix of the day; every choice in a saved course is explicit and reproducible; and what is handed to scoring is the saved course.

### Intended saved-course workflow: Draft, Decisions, Accepted (intended, not decided)

Stated by Pat on 7 October 2026 as the intended workflow. It becomes the workflow only after it has been built and has passed testing (`STATUS.md` A4).

1. **Draft.** The RO sets up the course: Race N, Start N, start time, classes starting, and the intended course by card import or by tapping chips. This is working state that can be saved and replaced; only a short undo window is needed, and early saves are not kept.
2. **Decisions.** This stage is triggered when the RO begins "Check recorded marks". The RO checks that the plotted course is what was created and is not distorted by a bad mark position or an unrecognised start line, and selects, for example, a moved weather mark for the second leg. Each edit records its own decision with its reason: for example "Weather Mark fix 2 used for 2nd beat due to wind shift", or "Start Pin for Race 1 inherited from Race 2 because no Start Pin was recorded in Race 1". Decisions are append-only; undo is a revoke.
3. **Accepted course.** When the course reflects the race as sailed, it becomes the accepted course. It is stored as a complete record naming the fix ids and decisions it came from, and it is not replaced.

Points to settle (none assumed): what starts stage 2 (pressing "Check recorded marks" or the first decision); whether editing the course after decisions have begun sends it back to draft, and what happens to decisions about marks no longer in the course; whether an accepted course can be reopened (one option: reopening makes a new accepted version and the old one stays); whether automatic choices (laid marks, line ends) are recorded in the accepted course, flagged as automatic, so it can be rebuilt exactly; and a "Draft, not accepted" banner on the leg table until acceptance. The server's decision record already has `action, race, start, role, from, note, who` fields; how `from` is used has not been established.

### Audit result: intended versus built (Phase 1, 7 October 2026)

| Workflow item | Audit finding |
|---|---|
| Step 1: RIB records laid marks as JSON, same-name fixes kept and told apart by time | Verified. Roles are free-text names, not a typed field. The RIB page offers Races 1 to 3 only; the server accepts 1 to 9 |
| Step 2: Series Name first; Get Latest Marks never edits source data | Get Latest Marks is GET only (verified). The series is one name per `data/` folder, not per course, and nothing requires it before building. The RO page can also re-post a fix under a different race and add typed fixes |
| Step 3: first course built from mark names, times and classes, saved as the original recorded course | Contradicted. The RO builds the course by taps or card import; every edit autosaves over the current `race|start` version. There is no designated original; history keeps the first autosave of the day once it is replaced |
| Step 4: wind gives line squareness and true-beat check | Verified |
| Step 5: Check recorded marks lets the RO choose marks | Read-only in the code. Selection happens in the line-end pickers, laid-mark picker and course-row taps; no decision is written. **Since PAGE_VERSION 2026-10-06.20:** *Add to Race N chips* brings a tapped fix into the race's chip bank (saved with the race); the box changes no fix and writes no decision |
| Step 6: saved course, derived from the recorded marks plus decisions | Not built. One record per `race|start`, replaced on each save; it references no decisions |
| Step 7: saved course handed to Sail Scoring as the As Sailed Course | Not built. The leg table is computed from the page's live state |

| Invariant | Audit finding |
|---|---|
| Observations never edited or overwritten | Contradicted (delete and re-post paths exist) |
| Original recorded course never overwritten | Superseded: no separate original course is kept (decided 7 October 2026). Replaced by the requirement that a saved course can be reproduced from the recorded marks plus decisions, which is not met today (`STATUS.md` A27) |
| Decisions append-only | Verified at the API (the endpoint is unused by the pages since 8 October 2026) |
| Saved course derived and reproducible, never hand-edited | Not established (no derived saved course exists; the course is built by hand by design) |
| What is handed to scoring is the saved course | Contradicted |

Course-history cap: the first saved version is never dropped by the keep rule or the 5 MB cap, but any intermediate version can be, and the first version is lost if the history file is removed (the README gives that as a recovery step). A course saved once and never replaced has no history entry.

### Design decisions and open questions (Pat, 7 October 2026)

Decided:
- There is no separate original recorded course. Pat chose, on 7 October 2026, option 1 of three considered: the recorded marks are the original and are never overwritten (only additional information or a flag may be appended), and the course is always derived from them plus decisions. This only works if resolution is reproducible, which it is not today: automatic line ends and laid-mark choices re-resolve on each render, the laid-mark choice is kept on the phone only, and laid marks have no start-time limit. (8 October 2026: read "plus decisions" as "plus the choices saved with the course"; `STATUS.md` C8.)
- `varW()` should use the race date, not today's date. Not yet changed in the code.

Open:
- The saved-course workflow (Draft, Decisions, Accepted) is intended, not decided; it must be built and pass testing first (`STATUS.md` A4).
- Is the missing start-time limit on automatic laid-mark choice intended? Mark's `course-days.md` describes the rule as the newest exact-name fix recorded before the start. To be investigated.
- Should the laid-mark choice (`laidSel`) be saved with the course instead of kept on the phone? To be investigated.
- Answered 8 October 2026: the page writes no decisions; the write path was built and taken out (`STATUS.md` A1, withdrawn).

### Phase 1 checks against this workflow (answered by the audit above)
- Does the code enforce each invariant, and can any path edit or delete an observation?
- The README says course history keeps the first version of the day plus the last 5 replaced versions, size-capped. Answered by the audit; the "original course" framing it was checked against was superseded by the 7 October decision.
- Does a saved course record which recorded marks (fix ids), which choices and which decisions it was derived from?
- Is the leg table produced from the saved course record, or from the page's live state?
- Does the Course Plot behave the same way for a start with no decisions (the saved course derived from the recorded marks alone)?
- Map the terms: updated course and As Sailed Course are this project's names; "original recorded course" was retired on 7 October 2026. "Race Day Course Record" appears in `PROJECT_HISTORY.md`, and "Course Record" is Mark's format. Settle one vocabulary before the Course Record export.

---

## 2. Decisions

### Decision 1: Who owns fix capture and day-level course storage? (settle first, with the Sail Scoring maintainer)

This project currently covers RIB/committee-boat GPS collection, RO tools and course construction, and Sail Scoring covers the scorer's record and scoring. The proposed `course-days.md` roadmap (public; status: proposed, October 2026; see its "Roadmap" section, steps 3 to 6) goes further. It puts these inside Sail Scoring:

- workspace-level "course days" holding marks, fixes and courses (step 3, which migrates today's per-series course libraries into days);
- fixes, resolution rules and a "check the day's fixes" view (step 4);
- a `race-officer` role and a phone layout (step 5);
- per-day RIB capability links with an offline page, whose rules the draft says are "worth porting rather than reinventing" from this project, and which replace the shared race key (step 6).

The draft justifies these as keeping the record of what was sailed, under the line "Sail Scoring keeps the record of what was sailed. It does not help run the race." (section "The line: scoring, not race management"). It separately describes a "race committee's app" (planning, laying, starting, course board, replays) as a different product, to be considered only if certain conditions arise (section "If it moves out"). The regionalised application in this roadmap resembles that product.

Pat's stated position (`PROJECT_HISTORY.md` section 17, 6 October 2026): the existing Cork Harbour tools remain working operational tools and should not be removed merely because overlapping functionality is proposed upstream; generic course-data concepts should be shared through `course-cards` rather than maintained as incompatible parallel models; the Cork project has a distinct continuing role in local navigation, validation, course visualisation and Race Officer operational decision support; and a versioned Course Record is a promising boundary. On the morning of 6 October Pat raised the duplication concern with Mark and suggested discussing the overlap (`PROJECT_HISTORY.md` section 13).

Options to discuss with the Sail Scoring maintainer (no decision made here):

1. This project owns capture and the day record; Sail Scoring imports the Course Record only.
2. Sail Scoring builds capture (his steps 3 to 6); this project's role narrows or hands over, and the offline code is ported.
3. A staged hybrid: this project keeps capture for the RCYC trial and the Autumn/Winter leagues while Sail Scoring builds steps 1 and 2 and the import; revisit before his step 3.
4. A split by function, following the line `course-days.md` draws between recording the course and running the race (its "The line: scoring, not race management" section): recording of fixes and the course record sit in Sail Scoring; race-operation decision support (line squaring and bias, mark moves after a wind shift, course choice) and local routing knowledge stay in this project, which then needs a clear interface and a decision about who maintains the capture pages in the meantime.

Until this is settled, Phases 3 to 8 below are provisional. Phases 1 and 2 are unaffected.

### Decision 2: Project scope and name
`cork-harbour-orc` describes the origin rather than the product. "Cork" is becoming Venue 1, and most of the system is not intrinsically ORC-specific. A candidate name is `race-course-ops` or similar. No rename yet. Decide after Decision 1. If renaming, rename the existing repository to preserve Git history. Note that `course-cards` already cites this repository's URL as the source of the Royal Cork routing overlay, so a rename needs Mark's coordination.

### Decision 3: What is a venue?
`course-cards` data sets are identified by club and season (for example `rcyc/keelboat-2026`). Mark's course days are identified by date plus "course area". Cork Harbour covers both the RCYC card and the Combined League with Cove and Monkstown Bay. `course-cards` issue #15 (marks used across clubs, and the case for harbour-level shared mark data) bears directly on this. Agree which level this project calls a venue.

**Deployment model.** The regional concept raised in the week beginning 28 September (before `course-days.md` appeared, and not a response to it) is a separate deployment and data set per sailing area or organisation on the ORC Ireland server, reusing the same methodology: RCYC/Cork Harbour, DBSC/Dublin Bay, HYC/Howth. This roadmap assumes one codebase with per-region deployments and data, not one shared operational dataset for all clubs.

### Decision 4: Authentication
See section 9.

### Decision 5: The Course Record format
Not this project's decision alone. See section 5.

---

## 3. Guardrails

1. Do not let regionalisation damage the working Cork Harbour system.
2. Do not invent a separate Course Record schema or routing format. Use and coordinate with the `course-cards` formats (see section 5).
3. Do not rewrite proven functionality merely to make the code look more generic.
4. Do not rewrite the offline queue / service-worker behaviour casually.
5. Do not remove the existing Sail Scoring leg-table handoff until its replacement is proven.
6. Do not replace JSON storage because Sail Scoring uses a database. Align interfaces, not internals.
7. Do not fork the application into separate Cork / DBSC / HYC copies.
8. Do not assume Cork navigation knowledge transfers to another venue.
9. Do not let human-readable mark names become the only long-term identity mechanism. The `course-cards` format already gives each mark an `id`.
10. Do not attempt all of DBSC as the first regional deployment.
11. Anything extracted into common code must continue to produce the same Cork behaviour.
12. Claude Code must never open pull requests or issues against `sailscoring/sailscoring` or `sailscoring/course-cards`, or publish anything there, without Pat reviewing it first.
13. Never re-save the master workbook through a library; use `scripts/xlsx_edit.py`.
14. Never rename `RW_Refinery_North` or `RW_West_of_Refinery` back, never conflate No.7/Corkbeg with Dosco/Corkbeg or EF1 with EF4, never restore the pre-v2.50 E4 coordinate, and never deduplicate repeated occurrences of a logical pair within a course.
15. Do not upload `marks.php` or the RO page to the live paths within 12 hours of a race, and take the three dated backups first (README, "Live install: backup and rollback").
16. The viewer stays dumb: it displays what the workbook says and never invents a route, substitutes a mark or infers an alias.
17. Never edit or overwrite the recorded marks (source observations). The as-sailed course is built from them, using any recorded fix of the day, without changing any fix; every choice in a saved course is explicit and reproducible (section 1b; `STATUS.md` C8). **Not yet enforced by the code** (audit, 7 October 2026): delete and re-post paths exist for fixes, the current course is replaced on every save, and automatic line ends and the laid-mark choice are not saved with the course.

---

## 4. Scope map

This map assumes Decision 1 option 1 or 3. If option 2 is chosen, the first two lists change.

### KEEP / EXPAND (this project)
- RIB / committee-boat GPS capture, including offline operation
- Mark-laying information and moved-mark handling
- Race Officer operational tools
- Local marks, local navigation and routing (the Royal Cork routing overlay and its evidence)
- Course selection / construction
- Start / finish geometry and wind information
- Observation review and reconstruction of what was actually sailed
- Race + start structure, the as-sailed course repair (choices saved with the course), course history
- Venue knowledge not carried by `course-cards`

### SHARED / COORDINATE (with Sail Scoring and course-cards)
- Course Record format (the boundary between the applications)
- Mark identity, the marks file and the routing overlay
- Interchange mechanism (paste / upload first)
- Bearing convention (true versus magnetic)
- Line-end conventions

### TRANSITIONAL
- Leg-table copy/paste into Sail Scoring
- WhatsApp / operational text output
- Anything likely to be replaced by formal Course Record transfer once proven

### SAIL SCORING RESPONSIBILITY (not this project)
- Receiving course evidence, scorer review and the durable authoritative course record
- Scoring and results

Boundary, as Mark states it: Sail Scoring keeps the record of what was sailed and does not help run the race. Mark's three tests for whether something is in scope are direction and purpose, whether a protest hearing would need it, and whether it is computed after the fact for a reader.

---

## 5. The three repositories

```
this repo (operations) -> race positions / Course Record -> sailscoring (scoring)
                              ^
                  course-cards (shared data formats + library + catalogue)
```

### `course-cards` (formats; MIT)
- Format version 2: a **marks file** (id, name, shape, colour, `position` or `placement`, per-mark `source`), a **course card file** (courses as ordered mark sequences with sides, `startLine`, optional `finish`, notes) and an optional **routing overlay** (`waypoints`, `passages`, `direct` pairs, and `assumed` positions with `toleranceM`, so a verdict goes stale mark by mark when positions move).
- The library turns a course plus per-race positions into legs with distance and **true** bearing; legs to and from a line are measured from its midpoint; courses called on the day are supported.
- The Royal Cork overlay already exists, with Pat Tanner as contributor and this repository as its source. It is the only overlay so far.
- Data sets exist for RCYC (keelboat-2026), DBSC (summer-2026: 26 marks, five keelboat cards, 592 courses), HYC, DLCC, Kinsale, Clontarf and Schull (per the `course-cards` README).
- A catalogue and immutable versioned URLs are published at courses.sailscoring.ie; three releases are retained.

### `sailscoring` (scoring application; MIT)
- Next.js, Postgres, Better Auth. ORC scoring support (#429, milestones M1 to M7 in `docs/design/orc/orc-scoring.md`) is the current focus, targeting the HYC Autumn League 2026 (per `sailscoring/CLAUDE.md`).
- `docs/design/course-days.md` proposes the Course Record (to live in `course-cards`), course days and a nine-step roadmap. Its status is "proposed (October 2026)".

### This repository
- Python tooling, PHP/JSON server, two HTML pages, the audited master workbook (v3.19 as of this revision, 40 courses, 360 configurations, 3,759 physical legs, 186 directed chords) and a SHA-256-checked release process.

### Mandatory reading before any Claude Code work (verify that each exists and is current)
1. `PROJECT_HISTORY.md` and `README.md` in this repository. `PROJECT_HISTORY.md` is current to 8 October; record the outcome of Decision 1 in it once settled.
2. `sailscoring/docs/design/course-days.md`
3. `course-cards/docs/format.md` and the RCYC and DBSC data-set READMEs
4. `sailscoring/docs/design/orc/orc-scoring.md` and `docs/goals.md` (not yet read by this roadmap's author)
5. Upstream issues named in `PROJECT_HISTORY.md` and visible in the public trackers: `course-cards` #14 (mark identity), #15 (shared marks), #16 (straight-line legs), #17 (Cork mark positions), #18 (tidal and depth restrictions on legs), #19 (provenance and accuracy), and `sailscoring` #659 (a leg-table drawing bug, per #660), #660 (explicit magnetic and true bearings), #663 (imported marks whose positions changed), #664 (unrecognised starting-mark name). Titles are known; the threads have not been read.
6. `sailscoring/docs/design/horizon.md` and ADR-009 (API/CLI), ADR-012 (published JSON sidecar), ADR-013 (versioning stored formats). Likely relevant to interchange and versioning; not yet read.

### Contribution rules (from `sailscoring/CONTRIBUTING.md` and `CLAUDE.md`)
- Features start as an issue so the approach is agreed first; scoring changes need a rules citation.
- Merges need `pnpm lint`, `pnpm test:unit:db` and the Playwright suite green; scoring-logic changes need human-verifiable YAML fixtures.
- AI-assisted pull requests: no "pure agent" PRs, the person must have reviewed every line, disclose AI use in the PR and with a `Co-authored-by` trailer, no single-typo PRs.
- Sign commits off (`git commit -s`, DCO). MIT licence; the "Sail Scoring" name and logo are trademarks, not covered by the code licence (per `sailscoring/CLAUDE.md`).
- Credit people who report issues: the issue body and a row in `CONTRIBUTORS.md`.
- `course-cards` shows no `CONTRIBUTING.md`. Ask Mark whether the same rules apply there.

### Course Record
Mark's proposal (one record per start) has these groups: race (date, course area, race number, start number, classes, start time), reference (bearings stored true with variation, model, position and date), marks (id, name, kind, position and the fix it came from), lines, sequence (with which fix each rounding used), legs (distance to 0.01 NM, true bearing, wind, current, routed-via waypoints) and provenance. His step 1 adds it to `course-cards` and adds "Import course..." (paste, upload or URL) to Sail Scoring, and asks this project to emit records.

Claude may analyse how existing Cork data maps to it. It must not create a competing schema (for example `pat-course-record-v1.json`).

---

## 6. Venue package (revised)

A venue package should be a **`course-cards` data set** (marks file, course card, routing overlay) **plus local configuration** for what that format does not carry. Do not define a separate package format.

| Concept | Where it lives |
|---|---|
| Marks, stable id, position, provenance per mark | course-cards marks file |
| Published courses and start lines | course-cards card file |
| Authored passages, routing waypoints, direct pairs, assumed positions and tolerances | course-cards routing overlay (Royal Cork's is derived from this repository's workbook) |
| Per-chord bathymetric evidence and the evidence register | this repository's workbook only; the overlay holds a method line, not the per-chord evidence |
| Navigation restrictions, including tidal and depth conditions (for example the SI para 21 jetty exclusion) | overlay passages, as notes; no structured field. `course-cards` issue #18 concerns representing leg conditions, and the Cork work argued for attaching a restriction to the physical leg or passage that causes it |
| RIB quick-pick marks (Curlane, Dutchman, White Bay) | currently in this repository's pages; to be moved to venue config |
| Diagnostic thresholds (stale-position age, pin proximity 60 m, line 45 degrees off square, 500 m mark disagreement) | currently constants in the RO page; classify as common defaults or venue overrides |
| Cork rules in the page code (Grassy Mid and Grassy Walk, No.8/Dosco finish rule, 500 m line-midpoint warning, near-miss name handling) | currently in this repository's page code; the largest extraction task |

The existing pipeline workbook -> `make_snapshot.py` -> `rebuild_page.py` -> snapshot embedded in the RO page already behaves like a venue package build. The application should not know what "Curlane" means; the Cork venue package should.

---

## 7. Mapping items to resolve before any Course Record export

| Item | Detail |
|---|---|
| Bearings | This project's SailScoring leg table is in magnetic degrees, an assumption noted in the README as pending confirmation with Mark. `sailscoring` #660 proposes storing bearings true and accepting and showing magnetic by default, converting with the World Magnetic Model at the course's position and falling back to a venue (series or workspace) setting when a leg table has no position. Whether this has been implemented should be confirmed against the live app. `course-cards` and the Course Record store **true** bearings and show magnetic only for display, using the World Magnetic Model for the date and place. |
| Line ends | course-cards names the ends starboard and port, looking towards the first mark, and says the committee boat is not always at the starboard end. This project records committee boat and pin, so an orientation step is needed. |
| Mark identity | This project matches fixes to marks in three ways (audit): laid card marks by normalised exact name, line ends and roles by name pattern, and course rows by fix id. course-cards marks have an `id`, matched verbatim by course sequences. Map workbook mark names to ids and preserve the exact-name matching rule for laid marks. Related upstream issues: `course-cards` #14, and `sailscoring` #663 and #664, which came out of the 5 October integration test (`PROJECT_HISTORY.md` section 12). |
| Venue identity | Storage is by day file and one series name, with no venue or club. See Decision 3. |
| Moved marks | The Course Record rule is that each rounding uses the position in force when it was rounded. The README mentions moved-mark alerts; per the audit, per-rounding positions are kept for ordinary marks (course rows reference a specific fix by id) but not for laid marks, which re-resolve to the latest fix on each render (`docs/audit/PHASE1_AUDIT.md`). |
| Distance method | The page measures hops between non-card marks by rhumb line; card legs use the workbook's Vincenty geodesics; the course-cards library uses great-circle distance. The line midpoint here is the arithmetic mean of lat/lon; format.md uses the geodesic midpoint |
| Curlane and pair direction | The snapshot carries Curlane pairs; the overlay leaves Curlane out. Workbook pairs are directed; the overlay merges each pair with its reverse and refuses a pair routed differently each way |
| Laid-mark rule | course-days: newest exact-name fix recorded before the start. Code: no start-time limit (see open design questions) |
| Wind | course-cards `windDirectionDeg` is the wind a card row was laid out for, not recorded wind. The Course Record legs carry recorded wind. |
| Leg table | Each leg is rounded separately, so the lines can differ from the legs table total by a few hundredths. Keep as is. |
| Anchor | A bare leg table is a free-floating chain of vectors. `course-days.md` ("The course record" section) says a leg table with one known point, an anchor, as Pat proposes, is a record whose single mark locates the rest. `PROJECT_HISTORY.md` section 11 lists a known geographical anchor among the richer handoff contents. Whether the paste format or the Course Record will carry an anchor is not established. |

---

## 8. Phases

### Phase 1: Document before changing (no code changes). Completed 7 October 2026; report `docs/audit/PHASE1_AUDIT.md` at commit `f30882f`
Claude Code should:
1. Read this repository, `PROJECT_HISTORY.md`, and the mandatory reading in section 5.
2. Document the actual current architecture.
3. Verify every README claim listed in section 1a, and the intended workflow in section 1b, against the code and tests.
4. Identify every Cork/RCYC-specific dependency, including the rules inside the page code.
5. Identify genuinely generic components.
6. Map workbook, snapshot and page data to the course-cards marks, card and routing overlay, and list the missing fields and incompatibilities (section 7).
7. Identify areas already aligned with Course Days, overlaps with Mark's proposed responsibilities, and transitional components.
8. Record the hosting constraint (the live host's PHP version and server behaviour, and the planned move to orc-ireland.org).
9. Make no architectural changes.

Output: an analysis document for review.

### Audit findings that constrain Phases 4 and 5
Blockers to a second deployment on the same server or origin:
- The RIB page uses absolute paths to `/marks/marks.php` and `/marks/key.js` and has no `MARKS_BASE`.
- The RIB service worker deletes every `record-` cache on the origin when it activates.
- RIB localStorage keys are unprefixed, so two RIB deployments on one origin would share the queue, device id and race key.
- The snapshot is embedded in each built RO page, so each venue needs its own built page and its own `marks.php` folder.
- Cork constants in the RO page: map centre, `CARD_STARTS`, `CLASSES`, `varW()`, role-name regexes, start and finish rules.
- `marks.php` itself contains no Cork or RCYC content.
No venue, club or course-area identifier exists in any stored file. The race key is also accepted as a URL parameter (`?key=`) as well as a header.

### Phase 2: Settle Decision 1 with Mark; revise this roadmap
Take the audit and Decision 1 to Mark, then revise this roadmap in place.

### Phase 3: Decide project identity
Settle application scope, repo name (Decision 2) and what a venue is (Decision 3). Update README and documentation.

### Phase 4: Extract Cork as Venue 1
Incrementally, one class of configuration at a time, and only after Decision 1 supports it:

```
mark presets -> marks (course-cards ids) -> courses -> routing/passages -> restrictions -> venue-specific thresholds/config
```

After each step, confirm Cork still produces exactly the same operational result. Use the existing parallel test install (`scripts/build_test.py`, `/course-test/`, `/marks-test/`) and a copy of a real day's files as the regression harness. Do not begin by rewriting Course Plot.

### Phase 5: DBSC as Venue 2
Only once Cork operates through the venue abstraction. Start from the existing `dbsc/summer-2026` data set (26 marks, five keelboat cards, start lines from the sailing instructions) and one fleet or race area. A DBSC routing overlay is needed only if the water requires it. Check `dbsc-archive` and `hyc-archive` (listed as sibling repositories in `sailscoring/CLAUDE.md`) for further reference data. Do not attempt all of DBSC.

### Phase 6: Shadow testing
Use historical or live DBSC races without affecting race management. Compare the published course plus observations, our reconstruction, and the known outcome.

### Phase 7: Course Record interoperability (in parallel)
Once the format is agreed in `course-cards`: adapter/exporter from existing internal data to the Course Record. Start with paste/upload, not an API. Do not emit records from the RO page until the format, the bearing convention and the line-end convention are agreed with Mark.

Note (10 October 2026): this phase, and `STATUS.md` C5, concern the Course Record only. The Course Plot's "Copy for Sail Scoring" button (`STATUS.md` A37) emits Sail Scoring's ORC constructed course format, which is a different format and not the Course Record, so this rule does not apply to it.

### Phase 8: Controlled DBSC operational trial
Only after shadow testing: one race area, one operation, limited users, existing DBSC process remains authoritative.

---

## 9. Authentication

Current state per the README: a **race key** (in `key.js`, loaded by both pages, so readable by anyone who loads a page) covers fix and course writes and reads; a separate **RO key** (read from `data/ro-key.php`, taken only from the `X-RO-Key` header) is required to write decisions, an endpoint no page uses since 8 October 2026; it is reserved for a possible lock on the as-sailed course (intended, not built). Mark's `course-days.md` says the shared race key is what step 6 replaces.

Evaluate, without adopting blindly, Mark's proposal: per-day capability links tied to a RIB or user purpose, stored hashed, expiring and revocable, with fixes from a revoked link quarantined, and a narrow offline page with client-generated fix ids so retries are harmless. Review before any larger deployment. This is tied to Decision 1.

---

## 10. Testing priorities

Emphasis: preserve operational behaviour. Existing coverage is `tests/test_marks.py` and `tests/test_build_test.py`; browser behaviour is untested.

- **Geometry:** known coordinates A and B give a known distance and true bearing.
- **Fix resolution:** fixes at 11:55, 12:02 and 12:09 with a 12:05 start; verify the intended candidate and resolution behaviour.
- **Moved mark:** Race 1 position, mark moved, Race 2 position. Historical Race 1 reconstruction must not change.
- **Browser workflow (regression of 4 October):** record mark, lose connectivity, queue fix, reconnect, server receives delayed fix, mark moves, second fix, Course Plot, RO reviews evidence, correct fix selected.
- **Equivalence after each extraction step:** same operational output for a copied real day.

---

## 11. Required release steps by repository

### This repository (workbook or page release; from the README)
1. `python scripts/audit_workbook.py <workbook>` passes all 16 checks.
2. `cell_diff` shows exactly the intended changed cells.
3. Open in Excel itself (no repair dialog).
4. If any coordinate changed, retest every dependent chord with `scripts/test_chords.py` (always pass `--rasters GEO12_04,KRY12_05,CB12_01`) and update its Evidence Register row.
5. Add a Read Me change record with the SHA-256 of the workbook it was made from.
6. `python scripts/rebuild_page.py <workbook>`; upload `pages/course/index.html`.
7. Record the new SHA-256 in the README.
8. Run `tests/test_marks.py` on PHP 8.4 and PHP 5.5 before uploading any change to `marks.php`.

### `course-cards`
Bump `version` in `package.json` in the same commit as any data change (otherwise the deploy does nothing); tag `vX.Y.Z`; the release workflow stages an npm publish that Mark must approve with 2FA; versioned URLs are immutable. Data is generated from the source PDFs (`pnpm data`, then `pnpm data:check`).

### `sailscoring`
Contribution rules in section 5.

---

## 12. Output migration path

```
Course Plot
|- existing leg-table output       (keep)
|- existing operational/WhatsApp   (keep)
|- Course Record export            (add when format, bearings and line ends are agreed)
```

A migration path, not a cliff edge.

---

## 13. Timing

- `course-days.md` timing note (end of its "Roadmap" section): while the autumn leagues run, only steps 1 and 2 (Course Record import, two-ended lines) touch the race-day path; step 3 is a restructure for the gap between leagues; steps 5 and 6 need on-water testing, so a winter series is the next chance.
- Sail Scoring's current ORC work targets the HYC Autumn League 2026.
- This project's rule: nothing goes live within 12 hours of a race.
- Raise Decision 1 with Mark before his step 3 is scheduled, since it affects what he builds.

---

## 14. Immediate next steps

1. Pat to confirm which 4 October issues have been re-tested live.
2. Discuss Decision 1 with the Sail Scoring maintainer. Share a sample day's JSON files (recorder names and device ids removed; never the race key or RO key) so the common ground between observations and the resolved course can be seen before the Course Record format is fixed.
3. Update `PROJECT_HISTORY.md` with the outcome of Decision 1.
4. Done (7 October 2026): the Phase 1 architecture and regional-readiness audit (no code changes).
5. Review the audit together; revise this roadmap in place.
6. Settle scope, name and venue definition.
7. Agree bearing and line-end conventions and the Course Record with Mark.
8. Extract Cork as Venue 1 incrementally.
9. Check DBSC data against the venue contract using `dbsc/summer-2026`.
10. Build a small DBSC Venue 2 proof of concept.
11. Only then consider a live DBSC trial.

---

## 15. Open questions

The Phase 1 audit lists 19 questions (its section 11). Pat's answers to the design-critical ones are in section 1b. The rest, including the live host's PHP version and server, header pass-through, the orc-ireland.org plan, which code ran on 27 September, and whether the RIB page is limited to Races 1 to 3 by design, are unanswered. (9 October 2026: the live host's PHP version, 5.5.38, the server software, Apache, and the `data/` deny-all were checked; `STATUS.md` A26.)

- Decision 1: who owns fix capture and the day record, given `course-days.md` steps 3 to 6?
- Does the Course Record's definition live in `course-cards`, and what is Mark's timetable?
- Do `sailscoring` contribution rules apply to `course-cards`?
- Which level is a venue: club and season, or course area?
- How much of the diagnostic threshold set is genuinely universal?
- Who supplies and vouches for authoritative DBSC mark data beyond the club's published sheets?
- The Royal Cork routing overlay in `course-cards` cites this repository's workbook as its source. How is it kept in step with the workbook, and who is responsible for it?
- How does a repository rename affect the source URL cited in the overlay?
- What is the status of `sailscoring` #663 and #664, and of `course-cards` #14 to #19?
- Cage position (decided by Pat on 7 October): the workbook keeps eOceanic's C1, 51 48.818 N 008 16.990 W (Fl.G.10s), attributed to eOceanic. A Navionics reading of 51 48.826 N 008 16.970 W is about 27 m away (15 m north, 23 m east, bearing about 057 T). A buoy swings round its sinker and the mooring chain length is not known, so the difference is treated as of the same order as the swing circle: a judgement, not a measurement. The Navionics reading is a cross-check only. Follow-up: confirm that the `course-cards` marks file and routing overlay hold a position within the overlay's 20 m trust tolerance of C1; otherwise passages through Cage stay unreviewed.
- Does Sail Scoring build a start or finish line from a committee boat and pin position, with legs measured from the midpoint? Not established. The `course-cards` library supports two-ended lines; the app's behaviour is not confirmed.
- Open data questions from the README: Harp and Ringabella positions, EF2, No.6 to Cage, twenty-three chords passing under 2.0 m, and Mark's 204 pairs.

## 16. Not yet reviewed

The threads of the `course-cards` and `sailscoring` issues named above (only their titles are known, via `PROJECT_HISTORY.md` and `course-days.md`; `course-cards` #13 is cited in `course-days.md` as the regional register of marks), `docs/design/orc/course-builder.md` and `orc-scoring.md`, `docs/goals.md`, `horizon.md`, the ADRs, and the `dbsc-archive` and `hyc-archive` repositories.
