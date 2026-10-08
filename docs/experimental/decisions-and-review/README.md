# Decisions and review: an experiment, taken out of the page

From 6 to 8 October 2026 the RO page (`pages/course/course_v8.html`) gained a review-decisions layer: a Review name and
RO key on each device, the day's decisions read and shown in Check recorded marks, Accept, Do not use and Undo with a
"Legs need updating" warning, Use as for course rows, and a review history with "Earlier records". It was PAGE_VERSION
2026-10-06.9 to .19 (.12, .15 and .17 were never committed). It was tested on the parallel test copy (`/course-test/`,
`/marks-test/`) only, never in a live race.

On 8 October 2026 Pat took it out of the page as an unnecessary complication, in commit `dd86687` (PAGE_VERSION
2026-10-06.20 to .24). The page now repairs the as-sailed course directly from the recorded fixes, which stay
untouched: picked chips (any recorded fix of the day as a chip of a race, saved with the race) and line ends from any
race's fixes.

The work stays in the history. The annotated tag `experiment/decisions-review` marks the last commit before it was
taken out (`b5062c9`).

## The commits

Document commits sit between these, so they are listed one by one:

| Commit | PAGE_VERSION | What |
|---|---|---|
| `d6d24a8` | | `marks.php`: RO key, course history, append-only decisions (server side; kept) |
| `73e8633` | .9 | Review name and RO key; the name sent as "by" on course saves |
| `56b7750` | .10 | the day's decisions read and shown in Check recorded marks |
| `f30882f` | .11 | review glyphs on the Check recorded marks sketch and chart |
| `3579dee` | .13 | Accept, Do not use, Undo; the "Legs need updating" warning |
| `1ef3a7a` | .14 | `legPts`, the legs of any race and start in one function (kept) |
| `26f0570` | .16 | Use as for course rows |
| `0cd524b` | .18 | the fix detail and review decisions directly under the sketch |
| `4313903` | .19 | the chart tap scrolls to the fix detail; the review history fold |

## What survives in the page

- `legPts` (`1ef3a7a`).
- The tapped fix's detail directly under the sketch or chart, and a tap in the sketch, the chart or the list scrolling
  it into view (`0cd524b`, `4313903`).
- The check in `tests/test_build_test.py` that the page's storage key names are exactly the known list (`73e8633`), now
  without `ro-name` and `ro-key`.

## What stays in marks.php, unused by the page

`pages/marks/marks.php` keeps the append-only decisions endpoint (`?type=decisions`, written only with the RO key, read
with the race key) and the RO key handling (`data/ro-key.php`, the `X-RO-Key` header), unchanged. No page uses them.
`tests/test_marks.py` still tests them: `t10_ro_key`, `t15_decisions`, and the "no decisions file" check in
`t16_old_pages`.

## Also removed in dd86687, not part of the experiment

The line in the fix detail listing other fixes of the same mark in use in the race ("Other ... fixes in use in Race
N ... Information only"), added in `2aec398` (PAGE_VERSION 2026-10-06.7). Its README sentence is quoted in
`README_sections_b5062c9.md`.

## Files here

- `README_sections_b5062c9.md`: the README.md paragraphs about this work, word for word, with their line numbers at
  `b5062c9`.
- `STATUS_rows_b5062c9.md`: the STATUS.md rows A1, C7, A4 and A27 and the update-log lines about A1 and C7, word for
  word, with their line numbers at `b5062c9`.

The page code is not copied here: `git show b5062c9:pages/course/course_v8.html` gives it.
