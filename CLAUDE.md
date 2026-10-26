# CLAUDE.md

Guidance for Claude Code in this repository (`cork-harbour-orc`): laid-mark recording (RIB page), RO course plotting (course page), the server (`marks.php`), and the hand-off to Sail Scoring. It is a working race-operations tool used on race days. Keep this file short.

## Start and finish lines

Start and finish lines: LINE_RULES.md is the single authority. Follow it exactly. Never add an automatic pick, default, carry-over or substitution for a start or finish line end. If a request, a document, a test or existing code conflicts with LINE_RULES.md, stop and report the conflict to Pat; never resolve it yourself.

## Read first

1. `STATUS.md`, every session: where every item stands and what comes next.
2. `README.md`: only the sections the task needs.
3. `PROJECT_HISTORY.md`: only when the task needs to know how something came about.
4. `docs/audit/PHASE1_AUDIT.md`: the dated baseline (commit `f30882f`). Never edit it.

## Working with Pat

- Never assume or guess. If something can't be established from the code, tests or documents, ask Pat before acting.
- Show what you plan to change before large or risky edits, and wait for approval.
- "Built and tested" means built and tested on the pages. Only Pat decides that something is confirmed in a live race.
- One job at a time. Every command has a 5-minute limit, including any loop inside it. If one hits the limit, stop it and tell Pat; don't retry silently.
- Close every browser, local server and PHP process you start, and confirm they are closed when you finish.

## Documentation rules

Each file has one job, and each fact lives in one file only. Where another file needs it, point to it; don't repeat it.

| File | Its job | Limit |
|---|---|---|
| `STATUS.md` | Where every item stands; the release order (Next block) | A 5-minute read |
| `README.md` | What the system is, how it works, how to deploy, test and roll back | No version numbers, no STATUS references, no history |
| `ROADMAP.md` | Direction: open decisions, venue phases, guardrails | About one page; nothing about current state |
| `PROJECT_HISTORY.md` | How the project got here | One short paragraph per release |
| `CLAUDE.md` | How Claude Code works here | This page |
| `LINE_RULES.md` | The start and finish line rules, in Pat's words | Changed only by Pat |

- Replace out-of-date text; never append corrections beside it. Git keeps the history.
- No hashes, byte counts, test step numbers or commit lists in any of these files. Release details belong in the release steps file and the backups.
- References are L, A and C only. Anything found in testing gets an A-number when it is recorded, or it isn't tracked. Don't invent other label schemes (T, Q, "fix N", "answer N" and so on).
- STATUS.md has its own update rules at its top. Follow them.
- Exception: CLAUDE.md restates the safety rules Claude Code must never break (releases, workbook, viewer, recorded marks). README holds the full procedures.

## Testing rules

- Regression is done by script, never by manual steps: compare the new build with the released one on copies of the live and test data (every start's legs, totals, outputs and saves).
- Manual test steps cover only what needs a person's eyes: layout, wording, colours, tablet and phone behaviour, reload and offline behaviour.
- 30 steps at most per test file, in Pat's format (Step N, one action, "You should see:"). Shared setup is written once, not repeated per start.
- After a fix, retest only the failed steps plus the script regression.
- Release steps: as few as the release safely needs.

## Commits

- Every commit that works on a `STATUS.md` item names it in a trailer above any `Co-Authored-By` line, e.g. `Status: A58` or `Status: A3, A7`. The trailer says a commit advances an item, not that it is complete.
- Before each commit, check whether the change advances a STATUS item. If it does and the message doesn't name it, the message isn't finished.
- Never renumber or reuse a reference. New items take the next free number.
- Don't create GitHub issues here unless Pat asks.

## Guardrails

- Never edit or overwrite recorded marks. They are the original; there is no separate original course. The as-sailed course is built from them using any recorded fix of the day, without changing any fix, and a saved course records every choice so it can be rebuilt (STATUS A2, A7, A27, C8).
- The viewer stays dumb: it shows what the workbook says and never invents a route, substitutes a mark or infers an alias. Reversed routes come from the snapshot build, not the page; with no route in the snapshot a leg is measured straight and labelled.
- The hand-off to Sail Scoring is Copy for Sail Scoring, in Sail Scoring's ORC constructed course format (`docs/constructed-course-format.md`). Don't invent another format; changes to it are agreed with Sail Scoring's maintainer.
- Don't rewrite proven behaviour, especially the RIB page's offline queue and service worker, just to make the code more generic.
- The review decisions UI was withdrawn; don't bring it back unless Pat asks. `marks.php` keeps the decisions endpoint, unused.
- Never re-save the master workbook through a library; use `scripts/xlsx_edit.py`. Never rename `RW_Refinery_North` or `RW_West_of_Refinery` back; never conflate No.7/Corkbeg with Dosco/Corkbeg or EF1 with EF4; never restore the pre-v2.50 E4 coordinate; never deduplicate repeated occurrences of a logical pair within a course.

## Never touch

- Don't read, print or copy `key.js` values, the RO key, or anything in a live data folder. Describe data shapes from the code that reads and writes them.
- Don't upload, deploy or change anything on a live host (tradboats.ie or orc-ireland.org). Pat does that.
- Don't open issues or pull requests, post comments or publish anything in `sailscoring/sailscoring` or `sailscoring/course-cards`.
- No private correspondence in any file in this repository.

## Releases

- Nothing goes to the live paths within 12 hours of a race.
- Before any change to `marks.php`, run `tests/test_marks.py` on PHP 8.4 and PHP 5.5.
- Every release is built and tested on the test copy (`/course-test/`, `/marks-test/`) first. The RIB page has no test copy until `/record-test/` exists (STATUS A17); until then RIB page changes are tested on the water before being relied on.
- Before a live upload: back up the live page, `marks.php` and the whole data folder (file count and SHA-256 list).
- Workbook releases follow the checklist in README.

## Vocabulary

- AsSailedCourse: the course actually sailed, built on the course page and sent to Sail Scoring.
- "Course Record": Sail Scoring's earlier proposed format, replaced by the ORC constructed course format (#667). Historical only.

## Scope

This repository's roadmap is this project's own. Don't act on roadmap phases beyond what Pat asks for in the current session.
