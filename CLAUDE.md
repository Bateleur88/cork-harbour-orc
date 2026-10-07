# CLAUDE.md

Guidance for Claude Code in this repository (`cork-harbour-orc`): a race-day workflow for laid-mark recording (RIB page), RO course plotting, and hand-off to Sail Scoring. It is a working race-operations tool. Keep this file short; the detail lives in the files named below.

## Read first, every session

1. `STATUS.md` - what is built, in progress, decided or open.
2. `README.md` and `PROJECT_HISTORY.md` - how the system works and how it got here.
3. `docs/audit/PHASE1_AUDIT.md` - dated baseline (commit `f30882f`). Never edit it.

## Working with Pat

- Never assume or guess. If something is unclear or cannot be established from the code, tests or documents, ask Pat before acting.
- Show what you plan to change before large or risky edits.
- "Completed" means built and tested on the pages. Only Pat decides that something is confirmed in a live race.

## STATUS.md rules

- When your work changes the state of an item, propose the exact edit to the relevant line and wait for Pat's approval. Do not edit status silently.
- Never mark an item CONFIRMED LIVE. Only Pat does that.
- Add a dated line to the update log for each approved change. Never delete earlier lines.

## Commits

- Every commit that works on a `STATUS.md` item names it in a trailer above any `Co-Authored-By` line: `Status: L4` or `Status: A3, A7`. Use the references in `STATUS.md` (L for the 4 October live-test problems, A for audit findings, C for coordination and decisions). The P-numbers used for page-edit phases (P1, P2, P3a, P3b, P4) are not status references.
- The trailer says a commit advances an item. It never means the item is complete; the state in `STATUS.md` is what counts, and Pat approves state changes.
- Before each commit, check whether the change advances a `STATUS.md` item. If it does and the message does not name it, the message is not finished.
- Do not renumber or reuse references. New items take the next number in their series.
- This repository does not use GitHub issues. Do not create issues here unless Pat asks.

## Guardrails

- Never edit or overwrite the recorded marks (source observations). There is no separate original course: the recorded marks are the original (`STATUS.md` A2, A7). A saved course must be reproducible from the recorded marks plus decisions (A27). RO / Scorer changes go in as decisions. The intended saved-course workflow (Draft, Decisions, Accepted) is in `STATUS.md` A4. It is intended, not decided: do not build it unless Pat asks. Not yet enforced by the code; see `STATUS.md`.
- Decisions are append-only.
- The viewer stays dumb: it shows what the workbook says and never invents a route, substitutes a mark or infers an alias.
- Never re-save the master workbook through a library; use `scripts/xlsx_edit.py`.
- Never rename `RW_Refinery_North` or `RW_West_of_Refinery` back; never conflate No.7/Corkbeg with Dosco/Corkbeg or EF1 with EF4; never restore the pre-v2.50 E4 coordinate; never deduplicate repeated occurrences of a logical pair within a course.
- Do not rewrite proven behaviour (especially the RIB offline queue and service worker) merely to make the code more generic.
- Do not remove the existing leg-table hand-off to Sail Scoring until its replacement is proven.
- Do not invent a separate Course Record schema. The shared formats are defined by Sail Scoring's `course-cards` and its `course-days.md` proposal; coordinate, do not duplicate.

## Never touch

- Do not read, print or copy `key.js` values, the RO key, or anything under a live data directory. Describe data shapes from the code that reads and writes them.
- Do not upload, deploy or change anything on the live host. Pat does that.
- Do not open issues or pull requests, post comments or publish anything in `sailscoring/sailscoring` or `sailscoring/course-cards`.
- Do not put private correspondence in any file in this repository.

## Release and live-install rules (see README for the full procedure)

- Workbook release: `scripts/audit_workbook.py` passes all 16 checks; `cell_diff` shows only intended changes; open in Excel with no repair dialog; retest affected chords with `scripts/test_chords.py` (always pass `--rasters GEO12_04,KRY12_05,CB12_01`); add a Read Me change record with the workbook SHA-256; run `scripts/rebuild_page.py <workbook>`; record the new SHA-256 in the README.
- Before any change to `marks.php`, run `tests/test_marks.py` on PHP 8.4 and PHP 5.5.
- No change goes to the live paths within 12 hours of a race. Take the three dated backups first.

## Vocabulary

- updated course, As Sailed Course: this project's terms. "Original recorded course" was retired on 7 October 2026 (`STATUS.md` A2); the final vocabulary is open (C5).
- "Race Day Course Record": the older term in `PROJECT_HISTORY.md` for the course the Course Plot builds from stored observations.
- "Course Record": only the versioned format proposed in Sail Scoring's `course-days.md`.

## Scope

This repository's roadmap is this project's own. Do not act on roadmap phases beyond what Pat asks for in the current session; Phases 3 to 8 are provisional.
