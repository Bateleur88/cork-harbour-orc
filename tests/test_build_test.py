#!/usr/bin/env python3
"""Tests for scripts/build_test.py, the parallel TEST copy of the race officer page and marks.php.

    python tests/test_build_test.py

Builds from the repository's page into a throwaway folder and checks the result, then feeds the script pages
altered in ways it must refuse and checks that it writes nothing:

  0  build      the test page talks only to /marks-test/, prefixes every browser storage key with "test-", shows
                the red TEST banner with its PAGE_VERSION, "TEST" in the title and noindex; marks.php is copied
                byte for byte; nothing else in the page changed; BUILD.txt names the version and both hashes
  1  live page  the live page itself uses no browser storage key without STORE (so a key added later is caught), and
                the STORE+ key names in its code are exactly STORE_NAMES (a key added or dropped must update the list)
  2  refusals   a storage key without STORE (setItem, getItem, removeItem), any other use of localStorage or
                sessionStorage (bracket access, .clear(), .key(), an alias, window['localStorage'],
                window.localStorage, typeof, passing it as an argument), IndexedDB, document.cookie (also
                document['cookie']), the Cache API, a service worker, a stray "/marks/" path, a missing or doubled
                key.js tag, a missing STORE line, a missing <title>: each is refused, exits non-zero and leaves an
                earlier build in the output folder untouched; a division followed by a call on the same line
                ((a+b)/2;localStorage.setItem('x',1) and var h=x/y;sessionStorage.getItem('z')) does not hide the call
  3  allowed    the same words in comments only, a regex literal holding a quote and "//" before a prefixed call,
                and the two division lines with STORE+ keys, still build
  4  saves      static guards for the course save status in the live page (2026-10-06.25; STATUS A33, A34, A35, A29):
                #saveStatus and #dayAnyway once each; saveCourses has no empty catch, passes the 20 s limit and has its
                day-change mode; postFix reads the server's error, sets .status, keeps "server <status>" and can abandon
                a request; pull waits for a running save (DAY_WAIT_MS) and checks the day-change save's result before
                deleting the old day's courses, and records made for third days stop it too; Clear everything
                resets the save state and names saveStatus and
                dayAnyway; "Race key not loaded yet" has its save message; the comment above Check recorded marks says
                picked chips are saved. Guards, not proof: no JavaScript is run
  5  copy       static guards for "Copy for Sail Scoring" in the live page (2026-10-06.26; STATUS A37): #ccCopy once,
                labelled "Copy for Sail Scoring"; the "Copy legs for SailScoring" button, its line format and its
                copy code unchanged; ccDoc takes its legs from legPts with the leg table's figures and writes nothing;
                buildLegs calls setCC beside each setSS. Guards, not proof: no JavaScript is run
  6  A38        static guards for typed and pasted positions and the queue (2026-10-06.27; STATUS A38): the position
                reader takes ' ′ ’ as the minutes mark; a card row (tabs) is named by its short name; pasted positions
                are marked and get an id ("paste|") no server fix can have; each queued send has the 20 s limit, a
                refusal (400, 429) goes to the "Not sent" list and the queue carries on, anything else stops it;
                #notSent once, moved with the committee boat button, drawn on every render, reset by Clear everything;
                Clear everything counts "Not sent" fixes and pasted positions; the 8 nm flag is measured from
                51.82 N 8.27 W and only for typed and pasted positions; a missing mark stays a row ("Mark missing"),
                its legs are not measured, Copy for Sail Scoring names them INCOMPLETE and anchors on the first measured
                leg, and a row naming a fix that is gone keeps its reference; the count is split into recorded fixes and
                other marks, and flagged ones are "fixes and marks to check"; Copy for Sail Scoring's name is the race
                name first, then the warnings in short form, the full ones beside the button; the approved wording is
                present. 2026-10-06.28: the typing message follows its fix (sent, refused, waiting, sending again,
                removed), the line under Get latest marks splits recorded fixes and typed positions, and a pasted
                position's detail says it is a chip of its race. 2026-10-06.29: so does a typed position's, and no
                detail says "Not offered as a chip". Guards, not proof: no JavaScript is run
  7  A40, A45   static guards for fixed marks and far positions (2026-10-06.30; STATUS A40, A45): the embedded snapshot
                has all 63 marks of the Marks sheet, its authored routes and its courses are exactly v3.19's (frozen
                hashes), plus exactly 85 reversed routes, each the reverse of a one-way authored route; no Position
                Source, Source URL or Verification / Use text is in the page; Copy for Sail Scoring (ccDoc, setCC) and
                the SailScoring lines (setSS) are unchanged from 2026-10-06.29; card marks are added only where a mark
                is tapped, imported or named by a row (never every mark at once); the page never reverses a route itself;
                the Fixed marks fold is there, closed; the WhatsApp text has no analysis, wind, route notes or labels;
                the approved wording is present; far positions are named under Check recorded marks and drawn "off the
                plot". Guards, not proof: no JavaScript is run
  8  .31        static guards for the five fixes after Pat's test of 2026-10-06.30-test (STATUS A40): Course Card marks
                are not carried into later races' chips; every race drawn gets its All races switch (Course Card marks
                and the selected race's course too); the paste box and the typing box refuse a card mark's own name
                (laid marks excepted, no other names) and store nothing, the typing box before it asks for a position;
                a routing waypoint with nothing on one side is warned on its row, belongs to no leg and makes Copy for
                Sail Scoring INCOMPLETE (ccDoc changes by that one line only); the laid-mark notice's earlier total
                takes a leg through RO-chosen waypoints with roLeg. Guards, not proof: no JavaScript is run
  9  .32        static guards for the follow-ups after Pat's test of 2026-10-06.31-test (STATUS A40, A45): the WhatsApp
                heading's date is the Race day box (never S.date) and follows it at once; routing waypoints are not
                carried either; one line per refused name; the refusal's second sentence by kind (a buoy, or a point:
                Grassy Mid and the routing waypoints); no "(planning position)" or "(RIB fix …)" in the WhatsApp text;
                the laid-mark notice names each source in words and says when nothing moved; a far typed or pasted
                position is left out of the magnetic variation. Guards, not proof: no JavaScript is run
 10  .33        static guards for the changes of 13 October 2026 (STATUS A40, A46, A47, A11): a course with a missing
                mark or a leg not measured is held back from competitors (#sendWarn; WhatsApp, Share and Copy text each
                ask "Send anyway?"; all three greyed when there is nothing to send); Spit Bank Lighthouse (a fixed light)
                is a point in the refusal; a laid mark's pasted or typed fix named as such in its chip, position box and
                leg note; a × on a card-mark chip only while unused; Withdraw and Correct of a typed position (A46: the
                server actions, the confirmation, the in-use refusal, withdrawn fixes never loaded, rows following a
                correction); pasted positions in red where used with "Save to the race record", no duplicate saved, the
                card-name refusal applied (A47); a saved typed position counts for its laid mark; the magnetic variation
                for the Race day, not today (A11). Guards, not proof: no JavaScript is run
 11  .34        static guards for the changes after Pat's test of 2026-10-06.33-test (STATUS A11, A40, A45, A47): Share
                and Copy text greyed like WhatsApp when switched off; the magnetic variation from the World Magnetic Model
                (WMM2025, the 90 coefficient lines exactly as the official WMM.COF, by their SHA-256) at the map centre for
                the day loaded, never from the marks loaded; a far typed or pasted position in a course holds Send back;
                the WhatsApp heading's date is the day loaded, and a Race day changed but not loaded is said and holds Send
                back; a pasted line matching a saved position makes no chip and says so; typed and pasted positions are
                never checked for their age; a leg through RO-chosen waypoints names a laid mark's fix on the physical leg
                touching it; every start with a saved course is shown. Guards, not proof: no JavaScript is run

 22  .38        static guards for A8 (the series name per race day, T21) and T20 (group 22): the day's _day record
                saved and loaded by the course-save machinery; no series.json and no series refresh; the device's old
                series name removed; carried from the latest earlier day with Confirm, the first save's question,
                "No series set for this day"; the outputs use the day's own series; a day loaded opens Start 1 or its
                first start with a course. Guards, not proof: no JavaScript is run
 23  worker     the course page's service worker (STATUS A65, group 23): the test build writes course-test/sw.js, the
                live worker with only its key.js line changed to /marks-test/key.js, and BUILD.txt names its hash; the
                live worker names /marks/ only in that line; neither names a "record-" cache; the cache is named
                "coursepage|"+folder+"|"+version and the clean-up deletes only caches of exactly its own folder, so the
                test worker's can never match a /course/ cache (the rule also run on sample names); a page is kept only
                if its PAGE_VERSION is the worker's own, at install and on refresh; the kill switch deletes only its own
                folder's caches and unregisters; a saved copy keeps Content-Type only, with status 200 (no
                Content-Encoding or Content-Length from the server). Refusals: a worker with no key.js line, a stray
                /marks/ path, a "record-" cache or no own-version check, or whose answer to the browser waits on
                reading a copy of it (the A65 Step 23 stall), and a page registering a worker twice or in any other
                form; the one registration form builds. Guards, not proof: no JavaScript is run
 24  .39        static guards for A65 in the page (group 24): it registers the worker in exactly the one form, once; the
                font stylesheet does not hold the page; saveCourses holds every save until the version is confirmed and
                starts the check, before anything is sent; the change of day checks the version first and stops with its
                own message and no "Change day anyway"; withdraw, correct, move, Undo's and Remove Start's withdrawals
                wait for it (verReady) before they post; new fixes (sendOutbox) and Send (freezeSend) never wait; once
                confirmed the check never runs again; a newer page reloads at most once a minute and twice in all, and
                never where sessionStorage fails; the waiting and stuck lines and the Reload button. Guards, not proof:
                no JavaScript is run
 25  .40 A78    static guards for withdrawing placed line ends (group 25): the fix detail of a typed or placed line end
                offers Withdraw (never Correct) only when it is no start's estimate, or still has its estimate or set-pin
                record but no start uses it (lineUsers with placed); a withdrawal there takes that record with it before
                the reload; placing an end again, or setting the Start Pin again, hands the replaced end to
                withdrawReplaced, which checks every use, the sending state and the page version before posting the
                withdrawal with "replaced by placing again", and leaves a note under the end's list (this device only)
                on every way out short of withdrawing it; the placement itself never waits. .41: the replaced end is
                saved with its start (lineGone) before any withdrawal, read as a placed estimate or set pin (estOf,
                setOf), labelled ", replaced", left out of auto and the earlier-race offer, still offered Withdraw;
                every withdrawal, Undo and Remove Start handle it; an entry whose fix is gone from its race is removed
                on load, saved and said (checkGoneRefs), and Remove Start never withdraws a fix already gone. Guards,
                not proof: no JavaScript is run
 28  LOCAL      --label LOCAL, the local test site's build: PAGE_VERSION <version>-test-L<HHMM>, "LOCAL TEST" banner and
                title, BUILD.txt says LOCAL; nothing else differs from the normal build, whose worker and marks.php it
                shares byte for byte. Refused in a LOCAL build (and written nothing), but built normally: tradboats.ie or
                orc-ireland.org named anywhere (a comment too), a full web address not in LOCAL_URLS, one starting //,
                and one that only begins like an allowed host; an unknown label or a build time not HHMM is refused
 29  pins       static guards for the pin routes in .44 (Pat, 22 October 2026): with a committee boat in use, both Set
                Start Pin at and Place Start Pin; the Start Pin's "from" list is the committee boat in use and this race's
                laid marks only, a held harbour-mark "from" refused; an earlier race's Start or Finish Pin set at its
                position; Place Finish Pin from the committee boat end in use only, saved, read and shown as an estimate;
                the committee boat placed from a harbour mark sets the Start Pin at it, and with another pin in use
                nothing is placed; one pin record per start; saved data read as before. Guards, not proof
 30  .45        static guards for .45 (Pat, 23 October 2026): A117, box 2's suggestions on its "from it" line and Set pin
                and place boat bigger and bold on its own line; A118, box 3's list gives a recorded fix's accuracy, none for a
                typed position; A119, a green "…: sent." message, and the line under Record committee boat when all it says
                is what was sent, clears after SENT_CLEAR_MS if unchanged, never a red, amber or not-sent one
 31  .45b       static guards for .45b (Pat, 23 October 2026): A121, box 3 laid out as box 2 (its Suggest buttons on the
                line, Use the boat and place the pin bigger and bold on its own line, its message under it); A122, how
                square the first mark after the start is to the wind, from the start line's midpoint, named, with a note
                and no figure when there is no start line
 32  .46        static guards and builds for .46 (Pat, 23 October 2026): A123, "Line not set" in red beside the Start line
                heading while a start that needs a committee boat and Start Pin lacks either, and section 4's first-mark
                note in amber; A80, the manifest link and theme colour in the page, the live manifest's fields, the icon
                sources and their sizes; the test build writes the test manifest (TEST names, /course-test/ only) and the
                TEST icons byte for byte, and refuses a live manifest not naming /course/, a page whose manifest link is
                not relative, and a missing test icon; the worker still handles only the page and key.js
Needs no PHP and no browser. Exits non-zero if any test fails.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'build_test.py')
PAGE = os.path.join(ROOT, 'pages', 'course', 'course_v8.html')
SW = os.path.join(ROOT, 'pages', 'course', 'sw.js')
SW_KILL = os.path.join(ROOT, 'pages', 'course', 'sw-kill.js')
MARKS = os.path.join(ROOT, 'pages', 'marks', 'marks.php')
# every browser storage key name the page writes after STORE ('pv-' is followed by a PAGE_VERSION). The Review name and
# RO key (ro-name, ro-key) went with the review decisions in 2026-10-06.20; the page no longer reads or writes them.
# From 2026-10-06.38 (A8) course-series is only removed, never read or written
STORE_NAMES = {'pv-', 'race-key', 'course-plot-v1', 'course-series'}
failed = []
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_test import SW_REGISTER, SW_KEY_LIVE  # noqa: E402  the one registration form and the worker's key.js line


def report(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + (': ' + detail if detail and not ok else ''))
    if not ok:
        failed.append(name)


def run(page, out, sw=SW, label=''):
    return subprocess.run([sys.executable, SCRIPT, '--page', page, '--sw', sw, '--marks', MARKS, '--out', out]
                          + (['--label', label] if label else []), capture_output=True, text=True, encoding='utf-8')


def read(p, mode='r'):
    with open(p, mode, **({} if 'b' in mode else {'encoding': 'utf-8', 'newline': ''})) as f:
        return f.read()


def t0_build(tmp):
    out = os.path.join(tmp, 'out0')
    r = run(PAGE, out)
    report('0 build exits 0', r.returncode == 0, r.stdout + r.stderr)
    if r.returncode:
        return
    live, test = read(PAGE), read(os.path.join(out, 'course-test', 'index.html'))
    v = re.search(r"const PAGE_VERSION='([^']+)';", live).group(1)
    checks = {
        'key.js from /marks-test/': '<script src="/marks-test/key.js"></script>' in test,
        'MARKS_BASE and STORE': "const MARKS_BASE='/marks-test/', STORE='test-';" in test,
        'PAGE_VERSION -test': f"const PAGE_VERSION='{v}-test';" in test,
        'no /marks other than /marks-test/': not re.search(r'/marks(?!-test/)', test),
        'banner with version': f'PAGE_VERSION {v}-test</div>' in test and 'TEST COPY – not live data' in test,
        'TEST title': '<title>TEST – ' in test,
        'noindex': '<meta name="robots" content="noindex,nofollow">' in test,
        'marks.php byte-identical': read(os.path.join(out, 'marks-test', 'marks.php'), 'rb') == read(MARKS, 'rb'),
        'BUILD.txt': f'PAGE_VERSION {v}-test' in read(os.path.join(out, 'BUILD.txt')),
    }
    for k, ok in checks.items():
        report('0 ' + k, ok)
    # nothing else changed: undo the known replacements and compare with the live page
    back = (test.replace('<script src="/marks-test/key.js"></script>', '<script src="/marks/key.js"></script>')
                .replace("const MARKS_BASE='/marks-test/', STORE='test-';", "const MARKS_BASE='/marks/', STORE='';")
                .replace(f"const PAGE_VERSION='{v}-test';", f"const PAGE_VERSION='{v}';")
                .replace('<title>TEST – ', '<title>')
                .replace('<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">', '<meta charset="utf-8">'))
    back = re.sub(r'<body>\n<div id="testBanner"[^\n]*</div>', '<body>', back)
    report('0 nothing else changed', back == live)
    # the worker (STATUS A65): only its key.js line differs from the live one
    lw, tw = read(SW), read(os.path.join(out, 'course-test', 'sw.js'))
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    report('0 worker: key.js from /marks-test/', tw.count(build_test.SW_KEY_TEST) == 1)
    report('0 worker: no /marks other than /marks-test/', not re.search(r'/marks(?!-test/)', tw))
    report('0 worker: nothing else changed', tw.replace(build_test.SW_KEY_TEST, build_test.SW_KEY_LIVE) == lw)
    report('0 worker: BUILD.txt names its hash', 'course-test/sw.js      sha256 ' in read(os.path.join(out, 'BUILD.txt')))


def t1_live_page():
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    problems = build_test.storage_problems(read(PAGE))
    report('1 live page: every storage key uses STORE', not problems, '; '.join(problems))
    names = set(re.findall(r"\bSTORE\s*\+\s*'([^']*)'", build_test.strip_comments(read(PAGE))))
    report('1 live page: STORE+ key names are exactly STORE_NAMES', names == STORE_NAMES,
           f'unexpected {sorted(names - STORE_NAMES)}, missing {sorted(STORE_NAMES - names)}')


def fn_body(src, head):
    """The source of the function that starts with head, up to the next top-level function ('' if not found)."""
    i = src.find(head)
    if i < 0:
        return ''
    j = re.search(r'\n(?:async )?function |\n\$\(', src[i + len(head):])
    return src[i:i + len(head) + (j.start() if j else len(src))]


def t4_save_guards():
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    report('4 saves: id="saveStatus" exactly once', page.count('id="saveStatus"') == 1)
    report('4 saves: id="dayAnyway" exactly once', page.count('id="dayAnyway"') == 1)
    sc = fn_body(code, 'async function saveCourses(')
    report('4 saves: saveCourses found', bool(sc))
    report('4 saves: saveCourses has no empty catch', not re.search(r'catch\s*\(\s*\w*\s*\)\s*\{\s*\}', sc))
    report('4 saves: saveCourses passes the 20 s limit', 'SAVE_TIMEOUT_MS' in sc and 'SAVE_TIMEOUT_MS=20000' in code)
    report('4 saves: saveCourses has its day-change mode', 'dayMode' in sc)
    pf = fn_body(code, 'async function postFix(')
    report('4 saves: postFix reads the server error and sets .status',
           bool(pf) and '.error' in pf and 'e.status=' in pf and 'e.text=' in pf)
    report("4 saves: postFix still throws 'server '+status", "new Error('server '+r.status)" in pf)
    report('4 saves: postFix can abandon a request', 'AbortController' in pf and '.abort()' in pf)
    pl = fn_body(code, 'async function pull(')
    a = pl.find('saveCourses(true,k=>!mine(k),true)')
    o = pl.find('otherDayKeys(', a + 1)
    b, c = pl.find('blockDay(', o + 1), pl.find("['courses','startTimes'")
    report('4 saves: pull checks the day-change save before deleting the old day', -1 < a < b < c, f'{a} {b} {c}')
    report('4 saves: pull checks records made for third days before deleting', -1 < a < o < b < c, f'{a} {o} {b} {c}')
    report('4 saves: blockDay takes the third-day records', 'function blockDay(from,to,res,left,other,quiet)' in code)
    report('4 saves: pull waits for a running save', 'savingP' in pl and 'DAY_WAIT_MS' in pl and 'DAY_WAIT_MS=25000' in code)
    cp = fn_body(code, 'function clearPageState(')
    report('4 saves: Clear everything resets the save state',
           all(x in cp for x in ('saveState=', 'saveStop=false', 'dayDrop=null', "'saveStatus'", "'dayAnyway'")))
    report('4 saves: "Race key not loaded yet" has its save message', 'Race key not loaded yet.' in fn_body(code, 'function saveLines('))
    report('4 saves: the comment above Check recorded marks says picked chips are saved',
           "saved with the race's start groups); one element for both views" in page and 'chip bank (page' not in page)


def t5_copy_guards():
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    report('5 copy: id="ccCopy" exactly once, labelled "Copy for Sail Scoring"',
           page.count('id="ccCopy"') == 1 and 'id="ccCopy" style="grid-column:1/-1">Copy for Sail Scoring</button>' in page)
    report('5 copy: the "Copy legs for SailScoring" button unchanged',
           page.count('id="ssCopy"') == 1 and 'id="ssCopy" style="grid-column:1/-1">Copy legs for SailScoring</button>' in page)
    report('5 copy: the leg table line format unchanged', "g.parts.forEach(pt=>ss.push(pt.nm.toFixed(2)+' '+pad(magOf(pt.brg,vr),3)));" in code)   # .36: the course's own variation (A11)
    report('5 copy: the leg table copy code unchanged',
           "await navigator.clipboard.writeText(ssText);$('ssCopy').textContent='Copied';"
           "setTimeout(()=>$('ssCopy').textContent='Copy legs for SailScoring',1500);" in code and
           "ssText=lines.join('\\n');" in fn_body(code, 'function setSS('))
    cd = fn_body(code, 'function ccDoc(')
    report('5 copy: ccDoc found', bool(cd))
    report("5 copy: ccDoc takes the leg table's legs and figures",
           'legPts(r,st)' in cd and 'g.parts.forEach' in cd and 'pt.nm.toFixed(2)' in cd and 'mag1(pt.brg,vc)' in cd and 'vc=varOf(L)' in cd)
    report('5 copy: ccDoc writes nothing',
           not re.search(r'\b(commit|save|stamp|scheduleSave|render|course)\(', cd) and not re.search(r'\bS\.\w+(\[[^\]]*\])?\s*=[^=]', cd))
    bl = fn_body(code, 'function buildLegs(')
    report('5 copy: buildLegs calls setCC beside each setSS', bl.count('setSS(') == 2 and bl.count('setCC();') == 2)


def t6_a38_guards():
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('6 A38: ' + name, ok)
    pp = fn_body(code, 'function parsePos(')
    g('parsePos takes a plain, prime or curly minutes mark', pp.count("\\s*['\u2032\u2019]?\\s*") == 2)
    rp = fn_body(code, 'function readPaste(')
    g('readPaste names a card row by its short name', "line.indexOf('\\t')>=0" in rp and "cols[0].split(' / ')[0].trim()" in rp)
    g('readPaste marks every position pasted and returns them', 'm.pasted=true;push(m);added.push(m);' in rp and 'return added;' in rp
      and 'push({' not in rp)
    g('a pasted id starts with "paste|"', "function pasteId(race,nm,fix){return 'paste|'+" in code
      and 'm.pasted?pasteId(m.race,m.name,m.fix):' in fn_body(code, 'function push('))
    so = fn_body(code, 'async function sendOutbox(')
    g('sendOutbox found', bool(so))
    g('each queued send has the 20 s limit', 'postFix(f,OUTBOX_TIMEOUT_MS)' in so and 'const OUTBOX_TIMEOUT_MS=20000;' in code)
    g('a refusal (400, 429) goes to Not sent and the queue carries on',
      "if(k==='refused'||k==='full')" in so and 's0.notSent.push(' in so and 'continue;}' in so)
    g('anything else stops the queue, keeping every fix', 'stop={f,k,e}; break;' in so and so.count('s0.outbox.shift()') == 2)
    g('sendOutbox has no empty catch', not re.search(r'catch\s*\(\s*\w*\s*\)\s*\{\s*\}', so))
    g('id="notSent" exactly once', page.count('id="notSent"') == 1)
    g('Not sent moves with the committee boat button', "['notSent','slotCB']" in code)
    g('Not sent drawn on every render', 'renderNotSent(); paintMsgs();\n}' in fn_body(code, 'function render('))
    g('notSent in the fresh state (Clear everything resets it)', 'outbox:[],notSent:[]' in fn_body(code, 'function fresh('))
    ut = fn_body(code, 'function unsentText(')
    g('Clear everything counts Not sent and pasted positions', 'S.notSent' in ut and 'S.marks.filter(isPasted)' in ut)
    g('the 8 nm flag: 51.82 N 8.27 W, typed and pasted only', 'const HARBOUR_CENTRE={lat:51.82,lon:-8.27}, FAR_NM=8;' in code
      and 'if(!isOtherMark(m)' in fn_body(code, 'function farNm('))
    lp = fn_body(code, 'function legPts(')
    g('legPts keeps a missing mark as a placeholder', "{id:e.id,name:'mark missing',missing:true}" in lp
      and 'legs.push({missing:true' in lp and 'rows,miss,seq' in lp)
    bl = fn_body(code, 'function buildLegs(')
    g('buildLegs says a leg is not measured, before its total', -1 < bl.find('if(g.missing)') < bl.find('total+=r.nm;'))
    cd = fn_body(code, 'function ccDoc(')
    g('Copy for Sail Scoring names missing legs INCOMPLETE and anchors on the first measured leg',
      'g.missing?' in cd and 'inc.push(' in cd and 'const a=L.pts[i0];' in cd)
    g('section 3 shows a missing mark as a row', "⚠ Mark missing" in fn_body(code, 'function render('))
    g('a row naming a fix that is gone keeps its reference', "return m?m.id:r;}" in fn_body(code, 'function resolveRef(')
      and "if(!m&&/^s:/.test(id))return id;" in fn_body(code, 'function refOf('))
    rf = fn_body(code, 'function renderFix(')
    g('the count is split into recorded fixes and other marks', "'recorded fix','recorded fixes'" in rf and "'other mark','other marks'" in rf)
    g('approved wording: reader message', "' read for Race '" in code and
      "' kept on this device only: not sent to the server, not seen by other devices, and lost if this device is cleared.'" in code)
    g('approved wording: chip', "'pasted position',m.time,accOf(m),'this device only'" in code)
    g('approved wording: Check recorded marks', "'pasted position, on this device only · '" in rf and "'pasted position'" in rf)
    g('Copy for Sail Scoring: the race name first, then the warnings in short form',
      "const name=label+(preS.length?' - '+preS.join('. '):'');" in cd and "'INCOMPLETE - '+incS.join('; ')" in cd
      and "noS&&noF?'start line and finish line':noS?'start line':'finish line'" in cd and "'mark missing: '" in cd)
    g('Copy for Sail Scoring: one count in the name, each leg once, the reasons joined by "; "',
      "n=ml.length+(noS?1:0)+(noF?1:0)" in cd and "incS.push(nOf(n,'leg','legs')+' not measured ('+why.join('; ')+')')" in cd
      # one count for legs not measured; .31 adds one more, for a routing waypoint with nothing on one side (orphanText)
      and sum(1 for x in cd.split(chr(10)) if 'incS.push(' in x and 'orphanText(L)' not in x) == 1)
    g('Copy for Sail Scoring: the full warnings stay beside the button', 'warns:pre.map(' in cd and "'INCOMPLETE - '+inc.join('; ')" in cd)
    g('the check count says fixes and marks', "' fixes and marks')+' to check'" in rf)
    # 2026-10-06.28: three fixes after Pat's test of 2026-10-06.27-test
    ns = code[code.find("$('notSent').onclick="):]
    ns = ns[:ns.find('\n', ns.find("removed from this device.','');commit();};"))]
    g('the typing message follows its fix: sent, refused, waiting', 'function readSays(f,msg,cls)' in code
      and "readSays(f,outRefused(f,why),'err')" in so and "readSays(f,outName(f)+': sent.'" in so
      and "const own=s0.outbox.filter(q=>{readSays(q,outWait(q,stop.k,stop.e),'');return fixSays(q,'wait',outReason(stop.k,stop.e));})" in so)
    g('the typing message follows its fix: sending again, removed',
      "readSays(x.f,outName(x.f)+': sending again" in ns and "readSays(x.f,outName(x.f)+': removed from this device.'" in ns)
    g('readSays changes only a message still about that fix', "actMsgs[x].t.indexOf(outName(f)+':')===0);if(!key)return;" in code)
    pl = fn_body(code, 'async function pull(')
    g('the line under Get latest marks splits recorded fixes and typed positions',
      "nOf(list.length-nTyped,'recorded fix','recorded fixes')" in pl and "nOf(nTyped,'typed position','typed positions')" in pl
      and "list.filter(m=>m.acc===0&&!m.device)" in pl)
    ph = fn_body(code, 'function pickHtml(')
    g('a pasted position\'s detail says it is a chip of its race',
      -1 < ph.find("if(isPasted(m))return") < ph.find('if(!pickable(m))') and "A chip of Race '+m.race+', as a pasted position on this device only." in ph
      and 'Not offered as a chip: \'+(isPasted' not in ph)
    # 2026-10-06.29: a typed position's detail says it is a chip of its race; no detail says "Not offered as a chip"
    g("a typed position's detail says it is a chip of its race, and why it cannot be added to another race",
      "'A chip of Race '+m.race+', as a typed position'" in ph and 'Being typed in by hand, not recorded by GPS' in ph)
    g('no detail line says "Not offered as a chip"', 'Not offered as a chip' not in code)
    g('the RIB page is not touched by this step', 'notSent' not in read(os.path.join(ROOT, 'pages', 'record', 'record.html')))


def t2_refusals(tmp):
    live = read(PAGE)
    out = os.path.join(tmp, 'out2')
    r = run(PAGE, out)                                  # a good build first: a refusal must leave it as it was
    before = read(os.path.join(out, 'course-test', 'index.html'), 'rb') if r.returncode == 0 else None
    script_end = live.rindex('</script>')
    inject = lambda code: live[:script_end] + code + '\n' + live[script_end:]
    cases = {
        'setItem without STORE': inject("try{localStorage.setItem('ro-name','x');}catch(e){}"),
        'getItem without STORE': inject("try{sessionStorage.getItem('undo');}catch(e){}"),
        'removeItem without STORE': inject("try{localStorage.removeItem('ro-key');}catch(e){}"),
        'bracket access': inject("try{localStorage['x']='1';}catch(e){}"),
        'clear()': inject("try{sessionStorage.clear();}catch(e){}"),
        'alias const ls=localStorage': inject("const ls=localStorage;"),
        "window['localStorage']": inject("const s=window['localStorage'];"),
        'window.localStorage': inject("try{window.localStorage.getItem(STORE+'x');}catch(e){}"),
        'typeof localStorage': inject("if(typeof localStorage!=='undefined'){}"),
        'passed as an argument': inject("const keep=s=>s;keep(sessionStorage);"),
        '.key()': inject("try{localStorage.key(0);}catch(e){}"),
        'indexedDB': inject("try{indexedDB.open('x');}catch(e){}"),
        'document.cookie': inject("document.cookie='a=1';"),
        "document['cookie']": inject("const c=document['cookie'];"),
        'Cache API': inject("try{caches.open('x');}catch(e){}"),
        'service worker (any other registration)': inject("try{navigator.serviceWorker.register('sw.js');}catch(e){}"),
        'service worker registered twice': inject(SW_REGISTER + SW_REGISTER),
        'division then setItem, no STORE': inject("(a+b)/2;localStorage.setItem('x',1)"),
        'division then getItem, no STORE': inject("var h=x/y;sessionStorage.getItem('z')"),
        'stray /marks/ path': inject("const OLD='/marks/marks.php';"),
        'key.js tag missing': live.replace('<script src="/marks/key.js"></script>', ''),
        'key.js tag twice': live.replace('<script src="/marks/key.js"></script>', '<script src="/marks/key.js"></script>' * 2),
        'STORE line missing': live.replace("const MARKS_BASE='/marks/', STORE='';", "const MARKS_BASE='/marks/';"),
        'title missing': re.sub(r'<title>[^<]*</title>', '', live),
    }
    for name, text in cases.items():
        p = os.path.join(tmp, 'bad.html')
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        r = run(p, out)
        after = read(os.path.join(out, 'course-test', 'index.html'), 'rb')
        report('2 refused: ' + name, r.returncode != 0 and 'REFUSED' in r.stdout and after == before,
               f'exit {r.returncode}; {r.stdout.strip()[:160]}; earlier build {"kept" if after == before else "CHANGED"}')
    # a worker the build must refuse (STATUS A65), with the good page
    lw = read(SW)
    workers = {
        'worker: key.js line missing': lw.replace(SW_KEY_LIVE, "const KEY='';"),
        'worker: stray /marks/ path': lw.replace("const WAIT=3000", "const OLD='/marks/marks.php', WAIT=3000"),
        'worker: a "record-" cache': lw.replace("const CACHE='coursepage|'+PAGE_PATH+'|'+VERSION;",
                                                "const CACHE='record-'+VERSION;"),
        'worker: no own-version check': lw.replace("return !!VERSION&&!!m&&m[1]===VERSION;", "return !!m;"),
        'worker: the answer waits on reading a copy': lw.replace(
            "const net=fetch(r).then(res=>{copy=res.clone();return res;});",
            "const net=fetch(r).then(async res=>{copy=res.clone();await res.clone().text();return res;});"),
    }
    for name, text in workers.items():
        p = os.path.join(tmp, 'bad-sw.js')
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        r = run(PAGE, out, p)
        after = read(os.path.join(out, 'course-test', 'index.html'), 'rb')
        report('2 refused: ' + name, text != lw and r.returncode != 0 and 'REFUSED' in r.stdout and after == before,
               f'exit {r.returncode}; {r.stdout.strip()[:160]}')


def t3_allowed(tmp):
    """What the check must NOT refuse: the forbidden words in comments only, and a regex literal holding a quote and
    // followed by a prefixed call (the tokenizer must not read the regex as a string or a comment)."""
    live = read(PAGE)
    script_end = live.rindex('</script>')
    inject = lambda code: live[:script_end] + code + '\n' + live[script_end:]
    cases = {
        'words in comments only': inject("/* no document.cookie, indexedDB, caches, serviceWorker or a bare localStorage here */\n"
                                         "// window['localStorage'] and typeof sessionStorage are only mentioned"),
        "regex literal with ' and //": inject("const rx=/a'b\\/\\//;try{localStorage.setItem(STORE+'rx',String(rx));}catch(e){}"),
        'division then setItem with STORE': inject("(a+b)/2;localStorage.setItem(STORE+'x',1)"),
        'division then getItem with STORE': inject("var h=x/y;sessionStorage.getItem(STORE+'z')"),
    }
    cases['the one service worker registration, moved'] = inject(SW_REGISTER).replace(SW_REGISTER, '', 1) \
        if SW_REGISTER in live else inject(SW_REGISTER)
    for name, text in cases.items():
        p = os.path.join(tmp, 'ok.html')
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        r = run(p, os.path.join(tmp, 'out3'))
        report('3 allowed: ' + name, r.returncode == 0, r.stdout.strip()[:200])


# v3.19's routes and courses in the embedded snapshot, as json.dumps(..., sort_keys=True, separators=(',', ':')) hashes:
# a later workbook may only add reversed routes (STATUS A40); anything else changing them must update these on purpose
V319_PAIRS = '89f144a36d7ae872dc8e695ba690f5de18342cb9975094efb14271369dee056e'
V319_COURSES = '28821f64e2df8de1f55bf2290dea6e28169421dc3c8ee55d6a634d76c80fe9cd'
# ccDoc, setCC and setSS as in 2026-10-06.29 (comments stripped, as fn_body reads them)
CODE_29 = {'function ccDoc(': '666634c21f5354bc85f15a22e3453aee1ce92b5dd45179a60070314a57c4a9ea',
           'function setCC(': '14f562a2cf731e9dda272f7e6d6cd0dbb4bddec45c758a1b30900257d8a371d5',
           'function setSS(': '9ab51a1f6b63f8803874377372b93245cb3fcfbe69470713d11b221f411d47ab'}


def t7_a40_guards():
    import hashlib
    import json
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok, detail='': report('7 A40: ' + name, ok, detail)
    h = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    card = json.loads(re.search(r'^const CARD=(\{.*\});\s*$', page, re.M).group(1))
    g('the snapshot has all 63 marks of the Marks sheet', len(card['marks']) == 63, str(len(card['marks'])))
    auth = {k: v for k, v in card['pairs'].items() if not v.get('rev')}
    rev = {k: v for k, v in card['pairs'].items() if v.get('rev')}
    g("authored routes exactly v3.19's", h(auth) == V319_PAIRS)
    g("courses exactly v3.19's", h(card['courses']) == V319_COURSES)
    g('exactly 85 reversed routes', len(rev) == 85, str(len(rev)))

    def mirror(k):
        a, b = k.split('|')
        f = auth.get(f'{b}|{a}')
        if not f or f'{b}|{a}' in rev:
            return False
        fwd = [b] + [x['to'] for x in f['segs']]
        back = [a] + [x['to'] for x in rev[k]['segs']]
        return back == fwd[::-1] and [x['nm'] for x in rev[k]['segs']] == [x['nm'] for x in f['segs']][::-1]             and rev[k]['nm'] == f['nm'] and k not in auth
    g('each reversed route is the exact mirror of a one-way authored route', all(mirror(k) for k in rev))
    g('every one-way authored route has its reverse',
      all('|'.join(k.split('|')[::-1]) in card['pairs'] for k in auth))
    low = page.lower()
    g('no Position Source, Source URL or Verification / Use text in the page',
      not any(x in low for x in ('eoceanic', 'position source', 'source url', 'verification / use', 'reference mark only')))
    for head, want in CODE_29.items():
        body = fn_body(code, head)
        if head == 'function ccDoc(':   # .31 adds one line, the routing waypoint INCOMPLETE (orphanText)
            body = chr(10).join(x for x in body.split(chr(10)) if 'orphanText(L)' not in x)
            # .36 converts at the course's own variation (A11, Pat 13 October 2026): the only other change
            body = body.replace('const legs=[], vc=varOf(L);', 'const legs=[];').replace('magOf(pt.brg,vc)', 'magOf(pt.brg)')
            # .36 rebuilt: the series field is "x-series", an extra field in Mark McLoughlin's convention (Pat, 13 October 2026)
            body = body.replace('\'  "x-series": \'', '\'  "series": \'')
            # and "course" to one decimal of a degree magnetic, as agreed with Mark McLoughlin on 10 October 2026
            body = body.replace('mag1(pt.brg,vc)', 'magOf(pt.brg)')
            # and "x-estimate" when the start line is the RO's estimate (A58, Pat 14 October 2026)
            body = body.replace("+(xEst(r,st)?'  \"x-estimate\": '+JSON.stringify(xEst(r,st))+',\\n':'')", '')
            # .43 fix 7: the finish is the last mark also on a card course's Laid line (finIsLast)
            body = body.replace("noF=!L.fPt&&!finIsLast(r,st);", "noF=!L.fPt&&(L.ccfg||finishMode(r,st)!=='last');")
            # .46, A123 (Pat, 26 October 2026): the card's STAND-IN lines beside the button only while the row says to place
            # the boat (a Dosco or No.8 start on Automatic, a finish with no finish boat); not for Grassy or a midpoint
            body = body.replace("\n   \n  if(L.sPt&&!L.sl&&L.ccfg&&markStartOf(r,st))cardSti.push('start line not recorded, first leg ('+L.sPt.name+' - '+first+') measured from the card\\'s '+L.ccfg.s+' start point');",
                                "\n  if(L.sPt&&!L.sl&&L.ccfg)cardSti.push('start line not recorded, first leg ('+L.sPt.name+' - '+first+') measured from the card\\'s '+L.ccfg.s+' start point'+\n    (cardEndMode('s',r,st)==='card'?' (Card mark chosen)':''));")
            body = body.replace("if(L.fPt&&!L.fl&&L.fsx&&L.fsx.kind==='cardpt'&&L.fsx.noBoat)cardSti.push('finish line not recorded, last leg ('+last+' - '+L.fPt.name+') measured to the card\\'s '+L.ccfg.f+' finish point');",
                                "if(L.fPt&&!L.fl&&L.fsx&&L.fsx.kind==='cardpt')cardSti.push('finish line not recorded, last leg ('+last+' - '+L.fPt.name+') measured to the card\\'s '+L.ccfg.f+' finish point'+\n    (cardEndMode('f',r,st)==='card'?' (Card mark chosen)':''));")
            # .37: a hand-built Grassy start gets the STAND-IN note beside the button, as an imported one does (A58 part 2)
            body = body.replace('if(L.sPt&&!L.sl&&L.ccfg)', 'if(L.sPt&&!L.sl)')
            body = chr(10).join(x for x in body.split(chr(10)) if 'gsOf(r,st))cardSti.push(' not in x)
            # .37 T14 (Pat, 15 October 2026): the Grassy start notes beside the button, plain and orange, not STAND-IN;
            # the copied text is unchanged
            body = chr(10).join(x for x in body.split(chr(10)) if 'gsN.push(' not in x and 'const gsN=[]' not in x)
            # .38 A8 (Pat, 16 October 2026): the series is the day's (daySeries), with the warning for the day
            body = re.sub(r"const ser=daySeries\(\);[ ]*\n", "const ser=String(series.name||'').trim();\n", body)
            body = body.replace("side.push('Series not set for this day: the copy has no series.');",
                                "side.push('Series name not set: the copy has no series. Set it at the top of Setup.');")
            # and the series out of the name: "x-series" only (Pat, 16 October 2026)
            body = re.sub(r"\n[ ]*\n  const label=\[ccDate\(", "\n  const label=[ser,ccDate(", body)
            body = body.replace("side),\n    notes:(gsN.length?[{cls:'cardnote',t:'Grassy start: '+gsN.join('; ')+'.'}]:[]).concat(gsA?[{cls:'cardnote amberTxt',t:gsA}]:[])};}", 'side)};}')
            # .44 (Pat, 22 October 2026): the start's own wind or the day's (windOf); the same for a start with its own
            body = body.replace("const w=windOf(k), num=", "const w=(S.winds||{})[k]||{}, num=")
        if head == 'function setCC(':   # .37 T14: the plain and orange notes after the warnings
            body = body.replace("+(d.notes||[]).map(n=>'<p class=\"'+n.cls+'\">'+esc(n.t)+'</p>').join('')", '')
            body = body.replace("'<p class=\"cardnote '+(/^INCOMPLETE/.test(t)?'flag':'caut')+'\">'", "'<p class=\"cardnote flag\">'")
        got = hashlib.sha256(body.encode()).hexdigest()
        g(head.split()[1].rstrip('(') + ' unchanged from 2026-10-06.29' + (' apart from its routing waypoint line' if
          head == 'function ccDoc(' else ''), got == want)
    g('card marks are added only by tap, import, a saved row or the laid-mark chip (A50, .36) (five callers)', code.count('pushCardMark(') == 6,
      str(code.count('pushCardMark(')))
    g('the page never reverses a route itself', not re.search(r"split\('\|'\)\.reverse\(\)|segs\.slice\(\)\.reverse", code))
    g('the Fixed marks fold is there once, closed', page.count('id="fixedWrap"') == 1 and
      '<details class="movefix" id="fixedWrap">' in page and code.count('fixedInit();') == 1)
    bl = fn_body(code, 'function buildLegs(')
    g('the WhatsApp text has no analysis, wind, route notes or labels',
      "an.txt.join" not in bl and "'\nWind '" not in bl and "(via?' ('+via.trim()" not in bl and "(fixNote?' ['" not in bl
      and "wRows=L.rows.filter(e=>!isRwCard(markById(e.id)))" in bl)
    for w in ("position from the course card, not a fix recorded today.", "'not depth-checked'", "'card route reversed'",
              "' (RO-chosen)'", "'routing waypoint'", "'laid mark'", "'Course Card'", "' nm, off the plot'"):
        g('approved wording: ' + w, w in code)
    g('a routing waypoint row has no side button and has ↓', "(rw?'':'<button data-a=\"side\"" in code and 'data-a="down"' in code
      and "b.dataset.a==='down'" in code)
    g('far positions are named under Check recorded marks', page.count('id="fxFar"') == 1
      and "$('fxFar').textContent=" in code)


def t8_fixes31_guards():
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('8 .31: ' + name, ok)
    g('1 Course Card marks are not carried into later races', 'S.marks.filter(m=>m.race<S.race&&!isCourseCard(m)' in fn_body(code, 'function bank('))
    rf = fn_body(code, 'function renderFix(')
    g('2 every race drawn gets its switch', 'all.map(m=>m.race).concat(cardsIn.map(m=>m.race),lastPlot&&lastPlot.pts.length>1?[r]:[])' in rf
      and rf.find('const cardsIn=') < rf.find('const days='))
    g('3 cardNameOf: own names only, laid marks excepted, compared as norm',
      "function cardNameOf(nm){const k=norm(nm);return k?Object.keys(CARD.marks).find(x=>!CARD.marks[x].laid&&norm(x)===k)||'':'';}" in code)
    g('3 the refusal message', "c+' is on the course card: tap it under Fixed marks. '" in code and
      "'If the buoy has moved, give it a different name, such as '+c+' moved.'" in code)
    rp = fn_body(code, 'function readPaste(')
    g('3 every pasted line goes through the refusal', 'const add=m=>{const c=cardNameOf(m.name);if(c){' in rp and rp.count('add({') == 3
      and 'push(m)' not in rp.replace('m.pasted=true;push(m);added.push(m);', ''))
    am = code[code.find("$('addManual').onclick"):]
    g('3 the typing box refuses before it asks for a position and stores nothing',
      -1 < am.find('cardNameOf(name.trim())') < am.find("prompt('Position") and
      am.find('cardNameOf(name.trim())') < am.find('S.outbox.push'))
    lp = fn_body(code, 'function legPts(')
    g('4 legPts keeps a routing waypoint with nothing on one side out of every leg',
      'orphan.push({i:x.i,lead:true})' in lp and 'orphan.push({i:x.i,lead:false})' in lp and ',orphan};' in lp)
    g('4 its row says so', "routing waypoint must sit between two marks: move it with '+(orph.lead?'↓':'↑')" in code)
    g('4 Copy for Sail Scoring says INCOMPLETE', 'if(orphanText(L)){inc.push(orphanText(L));incS.push(' in fn_body(code, 'function ccDoc('))
    g('4 the leg table says so', 'orphanText(L)?[orphanText(L)+' in fn_body(code, 'function buildLegs('))
    ln = fn_body(code, 'function laidNotice(')
    g('5 the laid-mark notice counts RO-chosen waypoints', 'function laidNotice(pts,total,legs){' in code and
      'g&&g.ro?roLeg(oldPts[i],g.route,oldPts[i+1])' in ln and 'laidNotice(pts,total,L.legs);' in code)


def t9_fixes32_guards():
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('9 .32: ' + name, ok)
    bl = fn_body(code, 'function buildLegs(')
    # .34 (Pat, 13 October 2026): the date is the day loaded, and a Race day changed but not loaded holds Send back (group 11)
    g('1 the WhatsApp date is the day loaded, never S.date',
      # .38 A8: the series is the day's (daySeries), the date as before
      "const head=[daySeries(),S.pulledDay?longDate(S.pulledDay):''].filter(Boolean).join(' – ')||'Course';" in bl
      and 'S.date' not in bl)
    g('1 the heading follows the Race day box at once', "$('day').addEventListener('change',()=>{render();" in code)
    g('2 routing waypoints are not carried either', 'm.race<S.race&&!isCourseCard(m)&&!isRwCard(m)' in fn_body(code, 'function bank('))
    g('4 one line per refused name', "refused.map(cardRefusal));" in code and "say(said.join('\\n'),!!(n&&!far.length&&!refused.length));" in code
      and '.actMsg{white-space:pre-line}' in page)
    cr = fn_body(code, 'function cardRefusal(')
    g('5 the refusal by kind: a buoy, or a point (routing waypoint, Grassy Mid)',
      "point=m.rw||m.type==='Start/finish modelling point'" in cr and "'If you need a different point, give it a different name.'" in cr
      and "'If the buoy has moved, give it a different name, such as '+c+' moved.'" in cr)
    g('6, 7 no laid-mark tag in the WhatsApp text', 'laidTag(' not in bl)
    g('8 the laid-mark notice names each source in words',
      "label:laidSrcText(u,m.race)" in code and "'a pasted position'" in code and "', kept on this device only'" in code
      and "'its planning position (the card position)'" in code and "'the RIB fix'" in code and "'the RIB fix at '" not in code)
    ln = fn_body(code, 'function laidNotice(')
    g('8 the notice says when nothing moved', "'It has not moved, so no leg has changed.'" in ln and "' nm, unchanged.'" in ln)
    # .34: the variation is at one fixed point, so no position (far or not) can change it (group 11)
    g('9 no position, far or not, changes the magnetic variation', 'S.marks' not in fn_body(code, 'function varW('))


def t10_changes33_guards():
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('10 .33: ' + name, ok)
    g('1 the Send warning is there once, above the buttons', page.count('id="sendWarn"') == 1
      and page.find('id="sendWarn"') < page.find('id="wa"'))
    g('1 its wording', "'This course has a missing mark: fix it before sending to competitors.'" in code
      and "'This course has a leg that is not measured (routing waypoint '" in code)
    g('1 WhatsApp, Share and Copy text each ask "Send anyway?"', "confirm(sendBad+'\\n\\nSend anyway?')" in code
      and "$('wa').addEventListener('click',e=>{if(!text||!sendOk()){e.preventDefault();return;}freezeSend();});" in code
      and "$('share').onclick=async()=>{if(!text||!sendOk())return;" in code and "$('copy').onclick=async()=>{if(!text||!sendOk())return;" in code)
    g('1 all three greyed when there is nothing to send', "$('share').disabled=!t; $('copy').disabled=!t;" in fn_body(code, 'function setOut('))
    g('1 buildLegs sets the warning for every course', 'setSendWarn(L);' in fn_body(code, 'function buildLegs('))
    g('2 Spit Bank Lighthouse is a point in the refusal', "m.type==='Fixed light'" in fn_body(code, 'function cardRefusal('))
    g('3 a pasted or typed fix named as such', "'pasted position, this device only'" in code and "isTypedPos(x)?'typed position'" in code
      and "'auto (latest: '+fixWords(st.latest,m.race)+')'" in code and 'fixWords(x,m.race)' in fn_body(code, 'function laidPicker('))
    g('3 the leg note too', "'to '+(isPasted(u)?'pasted':'typed')+' position, not depth-checked'" in fn_body(code, 'function resolveLaid('))
    bank_render = code[code.find("const bm0=bank().filter(m=>!isLineMark(m.name));"):code.find('renderPicked(bm);')]
    g('4 a × on a card-mark chip only while no row of the race uses it',
      'if(m.card&&m.race===S.race&&!startsUsing(S.race,m.id).length)' in bank_render and "x.className='pickX'" in bank_render)
    ta = fn_body(code, 'async function typedAct(')
    g('5 withdraw and correct: typed positions on the server only', 'if(!m||!isTypedPos(m)||!m.sid||m.pending)return;' in ta)
    g('5 the confirmation names the position, race, time and distance from the map centre',
      "' nm from the map centre (51.82 N, 8.27 W)'" in ta and "'Withdraw the typed position '+who" in ta and "'Correct the typed position '+who" in ta)
    g('5 withdraw is refused while a course uses it, naming each race and start', 'const u=usesOf(m,isLineMark(m.name));' in ta and "' cannot be withdrawn: it is used in '" in ta)
    g('5 the server actions', "action:'withdraw',date:day,id:m.sid,reason:why" in ta and "action:'correct',date:day,id:m.sid,new_id:nid,lat:p.lat,lon:p.lon" in ta)
    g('5 the card-name refusal applies to a correction', 'if(cardNameOf(m.name)){typedSays(cardRefusal(cardNameOf(m.name)),false);return;}' in ta)
    g('5 a withdrawn fix is never loaded', 'const list=j.marks.filter(m=>!m.withdrawn).sort(' in code)
    g('5 rows and line ends follow a correction', 'sid===sidNow(r.slice(2))' in fn_body(code, 'function resolveRef(')
      and 'sid===sidNow(ref.slice(2))' in fn_body(code, 'function refFix(') and "if(ls[w]==='s:'+m.sid)ls[w]='s:'+nid;" in ta)
    marks = read(MARKS)
    g('5 marks.php: withdraw and correct for typed positions only, never deleted',
      "if ($action === 'withdraw' || $action === 'correct') {" in marks
      and "(float)arg($old, 'acc', -1) != 0 || isset($old['device'])" in marks
      and "'withdrawn_reason'] = 'replaced by correction'" in marks
      and 'unset(' not in marks.split("if ($action === 'withdraw' || $action === 'correct') {")[-1].split('$rec = null;')[0])
    sp = fn_body(code, 'function savePasted(')
    g('6 pasted positions in red where used, with Save to the race record',
      "const PASTE_WARN='pasted position: on this device only, not in the race record';" in code and page.count('id="ccPasted"') == 1
      and "data-a=\"savepaste\"" in code and 'data-savepaste' in fn_body(code, 'function pastedHtml('))
    g('6 save: the card-name refusal, no duplicate, rows moved', 'const c=cardNameOf(m.name);' in sp and 'is already in the race record with the same position' in sp
      and "S.outbox.push({action:'add',id:pid,date:d,race:m.race,name:m.name,lat:m.lat,lon:m.lon,acc:0,time:t});" in sp and 'if(ch)stamp(k);' in sp)
    g('7 a saved typed position counts for its laid mark', 'const cand=S.marks.filter(x=>(ribFix(x)||(isTypedPos(x)&&!!x.sid))&&x.race<=race)' in fn_body(code, 'function laidState('))
    vw = fn_body(code, 'function varAt(')   # .36: varAt, at the course's anchor (A11)
    g('8 the magnetic variation for the race date, not today', "const d=S.pulledDay||$('day').value||todayISO(), y0=wmmYear(d)" in vw)


# the 90 coefficient lines of WMM2025 (WMM.COF, NOAA NCEI and BGS, 13 November 2024), each "g h g-dot h-dot", joined by ";"
# as the page holds them (WMM_COF): SHA-256 of that text, so the table cannot drift from the official file unnoticed
WMM2025_COF_SHA = 'd6eb9370bf06b7d80fef2543fe121e317fbba41a737d24522457971980b75c1a'


def t11_changes34_guards():
    import hashlib
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('11 .34: ' + name, ok)
    g('1 Share and Copy text greyed when switched off, as WhatsApp is', '.btn[aria-disabled="true"],.btn:disabled{opacity:.4;pointer-events:none}' in page)
    cof = re.search(r"WMM_COF='([^']*)'", code)
    g('2 the WMM2025 coefficients are the official file', bool(cof) and hashlib.sha256(cof.group(1).encode()).hexdigest() == WMM2025_COF_SHA
      and len(cof.group(1).split(';')) == 90 and 'const WMM_EPOCH=2025.0' in code)
    vw = fn_body(code, 'function varAt(')   # .36 replaced the map centre with the course's anchor (A11): group 13
    g('2 the variation from the model for the day loaded, never from the marks loaded', "S.pulledDay||$('day').value||todayISO()" in vw
      and 'wmmDecl(lat,lon,noon)' in vw and 'S.marks' not in vw)
    sw = fn_body(code, 'function setSendWarn(')
    g('3 a far position in a course holds Send back', "filter(m=>farNm(m))" in sw and "'This course uses a position more than '+FAR_NM+' nm from the map centre ('" in sw)
    g('4 a Race day changed but not loaded is said and holds Send back', page.count('id="dayChanged"') == 1
      and "'Race day is '+longDate(dc)+' but '+longDate(S.pulledDay)+' is loaded: tap Get latest marks.'" in sw and "$('day').value!==S.pulledDay" in sw)
    g('4 the heading date is the day loaded', "S.pulledDay?longDate(S.pulledDay):''" in fn_body(code, 'function buildLegs('))
    rp = fn_body(code, 'function readPaste(')
    g('5 a pasted line matching a saved position makes no chip', 'x.sid&&x.race===m.race' in rp and 'dup.push(t);return;}' in rp
      and "' is already in the race record with the same position.'" in code)
    g('6 typed and pasted positions are never checked for their age', 'list.forEach(m=>{if(isOtherMark(m))return;const a=fixAge(m);' in fn_body(code, 'function fxChecks('))
    g('7 a laid mark at its fix named on a physical leg through RO-chosen waypoints', "p.atFix&&(p.moveNote||'to RIB fix, not depth-checked')" in fn_body(code, 'function roLeg('))
    g('9 every start with a saved course is shown', '+k.split(\'|\')[1]+1' in fn_body(code, 'function classesOf('))


def t12_changes35_guards():
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('12 .35: ' + name, ok)
    pl = fn_body(code, 'async function pull(')
    g('1 messages of the old day clear when a different day is loaded',
      "['fxStatus','cardStatus'].concat(S.outbox.length?[]:['cbStatus']).forEach(id=>{$(id).textContent='';" in pl
      and pl.index("['fxStatus','cardStatus']") > pl.index('if(day!==S.pulledDay){'))
    g('4 a race with more than three starts is saved even with no classes',
      "r.classes.length<=3" in fn_body(code, 'function isEmptyRec(') and 'classesOf(r).map(l=>l.slice())' in fn_body(code, 'function editClasses('))
    sp = fn_body(code, 'function savePasted(')
    g('5 a pasted line with no time asks for the time on the water; Cancel saves nothing',
      "prompt('Time on the water for '" in sp and 'if(a===null)return;' in sp and 'Date.now():' not in sp)
    sw = fn_body(code, 'function setSendWarn(')
    g('6 a leg shorter than 50 m holds Send back and is flagged in the leg table', 'const SHORT_M=50;' in code
      and 'const sh=shortLegs(L);' in sw and "(r.m<SHORT_M?'<br><span class=\"viaTxt warnTxt\">⚠ two marks at nearly the same position ('" in code)
    g('7 the choices are saved with the course when it is saved', 'freezeFor(k);' in fn_body(code, 'function stamp(')
      and 'o.laid=ld' in fn_body(code, 'function recordFor(') and '{lineAuto:Object.assign({},S.lineAuto[k])}' in fn_body(code, 'function recordFor(')
      and 'Object.keys(S.laidFrz||{})' in fn_body(code, 'function allKeys('))
    g('7 a saved auto choice is used, and a newer fix waits for the RO', "mode='saved'" in fn_body(code, 'function laidState(')
      and "reason:'Auto (saved)',live:" in fn_body(code, 'function autoUse(')
      and "e.saved&&e.live?use(((fixMoment(e.live)||0)>(fixMoment(e.m)||0)?'Newer: ':'Auto now gives: ')+fixText(e.live,w),e.live):''" in fn_body(code, 'function endPicker('))
    g('7 only fixes saved on the server are saved as choices', 'st.latest&&st.latest.sid' in fn_body(code, 'function freezeLaid(')
      and 'e.m&&e.m.sid' in fn_body(code, 'function freezeLines('))


def t13_changes36_guards():
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('13 .36: ' + name, ok)
    va = fn_body(code, 'function varAt(')
    g('fix 2: the variation at the Copy for Sail Scoring anchor, noon UTC, 2 decimals; the map centre only with no measured leg',
      "L.legs.findIndex(g=>!g.missing)" in va and "+a.lat.toFixed(6)" in va and "noon=y+0.5/" in va
      and "-Math.round(wmmDecl(lat,lon,noon)*100)/100" in va and "centre:!a" in va)
    g('fix 2: the map-centre note beside both wind arrows', code.count("variation at the map centre: no leg measured") == 2)
    g('fix 3: Vincenty for figures; rhumb only for drawing (4 places)', 'function geo(a,b){' in code and 'function geoDest(a,brgT,d){' in code
      and len(re.findall(r'\brhumb\(', code)) == 6)
    g('A10 (a): saved when shown on the race day only, and before every send',
      "S.pulledDay&&S.pulledDay===todayISO()&&$('day').value===S.pulledDay&&freezeNow())scheduleSave();" in fn_body(code, 'function render(')
      and code.count('freezeSend();') == 4)
    g('A48: the save line cleared on a change of day', 'saveState.okAt=0; showSave();' in fn_body(code, 'async function pull('))
    g('A49: a typed position asks for the time on the water, saved on the race day',
      "prompt('Time on the water for '+name.trim()" in code and "date:day,race:S.race,name:nm,lat:p.lat,lon:p.lon,acc:0,time:t}" in code)
    g('A49: a typed position from another date says it', "time:hhmm(m.time)+otherDate(m,day)" in code)
    g('A50: no chip of its own for a fix under a laid mark\'s name', 'const bm=bm0.filter(m=>!underLaid(m));' in code
      and '!isPasted(m)&&laidK.has(norm(m.name))' in code)
    g('A54: the start line under the Start line lists', "<div id=\"lineInfo\" class=\"endSec\">'+lineInfo()+'</div>'+gsLink+" in code and "'<div class=\"meta cautTxt\">Set the start time, or choose both ends.</div>'" in code)
    g('A55: the scale bar in metres below 0.1 nm', "barNm<0.1?Math.round(barNm*1852)+' m'" in code)
    g('A56: a wind direction used only from 0 to 360, saved when the box is left', 'function twdOk(v)' in code and page.count('id="twdWarn"') == 1
      and "twdBad='';S.twd=v;buildLegs();};" in code and "twdBad='';S.twd=v;saveWind();};" in code)
    g('A49: no date label in the WhatsApp text', r".replace(/ on \S+ \d{1,2} \S+$/,'')" in code)
    g('A10: opening an old race never writes a choice: device-only laid choices from before .35 are not saved by a load, and a load-led save adds no auto choice',
      'S.laidLegacy[key])return;' in fn_body(code, 'function laidRec(') and "if(S.laidShape!==35)" in code
      and code.count('stamp(k,true);if(ln&&!ln[k])ln[k]=LOAD_WHY[') == 4 and 'if(!noFreeze)freezeFor(k);' in code)
    g('A54: section 3\'s start line note follows the wind box as section 4 does', "sMiss+'<div id=\"lineInfo\" class=\"endSec\">'+lineInfo()+'</div>'+gsLink+" in code
      and "if($('lineInfo')){$('lineInfo').innerHTML=lineInfo();paintMsgs();}" in fn_body(code, 'function buildLegs('))
    g('A56: an out-of-range direction is used as none and never saved', "twdBad=ckey(S.race,S.start);S.twd='';buildLegs();return;}" in code
      and code.count("if(!twdWarnSay(v)){twdBad=ckey(S.race,S.start);S.twd='';buildLegs();return;}") == 2 and 'if(twdBad)S.twd=\'\';' in code)
    g('Copy for Sail Scoring: course to one decimal of a degree magnetic', 'function mag1(brgT,v){' in code and '"course": \'+mag1(pt.brg,vc)' in code)
    g('C: Copy for Sail Scoring names the series "x-series"', '\'  "x-series": \'' in code and '\'  "series": \'' not in code)


def t14_one_end_line_guards():
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('14 .36 A58: ' + name, ok)
    eo = fn_body(code, 'function estOffer(')
    g('the options only with a start time and exactly one end, not on a Card mark start', "if(!startTime()||lineOff()||midLine()||!!cb===!!pin)return '';" in eo
      and "function lineOff(r,st){return cardEndMode('s',r,st)==='card'||!!gsOf(r,st)||cardGrassyStart(r,st);}" in code
      and "const can=!!startTime()&&!lineOff()&&!midLine(), mk=" in fn_body(code, 'function startSec(') and "const open=!e.m&&!mk||helpIs('start',w);" in fn_body(code, 'function startSec('))
    g('the options write nothing until the RO acts (no save, stamp or commit in the offer)', not re.search(r'(commit|save|stamp|scheduleSave|saveCourses|sendOutbox)\(', eo))
    g('option 1 saves a typed position named for the missing end, and the line end of this start',"nm=w==='cb'?'Committee boat':'Start Pin'" in code
      and "S.lineAuto[k]=Object.assign({},S.lineAuto[k]||{},{[w]:'s:'+id});" in code and 'geoDest(ref,((brgM-varW())%360+360)%360,dist)' in code)
    g('option 2: the recorded end as midpoint, for the start and a start-line finish', "(midLine(r,st)||startLine(r,st,sel))" in code
      and "return midLine(r,st)||startLine(r,st,sel);}" in code)
    g('both saved with the course and read back', "{lineMid:Object.assign({},S.lineMid[k])}" in code and "{lineEst:estSaved(k)}" in code
      and 'S.lineMid[k]={w:lm.w,ref:lm.ref}' in code)
    g('a real end recorded later is offered, never taken (.44: only when newer, "Newer: …")', "re?use('Newer: '+fixText(re,w),re):" in code and "Recorded '+(md.w==='cb'?'Start Pin':'committee boat')+' now available '" in code)
    g('Copy for Sail Scoring says x-estimate; the WhatsApp text does not', "'  \"x-estimate\": '+JSON.stringify(xEst(r,st))" in code
      and "function xEst(r,st){const a=lineEstNow(r,st), b=finEstNow(r,st);return a&&b?a.x+'; '+b.x:a?a.x:b?b.x:'';}" in code
      and 'estimate' not in fn_body(code, 'function setOut('))
    g('D: the WhatsApp leg lines give °M only', "+pad(brgM,3)+'°M · '+r.nm.toFixed(2)+' nm'" in code and "°M ('+pad(brgT,3)+'°T)" not in code)


def t15_start_line_setup_guards():
    """.37, A58 part 2 (Pat, 14 October 2026): the start line setup."""
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('15 .37 A58 part 2: ' + name, ok)
    eo, bo, li = fn_body(code, 'function estOffer('), fn_body(code, 'function bothOffer('), fn_body(code, 'function lineInfo(')
    es = fn_body(code, 'function estSuggest(')
    g('the helper offers write nothing (no save, stamp, commit or send)', not any(re.search(r'(commit|save|stamp|scheduleSave|saveCourses|sendOutbox)\(', b)
      for b in (eo, bo, li, es, fn_body(code, 'function raceMarkOpts('), fn_body(code, 'function fixedOpts('))))
    g('the Start Pin set at a mark, offered only with a start time, no Card mark or Grassy start, no midpoint; .44: beside placing it when a committee boat is in use, and set again',
      "const can=!!startTime()&&!lineOff()&&!midLine(), mk=" in fn_body(code, 'function startSec(')
      and "pinAtBox(!!oth)+(oth?routeOr()+placeBox('pin',oth,!e.m):'')" in fn_body(code, 'function startSec(')
      and "if(endPick('cb').m)return;" not in code[code.find("if(act==='pinAt'){"):code.find("if(act==='place'){")])
    g('suggestions are greyed placeholders only: the boxes keep what the RO typed', 'placeholder="200" value="\'+esc(d.dist)+\'"' in fn_body(code, 'function placeBox(')
      and 'placeholder="\'+ph+\'" value="\'+esc(d.brg)+\'"' in fn_body(code, 'function placeBox(') and 'd.dist=' not in code and 'd.brg=' not in code)
    g('starboard: committee boat 90 deg right of the pin looking upwind or to the first mark; pin = cb - 90; port swaps',
      "const turn=(w==='cb'?90:-90)*(d.port==='1'?-1:1)" in es and 'n(+S.twd)' in es and 'n(magOf(geo(have,f.m).brg,varW()))' in es)
    g('no wind or no first mark: a warning, no suggestion', "'No wind direction: type it in the wind box first" in es and "'No first mark yet: add the course first" in es)
    g('the first mark skips routing waypoints', 'if(m&&isRwCard(m)){rw=true;continue;}' in fn_body(code, 'function firstMarkOf('))
    g('the committee boat\'s "from" list and the Start Pin list offer the Fixed marks list, real marks only (.44 fault 4); the Start Pin\'s "from" list does not (group 29)', fn_body(code, 'function placeBox(').count('fixedOpts(d.ref)') == 1
      and fn_body(code, 'function pinAtBox(').count('fixedOpts(d.at)') == 1
      and 'Object.keys(CARD.marks).forEach(nm=>{if(!isRealMark({card:nm}))return;' in fn_body(code, 'function fixedOpts('))
    g('a Start Pin set at a mark: a typed position and this start\'s pin, the RO\'s choice, not an estimate (answer 2 corrected)', "name:'Start Pin',lat:src.lat,lon:src.lon,acc:0,time:t" in code
      and "S.linePinAt[k]=Object.assign({ref:'s:'+id,at},was?{was}:{});" in code and "S.lineAuto[k]=Object.assign({},S.lineAuto[k]||{},{pin:'s:'+id});" in code
      and "function setOf(m){return m?Object.values(S.linePinAt||{}).find(refHit(m))||goneAll().find(g=>'at' in g&&refHit(m)(g))||null:null;}" in code
      and "function estOf(m){return m?estAll().find(refHit(m))||goneAll().find(g=>!('at' in g)&&refHit(m)(g))||null:null;}" in code)
    g('its time defaults to the start time', "tt=String(v||'').trim()||startTime()" in fn_body(code, 'function onWater(')
      and "const t=onWater(d.ptime);" in code[code.find("if(act==='pinAt'){"):code.find("if(act==='place'){")])
    g('one Undo withdraws every estimate of the start, committee boat first, after one confirmation', "sort((a,b)=>(a.w==='cb'?0:1)-(b.w==='cb'?0:1))" in code
      and code.count("reason:'estimate undone by the RO'") == 2)
    g('a recorded end while auto uses an estimate: offered, never taken (.44: only a newer one)', "re=e.how==='auto'&&e.m&&helpOf(e.m)?newerEnd(w,e.m):null" in code
      and "const use=(t,f)=>'<div class=\"newer\">'+esc(t)+' <button type=\"button\" class=\"endLive\" data-w=\"'+w+'\" data-f=\"'+esc(refFor(f))+'\">Use it</button></div>';" in code)
    g('Grassy start: hand-built only, saved as startPt, read back, line not used, finish at Grassy Mid on Start line',
      "if(act==='grassy'){if(cardCfgNow())return;S.startPt[k]='Grassy Mid';" in code and "{startPt:S.startPt[k]}" in code
      and "if(rec.startPt==='Grassy Mid')S.startPt[k]='Grassy Mid'; else delete S.startPt[k];" in code
      and "return lineOff(r,st)?null:(midLine(r,st)||startLine(r,st,sel));" in code
      and "gsOf(r,st)&&finishMode(r,st)==='start'?cardEnd('Grassy Mid','Finish'):null" in code)
    cc = fn_body(code, 'function ccDoc(')
    g('Grassy start: its note beside Copy for Sail Scoring, never in the name (T14: not a STAND-IN)', "measured from Grassy, the midpoint of the Grassy Walk line');" in cc
      and 'gsOf' not in cc.split('const pre=')[1].split('const name=')[0])
    g('the new fields are written only when used, so other records save exactly as before',
      "...(S.startPt&&S.startPt[k]?{startPt:S.startPt[k]}:{})," in code and "...(S.linePinAt&&S.linePinAt[k]?{linePinAt:" in code)
    bl = fn_body(code, 'function buildLegs(')
    g('the midpoint is drawn as a 200 m line square to the first leg, drawing only', 'A=geoDest(sl.end,(b+90)%360,100), B=geoDest(sl.end,(b+270)%360,100)' in bl
      and "drawn:true},kind:'start',est:true}" in bl and '!g.a.drawn' in fn_body(code, 'function courseMarks('))
    g('the chart labels an estimated line', "ln.est?(ln.kind==='finish'?'Finish line: estimate':'Start line: estimate')" in code and "permanent:true,direction:'bottom',offset:[0,12],className:'estTip'" in code)
    g('decision 2a: an estimated end carries forward only within its race; a later race is offered it, never given it by auto',
      "&&!(m.race<r&&helpOf(m))&&!(isFinW(w)&&finOf(m))&&!goneOf(m)).sort(" in fn_body(code, 'function candidates(') and "eo=!e.m&&e.how==='unset'?estEarlier(w):null" in code
      and "eo?use((estOf(eo)?'Estimate from Race '+eo.race:'Start Pin set in Race '+eo.race)+': '+fixText(eo,w),eo):" in code)
    g('T7: a helper end named by what the RO did, time last, in lists, notes and Check recorded marks; short on the drawings',
      "const setFor=(lab,at)=>isMarkEnd(at)?at+rp:lab+': at '+at+', set for Race '+m.race+' at '" in code and "if(p)return setFor('Start Pin',p.at);" in code
      and "' – estimate: '+e.m+' m at '+pad(e.brgM,3)+'°M from '+f+(f.endsWith(' '+w)?'':' ('+w+')')" in code
      and "'Start Pin ('+shortAt(p.at)+')'" in code and "' (est.)'" in code and "function fixText(m,w){if(helpOf(m))return helpLong(m);" in code
      and "const lab1=m=>helpOf(m)?helpLong(m):" in code)
    g('T7: no "unattributed": a typed position, pasted, or phone not known', "'unattributed'" not in code
      and "isPasted(m)?'pasted':isTypedPos(m)?'typed position':'phone not known'" in code)
    g('T7: a pin at a mark with an uncertain card position, or a laid mark at its planning position, keeps its warning',
      "c.laid?p.at+': planning position until laid, not a fix recorded today':(c.flag||'')" in code and code.count('helpWarn(') >= 3)
    so = fn_body(code, 'function setOut(')
    g('the WhatsApp text still carries no estimate note', 'estimate' not in so and 'Grassy' not in so)


def t16_day_guards():
    """.37, A64 (Pat, 14 October 2026): never show or save a course for another day than the Race day box's; T1, Q1."""
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('16 .37 A64: ' + name, ok)
    g('every course edit is labelled with the day loaded, never just the box', "S.courseDay[k]=workDay();" in code
      and "function workDay(){return S.pulledDay||$('day').value||todayISO();}" in code and "S.courseDay[k]=$('day').value" not in code)
    g('fixes recorded, typed or moved on this page belong to the day loaded', code.count('day=workDay();') == 3
      and "day=$('day').value||todayISO()" not in code.replace("const day=$('day').value||todayISO(), st=$('readStatus');", ''))
    g('held while the box and the day loaded differ, said in both views', "function dayHeld(){return !!(S.pulledDay&&$('day').value&&$('day').value!==S.pulledDay);}" in code
      and page.count('id="dayHeldNote"') == 1 and "'Race day is '+longDate($('day').value)+' but '+longDate(S.pulledDay)+' is loaded: tap Get latest marks.'" in code
      and "heldSay();" in fn_body(code, 'function render('))
    # .38 A8: the series name is the loaded day's, so it is held and hidden too (and the first save's question)
    g('while held the loaded day is hidden and every other control does nothing',
      'body.dayHeld .wrap>.raceOnly,body.dayHeld #seriesBox,body.dayHeld #seriesAsk,body.dayHeld #recCB,body.dayHeld #recCB~*,' in page
      and "['click','change','input','keydown'].forEach(ev=>document.addEventListener(ev,e=>{if(!dayHeld())return;" in code
      and "#day,#pull,#heldPull,#dayAnyway,#clear,.modebar,#dayHeldNote" in code)
    g('the 30-second refresh never loads a day by itself while held', "!dayHeld()&&(reopenWait||pullOk&&$('day').value===todayISO()))pull(true);" in code)
    g('reopening the page when a day was loaded before says so when that was another day (changed by group 17)',
      "if(S.pulledDay){const was=S.pulledDay, now=$('day').value;" in code and "'The page was reopened: Race day is back to today, '" in code)
    g('T1: no comma before "on the water", in every helper (Set Start Pin at, Set Finish Pin at, Place, Place Finish boat)', ", on the water" not in page
      and code.count("</select> on the water '") == 4 and "°M from the '+esc(pw)+' on the water '" in fn_body(code, 'function finBoatBox('))
    g('Q1: one end found and no line in use is drawn on the sketch and the chart, named an estimate when it is one',
      "const one=!sl&&!lineOff()&&!midLine()?[endPick('cb').m,endPick('pin').m].filter(Boolean):[];" in code
      and "label:helpShort(m)||m.name" in code and "plot(pts,plotLines,solo);" in code and "(P.solo||[]).map(m=>({a:m,b:m}))" in code)


def t17_reopen_names_guards():
    """.37, Pat's answers of 14 October 2026 to the first .37 report: reopening on the same day shows the stored copy at
    once and refreshes in the background, held only on another day (A64, answer 3); a reference's time is not said twice
    (A58, answer 2); "phone with no name" (A58, answer 4)."""
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('17 .37 answers: ' + name, ok)
    tail = code[code.index("if(S.pulledDay){const was=S.pulledDay, now=$('day').value;"):]
    tail = tail[:tail.index('})();')]
    g('3 reopened on another day: held, nothing loaded by itself, said with the way back',
      "if(was!==now){reopenFrom=was;$('reopenNote').hidden=false;" in tail and 'pull(false)' not in tail
      and "' was loaded before and is still on this device: to carry on with it, set Race day back to it. To load today, tap Get latest marks.'" in tail)
    g('3 reopened on the same day: the stored copy shown at once, refreshed quietly in the background',
      "else{$('readStatus').textContent='The page was reopened: showing what this device holds for '+longDate(was)+'. It refreshes from the server when there is signal.';" in tail
      and tail.count('pull(true);') == 1)
    g('3 the background refresh is retried every 30 seconds and when the signal comes back, until one load succeeds',
      "reopenWait=!!S.pulledDay&&S.pulledDay===$('day').value;" in code
      and "!dayHeld()&&(reopenWait||pullOk&&$('day').value===todayISO()))pull(true);" in code
      and "window.addEventListener('online',()=>{if(reopenWait&&!dayHeld())pull(true);});" in code
      and "pullOk=true; lastPullAt=Date.now(); reopenWait=false; reopenFrom='';" in code)
    g('3 the race-day save of A10 (a) waits for that refresh',
      "if(!reopenWait&&S.pulledDay&&S.pulledDay===todayISO()&&$('day').value===S.pulledDay&&freezeNow())scheduleSave();" in fn_body(code, 'function render('))
    g('3 the first render comes after reopenWait is set', 0 <= code.index("reopenWait=!!S.pulledDay") < code.index('\nrender();\n'))
    g('3 the reopen note goes once the box and the day loaded agree', "if(!h)$('reopenNote').hidden=true;" in fn_body(code, 'function heldSay('))
    g('3 Clear everything leaves nothing to refresh', "reopenWait=false; reopenFrom=''; $('reopenNote').hidden=true;" in fn_body(code, 'function clearPageState('))
    rb = fn_body(code, 'function reopenBack(')
    g('3 (15 October) held on another day, the day loaded before is kept until Race day is set back to it',
      "if(was!==now){reopenFrom=was;" in tail and "$('day').addEventListener('change',()=>{render();reopenBack();});" in code)
    g('3 (15 October) Race day set back to it: shown at once and refreshed in the background, as on the same day',
      "if(!reopenFrom||dayHeld()||$('day').value!==reopenFrom)return;" in rb and "reopenFrom='';reopenWait=true;" in rb
      and "'The page was reopened: showing what this device holds for '+longDate(S.pulledDay)+'. It refreshes from the server when there is signal.'" in rb
      and rb.count('pull(true);') == 1)
    g('3 (15 October) the 30-second retry is not limited to today while a reopened day waits for its refresh',
      "setInterval(()=>{if(!document.hidden&&!dayHeld()&&(reopenWait||pullOk&&$('day').value===todayISO()))pull(true);},30000);" in code)
    hl = fn_body(code, 'function helpLong(')
    g('2 the time in brackets is left out when the reference already ends with it',
      "if(!mm||/ R\\d+( \\d{1,2}:\\d{2})?$/.test(f))return '';" in fn_body(code, 'function fromWhenOf(')
      and "return String(from).endsWith(' '+w)?'':w;" in fn_body(code, 'function fromWhenNew(')
      and "f.endsWith(' '+w)?'':' ('+w+')'" in fn_body(code, 'function helpX(') and "'°M from '+e.from+' ('+fixWhen(m)+')'" not in code)
    g('4 a RIB phone with no recorder name is "phone with no name"', "return m.recorder||'phone with no name';" in code and "'unnamed phone'" not in code)


def t18_gone_start_guards():
    """.37, Pat's decisions of 15 October 2026 after the start line analysis: a start that has gone never loses its line
    through an action on another start, and no estimate label is lost (a to e)."""
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('18 .37 gone starts: ' + name, ok)
    lu = fn_body(code, 'function lineUsers(')
    g('lineUsers: a start using the fix by its choice, saved auto, its estimate, set-pin or midpoint record, or auto right now',
      "Object.values(S.lineSel[k]||{}).concat(Object.values(S.lineAuto[k]||{})).some(v=>refIs(v,m))" in lu
      and "(placed?[]:estsOf(k).concat(S.linePinAt[k]?[S.linePinAt[k]]:[])).concat(S.lineMid[k]?[S.lineMid[k]]:[],frec).some(e=>refIs(e.ref,m))" in lu
      and "frec=[fz.mid].concat(placed&&!fz.src?[]:[fz.cb,finPinOwn(fz.pin)?fz.pin:null]).filter(Boolean);" in lu
      and "function lineUsers(m,skip,placed){" in code
      and "['cb','pin','fcb','fpin'].some(w=>endPick(w,r,st).m===m)" in lu and "if(k===skip)return;" in lu)
    g('lineUsers looks at every start of the day',
      "['courses','startTimes','lineSel','lineAuto','lineEst','linePinAt','lineMid','lineFin'].forEach(f=>" in fn_body(code, 'function startKeys('))
    g('a: Undo is refused, naming the starts, while any other start uses the estimate',
      "const others=[...new Set(its.reduce((a,i)=>a.concat(lineUsers(i.m,k)),[]))];" in code
      and "'Not undone: this estimate is also used by '+others.join(', ')+'. Undo would change '" in code
      and code.index("const others=[...new Set(") < code.index("await postFix({action:'withdraw',date:S.pulledDay,id:i.m.sid,reason:'estimate undone by the RO'}"))
    g('b, .44: placing an end or setting the pin clears that end\'s choice on the start ("None" or a fix chosen in its list)',
      "if((S.lineSel[k]||{})[w])delete S.lineSel[k][w];" in code and "if((S.lineSel[k]||{}).pin)delete S.lineSel[k].pin;" in code)
    g('c: a placed end\'s time on the water defaults to the start\'s own time, as the set pin does',
      "const t=onWater(estDraft.time);" in code[code.find("if(act==='place'){"):code.find("if(act==='undoPlaced'){")]
      and "tt=String(v||'').trim()||startTime()" in fn_body(code, 'function onWater(') and "String(ref.time||have.time||'')" not in code
      and """data-f="time" type="text" inputmode="numeric" placeholder="'+esc(startTime())+'\"""" in code)
    g('d: one estimate record per end of a start; placing one end keeps the other',
      "S.lineEst[k]=Object.assign({},S.lineEst[k]||{},{[w]:rec});" in code
      and "function estsOf(k){const o=(S.lineEst||{})[k];return o?[o.cb,o.pin].filter(Boolean):[];}" in code
      and "function estOf(m){return m?estAll().find(refHit(m))||goneAll().find(g=>!('at' in g)&&refHit(m)(g))||null:null;}" in code)
    g('d: the old shape is read as that end\'s, from the server and from this device',
      "function estNorm(v){const one=estRec(v);if(one)return {[one.w]:one};" in code
      and "const le=estNorm(rec.lineEst); if(le)S.lineEst[k]=le; else delete S.lineEst[k];" in code
      and "Object.keys(S.lineEst).forEach(k=>{const n=estNorm(S.lineEst[k]);if(n)S.lineEst[k]=n;else delete S.lineEst[k];});" in code)
    g('d: a start with one placed end is saved in the old shape; only both ends as {cb, pin}',
      "function estSaved(k){const l=estsOf(k);return l.length===1?Object.assign({},l[0]):l.length?{cb:Object.assign({},l[0]),pin:Object.assign({},l[1])}:null;}" in code
      and "...(estSaved(k)?{lineEst:estSaved(k)}:{})," in code
      and "{w:le.w,ref:le.ref,from:String(le.from||''),m:+le.m||0,brgM:+le.brgM||0}" in fn_body(code, 'function estRec('))
    g('d: Undo withdraws each end\'s record and keeps the rest', "estDrop(i.e);" in code
      and "let ts=estsOf(k).concat(S.linePinAt[k]?[S.linePinAt[k]]:[]);" in code)
    g('e: Withdraw counts every line end use (saved auto, estimate and set-pin records, auto right now)',
      "return [...new Set(out.concat(lineUsers(m,undefined,placed)))];" in fn_body(code, 'function usesOf(')
      and "const u=usesOf(m,isLineMark(m.name));" in fn_body(code, 'async function typedAct('))


def t19_remove_start_guards():
    """.37, Remove Start (Pat, 15 October 2026): every record kept per start moves with its start; nothing of the removed
    start passes to another."""
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('19 .37 Remove Start: ' + name, ok)
    m = re.search(r"const START_KEYED=\[([^\]]*)\];", code)
    keyed = set(re.findall(r"'(\w+)'", m.group(1))) if m else set()
    g('the saved auto choices, estimates, midpoints, Grassy starts and set pins move with their start',
      {'lineAuto', 'lineMid', 'lineEst', 'startPt', 'linePinAt'} <= keyed)
    rf = fn_body(code, 'function recordFor(')
    used = set(re.findall(r"S\.(\w+)\[k\]", rf)) | ({'lineEst'} if 'estSaved(k)' in rf else set())
    g('every per-start record a course saves is moved by Remove Start', bool(used) and used <= keyed)
    rs = fn_body(code, 'function removeStart(')
    g('the removed start\'s records are deleted, later ones moved down one, the rest left',
      "START_KEYED.forEach(f=>{const o=S[f]=S[f]||{};delete o[ckey(r,i)];" in rs
      and "for(let j=i+1;j<=last;j++){const a=ckey(r,j);if(a in o){o[ckey(r,j-1)]=o[a];delete o[a];}}});" in rs
      and "START_KEYED.forEach(f=>Object.keys(S[f]||{}).filter(own).forEach(k=>{last=Math.max(last,+k.split('|')[1]);}));" in rs)
    g('a helper draft is not carried to another start', "estDraft={};" in rs)


def t20_time_and_remove_guards():
    """.37, Pat's decisions of 15 October 2026 after the 37b test: a start's auto line-end choices are saved only once its
    start time is complete (fix 1); Remove Start withdraws the removed start's own helper fixes, or is refused (fix 2)."""
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('20 .37 time and Remove Start: ' + name, ok)
    fl = fn_body(code, 'function freezeLines(')
    g('1: nothing is saved for the open start while its time box has focus (a half-typed time)',
      "if(k===ckey(S.race,S.start)&&document.activeElement===$('startTime'))return;" in fl
      and fl.index("document.activeElement===$('startTime')") < fl.index("['cb','pin','fpin'].forEach"))
    g('1: leaving the box saves the choices for the time as set, redrawing only when something is saved',
      "$('startTime').addEventListener('blur',()=>{if(startTime()&&freezeNow()){render();scheduleSave();}});" in code)
    g('1: the start time itself is still saved on every change (.44: dropping unused Auto picks first)',
      "$('startTime').onchange=e=>{const k=ckey(S.race,S.start), used=startUsed(k);S.startTimes[k]=e.target.value;if(!used)dropAutoPicks(k);stamp();commit();};" in code)
    ra = fn_body(code, 'async function removeStartAsked(')
    g('2: the Remove Start button goes through removeStartAsked', "if(rm)rm.onclick=()=>removeStartAsked(S.start);" in code
      and "rm.onclick=()=>{removeStart(" not in code)
    g('2: the removed start\'s own placed ends and set pin are found', "estsOf(k).concat((S.lineGone||{})[k]||[]).map(e=>({e,w:e.w})).concat(S.linePinAt[k]?[{e:S.linePinAt[k],w:'pin'}]:[]," in ra
      and "fOwn&&fz.cb?[{e:fz.cb,w:'fcb'}]:[],fg.filter(g=>g.w==='fcb').map(e=>({e,w:'fcb'}))" in ra
      and "const post=fix((fOwn&&finPinOwn(fz.pin)?[{e:fz.pin,w:'fpin'}]:[]).concat(fg.filter(g=>g.w==='fpin').map(e=>({e,w:'fpin'}))));" in ra)
    g('2: refused, naming the starts, while any other start uses one of them',
      "const others=[...new Set(all.reduce((a,x)=>a.concat(lineUsers(x.m,k)),[]))];" in ra
      and "' not removed: its '" in ra and ra.index('const others=') < ra.index("action:'withdraw'"))
    g('2: each is withdrawn (kept, marked withdrawn) before the start is removed; a failed withdrawal removes nothing',
      "await postFix({action:'withdraw',date:S.pulledDay,id:x.m.sid,reason:'start removed by the RO'},OUTBOX_TIMEOUT_MS);" in ra
      and "await pull(true);commit();say('Start '+(i+1)+' not removed: '+why+'.',false);return;}" in ra
      and "say('Start '+(i+1)+' not removed: the change to its finish line could not be saved. Try again when there is signal.',false);return;}" in ra
      and ra.index('finSavedWithout(') < ra.index("action:'withdraw'") < ra.index('removeStart(i);'))


def t21_t14_guards():
    """.37 T14 (Pat, 15 October 2026): the Grassy start is the Grassy Walk line, measured from Grassy Mid, not a stand-in;
    wording only: nothing a leg, figure, finish point or save uses changes."""
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('21 .37 T14: ' + name, ok)
    g('no "standing in for the Grassy Walk line" and no Grassy STAND-IN in the page code (the workbook\'s own flag text aside)',
      'standing in for the Grassy Walk line' not in code.replace(code[code.index('const CARD='):code.index('\n', code.index('const CARD='))], '')
      and "'STAND-IN - '+cardSti" in code and 'gsOf(r,st))cardSti.push(' not in code)
    g('Start line row: the Grassy Walk line, measured from Grassy (shown so since .46); a recorded line not used said in orange',
      "'<div class=\"meta\">Start: <b>Grassy start</b>: the start line is the Grassy Walk line, measured from Grassy. " in code
      and "'<div class=\"meta amberTxt\">Grassy start chosen; the recorded line (committee boat '" in code and ".amberTxt{color:var(--r2)}" in page)
    g('beside Copy for Sail Scoring: a plain note, and the orange line when a recorded line is not used, never STAND-IN',
      "notes:(gsN.length?[{cls:'cardnote',t:'Grassy start: '+gsN.join('; ')+'.'}]:[]).concat(gsA?[{cls:'cardnote amberTxt',t:gsA}]:[])" in code
      and "(d.notes||[]).map(n=>'<p class=\"'+n.cls+'\">'+esc(n.t)+'</p>').join('')" in fn_body(code, 'function setCC('))
    g('real stand-ins keep their colour; .46: "no committee boat is set"', "'from the card\\'s '+ccfg.s+' start, standing in because no committee boat is set'" in code
      and "warns.map(t=>'<p class=\"cardnote '+(/^INCOMPLETE/.test(t)?'flag':'caut')+'\">'+esc(t)+'</p>')" in fn_body(code, 'function setCC('))
    g('the Grassy start point and finish point are found exactly as before', "gsOf(r,st)?cardEnd('Grassy Mid','Start')" in code)


def t22_day_series_guards():
    """.38 A8 (T21, Pat 16 October 2026): the series name per race day, the day's _day record saved by the course-save
    machinery; carried from the latest earlier day for the RO to check; T20: a day loaded opens Start 1 or its first
    start with a course."""
    page = read(PAGE)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(page)
    g = lambda name, ok: report('22 .38 A8: ' + name, ok)
    g('series.json is neither read nor written, and there is no series refresh',
      "type=series'" not in code and "action:'series'" not in code and 'syncSeries' not in code and 'series.name' not in code)
    g("the device's old series name and its unsent mark are removed, never read or written",
      code.count("course-series") == 1 and "try{localStorage.removeItem(STORE+'course-series');}catch(e){}" in code)
    g('no "saved for every RO device"', 'every RO device' not in page)
    g("the day's series is the _day record of the course-save machinery",
      "if(k==='_day'){const o={};if(typeof S.daySeries==='string')o.series=S.daySeries;" in fn_body(code, 'function recordFor(')
      and "function isEmptyRec(k,r){if(k==='_day')return !r.series&&!r.wind;" in code
      and "function allKeys(){return [...new Set((typeof S.daySeries==='string'||(S.dayWind&&S.dayWind.day===workDay())?['_day']:[]).concat(" in code
      and "k==='_day'?'Series name':" in fn_body(code, 'function saveLabel('))
    ap = fn_body(code, 'function applyServerCourses(')
    g("a load takes the server's series unless this device has an unsent edit, and labels it with its day",
      ap.index('if(S.synced[k]!==undefined&&isDirty(k))return;') < ap.index("if(k==='_day'){")
      and "S.daySeries=rec.series;S.courseDay=S.courseDay||{};S.courseDay._day=S.pulledDay;" in ap)
    g('an edit of the series is labelled with the day loaded and saved like a course',
      "function seriesSet(v){S.daySeries=v;stamp('_day',true);commit();}" in code)
    pl = fn_body(code, 'async function pull(')
    g('a change of day keeps only a series set for the day being loaded, unsent, and drops the carried one',
      "if(!mine('_day')||!S.daySeries){delete S.daySeries;delete S.courseDay._day;}" in pl and "S.carry=null; seriesAskDay='';" in pl
      and "if(S.daySeries)S.synced._day='';" in pl)
    g('the carried series is looked up only for a day with none of its own, and nothing is written',
      "if(!stale()&&!daySeries()){try{" in pl and "?type=seriesbefore&date='" in pl and code.count('seriesbefore') == 1)
    g("outputs use the day's own series: WhatsApp heading and Copy for Sail Scoring",
      "const head=[daySeries()," in fn_body(code, 'function buildLegs(') and "const ser=daySeries();" in fn_body(code, 'function ccDoc(')
      and "side.push('Series not set for this day: the copy has no series.');" in code
      and """(ser?'  "x-series": '+JSON.stringify(ser)+',\\n':'')""" in code)
    g('the box is labelled "Series Name for Message heading"; the series goes to Sail Scoring as "x-series" only, never in "name"',
      '<label>Series Name for Message heading<input id="series"' in page
      and "const label=[ccDate(S.pulledDay||$('day').value),'Race '+r,'Start '+(st+1)]" in fn_body(code, 'function ccDoc('))
    g('carried: "carried from dd/mm/yyyy: check" with Confirm; none: "No series set for this day" in orange',
      "'carried from '+dmy(c.from)+': check'" in code and 'id="seriesConfirm">Confirm</button>' in page
      and "'No series set for this day'" in code and "st.className='status'+(none?' amberTxt':'');" in code)
    sc = fn_body(code, 'async function saveCourses(')
    g('the first course save on a day showing a carried series asks once, never on a change of day or while held',
      "if(!dayMode&&!dayHeld()&&ks.some(k=>k!=='_day')&&carried()&&S.seriesAsked!==day){S.seriesAsked=day;save();askSeries();}" in sc
      and "'Series for this day: '+c.series+' (carried from '+dmy(c.from)+'). Use it?'" in code
      and '>Use it</button>' in page and '>Change</button>' in page)
    g('Confirm marks the day as asked; Change opens the Series name box',
      "$('seriesConfirm').onclick=()=>{const c=carried();if(!c)return;S.seriesAsked=c.day;seriesSet(c.series);};" in code
      and "$('seriesChange').onclick=()=>{seriesAskDay='';$('seriesAsk').hidden=true;setMode('setup');" in code)
    g('Clear everything resets the question', "seriesAskDay=''; $('seriesAsk').hidden=true;" in fn_body(code, 'function clearPageState('))
    g('T20: a different day opens Start 1, or the first start with a course, in the race chosen as before',
      pl.index('applyServerCourses(jc.courses)') < pl.index('if(newDay&&!stale()){const sts=') and 'S.start=sts.length?Math.min(...sts):0;' in pl
      and 'const newDay=day!==S.pulledDay;' in pl and 'if(!kept.has(S.race))S.race=kept.size?Math.min(...kept):1;' in pl)


def t23_worker_guards():
    """The course page's service worker and its kill switch (STATUS A65). Guards, not proof: no JavaScript is run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    g = lambda name, ok, detail='': report('23 worker: ' + name, ok, detail)
    code, kill = build_test.strip_js(read(SW)), build_test.strip_js(read(SW_KILL))
    g('the live worker passes worker_problems', not build_test.worker_problems(code), '; '.join(build_test.worker_problems(code)))
    g('the live worker names /marks/ only in its key.js line', re.findall(r'/marks[^\'"]*', code) == ['/marks/key.js']
      and code.count(SW_KEY_LIVE) == 1 and '/marks-test' not in code)
    g('no "record-" cache in the worker or the kill switch', 'record-' not in code and 'record-' not in kill)
    g('the folder and version come from its own address', "const VERSION=new URL(location.href).searchParams.get('v')||'';" in code
      and "const PAGE=new URL('./',location.href).href, PAGE_PATH=new URL(PAGE).pathname;" in code)
    g('install fetches ./?v=<its own version> and keeps it only if it is its own',
      "fetch(PAGE+'?v='+encodeURIComponent(VERSION),{cache:'reload'})" in code
      and "if(res.type!=='basic'||!buf||!isOwn(new TextDecoder().decode(buf)))throw" in code)
    g('a refresh keeps only its own version', "if(page&&!isOwn(new TextDecoder().decode(buf)))return;" in code)
    g("the browser's answer never waits on reading a copy of it (A65 Step 23)",
      "const net=fetch(r).then(res=>{copy=res.clone();return res;});" in code and "const buf=await copy.arrayBuffer();" in code
      and not any(x in code for x in ('.clone().text()', '.clone().arrayBuffer()', 'await isOwn(')))
    cp = re.search(r'const copyOf=.*', code)
    g('a saved copy keeps Content-Type only, status 200: no Content-Encoding or Content-Length',
      bool(cp) and "headers:t?{'Content-Type':t}:{}" in cp.group(0) and 'status:200' in cp.group(0)
      and not re.search(r'(?i)content-encoding|content-length|transfer-encoding|headers:res\.headers', cp.group(0))
      and code.count('copyOf(res,buf)') == 2)
    g('the clean-up deletes only its own folder', "if(ownCache(k)&&k!==CACHE)await caches.delete(k);" in code)
    g('a navigation to another version waits 10 s', "OTHER_WAIT=10000" in code and "wait=v!==null&&v!==VERSION?OTHER_WAIT:WAIT" in code)
    g('only the page and its key.js are handled', "const key=page?PAGE:(r.url===KEY?KEY:'');" in code and "if(!key)return;" in code)
    g('the kill switch deletes only its own folder and unregisters',
      "p.length===3&&p[0]==='coursepage'&&p[1]===PAGE_PATH" in kill and 'self.registration.unregister()' in kill)

    # the clean-up rule, as the worker states it, run on sample names: the test worker never touches a live cache
    def own(k, folder):
        p = k.split('|')
        return len(p) == 3 and p[0] == 'coursepage' and p[1] == folder
    names = ['coursepage|/course/|2026-10-06.39', 'coursepage|/course/|2026-10-06.40', 'coursepage|/course-test/|2026-10-06.39-test',
             'record-2026-10-06.1', 'coursepage|/course|x', 'coursepage|/course/|x|y']
    g("the test worker's clean-up never matches a /course/ cache", not any(own(k, '/course-test/') for k in names if '|/course/|' in k)
      and [k for k in names if own(k, '/course-test/')] == ['coursepage|/course-test/|2026-10-06.39-test'])
    g("the live worker's clean-up never matches a test or RIB cache",
      [k for k in names if own(k, '/course/')] == ['coursepage|/course/|2026-10-06.39', 'coursepage|/course/|2026-10-06.40'])


def t24_version_gate_guards():
    """A65 in the page (2026-10-06.39). Guards, not proof: no JavaScript is run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    page = read(PAGE)
    code = build_test.strip_comments(page)
    g = lambda name, ok, detail='': report('24 A65: ' + name, ok, detail)
    font = 'https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap'
    g('the worker registered in the one form, once', code.count(SW_REGISTER) == 1 and code.count('serviceWorker.register(') == 1)
    g('the font stylesheet does not hold the page',
      f'<link href="{font}" rel="stylesheet" media="print" onload="this.media=\'all\'">' in page
      and f'<noscript><link href="{font}" rel="stylesheet"></noscript>' in page and page.count(f'href="{font}"') == 2)
    ev = fn_body(code, 'function ensureVersion(')
    g('once confirmed, the check never runs again', ev.startswith('function ensureVersion(){\n  if(verOk)return Promise.resolve(true);'))
    g('the check: the page itself, no cache, a 20 s limit; confirmed only by its own PAGE_VERSION',
      "fetch(location.pathname+'?check='+Date.now(),{cache:'no-store',signal:ac.signal})" in ev and 'VER_TIMEOUT_MS=20000' in code
      and "if(m[1]===PAGE_VERSION){verOk=true;" in ev and 'if(!m)return false;' in ev)
    nv = fn_body(code, 'function verNewer(')
    g('a newer page: at most once a minute and twice in all, never where sessionStorage fails',
      'VER_GAP_MS=60000' in code and 'VER_TRIES=2' in code and "const pvKey=STORE+'pv-'+v;" in nv
      and '}catch(_){go=false;}' in nv and nv.count('location.replace(') == 1 and 'if(go){location.replace(' in nv)
    g('rechecked when the signal returns', "window.addEventListener('online',()=>{if(!verOk)ensureVersion();});" in code)
    sc = fn_body(code, 'async function saveCourses(')
    i, j = sc.find('if(!verOk){ensureVersion();'), sc.find('savingC=true')
    g('saveCourses holds every save and starts the check before anything is sent', 0 < i < j and sc.find('postFix(') > j)
    g('confirmed: the save line is redrawn whether held or stuck, and what was held is sent',
      'function verConfirmed(){saveState.verHeld=false;showSave();saveCourses();}' in code
      and "if(m[1]===PAGE_VERSION){verOk=true;verStuck='';verConfirmed();return true;}" in ev)
    pl = fn_body(code, 'async function pull(')
    a, b = pl.find('if(!verOk){await ensureVersion();if(stale())return;}'), pl.find('res=await saveCourses(true,k=>!mine(k),true);')
    g('a change of day checks the version first', 0 < a < b
      and "if(res.err&&res.err.kind==='version'){blockDay(oldDay,day,'version',[],[],quiet);return;}" in pl)
    bd = fn_body(code, 'function blockDay(')
    g('and stops with its own message, no "Change day anyway"',
      "else if(res==='version')msg='Still on '+F+': waiting to check the page version. Try again when there is signal.';" in bd)
    for head, name in (('async function typedAct(', 'withdraw and correct'), ('async function removeStartAsked(', "Remove Start's withdrawals"),
                       ('async function moveFix(', 'move to another race')):
        f = fn_body(code, head)
        k = f.find('if(!verReady(')
        g(name + ' wait for the version before posting', 0 < k < f.find('postFix('))
    u = code.find("if(act==='undoPlaced'){")
    g("Undo's withdrawals wait for the version before posting", u > 0 and u < code.find('if(!verReady(say))return;', u)
      < code.find("postFix({action:'withdraw',date:S.pulledDay,id:i.m.sid,reason:'estimate undone by the RO'}", u))
    g('verReady used exactly five times', code.count('if(!verReady(') == 5)
    g('new fixes never wait', 'verOk' not in fn_body(code, 'async function sendOutbox(') and 'verReady' not in fn_body(code, 'async function sendOutbox('))
    g('Send never waits', "const kept=keepWind(k,'sent'), fz=freezeNow();if(first||kept||fz){render();saveCourses();}}" in fn_body(code, 'function freezeSend(')
      and 'await' not in fn_body(code, 'function freezeSend('))
    g('the waiting and stuck lines', "['','Waiting: checking the page version']" in code
      and 'A newer page is on the server but this device keeps getting the old one.' in code)
    g('"All course changes saved" never while held', '!st.verHeld&&!verStuck&&st.okAt&&!n' in code)
    g('the Reload button, once, shown only when stuck', page.count('id="verReload"') == 1 and "$('verReload').hidden=!verStuck;" in code)


def t25_a78_guards():
    """A78 in the page (2026-10-06.40, .41). Guards, not proof: no JavaScript is run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    code = build_test.strip_comments(read(PAGE))
    g = lambda name, ok, detail='': report('25 A78: ' + name, ok, detail)
    ph = fn_body(code, 'function pickHtml(')
    i = ph.find('if(isLineMark(m.name))return')
    line = ph[i:ph.find('\n', ph.find('\n', i) + 1)]
    g("a line end's detail offers Withdraw only when endWithdrawable, and never Correct",
      i > 0 and "(endWithdrawable(m)?'<div class=\"fxDetAct\"><button type=\"button\" class=\"fxBtn\" data-fx=\"withdraw\"" in line
      and 'data-fx="correct"' not in line)
    g('endWithdrawable: a typed or placed position on the server, no estimate record, a replaced end, or none of its uses left',
      "function endWithdrawable(m){return isTypedPos(m)&&!!m.sid&&!m.pending&&(!helpOf(m)||!!goneOf(m)||!lineUsers(m,undefined,true).length);}" in code)
    ta = fn_body(code, 'async function typedAct(')
    a, b, c = ta.find("action:'withdraw',date:day,id:m.sid,reason:why"), ta.find('estsOf(k2).filter(refHit(m)).forEach(e=>{estDrop(e);hit=true;});'), ta.find("fxSel='';await pull(true);typedSays")
    g('a withdrawn placed end takes its estimate or set-pin record with it, after the server agreed and before the reload',
      0 < a < b < c and 'if(S.linePinAt[k2]&&refHit(m)(S.linePinAt[k2])){delete S.linePinAt[k2];hit=true;}' in ta and 'if(hit)stamp(k2,true);' in ta)
    wr = fn_body(code, 'async function withdrawReplaced(')
    pf = wr.find("postFix({action:'withdraw',date:S.pulledDay,id:m.sid,reason:'replaced by placing again'},OUTBOX_TIMEOUT_MS)")
    g('withdrawReplaced: typed positions only; every use, the sending state and the page version checked before posting',
      'if(!m||!isTypedPos(m))return;' in wr and 0 < wr.find('const used=lineUsers(m);') < wr.find('if(m.pending||!m.sid)return note(')
      < wr.find('if(!verOk){ensureVersion();return note(') < pf)
    g('withdrawReplaced never refuses or holds the placement (no verReady), and every way out short of withdrawing leaves a note',
      'verReady' not in wr and wr.count('return note(') == 5 and "if(w==='fpin'&&!(await finSavedWithout(old.ref)))return note('was not withdrawn: the course change is not saved yet." in wr and "catch(e){return note('was not withdrawn ('" in wr)
    g('the note is kept on this device only (S.orphans, not in a saved course record)',
      'S.orphans[m.sid||m.pid]={day:S.pulledDay,race:m.race,w,text:what+t};' in wr and 'orphans' not in fn_body(code, 'function recordFor('))
    g("the note shows under the end's list while the position is loaded", "+orphanNotes(w)+note;" in fn_body(code, 'function endPicker(')
      and "S.marks.some(x=>(x.sid||x.pid)===id)" in fn_body(code, 'function orphanNotes('))
    h = code[code.find("if(act==='pinAt'){"):code.find("if(act==='place'){")]
    sp = fn_body(code, 'function setPinAt(')
    g('setting the Start Pin again hands the replaced set pin to withdrawReplaced, after the new one is in place (.44: setPinAt)',
      0 < sp.find('old=S.linePinAt[k]||null') < sp.find("S.linePinAt[k]=Object.assign({ref:'s:'+id,at},was?{was}:{});") < sp.find("olds.push([old,'set at '+old.at]);")
      and 0 < h.find('set=setPinAt(k,src,t);') < h.find("for(const[o,did] of set.olds)await withdrawReplaced(k,'pin',o,did);"))
    h = code[code.find("if(act==='place'){"):code.find("if(act==='undoPlaced'){")]
    g('placing an end again hands the replaced end to withdrawReplaced, after the new one is in place',
      0 < h.find('const old=(S.lineEst[k]||{})[w]||null;') < h.find('S.lineEst[k]=Object.assign({},S.lineEst[k]||{},{[w]:rec});')
      < h.find("if(old)await withdrawReplaced(k,w,old,'placed '+old.m+' m at '+pad(old.brgM,3)+'°M');"))
    g('verReady still used exactly five times (the placement is never refused for the version)', code.count('if(!verReady(') == 5)
    # .41: a replaced end stays known as a page-placed end on every device until it is withdrawn
    h = code[code.find("if(act==='pinAt'){"):code.find("if(act==='place'){")]
    g('a replaced set pin is stored with its start before the withdrawal is tried (.44: in setPinAt)',
      "if(old){goneAdd(k,{w:'pin',ref:old.ref,at:old.at});" in fn_body(code, 'function setPinAt(')
      and 0 < h.find('set=setPinAt(k,src,t);') < h.find('stamp(k);commit();') < h.find('await withdrawReplaced('))
    h = code[code.find("if(act==='place'){"):code.find("if(act==='undoPlaced'){")]
    g('a replaced placed end is stored with its start before the withdrawal is tried',
      0 < h.find('if(old)goneAdd(k,Object.assign({},old));') < h.find('stamp(k);commit();') < h.find('if(old)await withdrawReplaced('))
    g('a stored replaced end is read as a placed estimate or a set Start Pin',
      "function estOf(m){return m?estAll().find(refHit(m))||goneAll().find(g=>!('at' in g)&&refHit(m)(g))||null:null;}" in code
      and "function setOf(m){return m?Object.values(S.linePinAt||{}).find(refHit(m))||goneAll().find(g=>'at' in g&&refHit(m)(g))||null:null;}" in code)
    hl = fn_body(code, 'function helpLong(')
    g('it is labelled ", replaced" in every shape (Start Pin set, start end placed, Finish Pin set, Finish boat placed)', "const rp=goneOf(m)?', replaced':'';" in hl and hl.count('+rp') == 3 and "fixWhen(m)+rp;};" in hl
      and "String(m.time||'').replace(/ on \\S+ \\d{1,2} \\S+$/,'')+rp;" in hl and "setFor('Finish Pin',fz.at)" in hl and "setFor('Start Pin',p.at)" in hl)
    g('auto (every race) and the earlier-race offer leave a replaced end out; the list still offers it',
      '&&!(m.race<r&&helpOf(m))&&!(isFinW(w)&&finOf(m))&&!goneOf(m)).sort(' in fn_body(code, 'function candidates(')
      and '&&helpOf(m)&&!goneOf(m)&&' in fn_body(code, 'function estEarlier(') and 'goneOf' not in fn_body(code, 'function endChoices('))
    g('every withdrawal takes the stored entry with it',
      'goneDrop(m);await pull(true);commit();}' in fn_body(code, 'async function withdrawReplaced(')
      and 'if(isLineMark(m.name))goneDrop(m);' in fn_body(code, 'async function typedAct('))
    u = code[code.find("if(act==='undoPlaced'){"):code.find('function setEnd(')]
    g('Undo on a start that chose a replaced end refuses with a message',
      "if((n.es||[]).some(e=>goneAll().includes(e))){say('Not undone: this end was replaced by placing again on another start." in u)
    rs = fn_body(code, 'async function removeStartAsked(')
    g('Remove Start withdraws its replaced ends too, and never a fix already gone (refFix, then filter)',
      'const its=fix(estsOf(k).concat((S.lineGone||{})[k]||[]).map(e=>({e,w:e.w}))' in rs
      and "const fix=l=>l.map(i=>Object.assign(i,{m:refFix(i.e.ref,i.w)})).filter(i=>i.m);" in rs
      and '.map(i=>Object.assign(i,{m:refFix(i.e.ref,i.w)})).filter(i=>i.m)' in rs
      and "'lineGone','lineFin','sent'];" in code[code.find('const START_KEYED='):code.find('const START_KEYED=') + 200])
    g('saved with the course only when there is one, counted as content, and read back (goneNorm)',
      '...(S.lineGone&&S.lineGone[k]&&S.lineGone[k].length?{lineGone:' in fn_body(code, 'function recordFor(')
      and '||r.linePinAt||r.lineGone||r.lineFin)return false;' in fn_body(code, 'function isEmptyRec(')
      and 'const lg=goneNorm(rec.lineGone); S.lineGone=S.lineGone||{}; if(lg)S.lineGone[k]=lg; else delete S.lineGone[k];' in fn_body(code, 'function applyServerCourses('))
    cg = fn_body(code, 'function checkGoneRefs(')
    g('a stored entry whose fix is gone from its race is removed on load, saved and said under the end\'s list (never silently)',
      'if(!stale()){finFollowAll();checkLineRefs(ln);checkGoneRefs(ln);checkFinRefs(ln);}' in code
      and '(S.lineGone[k]||[]).forEach(g=>{const m=refFix(g.ref,g.w);(m&&m.race===r?keep:out).push(g);});' in cg
      and 'if(!out.length)return;' in cg and 'S.lineFlags[k][g.w]=' in cg and 'stamp(k,true);if(ln&&!ln[k])ln[k]=LOAD_WHY[4];' in cg
      and "'a replaced line end whose fix is gone was removed',\n  'a finish line end whose fix is gone was removed'];" in code)
    g('a change of day clears the stored entries with the other per-start records',
      "'linePinAt','lineGone','lineFin','winds','cardCfg'].forEach(f=>" in code)


def t26_fixes43_guards():
    """.43 fix round (Pat, 21 October 2026) in the page. Guards, not proof: no JavaScript is run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    page = read(PAGE)
    code = build_test.strip_comments(page)
    g = lambda name, ok, detail='': report('26 .43: ' + name, ok, detail)
    # fix 1
    g('1: a chosen button in a one-of group is filled, the others outlined',
      '.ghost[aria-pressed="true"]{background:var(--sea);border-color:var(--sea);color:var(--paper)}' in page
      and code.count('aria-pressed="\'+(m===v)+\'"') == 1 and "aria-pressed=\"'+(d.sq==='wind')+'\"" in code)
    g('1: the finish side buttons are one row, Port filled red, Starboard filled green, Not given grey',
      '.sideBtns button[data-v="port"][aria-pressed="true"]{background:var(--warn);color:var(--paper)}' in page
      and '.sideBtns button[data-v="starboard"][aria-pressed="true"]{background:var(--ok);color:var(--paper)}' in page
      and '.sideBtns button[data-v=""][aria-pressed="true"]{background:var(--muted);color:var(--paper)}' in page
      and "b('port','Port')+b('starboard','Starboard')+b('','Not given')" in code)
    # fix 2
    rd = fn_body(code, 'function render(')
    g('2: messages are cleared for the start left, then drawn under their buttons, on every render',
      'msgsMoved();' in rd and rd.index('msgsMoved();') < rd.index('heldSay();') and 'renderNotSent(); paintMsgs();' in rd
      and 'if(newDay)actMsgs={};' in fn_body(code, 'async function pull('))
    mm = fn_body(code, 'function msgsMoved(')
    g('2: leaving a start or race clears what was said there, and only there',
      "if(actMsgK&&actMsgK!==k){" in mm and "x.indexOf(actMsgK+'|')===0" in mm and "x.indexOf(r+'|*|')===0" in mm)
    pm = fn_body(code, 'function paintMsgs(')
    g("2: a message goes in its button's slot, otherwise its row's",
      "slots.find(s=>s.dataset.msg===a)||slots.find(s=>s.dataset.msg===MSG_GROUP[a])" in pm and "kk!==ckey(S.race,S.start)&&kk!==S.race+'|*'" in pm)
    est = code[code.find("document.addEventListener('click',async e=>{const b=e.target.closest('.estAct')"):code.find('async function finAct(')]
    g('2: the start and finish line helpers say under their buttons, and an action clears its row first',
      "say=(t,ok)=>sayIn(act,k)(t,ok);" in est and 'msgClear(act);' in est and "$('readStatus')" not in est
      and "$('readStatus')" not in fn_body(code, 'async function finAct('))
    g('2: Remove Start, the Finish list, Check recorded marks, the mover, Read marks, typing and Save to the race record say under their buttons',
      "say=sayIn('removeStart');" in fn_body(code, 'async function removeStartAsked(')
      and "sayIn('finishSel')(t,false);" in code and "sayIn('fx:'+fxSel)(t,ok);" in fn_body(code, 'function typedSays(')
      and "say=sayIn('fx:'+k);" in fn_body(code, 'function pickFix(') and "const say=sayIn('move');" in fn_body(code, 'async function moveFix(')
      and "const say=sayIn('read');" in code and "const say=sayIn('typed');" in code and "sayIn('savepaste')(msg,true);" in fn_body(code, 'function savePasted(')
      and all(f"$('readStatus')" not in fn_body(code, h) for h in ('async function removeStartAsked(', 'function pickFix(', 'async function moveFix(', 'function savePasted(', 'async function typedAct('))
      and 'data-msg="removeStart"' in page and 'data-msg="savepaste"' in page and 'data-msg="read"' in page and 'data-msg="typed"' in page)
    # fix 3
    fs = fn_body(code, 'function finSay(')
    g('3: no side while the Finish Pin is the midpoint, in WhatsApp and in the row',
      'side=!z.mid&&z.pin&&z.pin.side;' in fs and 'if(pin&&!z.mid){' in fn_body(code, 'function finRowHtml('))
    # fix 4
    g('4: the finish choice goes home before the rows are redrawn and into the Finish line row after',
      "$('finishHome').appendChild($('finishCard'));$('finishHome').appendChild($('finishFields'));" in rd
      and rd.index("$('finishHome').appendChild") < rd.index("const ol=$('course');ol.innerHTML='';")
      and "box.appendChild($('finishFields'));box.appendChild($('finishCard'));" in rd
      and "<div class=\"finChoice\"></div>'+msgSlot('finishSel')+msgSlot('finFollow')+" in rd)
    # fix 5
    g('5: one plain line of this race\'s own line ends under the chips, never chips',
      "const le=S.marks.filter(m=>m.race===S.race&&!m.card&&!m.virtual&&isLineMark(m.name))" in rd
      and "p.textContent='Line ends: '+le.map(lineEndWords).join(' · ');" in rd
      and "const bm0=bank().filter(m=>!isLineMark(m.name));" in rd and 'function lineEndWords(m){' in code)
    # fix 6
    g('6: a line end set or placed on this page is never carried into a later race',
      "S.marks.filter(m=>m.race<S.race&&!isCourseCard(m)&&!isRwCard(m)&&!helpOf(m))" in fn_body(code, 'function bank('))
    # fix 7
    fst = fn_body(code, 'function finishState(')
    g('7: on Laid line the Finish list choice is saved with the card set-up (lfc); with none, Laid line is as before',
      "if(c.lfc==='start'||c.lfc==='finishpin'||c.lfc==='last')r.lfc=c.lfc;" in fn_body(code, 'function cardRec(')
      and "if(c.lfc==='last')return {kind:'last'};" in fst and fst.index("c.lfc==='last'") < fst.index('if(finPinLine(r,st,sel))return {kind:\'finishpin\'};')
      and "if(c.lfc)return c.lfc;return c.lfs==='start'&&!finPinLine(r,st)?'start':'finishpin';" in fn_body(code, 'function finChoiceOf(')
      and "else{c.lf='laid';c.lfc=v;if(v==='start')c.lfs='start';else delete c.lfs;}}" in code and "else S.finishes[k]=v;}" in code)
    # fix 8
    fa = fn_body(code, 'async function finAct(')
    g('8: copies follow their source on every render, and before the end the source replaces is withdrawn',
      rd.index('finFollowAll();') < rd.index('msgsMoved();')
      and fa.count('finFollowAll();commit();') == 7   # .44: also placing the Finish Pin, a newer fix, box 3 and the emergency midpoint; .46 the Finish boat from the mark
      and fa.index('finFollowAll();commit();') < fa.index("if(old)await withdrawReplaced(k,'fpin'")
      and all(fa.rfind('finFollowAll();commit();', 0, i) > fa.rfind('return;}', 0, i)
              for i in [x.start() for x in re.finditer(r"if\(old\)await withdrawReplaced\(k,'f(pin|cb)'", fa)]))
    g('8: Undo and Remove Start of a source are refused while starts share its line, naming them',
      "if(shr.length){say('Not undone: '+shr.join(', ')" in fa
      and "if(shr.length){say('Start '+(i+1)+' not removed: '+shr.join(', ')" in fn_body(code, 'async function removeStartAsked('))
    g('8: a sharing start that follows says so in its Finish line row',
      "actMsgs[msgKey('finFollow',k)]={t:'Finish line updated from Race '+r+' Start '+(st+1)+' at '+hhmm(Date.now())+'.',ok:null};" in fn_body(code, 'function finFollowAll('))
    # fix 9
    g('9: no finish sentence before there is a Finish Pin', "if(!pin)return '';" in fs and fs.index("if(!pin)return '';") < fs.index("return 'Finish between the committee boat and '"))
    # fix 10
    g("10: Copy for Sail Scoring keeps its x-estimate wording (helpX, the wording before .43)",
      'const w=helpX(md.end)||fixWords2(md.end);' in fn_body(code, 'function lineEstNow(') and 'const w=helpX(fl.end)||fixWords2(fl.end);' in fn_body(code, 'function finEstNow(')
      and 'helpLong(' not in fn_body(code, 'function lineEstNow(') and 'helpLong(' not in fn_body(code, 'function finEstNow('))
    g('10: a placed end says its reference with that end\'s time, then its own time on the water',
      "return lab+' – estimate: '+estAt(e)+(fw?' ('+fw+')':'')+'; on the water '+fixWhen(m)+rp;" in fn_body(code, 'function helpLong(')
      and "le.fromWhen?{fromWhen:String(le.fromWhen)}:{}" in fn_body(code, 'function estRec(')
      and "v.cb.fromWhen?{fromWhen:String(v.cb.fromWhen)}:{}" in fn_body(code, 'function finNorm('))


def t27_fixes44_guards():
    """.44 (Pat, 21 October 2026): four faults and the tidy of the Start line and Finish line rows. Guards, not proof: no
    JavaScript is run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    page = read(PAGE)
    code = build_test.strip_comments(page)
    g = lambda name, ok, detail='': report('27 .44: ' + name, ok, detail)
    so = fn_body(code, 'async function sendOutbox(')
    fa = fn_body(code, 'async function finAct(')
    # fault 1
    g('fault 1: a helper\'s "sending…" follows its fix: sent, refused, waiting; such fixes stay out of the committee boat line',
      "if(!fixSays(f,'sent'))said.push(" in so and "if(!fixSays(f,'refused',why))said.push(outRefused(f,why));" in so
      and "fixSays(q,'wait',outReason(stop.k,stop.e));" in so
      and "msgFix('finPinAt',k,ref.slice(2));" in fa and "msgFix('finPlace',k,rec.ref.slice(2));" in fa
      and "msgFix('pinAt',k,set.id);" in code and "msgFix('place',k,id);" in code and "msgFix(b.dataset.area||'finPinPlace',k,rec.ref.slice(2));" in fa
      and "x.t=x.base.replace('sending…',now);" in fn_body(code, 'function fixSays('))
    # fault 2
    cf = fn_body(code, 'function checkFinRefs(')
    g('fault 2: copies are brought into step before the stale check, which never reports what a copy holds and removes such notes',
      'if(!stale()){finFollowAll();checkLineRefs(ln);checkGoneRefs(ln);checkFinRefs(ln);}' in code
      and "if(z.pin&&!z.src&&!refFix(z.pin.ref,'fpin')){" in cf and "if(z.cb&&!z.src&&!refFix(z.cb.ref,'fcb')){" in cf
      and "if(z.mid&&!z.src&&!refFix(z.mid.ref,'fpin')){" in cf and "/, saved with Race \\d+ Start \\d+, is no longer among the day's fixes/.test(f[w])" in cf)
    # fault 3
    g('fault 3: the midpoint and a placed Finish boat keep the committee boat end they replaced, and Undo puts it back',
      "const was=x=>typeof x.fcb==='string'&&(x.fcb==='none'||/^[sl]:/.test(x.fcb))?{fcb:x.fcb}:{};" in fn_body(code, 'function finNorm(')
      and "mid:Object.assign({ref:sref(p)},was?{fcb:was}:{})" in fa and "{const was=z0.cb?z0.cb.fcb:ls().fcb;if(was)rec.fcb=was;}" in fa
      and "back=finBack(k,z0.mid);" in fa and "const back=finBack(k,z.cb);" in fa
      and "if(refFix(was,'fcb')){L.fcb=was;return '';}" in fn_body(code, 'function finBack('))
    # fault 4
    g('fault 4: only real marks in "Start Pin at", "Finish Pin at" and the Place helper\'s "from" list',
      "return !!m&&(!c||!c.rw&&c.type!=='Start/finish modelling point');" in fn_body(code, 'function isRealMark(')
      and "if(!isRealMark({card:nm}))return;" in fn_body(code, 'function fixedOpts(')
      and "&&!isLineMark(m.name)&&isRealMark(m)).map(m=>[m.id,m])" in fn_body(code, 'function raceMarkOpts(')
      and "&&!isLineMark(m.name)&&isRealMark(m);" in fn_body(code, 'function finPinOpts('))
    # a: colours
    g('a: the caution colour, light and dark, and its classes',
      page.count('--caution:') == 3 and '.cautTxt{color:var(--caution)!important}' in page and '.note.caut{border-color:var(--caution);color:var(--caution)}' in page
      and '.muteTxt{color:var(--muted)!important}' in page)
    bl = fn_body(code, 'function buildLegs(')
    g('a: section 4 keeps red only for what holds Send back; leg rows: depth notes grey, line estimates amber',
      "const warnC=farLine.concat(checks(ents,cs)), warnR=warn.filter(x=>!warnC.includes(x));" in bl
      and "(fixNote?'<br><span class=\"viaTxt muteTxt\">'+esc(fixNote)+'</span>':'')" in bl
      and "'<br><span class=\"viaTxt cautTxt\">start line: estimate</span>'" in bl and "'<br><span class=\"viaTxt cautTxt\">finish line: estimate</span>'" in bl)
    g('a: Copy for Sail Scoring: INCOMPLETE red, the rest amber; Check recorded marks: Likely wrong red, Check amber',
      "(/^INCOMPLETE/.test(t)?'flag':'caut')" in fn_body(code, 'function setCC(') and "(f.lvl==='bad'?' bad':' caut')" in fn_body(code, 'function fxFlag('))
    # b: two sections per row, in Pat's order
    rd = fn_body(code, 'function render(')
    fr = fn_body(code, 'function finRowHtml(')
    g('b: the Start line row is the Committee boat section, the Start Pin section, then the line',
      "startSec('cb',!!cardS||!!markStartOf())+startSec('pin',!!cardS||!!markStartOf());" in rd and "sw+ends+sMiss+'<div id=\"lineInfo\" class=\"endSec\">'+lineInfo()+'</div>'+gsLink+" in rd)
    g('b: the Finish line row: the Finish type list, then (a finish set) the Finish Pin section, the Committee boat section, the line',
      "box.appendChild($('finishFields'));box.appendChild($('finishCard'));" in rd and "h=p+c+l;}" in fr
      and fr.index("<div class=\"secHead\">Finish Pin</div>") < fr.index("<div class=\"secHead\">Committee boat</div>"))
    # c: helpers open by themselves only when their end is missing
    g('c: a helper opens by itself only while its end is missing, otherwise behind its Change … button (Close once open)',
      "const open=!e.m&&!mk||helpIs('start',w);" in fn_body(code, 'function startSec(') and "open=!set||helpIs('fin','all');" in fr
      and "changeBtn('fin','all',open?'Close':'Change finish…')" in fr and "return helpIs(row,w)?changeBtn(row,w,'Close'):'';" in fn_body(code, 'function helpTop('))
    # d and e
    ep = fn_body(code, 'function endPicker(')
    g('d: no echo line and no Back to auto under a list; only an estimate in use is said again, in amber',
      'endAuto' not in ep and "esc(e.reason)" not in ep and "(isEst?'<div class=\"meta cautTxt\">'+esc(helpLong(e.m))+'</div>':'')" in ep)
    g('e: one note per line: no second "estimate –" note beside an end\'s estimate label',
      'Finish line: estimate –' not in fn_body(code, 'function finLineNote(') and 'Start line: estimate –' not in fn_body(code, 'function lineInfo('))
    # f: shorter wording
    g('f: the shorter wording', "reason:'Auto: latest by '+hm" in code and "reason:'Auto (saved)'" in code and "reason:'As Start '+(from+1)" in code
      and "opt('none','None (not used)')" in ep and "Pin end:<div class=\"sideBtns\"" in fr and 'auto finds no committee boat or Start Pin' not in code)
    # g: Finish type, the card switch folded in
    g('g: "Finish type" is the row\'s main choice: bold label, larger text, dark border',
      '<label>Finish type<select id="finishSel">' in page and '.finType select{font-size:1.05rem;font-weight:700;border:2px solid var(--ink);padding:12px}' in page)
    g('g: on a card course the Finish type list holds the card\'s own finish and writes only what the switch wrote',
      "[['card:auto',mark?'From the card: the finish boat to '+c.f:'From the card: Grassy']]" in fn_body(code, 'function finTypeOpts(')
      and "if(c){if(v==='card:auto')delete c.lf;else if(v==='card:point')c.lf='card';" in code
      and "else{c.lf='laid';c.lfc=v;if(v==='start')c.lfs='start';else delete c.lfs;}}" in code
      and "lineSwitch('f')" not in code)


def t28_local_build(tmp):
    """--label LOCAL: the local test site's build (php -S on this PC), never uploaded."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    live = read(PAGE)
    v = re.search(r"const PAGE_VERSION='([^']+)';", live).group(1)
    g = lambda name, ok, detail='': report('28 LOCAL: ' + name, ok, detail)
    norm, loc = os.path.join(tmp, 'out28n'), os.path.join(tmp, 'out28l')
    rn, rl = run(PAGE, norm), run(PAGE, loc, label='LOCAL')
    g('normal and LOCAL builds exit 0', rn.returncode == 0 and rl.returncode == 0, rn.stdout + rl.stdout + rl.stderr)
    if rn.returncode or rl.returncode:
        return
    nt, lt = read(os.path.join(norm, 'course-test', 'index.html')), read(os.path.join(loc, 'course-test', 'index.html'))
    m = re.search(r"const PAGE_VERSION='([^']+)';", lt)
    lv = m.group(1) if m else ''
    g('PAGE_VERSION is <version>-test-L<HHMM>', re.fullmatch(re.escape(v) + r'-test-L\d{4}', lv) is not None, lv)
    g('the LOCAL TEST banner with that version, no TEST COPY',
      f'>LOCAL TEST – not live data · /marks-test/ · PAGE_VERSION {lv}</div>' in lt and 'TEST COPY' not in lt)
    g('the LOCAL TEST title', lt.count('<title>LOCAL TEST – ') == 1)
    b = read(os.path.join(loc, 'BUILD.txt'))
    g('BUILD.txt names the version and LOCAL', f'PAGE_VERSION {lv}\n' in b and 'label LOCAL: for the local test site only' in b)
    g('the normal build names no LOCAL', 'LOCAL' not in nt and 'label LOCAL' not in read(os.path.join(norm, 'BUILD.txt')))
    back = (lt.replace(f"const PAGE_VERSION='{lv}';", f"const PAGE_VERSION='{v}-test';")
              .replace(f'PAGE_VERSION {lv}</div>', f'PAGE_VERSION {v}-test</div>')
              .replace('<title>LOCAL TEST – ', '<title>TEST – ')
              .replace('>LOCAL TEST – not live data · ', '>TEST COPY – not live data · '))
    g('nothing else differs from the normal build', back == nt)
    for f in ('course-test/sw.js', 'marks-test/marks.php'):
        g(f + ' byte-identical to the normal build\'s', read(os.path.join(loc, f), 'rb') == read(os.path.join(norm, f), 'rb'))
    # refused in a LOCAL build, built normally; a refusal leaves the earlier LOCAL build as it was
    before = read(os.path.join(loc, 'course-test', 'index.html'), 'rb')
    script_end = live.rindex('</script>')
    inject = lambda code: live[:script_end] + code + '\n' + live[script_end:]
    cases = {
        'tradboats.ie in a comment': live.replace('<head>', '<head>\n<!-- copied from tradboats.ie -->', 1),
        'orc-ireland.org in a string': inject("const HOST='orc-ireland.org';"),
        'TRADBOATS in capitals': inject("const H='TRADBOATS.IE';"),
        'a web address not in the list': inject("const U='https://example.com/x';"),
        'an http address': inject("const U='http://192.168.0.34:8765/course-test/';"),
        'an address starting //': inject("const U='//example.com/x';"),
        'an address that only begins like an allowed host': inject("const U='https://fonts.googleapis.com.example.com/x';"),
        'another path on an allowed host': inject("const U='https://unpkg.com/other@1.0.0/x.js';"),
    }
    for name, text in cases.items():
        p = os.path.join(tmp, 'bad28.html')
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        r, rn2 = run(p, loc, label='LOCAL'), run(p, os.path.join(tmp, 'out28n2'))
        after = read(os.path.join(loc, 'course-test', 'index.html'), 'rb')
        g('refused: ' + name, text != live and r.returncode != 0 and 'REFUSED' in r.stdout and after == before
          and rn2.returncode == 0, f'LOCAL exit {r.returncode}; normal exit {rn2.returncode}; {r.stdout.strip()[:160]}')
    for name, args in {'an unknown label': ('TEST', '1432'), 'a build time not HHMM': ('LOCAL', '14:32')}.items():
        try:
            build_test.build_page(live, *args)
            g('refused: ' + name, False, 'built')
        except build_test.Refused:
            g('refused: ' + name, True)
    r = subprocess.run([sys.executable, SCRIPT, '--page', PAGE, '--out', os.path.join(tmp, 'out28x'), '--label', 'TEST'],
                       capture_output=True, text=True)
    g('refused: --label other than LOCAL on the command line', r.returncode != 0 and not os.path.exists(os.path.join(tmp, 'out28x')))


def t29_pin_routes_guards():
    """.44, the pin routes (Pat, 22 October 2026): a pin placed by distance and bearing is measured from the committee boat
    in use or another mark laid in this race, never a harbour mark; a pin at a harbour mark is set at it. Guards, not
    proof: no JavaScript is run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    page = read(PAGE)
    code = build_test.strip_comments(page)
    g = lambda name, ok, detail='': report('29 pin routes: ' + name, ok, detail)
    pb, ss, pa = fn_body(code, 'function placeBox('), fn_body(code, 'function startSec('), fn_body(code, 'function pinAtBox(')
    ok, po = fn_body(code, 'function pinFromOk('), fn_body(code, 'function pinFromOpts(')
    pin_h = code[code.find("if(act==='pinAt'){"):code.find("if(act==='place'){")]
    pl_h = code[code.find("if(act==='place'){"):code.find("if(act==='undoPlaced'){")]
    fa, fr, sp = fn_body(code, 'async function finAct('), fn_body(code, 'function finRowHtml('), fn_body(code, 'function setPinAt(')
    # 1: both Start Pin routes with a committee boat in use
    g('1: with a committee boat in use the Start Pin helper offers Set Start Pin at, then Place Start Pin',
      "pinAtBox(!!oth)+(oth?routeOr()+placeBox('pin',oth,!e.m):'')" in ss and "if(endPick('cb').m)return;" not in pin_h)
    g('1: the set-pin message drops "Now place the committee boat from it." while a boat is in use',
      "(cbInUse?'':' Now place the committee boat from it.')" in pin_h and "const cbInUse=!!endPick('cb').m, set=setPinAt(k,src,t);" in pin_h
      and "(cbInUse?'.':'; then place the committee boat from it.')" in pa)
    # 2: the Start Pin's "from" list
    g('2: the Start Pin\'s "from" list: "Committee boat in use: R1 10:50" first, then pinFromOpts, no Fixed marks',
      "w==='pin'?'Committee boat in use: '+fixWhen(have)" in pb
      and "(w==='pin'?pinFromOpts(d.ref,have.id):raceMarkOpts(d.ref,have?have.id:'')+fixedOpts(d.ref))" in pb
      and 'fixedOpts' not in po and 'raceMarkOpts' not in po and 'bank()' not in po)
    g('2: only this race\'s laid marks: its recorded or typed fixes, or a club laid mark at a fix (not pasted)',
      "if(!m||m.virtual||m.missing||!isFinite(m.lat)||isLineMark(m.name)||!isRealMark(m))return false;" in ok
      and "if(m.card)return isLaidCard(m)&&!!m.atFix&&!(m.laidSt&&m.laidSt.use&&isPasted(m.laidSt.use));" in ok
      and "return m.race===S.race&&!isPasted(m);" in ok and "S.marks.filter(m=>!m.card&&m.race===S.race)" in po)
    g('2: a held harbour-mark "from" is refused in the Place handler, with Pat\'s wording',
      "if(w==='pin'&&ref!==have&&!pinFromOk(ref)){" in pl_h
      and "'A Start Pin is never placed from a harbour mark: use Set Start Pin at to put it at the mark.'" in pl_h)
    g('2: the committee boat\'s own "from" list keeps the harbour marks (fixedOpts, once)', pb.count('fixedOpts(d.ref)') == 1
      and "function estRef(v){const c=/^card:/.test(v)&&CARD.marks[v.slice(5)];return c?{name:v.slice(5),lat:c.lat,lon:c.lon,card:v.slice(5)}:v?markById(v):null;}" in code)
    # 3: an earlier race's pin, set at its position
    ep = fn_body(code, 'function earlierPinOpts(')
    g('3: "Start Pin laid for an earlier race (set at its position)" in Set Start Pin at, and the Finish Pin one in Set Finish Pin at',
      "earlierPinOpts('pin',d.at)" in pa and "earlierPinOpts('fpin',sel)" in fn_body(code, 'function finPinOpts(')
      and "lab+' laid for an earlier race (set at its position)\">'" in ep and "'Race '+m.race+'\\'s '+lab+' ('+fixWhen(m)+')'" in ep
      and "m.race<S.race&&test(m.name)&&!isPasted(m)&&!goneOf(m)" in ep)
    g('3: set at it, named "Race 1\'s Start Pin (recorded R1 10:58)" (or Finish Pin); never "Start Pin Race 1\'s Start Pin"; short "Race 1\'s pin" on drawings',
      "isStartPin(src.name)&&src.race<S.race?earlierAt('Start Pin',src)" in sp
      and "isFinishPin(src.name)&&src.race<S.race?earlierAt('Finish Pin',src)" in fa
      and "function earlierAt(lab,src){return 'Race '+src.race+'\\'s '+lab+' ('+(isTypedPos(src)?'typed':'recorded')+' '+fixWhen(src)+')';}" in code
      and "function pinName(lab,at){return / Pin$/.test(at)||/'s (Start|Finish) Pin \\(/.test(at)?at:lab+' '+at;}" in code
      and "function shortAt(at){return String(at).replace(/^(Race \\d+'s) (Start|Finish) Pin\\b.*$/,'$1 pin');}" in code)
    # 6 (Pat, 22 October 2026): after a manual choice, only a NEWER recorded fix is offered; start ends never after the start
    fb = fn_body(code, 'function finPinPlaceBox(')
    nf = fn_body(code, 'function newerEnd(')
    g('6: "Newer: …" only for a fix newer than the end in use; a start line end never after the start time, a finish end after it too',
      "fixMoment(x)>t0&&(!startEnd||fixMoment(x)<=ts)" in nf and "const startEnd=w==='cb'||w==='pin'" in nf and "!helpOf(x)" in nf
      and "re?use('Newer: '+fixText(re,w),re):" in code and "data-act=\"finUse\"" in fr and "if(act==='finUse'){" in fa
      and "if(t.dataset.w==='fcb'){setEnd('fcb',t.dataset.f);return;}" in code)
    g('6: the in-use wording: "Start Pin: at …, set for Race 2 at 13:00" (Finish Pin the same)',
      "lab+': at '+at+', set for Race '+m.race+' at '" in fn_body(code, 'function helpLong('))
    # 7: the start's estimated committee boat at the finish
    g('7: the finish Auto uses the start\'s estimated committee boat, marked as an estimate; the finish line is then an estimate',
      "if(s.m&&helpOf(s.m))return {m:s.m,how:'auto',reason:'Auto: the start\\'s committee boat – estimate',est:true};" in fn_body(code, 'function autoEnd(')
      and "sc=!f&&estOf(fl.cb)" in fn_body(code, 'function finEstNow(') and "estWords(sc)+' (the start\\'s estimate)'" in fn_body(code, 'function finEstNow(')
      and 'Start boat is an estimate: choose a committee boat or place the Finish boat' not in code)
    # 5 and 12, 16: the suggested pin end, Square to the last leg, the Option 1 note
    g('5: the Finish Pin end suggested from the approach, on its button only, until the RO taps a side (sideSet)',
      "const sg=!side&&!(z.pin&&z.pin.sideSet)?finSideSuggest():null;" in fr and "' (suggested from the approach from '+esc(sg.from)+')'" in fr
      and "z.pin=Object.assign({},z.pin,{side:v,sideSet:true})" in fa and "return {v:rel<180?'starboard':'port',from:p.name};" in fn_body(code, 'function finSideSuggest(')
      and 'sideSet' not in fn_body(code, 'function setOut('))
    sqr = fn_body(code, 'function finSqRow(')
    g('12: "Suggest: Square to the last leg" in box 1, with which end the pin goes', "finSqRow(1,d)+note" in fb and 'data-act="sqLeg" data-b="\'+n+\'"' in sqr
      and 'Square to the last leg</button>' in sqr and "(n===2?'Committee boat':'Finish Pin')+': '+finSqEnd(n,d)+' end</button>" in sqr and 'function finSuggest(' not in code)
    g('16: Option 1 of the Finish Pin says it is saved at that mark\'s position', "Saved at that mark\\'s position as this start\\'s Finish Pin." in fn_body(code, 'function finPinBox('))
    # 4: Place Finish Pin from the committee boat end in use only
    fb = fn_body(code, 'function finPinPlaceBox(')
    fp = fa[fa.find("if(act==='finPinPlace'){"):fa.find("if(act==='finPlace'){")]
    g('4: box 1 is the committee boat that stays (its list), then Place Finish Pin from it, with no list of marks',
      "const b1=endPicker('fcb')+(ce.m?finPinPlaceBox(ce.m):" in fn_body(code, 'function finBoxes(') and 'data-f="ref"' not in fb and '<select' not in fb
      and "°M from the '+who+' in use: '+esc(fixWhen(cb))+' on the water '" in fb and 'data-act="finPinPlace">Place pin</button>' in fb)
    g('4: placed from endPick(\'fcb\') only, a typed position saved as this start\'s Finish Pin, an estimate',
      "const have=endPick('fcb').m;if(!have)return;" in fp and "const p=geoDest(have,((brgM-varW())%360+360)%360,dist);" in fp
      and "rec={ref:add('Finish Pin',p,t),at:'',side:z0.pin&&z0.pin.side||'',from:fixWords2(have),m:Math.round(dist),brgM:Math.round(brgM)%360};" in fp
      and 'ls().fpin=rec.ref;' in fp and "if(old)finGoneAdd(k,finPinRec(old));" in fp and "if(old)await withdrawReplaced(k,'fpin',old,endDid(old));" in fp)
    g('4: a placed Finish Pin is saved and read back (m, from, brgM) and counts as this start\'s own end everywhere',
      "+v.pin.m>0?Object.assign({from:String(v.pin.from||''),m:+v.pin.m,brgM:+v.pin.brgM||0}" in fn_body(code, 'function finNorm(')
      and "+g.m>0?{from:String(g.from||''),m:+g.m,brgM:+g.brgM||0}:{}" in fn_body(code, 'function finGoneRec(')
      and "function finPinOwn(p){return !!p&&(!!p.at||+p.m>0);}" in code
      and code.count('finPinOwn(') >= 10 and 'z.pin&&z.pin.at' not in code and 'fz.pin&&fz.pin.at' not in code)
    g('4: it is an estimate: amber, in the leg table and Copy for Sail Scoring ("Finish Pin placed …"), helpLong "Finish Pin – estimate"',
      "function finIsEst(m){const f=finOf(m);return !!f&&(f.w==='fcb'||+f.m>0);}" in code
      and "const est=m=>m&&(estOf(m)||finIsEst(m));" in fr and "const isEst=e.m&&(estOf(e.m)||finIsEst(e.m));" in code
      and "fp&&fp.w==='fpin'&&+fp.m>0?finPinWords(fp):''" in fn_body(code, 'function finEstNow(')
      and "(+fz.m>0?placed('Finish Pin',fz):" in fn_body(code, 'function helpLong(')
      and "function finPinWords(e){return 'Finish Pin placed '+e.m+' m at '+pad(e.brgM,3)+'°M from '+e.from;}" in code)
    g('4: box 2 sets the Finish Pin at the mark, then places the Finish boat from it (finPinAt, finPlace)',
      "await finAct('finPinAt',{dataset:{}},k,sayIn('finPinAt',k));" in fa and "await finAct('finPlace',{dataset:{}},k,sayIn('finPlace',k));" in fa
      and "if(act==='finPlace'){if(z0.mid)return;const have=endPick('fpin').m;if(!have)return;" in fa)
    # 5: the committee boat placed from a harbour mark
    g('5: from a harbour mark with no Start Pin in use, the Start Pin is set at that mark too (one placement, both ends)',
      "const harbour=w==='cb'&&ref!==have&&isCourseCard(ref)&&isRealMark(ref), hm=harbour?ref.card:'';" in pl_h
      and "set=harbour&&ref!==have?setPinAt(k,ref,t,prev):null;" in pl_h and "', and the Start Pin set at '+set.at+(prevW?' in place of '+prevW:'')+'; both saved as typed positions'" in pl_h
      and "if(w==='cb')h+=open?(e.m?helpTop('start','cb'):'')+placeBox('cb',oth,!e.m):changeBtn('start','cb','Change boat…');" in ss
      and 'From a harbour mark, the Start Pin is set at that mark too, so one placement gives both ends.' in pb)
    g('13: with a different Start Pin in use it is switched for the harbour mark, named, and Undo puts it back',
      "if(harbour&&have){const sp=setOf(have);if((sp&&sp.at===ref.card)||geo(have,ref).m<1)ref=have;else prev=have;}" in pl_h
      and 'Not placed: the Start Pin in use is' not in code and "was=prev?pinWas(k,prev):null" in sp
      and "const back=was?pinBack(k,was):'';" in code and "S.outbox.push({action:'add',id,date:day,race:S.race,name:'Start Pin',lat:was.lat,lon:was.lon,acc:0,time:t});" in fn_body(code, 'function pinBack(')
      and "const was=pinWasNorm(pa.was);" in code)
    g('5: from a laid mark or the Start Pin in use the Start Pin is unchanged (only a harbour mark sets it)',
      pl_h.count('setPinAt(') == 1 and 'isCourseCard(ref)' in pl_h)
    # one pin record per start: setting replaces a placed pin and placing replaces a set one, each kept as replaced (A78)
    g('one Start Pin of this start at a time: set replaces placed, placed replaces set, each kept as replaced until withdrawn',
      "if(oldP){estDrop(oldP);goneAdd(k,Object.assign({},oldP));" in sp
      and "if(oldAt){delete S.linePinAt[k];goneAdd(k,{w:'pin',ref:oldAt.ref,at:oldAt.at});}" in pl_h
      and "if(oldAt)await withdrawReplaced(k,'pin',oldAt,'set at '+oldAt.at);" in pl_h)
    # 6: saved data read as before
    g('6: saved data read as before: placements from a harbour mark keep their from; a record with no hm keeps its wording (A124)',
      "from:rp?pinName('Start Pin',rp.at):ref.card&&!ref.atFix?ref.name:fixWords2(ref)" in pl_h
      and "function estWords(e){return (e.w==='cb'?'committee boat':'Start Pin')+' placed '+estAt(e);}" in code
      and "e.m+' m at '+pad(e.brgM,3)+'°M from '+e.from;}" in fn_body(code, 'function estAt('))
    # layout (Pat, 22 October 2026): each pin route in its own box, its message inside it, "or" only between two
    rb = fn_body(code, 'function routeBox(')
    g('layout: "Option 1 – Pin at a mark" and "Option 2 – Pin by distance and bearing", each a bordered box',
      "(n===1?'Option 1 – Pin at a mark':'Option 2 – Pin by distance and bearing')" in rb and '<div class="routeBox" data-route="' in rb
      and '.routeBox{border:1px solid var(--line);border-radius:8px;' in page and "function routeOr(){return '<div class=\"routeOr\">or</div>';}" in code)
    g('layout: Set Start Pin at is Option 1, Place Start Pin is Option 2, each with its message inside its box',
      pa.startswith('function pinAtBox(cbInUse){') and "return routeBox(1,'<div class=\"meta estBox\">Set Start Pin at " in pa
      and "msgSlot('pinAt')+" in pa and pa.rstrip().endswith("'</div>');}")
      and "const body='<div class=\"meta estBox\">Place '+what+': " in pb and "return (w==='pin'?routeBox(2,body):body)+" in pb
      and pb.index("msgSlot('place')") < pb.index("return (w==='pin'?routeBox(2,body):body)+") and pb.index("data-act=\"sqWind\"") < pb.index("return (w==='pin'?routeBox(2,body):body)+"))
    g('layout: "or" only between the Start Pin\'s two routes, where a committee boat is in use',
      "pinAtBox(!!oth)+(oth?routeOr()+placeBox('pin',oth,!e.m):'')" in ss and code.count('routeOr()+') == 1)
    # .44 (Pat, 22 October 2026): the finish set as the RO works on the day
    bx = fn_body(code, 'function finBoxes(')
    fbx = fn_body(code, 'function finBox(')
    g('finish (item 2): the three ways in order, with Pat\'s titles, each collapsed to its title until tapped, one open at a time',
      bx.index("finBox(1,'1. Committee boat remains, place new Finish Pin',b1)") < bx.index("finBox(2,'2. Choose Finish mark and position Committee boat',b2)")
      < bx.index("finBox(3,'3. Move Committee boat and Finish Pin',b3)") and "return h+(open&&!z.mid?finBoxes(ce):'');}" in fr
      and 'data-act="finBoxOpen" data-b="\'+n+\'" aria-expanded="\'+o+\'"' in fbx and "+(o?body:'')+'</div>';}" in fbx
      and "if(act==='finBoxOpen'){const x=k+'|'+b.dataset.b, was=!!finOpen[x];finBoxesShut(k);if(!was)finOpen[x]=true;render();return;}" in code
      and "if(set&&!open)finBoxesShut(k);" in fr and "if(row==='fin')finBoxesShut(k);" in code and 'routeHead' not in fbx)
    g('finish: box 2\'s midpoint is an emergency option below its main action; box 3 (item 3) is a new recorded fix, then the pin from it, only',
      bx.index('data-act="finPinBoat" data-b="2"') < bx.index('Emergency only, no committee boat: ') and 'data-act="finMidAt"' in bx
      and 'data-act="finCbPin"' in bx and 'data-b="3">Place boat' not in bx and 'that mark is the Finish Pin' not in bx and 'b3at' not in code
      and 'finPinBoat3' not in code and "isCB(m.name)&&!helpOf(m)&&!goneOf(m)" in bx and "m.race===S.race" in bx)
    g('finish (items 4, 5): boxes 2 and 3 have "Square to the last leg" and their end switch, box 2 the committee boat\'s, box 3 the Finish Pin\'s',
      "'°M from it · '+finSqRow(2,d,true)+'</div>'+s2.note+" in bx and "' · '+finSqRow(3,d,true)+'</div>'+s3.note+" in bx
      and "inp('b2brg',s2.ph,'5em',1)" in bx and "inp('b3pbrg',s3.ph,'5em',1)" in bx
      and "2:{sq:'b2sq',end:'b2end',dist:'b2dist',brg:'b2brg',what:'committee boat'}" in code and "3:{sq:'b3sq',end:'b3end',dist:'b3pdist',brg:'b3pbrg',what:'pin'}" in code
      and "if(act==='sqLeg')d[f.sq]=d[f.sq]==='leg'?'':'leg';else d[f.end]=finSqEnd(n,d)==='port'?'starboard':'port';" in code
      and "return n===1?endPick('fcb').m:n===2?estRef(String(d.b2at||'')):refFix(String(d.b3cb||''),'fcb');" in fn_body(code, 'function finSqFrom('))
    g('finish (fault 6): square to the leg from the last mark to the line\'s midpoint, for the length typed or 200 m, in all three boxes',
      "const al=Math.acos(len/(2*g.m))*180/Math.PI, t=((g.brg+(end==='port'?al:-al))%360+360)%360;" in fn_body(code, 'function sqLegBrg(')
      and "if(!(g.m>len/2+1))return" in fn_body(code, 'function sqLegBrg(') and "len=+d[f.dist]>0?+d[f.dist]:200" in fn_body(code, 'function finSq(')
      and code.count('sqLegBrg(') == 2 and "if(n)finSqPaint(n);" in code and "['ref','b2at','b3cb'].includes(t.dataset.f)" in code)
    g('finish (fault 7): the emergency midpoint withdraws a placed Finish boat, kept as replaced until then',
      "if(z.cb){old=Object.assign({w:'fcb'},z.cb);delete z.cb;finSet(k,z);finGoneAdd(k,old);if(old.fcb)ls().fcb=old.fcb;else delete ls().fcb;}" in fa
      and "if(old){finFollowAll();commit();await withdrawReplaced(k,'fcb',old,endDid(old));}" in fa)
    g('finish (item 11): a finish line more than FIN_ALONG off square to the last leg (to its midpoint) is said in amber',
      'const FIN_ALONG=30;' in code and "⚠ Finish line runs nearly along the last leg ('+Math.round(off)+'° off square)" in fn_body(code, 'function finLineNote(')
      and "return 90-Math.min(x,180-x);" in fn_body(code, 'function finOffSquare('))
    pl = fn_body(code, 'function plot(')
    g('sketch (fault 8): labels keep off every line drawn, and by their own mark',
      pl.count('drawn.push(') == 3 and "drawn.filter(l=>cross(b,l)).length*6+(!ofLine&&notOwn(b,x,y)?8:0)" in pl and 'ring(95)' in pl
      and "const w=tw(txt,fs)+4," in pl and "mctx.measureText(t).width" in pl and pl.count("'var(--warn)',true)") == 2)
    g('start (item 9): Change boat… suggestions from a harbour mark chosen under "from" (it becomes the Start Pin)',
      "const hr=w==='cb'&&d.ref?harbourRef(d.ref):null, base=hr||(!d.ref?have:null);" in pb and "const sg=base?estSuggest(base,w,d):null" in pb
      and "(have||w==='cb'?'<div class=\"meta estBox\">Suggest: " in pb
      and "return r&&isFinite(r.lat)&&isCourseCard(r)&&isRealMark(r)?r:null;" in fn_body(code, 'function harbourRef('))
    g('finish: the Finish type list has no "At the last mark" except on a start saved with it; "Shared from another start"',
      "const own=[['start','Same as the start line'],['finishpin','Committee boat & Finish Pin']].concat(old?[['last','At the last mark (saved before .44)']]:[]);" in fn_body(code, 'function finTypeOpts(')
      and '<optgroup label="Shared from another start">' in code and 'Finish lines set on earlier starts' not in code
      and 'At the last mark</option>' not in page)
    ep2 = fn_body(code, 'function endPick(')
    g('finish: Auto never picks a Finish Pin for a start set up in .44; an earlier version\'s pick is kept, flagged "check it"',
      "if(w==='fpin'&&v&&v!=='auto')return {m:null,how:'none',reason:'No finish set'};" in ep2 and "if(w==='fpin'&&a.m)a.legacy=true;" in ep2
      and "if(!S.lineSel[k].fpin||S.lineSel[k].fpin==='auto')S.lineSel[k].fpin='none';" in code and "S.lineSel[k].fpin='none';   // .44: no Finish Pin, never Auto" not in code
      and "if(ls().fpin===i.e.ref)S.lineSel[k].fpin='none';" in fa
      and "⚠ Finish Pin chosen by Auto in an earlier version: '+esc(fixWords2(pin))+(pin.race<S.race?' (from Race '+pin.race+')':'')+' – check it</div>'" in fr)
    g('finish: a Finish Pin a RIB recorded for this race is offered ("Use it"), never chosen',
      "m.race===S.race&&isFinishPin(m.name)&&!helpOf(m)&&!goneOf(m)" in fr and "use('Finish Pin recorded for this race: '+fixText(rec,'fpin'),'fpin',rec)" in fr)
    g('finish: "No finish set" in amber in the row and on the leg table\'s last leg; Copy for Sail Scoring keeps INCOMPLETE, as .43 did',
      '<div class="meta cautTxt finNone">No finish set</div>' in fr and "(noFinSet&&i===L.legs.length-1?'<br><span class=\"viaTxt cautTxt\">no finish set</span>':'')" in code
      and 'No finish set: the course ends at the last mark.' not in code and "noF=!L.fPt&&!finIsLast(r,st);" in fn_body(code, 'function ccDoc('))
    g('Start Pin: the list holds this race\'s fixes (and one chosen); one carried from an earlier race says so',
      "(w!=='pin'||m.race===S.race||refFor(m)===v)" in fn_body(code, 'function endChoices(')
      and "'<div class=\"meta cautTxt\">carried from Race '+e.m.race+' ('+(isTypedPos(e.m)?'typed':'recorded')+' '+fixWhen(e.m)+')</div>'" in code
      and "if(!list.length&&!e.m&&!a.m)return" in fn_body(code, 'function endPicker('))
    g('a change in the Start line or Finish line row clears that row\'s old messages (the leftover Undo message)',
      "msgClear(w==='fcb'||w==='fpin'?'finish':'start');" in fn_body(code, 'function setEnd(') and "v=e.target.value;msgClear('finish');" in code
      and "const row=act==='open'?null:b.closest('#startRow,#finishRow');if(row)msgClear(row.id==='finishRow'?'finish':'start');" in code)


def t30_v45_guards():
    """.45 (Pat, 23 October 2026): A117, A118, A119. Guards, not proof: no JavaScript is run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    page = read(PAGE)
    code = build_test.strip_comments(page)
    g = lambda name, ok, detail='': report('30 .45: ' + name, ok, detail)
    bx, sq = fn_body(code, 'function finBoxes('), fn_body(code, 'function finSqRow(')
    g('PAGE_VERSION 2026-10-06.45 or later', re.search(r"const PAGE_VERSION='2026-10-06\.(4[5-9])[a-z]?';", code) is not None)
    g('A117: box 2\'s Suggest buttons on the "from it" line, then Set pin and place boat bigger and bold on its own line, its message under it',
      "'°M from it · '+finSqRow(2,d,true)+'</div>'+s2.note+" in bx
      and "'<div class=\"meta\"><button type=\"button\" class=\"estAct finBig\" data-act=\"finPinBoat\" data-b=\"2\">Set pin and place boat</button></div>'+msgSlot('finPinBoat')+" in bx
      and "(inline?'<span class=\"finSugIn\">':'<div class=\"meta estBox\">')" in sq and "(inline?'</span>':'</div>')" in sq
      and '.finBig{font-weight:700;font-size:1.05rem;padding:10px 20px;margin-top:4px}' in page
      and "finSqRow(1,d)+note" in fn_body(code, 'function finPinPlaceBox(') and "' · '+finSqRow(3,d,true)+'</div>'+s3.note+" in bx)
    g('A118: box 3\'s list gives a recorded fix\'s accuracy, a typed position none',
      "esc(fixWords2(m)+(m.acc>0?' ±'+Math.round(m.acc)+' m':''))" in bx)
    fade, cb = fn_body(code, 'function sentFade('), fn_body(code, 'function sentFadeCb(')
    g('A119: a green "…: sent." message clears after SENT_CLEAR_MS if it still says the same; nothing else clears this way',
      'const SENT_CLEAR_MS=10000;' in code and "if(!x||x.ok!==true||!/sent\\.$/.test(x.t))return;" in fade
      and "if(y&&y.ok===true&&y.t===t){delete actMsgs[key];paintMsgs();}" in fade
      and "sentFade(key);});" in fn_body(code, 'function fixSays(') and "sentFade(key);paintMsgs();}" in fn_body(code, 'function readSays('))
    g('A119: the line under Record committee boat clears the same way, only when all it says is what was sent',
      "if(!/\\bok\\b/.test(el.className)||!/sent\\.$/.test(t))return;" in cb
      and "if(el.textContent===t&&/\\bok\\b/.test(el.className)){el.textContent='';el.className='status';}" in cb
      and "if(!stop&&!moved&&said.length&&said.every(x=>/sent\\.$/.test(x)))sentFadeCb();" in fn_body(code, 'async function sendOutbox('))


def t31_v45b_guards():
    """.45b (Pat, 23 October 2026): A121, A122. Guards, not proof: no JavaScript is run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    page = read(PAGE)
    code = build_test.strip_comments(page)
    g = lambda name, ok, detail='': report('31 .45b: ' + name, ok, detail)
    bx, an = fn_body(code, 'function finBoxes('), fn_body(code, 'function analysis(')
    g('PAGE_VERSION 2026-10-06.45b or later', re.search(r"const PAGE_VERSION='2026-10-06\.(45b|4[6-9][a-z]?)';", code) is not None)
    g('A121: box 3\'s Suggest buttons on its line, then Use the boat and place the pin bigger and bold on its own line, its message under it',
      "inp('b3pwhen',startTime(),'4.5em')+' · '+finSqRow(3,d,true)+'</div>'+s3.note+" in bx
      and "'<div class=\"meta\"><button type=\"button\" class=\"estAct finBig\" data-act=\"finCbPin\">Use the boat and place the pin</button></div>'+msgSlot('finCbPin')+" in bx
      and bx.count('finBig') == 2)
    g('A122: the first mark after the start (firstMarkOf), not a mark found by its name',
      "const w=firstMarkOf().m;" in an and 'windward' not in an.lower())
    g('A122: with no start line, the note and no figure',
      "if(!sl){if(!midStart()){const line='First mark: set the start line to see how square it is to the wind';" in an)
    g('A122: with a start line, measured from its midpoint, the calculation as before, the mark named',
      "const r=geo(sl.mid,w);" in an and "let d=((r.brg-twdT+540)%360)-180;" in an
      and "const across=Math.abs(r.m*Math.sin(rad(d)));" in an and "const dir=(twdT+(d>0?-90:90)+360)%360;" in an
      and "'First mark ('+w.name+') '+Math.abs(Math.round(d))+'° '+(d>0?'right':'left')+' of square · move '+Math.round(across)+' m towards '+pad(magOf(dir,vA),3)+'°M to square it'" in an
      and "'First mark ('+w.name+') square with the wind, '+r.nm.toFixed(2)+' nm'" in an and 'cs[0]' not in an)


def png_size(p):
    with open(p, 'rb') as f:
        b = f.read(24)
    return (int.from_bytes(b[16:20], 'big'), int.from_bytes(b[20:24], 'big')) if b[:8] == b'\x89PNG\r\n\x1a\n' else None


def t32_v46(tmp):
    """.46 (Pat, 23 October 2026): A123 and A80. The page is guarded, not run; the test build is run."""
    import json
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    page = read(PAGE)
    code = build_test.strip_comments(page)
    g = lambda name, ok, detail='': report('32 .46: ' + name, ok, detail)
    g('PAGE_VERSION 2026-10-06.46', "const PAGE_VERSION='2026-10-06.46';" in code)
    # A123
    g('A123: "Line not set" beside the Start line heading, only when startWarn says so',
      "const notSet=swn&&swn.kind==='notset'?' <span class=\"lineNotSet\" role=\"status\">Line not set</span>':'';" in code
      and "<div><b>Start line</b>'+notSet+noBoat+sw+ends+sMiss+" in code)
    g('A123: it is red: the warning colour as its background',
      '.lineNotSet{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:6px;background:var(--warn);color:var(--paper);font-weight:700;font-size:.9rem}' in page)
    g('A123: section 4\'s first-mark note is amber (note caut)',
      "bits.push('<p class=\"note caut\">'+line+'</p>')" in fn_body(code, 'function analysis(') and '.note.caut{border-color:var(--caution);color:var(--caution)}' in page)
    # A124
    pl = code[code.index("if(act==='place'){"):]
    pl = pl[:pl.index("msgFix('place',k,id);")]
    g('A124: the committee boat placed from a harbour mark saves the mark chosen as hm, and no fromWhen; every other placement as before',
      "const harbour=w==='cb'&&ref!==have&&isCourseCard(ref)&&isRealMark(ref), hm=harbour?ref.card:'';" in pl
      and pl.index("hm=harbour?ref.card:''") < pl.index("ref=have;else prev=have;")
      and "if(hm)rec.hm=hm; else {const fw=fromWhenNew(ref,rec.from);if(fw)rec.fromWhen=fw;}" in pl
      and "from:rp?pinName('Start Pin',rp.at):ref.card&&!ref.atFix?ref.name:fixWords2(ref)" in pl)
    g('A124: hm is kept when a committee boat record is read (estRec), never for a Start Pin',
      "le.w==='cb'&&le.hm?{hm:String(le.hm)}:{}" in fn_body(code, 'function estRec('))
    g('A124: with hm, "<nm to one decimal> nm at <°M> from <mark>", below 0.1 nm "<m> m …"; without, "<m> m at <°M> from <from>"',
      "function estAt(e){return e.hm?(e.m*10<1852?e.m+' m':(e.m/1852).toFixed(1)+' nm')+' at '+pad(e.brgM,3)+'°M from '+e.hm:e.m+' m at '+pad(e.brgM,3)+'°M from '+e.from;}" in code)
    # the switch, worked here as the page works it: 185 m and less in metres, 186 m and more in nm, never "0.0 nm"
    dist = lambda m: f'{m} m' if m * 10 < 1852 else f'{m / 1852:.1f} nm'
    g('A124: the switch: 80 m, 185 m in metres; 186 m is 0.1 nm, 277 m 0.1 nm, 278 m 0.2 nm; 1 to 5000 m never "0.0 nm"',
      [dist(m) for m in (80, 185, 186, 277, 278, 1000)] == ['80 m', '185 m', '0.1 nm', '0.1 nm', '0.2 nm', '0.5 nm']
      and not any(dist(m) == '0.0 nm' for m in range(1, 5001)), str([dist(m) for m in (80, 185, 186, 277, 278, 1000)]))
    hl = fn_body(code, 'function helpLong(')
    g('A124: helpLong (Start line section, fixes list) and estWords (section 4, the message) use it; no bracketed time with hm',
      "const placed=(lab,e)=>{const fw=e.hm?'':fromWhenOf(e,m);return lab+' – estimate: '+estAt(e)+(fw?' ('+fw+')':'')+'; on the water '+fixWhen(m)+rp;};" in hl
      and "+' placed '+estAt(e);}" in code)
    g('A124: Copy for Sail Scoring (helpX) and the finish boat\'s and Finish Pin\'s words unchanged',
      'estAt' not in fn_body(code, 'function helpX(') and 'hm' not in fn_body(code, 'function helpX(')
      and "function finWords(e){return 'Finish boat placed '+e.m+' m at '+pad(e.brgM,3)+'°M from '+e.from;}" in code
      and "function finPinWords(e){return 'Finish Pin placed '+e.m+' m at '+pad(e.brgM,3)+'°M from '+e.from;}" in code)
    # A80, the page and the live manifest
    g('A80: the page links the manifest (relative) and gives the theme colour, once each',
      page.count('<link rel="manifest" href="manifest.webmanifest">') == 1 and page.count('<meta name="theme-color" content="#2E8E47">') == 1)
    mp = os.path.join(ROOT, 'pages', 'course', 'manifest.webmanifest')
    try:
        man = json.loads(read(mp))
    except Exception as e:
        man = {}
        g('A80: the manifest is valid JSON', False, str(e))
    want = {'name': 'Course plot – race officer', 'short_name': 'Course', 'id': '/course/', 'start_url': '/course/', 'scope': '/course/',
            'display': 'standalone', 'background_color': '#F5F8FA', 'theme_color': '#2E8E47'}
    g('A80: the live manifest\'s fields', all(man.get(k) == v for k, v in want.items()), json.dumps({k: man.get(k) for k in want}, ensure_ascii=False))
    g('A80: its icons: icon-192.png (192, any), icon-512.png (512, any), icon-maskable-512.png (512, maskable)',
      [(i.get('src'), i.get('sizes'), i.get('purpose'), i.get('type')) for i in man.get('icons', [])] ==
      [('icon-192.png', '192x192', 'any', 'image/png'), ('icon-512.png', '512x512', 'any', 'image/png'), ('icon-maskable-512.png', '512x512', 'maskable', 'image/png')])
    A = os.path.join(ROOT, 'pages', 'course', 'assets')
    sizes = {f: png_size(os.path.join(A, f)) for f in ('icon-course-192.png', 'icon-course-512.png', 'icon-course-maskable-512.png',
                                                       'icon-course-test-192.png', 'icon-course-test-512.png', 'icon-course-test-maskable-512.png')}
    g('A80: the icon sources are in pages/course/assets at their sizes', all(v == ((192, 192) if '192' in f else (512, 512)) for f, v in sizes.items()), str(sizes))
    sw = read(SW)
    g('A80: the worker is unchanged in what it handles: the page and key.js, never the manifest or icons',
      'manifest' not in sw and 'icon' not in sw and "if(!key)return;" in sw)
    # A80, the test build
    out = os.path.join(tmp, 'out32')
    r = run(PAGE, out)
    g('A80: the test build exits 0', r.returncode == 0, r.stdout + r.stderr)
    if r.returncode:
        return
    ct = os.path.join(out, 'course-test')
    tm = json.loads(read(os.path.join(ct, 'manifest.webmanifest')))
    g('A80: the test manifest: "TEST – Course plot", "TEST Course", and /course-test/ as id, start_url and scope',
      tm.get('name') == 'TEST – Course plot' and tm.get('short_name') == 'TEST Course' and all(tm.get(k) == '/course-test/' for k in ('id', 'start_url', 'scope')))
    tt = read(os.path.join(ct, 'manifest.webmanifest'))
    g('A80: the test manifest names /course-test/ and nothing else: no /course/ anywhere', re.search(r'/course(?!-test/)', tt) is None)
    g('A80: the test manifest is the live one in every other field',
      {k: v for k, v in tm.items() if k not in ('name', 'short_name', 'id', 'start_url', 'scope')} == {k: v for k, v in man.items() if k not in ('name', 'short_name', 'id', 'start_url', 'scope')})
    same = all(read(os.path.join(ct, d), 'rb') == read(os.path.join(A, s_), 'rb') for s_, d in build_test.TEST_ICONS)
    g('A80: the TEST icons copied in byte for byte as icon-192.png, icon-512.png, icon-maskable-512.png', same)
    b = read(os.path.join(out, 'BUILD.txt'))
    g('A80: BUILD.txt names the manifest and each icon with its SHA-256',
      'course-test/manifest.webmanifest sha256 ' in b and all(f'course-test/{d} sha256 ' in b for _, d in build_test.TEST_ICONS))
    tp = read(os.path.join(ct, 'index.html'))
    g('A80: the test page links its own manifest (relative), the live theme colour kept', tp.count('<link rel="manifest" href="manifest.webmanifest">') == 1)
    # refusals, each writing nothing
    bad = os.path.join(tmp, 'bad32.webmanifest')
    with open(bad, 'w', encoding='utf-8') as f:
        f.write(read(mp).replace('"scope": "/course/"', '"scope": "/"'))
    r = subprocess.run([sys.executable, SCRIPT, '--page', PAGE, '--manifest', bad, '--out', os.path.join(tmp, 'out32b')], capture_output=True, text=True, encoding='utf-8')
    g('A80: refused: a live manifest whose scope is not /course/', r.returncode != 0 and 'scope' in r.stdout and not os.path.exists(os.path.join(tmp, 'out32b', 'course-test')), r.stdout[:200])
    bp = os.path.join(tmp, 'bad32.html')
    with open(bp, 'w', encoding='utf-8', newline='') as f:
        f.write(page.replace('<link rel="manifest" href="manifest.webmanifest">', '<link rel="manifest" href="/course/manifest.webmanifest">'))
    r = run(bp, os.path.join(tmp, 'out32c'))
    g('A80: refused: a page whose manifest link is not the relative manifest.webmanifest', r.returncode != 0 and 'manifest link' in r.stdout, r.stdout[:200])
    ea = os.path.join(tmp, 'assets32')
    os.makedirs(ea, exist_ok=True)
    r = subprocess.run([sys.executable, SCRIPT, '--page', PAGE, '--assets', ea, '--out', os.path.join(tmp, 'out32d')], capture_output=True, text=True, encoding='utf-8')
    g('A80: refused: a test icon missing', r.returncode != 0 and 'icon' in r.stdout and not os.path.exists(os.path.join(tmp, 'out32d', 'course-test')), r.stdout[:200])


def t33_lines_guards():
    """.46 (Pat, 26 October 2026): A123, a mark as a line end; A125, a Grassy finish always Grassy; "Grassy" shown.
    Guards, not proof: the harness runs the page."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import build_test
    page = read(PAGE)
    code = build_test.strip_comments(page)
    g = lambda name, ok, detail='': report('33 .46 lines: ' + name, ok, detail)
    fs, sw = fn_body(code, 'function finishState('), fn_body(code, 'function startWarn(')
    g('rule 1: the start line is a recorded line, else the committee boat to the card\'s Dosco or No.8 mark on Automatic while no Start Pin is in use',
      "function startLine(r,st,sel){return mkLine(endPick('cb',r,st,undefined,sel).m,endPick('pin',r,st,undefined,sel).m)||markStartLine(r,st,sel);}" in code
      and "return c&&isMarkEnd(c.s)&&cardEndMode('s',r,st)==='auto'?c.s:'';" in fn_body(code, 'function markStartOf(')
      and "if(!cb||endPick('pin',r,st,undefined,sel).m)return null;" in fn_body(code, 'function markStartLine('))
    g('rule 1: the mark is a page-made pin end at its workbook position, named plainly, never a fix',
      "return {id:'_m'+nm,name:nm,lat:m.lat,lon:m.lon,virtual:true,card:nm,race:r,time:'',markEnd:true};" in fn_body(code, 'function markPt(')
      and "m.type!=='Start/finish modelling point'" in fn_body(code, 'function isMarkEnd('))
    g('rule 1, finish: the finish boat to the mark; a Finish Pin recorded after the start replaces it',
      "if(markFinOf(r,st))return markFinLine(r,st,sel)?{kind:'markline'}:{kind:'cardpt',noBoat:true};" in fs
      and "isFinishPin(m.name)&&!helpOf(m)&&!goneOf(m)&&fixMoment(m)!==null&&fixMoment(m)>t" in fn_body(code, 'function markFinPin('))
    ae = fn_body(code, 'function autoEnd(')
    g('d3: marks differ: the finish\'s own boat only (a Finish boat, or a committee boat after the start), the latest; never an estimate',
      "if(c&&markFinOf(r,st)&&c.f!==c.s){" in ae and "(isFinishBoat(m.name)||isCB(m.name)&&t!==null&&fixMoment(m)>t)" in ae and "!helpOf(m)&&!goneOf(m)" in ae)
    g('rule 2: no boat: "No committee boat: place the committee boat, or use … as the line\'s midpoint" with its button; not on a Grassy start, a midpoint, Card mark or Laid line',
      "if(gsOf()||cardGrassyStart()||midLine())return null;" in sw and "if(m!=='auto'||startLine())return null;" in sw
      and "⚠ No committee boat: place the committee boat, or use '+esc(swn.mark)+' as the line\\'s midpoint. " in code
      and "⚠ No finish boat: place the finish boat, or use '+esc(c.f)+' as the line\\'s midpoint. " in code
      and "else if(act==='useCardF'&&c){c.lf='card';stamp(k);commit();}" in code)
    g('rule 2: while it shows, the leg is still measured from or to the mark, and the STAND-IN lines are kept for it only',
      "if(L.sPt&&!L.sl&&L.ccfg&&markStartOf(r,st))cardSti.push(" in code and "L.fsx.kind==='cardpt'&&L.fsx.noBoat)cardSti.push(" in code)
    g('rule 3, A125: a Grassy finish is always Grassy; on Laid line never the start line by fallback; "Same as the start line" kept',
      "if(c.f==='Grassy Mid')return {kind:'cardpt'};" in fs and "if(c.f==='Grassy Mid')return {kind:'missing',warn:'Finish line missing'};" in fs
      and fs.index("if(c.lfc==='start')") < fs.index("if(c.f==='Grassy Mid')return {kind:'missing'"))
    g('d5: a Grassy card start on Automatic or Card mark is Grassy; Laid line uses the recorded line',
      "return !!c&&c.s==='Grassy Mid'&&cardEndMode('s',r,st)!=='laid';" in fn_body(code, 'function cardGrassyStart('))
    g('rule 4: Laid line keeps its own warning only', "if(m!=='auto'||startLine())return null;" in sw)
    g('rule 6: a pin set at a mark is named by the mark alone; with no boat, rule 2\'s warning',
      "isMarkEnd(at)?at+rp:" in fn_body(code, 'function helpLong(') and "if(sp&&isMarkEnd(sp.at)&&!endPick('cb').m)return {kind:'noboat',mark:sp.at,act:'mid'};" in sw
      and "data-act=\"finMid\">Use '+esc(mk)+' as the midpoint</button>" in code)
    g('rule 6 (section 4): the orange note is not shown for a midpoint start', "if(!sl){if(!midStart()){" in fn_body(code, 'function analysis(')
      and "return !!(gsOf()||cardGrassyStart()||midLine()||c&&isMarkEnd(c.s)&&cardEndMode('s')==='card');" in fn_body(code, 'function midStart('))
    g('7: "Finish at Grassy.", "Finish between the committee boat and Dosco.", "from the start line, not depth-checked"',
      "if(k==='grassy')return 'Finish at Grassy.';" in code and "'Finish between the committee boat and '+(ml.mk||'the Finish Pin')+'.'" in code
      and "dir+(ln&&ln.mk?' the '+(dir==='from'?'start':'finish')+' line':' the recorded line')+', not depth-checked'" in code)
    g('7, the rename: "Grassy" is shown; the stored names stay "Grassy Mid"',
      "function shownName(nm){return nm==='Grassy Mid'?'Grassy':nm;}" in code and "const CARD_STARTS=['Grassy Mid','No.8','Dosco'];" in code
      and "S.startPt[k]='Grassy Mid';" in code and "'+esc(s)+'\">'+esc(shownName(s))+'</option>'" in code
      and "name:label+' ('+shownName(nm)+')'" in code and 'data-act="grassy">Start from Grassy</button>' in code
      and 'Grassy Mid' not in re.sub(r"'Grassy Mid'", '', code.replace(code[code.index('const CARD='):code.index('\n', code.index('const CARD='))], '')))
    g('the Finish boat placed from the mark: a typed position, an estimate, Undo as the finish boat\'s',
      "const rec={ref:add('Finish boat',p,t),from:nm,m:Math.round(dist),brgM:Math.round(brgM)%360};" in code and 'data-act="finMarkPlace"' in code
      and "(finUsesPin(S.race,S.start)?finRowHtml():markFinOf()?markFinRow():'')" in code)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        t0_build(tmp)
        t1_live_page()
        t2_refusals(tmp)
        t3_allowed(tmp)
        t4_save_guards()
        t5_copy_guards()
        t6_a38_guards()
        t7_a40_guards()
        t8_fixes31_guards()
        t9_fixes32_guards()
        t10_changes33_guards()
        t11_changes34_guards()
        t12_changes35_guards()
        t13_changes36_guards()
        t14_one_end_line_guards()
        t15_start_line_setup_guards()
        t16_day_guards()
        t17_reopen_names_guards()
        t18_gone_start_guards()
        t19_remove_start_guards()
        t20_time_and_remove_guards()
        t21_t14_guards()
        t22_day_series_guards()
        t23_worker_guards()
        t24_version_gate_guards()
        t25_a78_guards()
        t26_fixes43_guards()
        t27_fixes44_guards()
        t28_local_build(tmp)
        t29_pin_routes_guards()
        t30_v45_guards()
        t31_v45b_guards()
        t32_v46(tmp)
        t33_lines_guards()
    print(f'\n{len(failed)} failed' if failed else '\nall passed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())