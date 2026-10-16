# ROADMAP

This project's own roadmap: where it is heading, not where it stands (that is `STATUS.md`). It does not set Sail Scoring's roadmap, and the upstream processes of `sailscoring/sailscoring` and `sailscoring/course-cards` are respected.

## What this project is for

Race-day course work: recording laid marks from the RIBs, helping the race officer build the course actually sailed, and handing it to Sail Scoring. Settled with Sail Scoring's maintainer (#667): this project records the fixes and builds the AsSailedCourse; Sail Scoring imports it in its ORC constructed course format and does the scoring. The race officer's facts (actual start time, classes per start, course sailed) come first, and scoring works from them.

## Open decisions

1. **Project name and scope** (STATUS C6). `cork-harbour-orc` describes where it started, not what it is. If renamed, rename the existing repository so its history and cited URLs carry over.
2. **What a venue is** (STATUS C6). The direction: a record page and course page per venue, with separate course data per venue (for example one workbook per venue, like the RCYC workbook), never mixing one venue's data with another's. Cork Harbour clubs (RCYC, Cove, Monkstown Bay) share much of the same course data, maintained by Pat. A race is identified by club, date, day race and start; the page keeps one headline series per race day, for the WhatsApp heading and the day's record; which series a race counts in is for scoring.
3. **Authentication.** Current state: STATUS A26 and C9. Before wider use, evaluate per-device or per-day links that can expire and be revoked, without adopting any scheme blindly.

## Phases

| Phase | Gate |
|---|---|
| 3. Decide name, scope and venue (decisions 1 and 2) | Before any extraction |
| 4. Extract Cork as Venue 1, one kind of configuration at a time | Cork's results must stay identical after every step |
| 5. DBSC as Venue 2, starting with one fleet or race area | Only once Cork runs through the venue set-up |
| 6. Shadow testing on DBSC races | No effect on DBSC race management |
| 7. Course hand-off to Sail Scoring | Format settled with Sail Scoring (#667); further steps agreed with Sail Scoring |
| 8. Controlled DBSC trial | Only after shadow testing; DBSC's own process stays authoritative |

## Guardrails

1. Regionalisation must not damage the working Cork Harbour system: anything moved into common code produces exactly the same Cork result.
2. One codebase with per-venue deployments and data, not separate copies of the application.
3. Don't rewrite proven behaviour, especially the RIB offline queue, just to make the code more generic.
4. Keep JSON storage; align interfaces with Sail Scoring, not internals.
5. Don't assume Cork navigation knowledge transfers to another venue.
6. Mark names must not stay the only lasting identity; use stable mark ids (as `course-cards` does).
7. Don't attempt all of DBSC as the first regional deployment.

The working rules for code, data and releases are in `CLAUDE.md`.

## Testing priorities

Script tests of the page's logic on the saved race days (STATUS A24): distances and bearings, fix choice, a moved mark not changing an earlier race, line ends, outputs and saves, and the same results after every extraction step.

## Open questions

- Do `sailscoring` contribution rules apply to `course-cards`?
- Which diagnostic thresholds (stale position, pin proximity, line off square, mark disagreement) are universal, and which are per venue?
- Who supplies and vouches for authoritative DBSC mark data beyond the club's published sheets?
- The Royal Cork routing overlay in `course-cards` cites this repository's workbook: how is it kept in step, and what does a rename do to the cited URL?
