# README sections at b5062c9

Quoted word for word from `README.md` at commit `b5062c9` (tag `experiment/decisions-review`). Each block gives its line numbers in that file. Nothing here describes the current page.

## README.md lines 174 to 177: Course history: the `by` field sent by the RO page (reworded: the page no longer sends it)

~~~~text
carry `by`, the name of whoever saved it (text, cut to 40 characters, dropped if not
text); it is stored with that version and moves into the history with it. The RO
page sends its Review name (below) as `by`; with no name set, and from older pages,
there is none, and an older `marks.php` ignores it. Read with
~~~~

## README.md lines 181 to 194: Review decisions (replaced by one sentence on the unused decisions endpoint)

~~~~text
*Review decisions.* The scoring review (use as, do not use, accept, and revoke to
undo) is kept in `/marks/data/decisions-YYYY-MM-DD.json`, append-only, keyed by the
record id the page makes (a retry writes nothing), at most 2000 a day. Decisions are
**written only with the RO key** and **read with the race key**
(`GET ?type=decisions&date=`). `key.js` is public, so names and notes in decisions
are effectively readable by anyone with the race key: no personal details in notes.
Each record names a fix by its server id and never changes it; `marks.php` adds its
own time and the series name. Course and series writes stay on the race key.
A decision can only name a fix already on the server (`s:` and its server id), so a
page must say "not on the server yet" for a fix still waiting in a phone's outbox.
The `from` of a "use as" record is what the page says it replaced: the server checks
its format only and does not verify it against the course. A name (`who`) or note
containing `<` or `>` is refused with 400 "bad decision: who" or "bad decision:
note", so a page must check both before sending.
~~~~

## README.md lines 196 to 203: RO key (reworded: it now protects only the unused decisions endpoint)

~~~~text
*RO key.* `pages/marks/ro-key.example.php`, copied on the server to
`/marks/data/ro-key.php` with `CHANGE_ME` replaced: 16 to 64 letters, digits, `-` or
`_`. `marks.php` reads it as text, never runs it, and takes the RO key only from the
`X-RO-Key` header, never from the URL. While it is missing, malformed or still
`CHANGE_ME`, every decision write is refused ("RO key not set on the server"). The
real file is never committed. Backups of `/marks/data/` contain it: keep them outside
the repository and never share them.
`tests/test_marks.py` checks all of this.
~~~~

## README.md lines 215 to 242: Setup: Review name and RO key (removed)

~~~~text
- *Review* (under the series name, closed on every load): "RO or Scorer name" and
  "RO key", each typed once per device and kept on it outside the saved state, so
  Clear everything keeps them, like the series name and race key. Each has Save and
  Remove; a new value replaces the old one. The name follows the rules of
  `marks.php` (1 to 40 characters, white space runs made one space, no `<` or `>`, no
  control characters, and here no U+0080 to U+009F either) and goes as `by` with
  every course save while it is valid; with no name the request is as before. The
  RO key must be 16 to 64 letters, digits, `-` or `_`; its field is a password field,
  emptied when Save is tapped whether or not the key was valid, and the key is never
  shown again, never put in a URL, a message or any text the page builds. It is sent
  only as the `X-RO-Key` header of a review decision write (see *Recording review
  decisions* below), read from storage at that moment, and on no other request.
  Both are stored in clear text in this device's browser storage, like the race key,
  so anyone with the device can read them: if a device that holds the RO key is
  lost, change the RO key on the server. A name sent as `by` is stored with that
  course version and is readable through `?type=courses` and `?type=coursehistory`
  with the race key, so it is effectively public to anyone with the race key.
  A decision write does not go through `keyFetch`, which treats every 403 as a race
  key that may have changed, re-reads `key.js` and sends again (that retry is left as
  it is): the write reads the error first, and only "bad key", the race key, re-reads
  `key.js` and sends once more. "RO key not set on the server…" shows "Not saved: the
  RO key has not been set up on the server yet." and "bad RO key" shows "Not saved:
  the server did not accept this phone's RO key. Enter it again in Setup → Review.",
  each followed by "Nothing was changed."; after "bad RO key" the Review line reads
  "key refused by the server" until the key is saved again or removed, or a write is
  accepted (the key is kept, not deleted). Each shows beside the decision in the fix
  detail and in Review. With no key saved, the decision actions say "Enter the RO key
  in Setup → Review to record decisions."
~~~~

## README.md lines 261 to 267: Check recorded marks: the tapped fix's detail, with the review decisions under it (reworded)

~~~~text
  fix of a switched-off race is deselected. Tapping a fix gives its
  name, race, time, accuracy, phone (lettered A, B… by first fix of the day),
  recorder, position, and how old the position was when saved: the fix id starts
  with the phone's clock, so id time minus the fix's time, falling back to when the
  server received it. The detail, with the review decisions under it, sits directly
  under the sketch or chart, above its key and notes; tapping a fix in the sketch or
  the list scrolls it into view.
~~~~

## README.md lines 307 to 429: Reading and recording review decisions, Use as, Undo, Earlier records (removed)

~~~~text
  **Review decisions (reading them).** With every Get latest marks and 30 s refresh,
  after the fixes and courses, the page reads the loaded day's review decisions
  (`?type=decisions`, race key only) and shows them as a separate layer; reading
  them never uses the RO key, and changes no line, line-end pick, course, leg or
  output; it adds a warning with the legs where the selected start still uses a
  fix marked do not use (below). They are held in memory for that day only
  (nothing is stored on the phone) and Clear everything empties them; a past day
  gets no 30 s refresh, so tap Get latest marks again there. A line under the plot
  gives their state: how many are in force, undone and replaced, how many records
  the day holds of the server's 2000, and "as of" the
  last read; with no signal or a refused key the last read is kept and says it
  could not refresh; an older `marks.php` gives "This server does not keep review
  decisions yet". What is in force, in the order written: an undo (revoke)
  cancels the record it names; for
  each race, start and role (committee boat, Start Pin, finish committee boat,
  Finish Pin, Windward, Leeward, Gybe) the latest use-as or accept not undone
  applies and earlier ones are "replaced by a later decision" (undoing the latest
  lets the one before apply again). A use-as for Windward, Leeward or Gybe course
  rows is the exception: it replaces only the rows it lists, so it is kept per race,
  start, role and the fix it replaced, and two use-as replacing different fixes in
  one start (a deliberate second Leeward, say) both apply; one that replaces the fix
  an earlier use-as put in replaces that earlier one. A fix is "do not use" for the
  whole day while it has a do-not-use not undone. Records the page does not
  understand are counted and
  ignored. Under each fix in the list: "✓ accepted as Race 1 Start 1 Leeward",
  "→ used for Race 1 Start 1 Leeward" or "✗ do not use: reason" (the fix's row struck
  through), with who and when; the fix's detail gives its whole review history:
  the records in force, with who and when, then a closed "Earlier records (N)" with
  the undone and replaced records and the Undo records (it stays open or closed as
  left, also when another fix is tapped). Under the plot, kept apart from the page's
  own checks, the review flags (⚑), never corrected by the page: the start's course
  rows or its line end in use (chosen, inherited or automatic) differ from the use-as
  or accept that applies (for a use-as of rows, one of the rows it lists no longer
  holds its fix); a do-not-use fix still used by a course row (directly or
  as a laid mark) or by a start's line end in use; a decision naming a fix no longer
  on the server. Information only, not counted: the box's default lines still
  joining a do-not-use fix (the defaults ignore the review); a decision for a fix of
  another race or recorded after that start; two decisions for one start and role;
  do not use and use as on the same fix. The closed line adds "N review decisions"
  (in force, for the race shown or all races) and "N review flags", never adding
  them to the fixes to check or the candidates. On the sketch and the chart, a fix
  marked do not use has its fill faded with a grey strike (on the chart a grey dashed
  outline, or the warning colour when it is also likely wrong), and a fix accepted or
  used for a start has a ✓ or → beside it, placed after the labels; in All races the
  short labels add " ✗", " ✓" or " →R1S1", and the labels make room for it. A fix
  that a decision in force takes from another race for a start of a race shown (the
  Race 3 Leeward used for Race 1 Start 1, say) is plotted dashed like a carried fix
  and labelled "used by review for…"; it can be tapped, but no line is drawn to it
  and it is not counted. With All races it is added only when its own race is
  switched off and the race that uses it is on. The key names these only while a
  decision is in force.
  **Recording review decisions.** Under a tapped fix's detail, for the race and
  start selected in the pickers (also with *All races* ticked), every button and
  preview naming its target: *Accept as Race 1 Start 1 Windward*, once for each role
  in which that start uses the fix now (a line end its outputs use, chosen,
  inherited or automatic, or a Windward, Leeward or Gybe course row; a laid mark has
  no role in the review; not for a fix marked do not use, which is undone first);
  *Do not use* the fix, for the whole day, with a reason (required); *Use as* (below);
  *Undo* a decision in force, a do-not-use, one for the selected start, or a use-as
  of the selected race (a decision replaced by a later one says to undo that one
  first). A note is optional on Accept, Use as and Undo; names and notes are readable
  by anyone with the race key, so no personal details. Only Use as and its Undo
  change a course, and only its rows; none of these changes a line end, a recorded
  fix or the box's lines. A do-not-use fix stays in automatic line-end picks
  and in the course builder's offers. Where the selected start still uses it, in a
  course row (directly or as a laid mark following it) or as a line end its outputs
  use (committee boat, Start Pin, finish committee boat or Finish Pin; chosen,
  inherited or automatic), a warning with the legs, "Legs need updating", names the
  fix, who and when, the rows and line ends, and whether the race has another fix
  of that mark type ("Race 1 has no other Leeward fix"), and says how to change
  them: Use as for Windward, Leeward or Gybe rows (or the course chips); for now
  the course chips for other marks, the laid mark's Position list, or the line-end
  choices. The legs, total, sketch, SailScoring table and Send text keep their
  numbers until then; the note above the SailScoring table (not copied) adds a line
  naming the fix. The same shows as a review flag in Check recorded marks, for every
  start. The warning goes when the decision is undone or the rows and line ends no
  longer use the fix, and comes back from the server after a reload. While the day's
  decisions cannot be read, a line with the legs says so ("a fix marked do not use is
  not flagged here"), or "as of" the last read that could not be refreshed.
  *Use as*: tap the fix to use instead (a Windward, Leeward or Gybe); it offers
  *Use as Leeward in Race 1 Starts 1, 2, 3, in place of the R1 11:03 Leeward* for
  each fix of the same mark type marked do not use that the selected race's course
  rows use. It works on the selected race only: where such a fix is used by other
  races' rows instead, the panel says so ("…is used by Race 1 Starts 1, 2, 3, not by
  Race 2. Select Race 1 to replace it there."). It replaces ONLY the rows that
  point at that fix, in every start of the race that uses it, each row keeping its
  side, so a deliberate second Leeward is never overwritten. A deliberate limit of
  this version: it is offered only in place
  of a fix marked do not use; correcting a fix that is not is done with the course
  chips, and Use as may be widened to that later. A laid mark following a fix, and
  line ends, are not replaced here. The preview lists each start with its rows, its
  legs and total before and after (worked out without changing anything), and
  whether its warning clears. One review decision is recorded per start (their ids
  share a prefix), sent one after another; a start's rows change only once its own
  decision is saved, and the course is then saved as usual, with the name as "by".
  Just before each send that start is checked again; one whose rows changed since
  the preview is not sent and says so. The first failure stops the run: the starts
  saved so far stay saved, and Retry sends the rest with the same records. Leaving
  the page, the fix, the race or the day while a failed action waits for Retry drops
  its unsent records, and a new action then uses new record ids (if an earlier
  answer was lost, that start can end up with two use-as records, the later one
  replacing the earlier). The
  whole action is refused before anything is sent if the day's records plus its own
  would pass the server's limit of 2000. A use-as records its rows by position in
  the course at that time. Its *Undo* (each start, or all starts of one action
  together) records a revoke and puts those rows back to the fix they held, sides
  kept; it is refused for a start where one of those rows no longer holds the
  replacement (change it with the course chips; the course history keeps the
  earlier versions).
  Before anything is sent the page
  checks the Review name and RO key are saved, that the fix is on the server ("not
  on the server yet" for one still waiting on a phone) and that the day's decisions
  have been read; then it shows a preview (for Do not use, every start still using
  the fix, where a flag will show; for Use as, as above) with Confirm and Cancel.
  Confirm checks again, makes the record with its own id and sends it, with the race
  key and the RO key.
  There is no queue on the phone: a write that fails (no signal, a refused key, the
  server refusing the record, the day's limit) changes nothing and says so, and
  Retry sends the same record with the same id, so one whose answer was lost is not
  written twice. After every write, failed or not, the day's decisions are read again
  at once (a past day has no 30 s refresh). The preview, a record kept for Retry and
  the messages are page state only: nothing is stored on the phone, a decision is
  never counted as not sent, and Clear everything drops them.
~~~~

## README.md lines 434 to 438: Setup view: the last sentence, other fixes of the same mark in use (removed in dd86687; from 2aec398, not part of the experiment)

~~~~text
  loaded, at the dock say, is kept when they load. A course row whose fix comes
  from another race, earlier or later, names it, e.g. "Leeward (R3 14:39)"; a second
  fix of the same race reads "(fix 2)". Tapping a fix in *Check recorded marks* also
  lists the starts of that race that use a different fix of the same mark
  (information only).
~~~~

## README.md lines 453 to 455: Legs: legPts and "the review's previews" (reworded)

~~~~text
  The legs of any race and start are worked out by one function that only reads
  the page's state (it changes no course, choice or output), so the review's
  previews, when they come, will give the same figures as the legs table.
~~~~

## README.md lines 484 to 486: Clear everything: the Review name and RO key (reworded)

~~~~text
  courses saved there come back with Get latest marks. The series name and race key
  last seen, and the Review name and RO key, are kept (none of them is counted as
  not sent). If this phone holds fixes not yet sent or course edits not
~~~~

## README.md lines 589 to 594: Tests: the RO key, course history and decisions (reworded)

~~~~text
It also checks the RO key (missing, malformed, wrong, right, header only), the course
history (first plus last 5, the 5 MB cap, an identical save writing nothing, a failed
history write refusing the save, saves arriving at once), the decisions (every field
validated, a malformed record writing nothing, a retry writing nothing, the daily
cap, revoke) and that every request the current RIB and RO pages send is accepted
as before. The race key and RO key in its throwaway folders are made at run time.
~~~~

## README.md lines 610 to 613: Tests: the storage key names, with ro-name and ro-key (reworded)

~~~~text
refused and leaves an earlier build untouched. It also checks that the page's
storage key names (what follows `STORE+`) are exactly the known list, `pv-`,
`race-key`, `course-plot-v1`, `course-series`, `ro-name` and `ro-key`, so a key
added or dropped must update the test. Needs no PHP and no browser.
~~~~

## README.md lines 682 to 687: Parallel test install, step 5: the test RO key (reworded)

~~~~text
5. Once a `marks.php` with the RO key is installed there: place
   `/marks-test/data/ro-key.php` by hand, exactly two lines, `<?php` and
   `return '...';`, with a TEST RO key of 16 to 64 letters, digits, `-` or `_`,
   **different from the live RO key**. Check
   `https://tradboats.ie/marks-test/data/ro-key.php` is refused (403) or blank,
   never showing the key.
~~~~
