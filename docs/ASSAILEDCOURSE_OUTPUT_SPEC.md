# AsSailedCourse: page rules and export to Sail Scoring

Draft, 10 October 2026.

## Purpose

The course plot page keeps the AsSailedCourse: the course a start was actually sailed over, built from the marks recorded on the day. It exports that course to Sail Scoring as an ORC constructed course, the format in `docs/design/orc/constructed-course-format.md` (Sail Scoring #667, commit 6302f85). This page sets out the rules the page follows, how its data maps onto that format, and what is still open. Items marked **Pat** or **Mark** need a decision from them.

## Page rules

These are Pat's decisions about how the page builds and keeps the course. They don't depend on the export format.

1. **Rule 1.** The page never creates a leg that was not sailed, and never presents an estimated position or leg as measured. A leg it cannot create is flagged.
2. **Measuring.** WGS84 geodesics. Legs to and from a start or finish line are measured from the line's geodesic midpoint.
3. **Finish.** The finish is never applied by default. Finishing on the start line is the first option for the RO; until the RO chooses, the finish is "Line not set". A finish always has a previous mark. A shortened course ends at the as-sailed finish. (Changed 26 Oct 2026, see LINE_RULES.md.)
4. **Lines.** Both ends known: measure from the midpoint. One end recorded: using that end as the midpoint estimate is the RO's tap, never automatic; the legs are then flagged "estimate - one end missing". Neither end recorded: the legs touching the line cannot be created. (Changed 26 Oct 2026, see LINE_RULES.md.)
5. **Line sides.** Port and starboard are calculated once, when the AsSailedCourse is established, stored with it, and not shown or exported. Start: look from the midpoint towards the first mark. Finish: look from the previous mark towards the midpoint. A flip between start and finish is possible if the approach direction is reversed. A near-parallel line is an anomaly.
6. **Start time.** Each start holds an actual start time. A start without one is not exported, and the page says so, with a visible "start time missing" warning, because it may be a valid race. Starts skipped for other reasons are listed with their reason.
7. **Race date.** The date of the actual start time, in Irish local time. It is used to convert between true and magnetic.
8. **Stored course (proposed).** The AsSailedCourse keeps its positions, each with when it was recorded (`recordedAt`), where it came from and its accuracy. A moved mark is two positions, and each leg records which one it used. The export is built from the stored course, never recomputed from live state.
9. **Leg table.** The page's own leg table shows a leg it cannot create as a dash row, and labels the total "Legs between placed marks" when any leg is missing.

Three records are in play and are easy to confuse. The **saved day record** on the server holds the fixes, courses, history and notes about skipped starts. The **AsSailedCourse** is the saved course for one race and start, inside it. The **export** is the small document sent to Sail Scoring, derived from the AsSailedCourse.

## Export to Sail Scoring

The export is one JSON document per start, in Mark's ORC constructed course format. Every direction in it is magnetic, and it carries legs only, with one optional anchor position.

| Page | Document field |
| --- | --- |
| Fixed text | `format: "orc-constructed-course"`, `version: 1`, `north: "magnetic"` |
| Race and start label | `name` (shown when importing) |
| Start line midpoint, or the recorded end if only one end is recorded | `anchor { lat, lng }`, WGS84 decimal degrees |
| Each leg's distance, to 0.01 nm | `distance` |
| Each leg's bearing, converted from true to magnetic at the race date | `course` |
| The course wind direction, as read on the compass, written on every leg | `windDirection` |
| Wind speed in knots, if recorded, written on every leg | `windSpeed` |
| Leg label such as "Start - Windward" | leg `name` |

Wind direction and wind speed go on every leg or on none. Marks, sides, line ends, recorded times, flags and the start identity are not exported. They stay in the page.

Example, 27 September 2026 Race 1, using the numbers the page sent that day:

```json
{
  "format": "orc-constructed-course",
  "version": 1,
  "name": "Autumn League, Sun 27 Sept 2026, Race 1, Start 1",
  "north": "magnetic",
  "anchor": { "lat": 51.781475, "lng": -8.234750 },
  "legs": [
    { "name": "Start - Windward",   "distance": 0.67, "course": 282, "windDirection": 280 },
    { "name": "Windward - Gybe",    "distance": 0.78, "course": 144, "windDirection": 280 },
    { "name": "Gybe - Leeward",     "distance": 0.73, "course": 48,  "windDirection": 280 },
    { "name": "Leeward - Windward", "distance": 1.01, "course": 278, "windDirection": 280 },
    { "name": "Windward - Leeward", "distance": 1.01, "course": 98,  "windDirection": 280 },
    { "name": "Leeward - Finish",   "distance": 0.34, "course": 271, "windDirection": 280 }
  ]
}
```

The legs total 4.54 nm. Because the wind is read on the compass and the course comes from positions, the variation used to convert the course to magnetic goes straight into each leg's wind angle (ORC scores wind direction minus course).

## What the format cannot carry

`distance` and `course` are required on every leg, and there is no flag field. So the format has no way to carry a leg the page could not create, or one it estimated.

**Proposed handling (Pat to decide):**

- **Missing leg.** Export the legs the page can create, leaving the missing leg out, and put a loud warning in the document `name`, for example "INCOMPLETE - start line not recorded, first leg (Start - Windward) missing". The `name` is shown when importing, and the scorer adds the leg by hand. The page shows the same warning and the dash row.
- **Estimated leg (one line end recorded).** Export its numbers with the same kind of warning in the document `name`.
- **Never silent.** Any gap or estimate appears in the `name`, so the scorer sees it before applying the course. Leg names are printed on published pages, so flags don't go there.

The alternative is to refuse the export when a leg is missing. Pat's view is that this makes the recorded data nearly unusable, so it is the least preferred.

A reader ignores fields it doesn't know. An extra field such as a list of flagged legs would therefore be harmless, but Sail Scoring wouldn't show it.

## Open items

**Pat**

1. **Course length.** Mark's spec says the course length is the sum of the legs, each written to 0.01 nm, with no declared total, citing ORC rule 401.3. Pat's rule is the rounded sum of the exact legs. They agree on 27 September (4.54 nm) and can differ elsewhere. Which does ORC's rule say?
2. **Course precision.** Whole degrees magnetic, as the page's leg table sends today, or one decimal? The format accepts either.
3. **Variation.** The page's `varW()` is an Irish-fitted formula using today's date. It should use the race date, and be compared with WMM for Cork in 2026, because it feeds each leg's wind angle.
4. **Wind.** Which figure the export carries, and what happens when wind is blank (the document then carries no wind at all, and the scorer's course wind fills the legs).
5. **Missing and estimated legs.** Confirm the proposed handling above.
6. **Early outputs against the stored-course rule.** Legs are not stored yet. Decide whether the first export may be built from live state, labelled as such, or whether storing legs comes first.
7. **Master copy.** Which of the Claude Doc and the file in the repo is the master.

**Mark**

1. When does the new import ship, and does the old paste box keep working until the page emits this format?
2. Can the document carry a course-level note for warnings, shown on import and not published?
3. Does the sum-of-legs rule match ORC's own, given Pat's rule above?
4. Please send feedback on the two test files made from the 27 September course, a complete one and one with the start line missing.
