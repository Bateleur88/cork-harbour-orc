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
MARKS = os.path.join(ROOT, 'pages', 'marks', 'marks.php')
# every browser storage key name the page writes after STORE ('pv-' is followed by a PAGE_VERSION). The Review name and
# RO key (ro-name, ro-key) went with the review decisions in 2026-10-06.20; the page no longer reads or writes them
STORE_NAMES = {'pv-', 'race-key', 'course-plot-v1', 'course-series'}
failed = []


def report(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + (': ' + detail if detail and not ok else ''))
    if not ok:
        failed.append(name)


def run(page, out):
    return subprocess.run([sys.executable, SCRIPT, '--page', page, '--marks', MARKS, '--out', out],
                          capture_output=True, text=True, encoding='utf-8')


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
    g('Not sent drawn on every render', 'renderNotSent();\n}' in fn_body(code, 'function render('))
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
      and 's0.outbox.forEach(q=>readSays(q,outWait(q,stop.k,stop.e),' in so)
    g('the typing message follows its fix: sending again, removed',
      "readSays(x.f,outName(x.f)+': sending again" in ns and "readSays(x.f,outName(x.f)+': removed from this device.'" in ns)
    g('readSays changes only a message still about that fix', "el.textContent.indexOf(outName(f)+':')!==0)return;" in code)
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
        'service worker': inject("try{navigator.serviceWorker.register('sw.js');}catch(e){}"),
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
            body = body.replace("+(lineEstNow(r,st)?'  \"x-estimate\": '+JSON.stringify(lineEstNow(r,st).x)+',\\n':'')", '')
            # .37: a hand-built Grassy start gets the STAND-IN note beside the button, as an imported one does (A58 part 2)
            body = body.replace('if(L.sPt&&!L.sl&&L.ccfg)', 'if(L.sPt&&!L.sl)')
            body = chr(10).join(x for x in body.split(chr(10)) if 'gsOf(r,st))cardSti.push(' not in x)
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
      "const head=[series.name,S.pulledDay?longDate(S.pulledDay):''].filter(Boolean).join(' – ')||'Course';" in bl
      and 'S.date' not in bl)
    g('1 the heading follows the Race day box at once', "$('day').addEventListener('change',()=>{render();" in code)
    g('2 routing waypoints are not carried either', 'm.race<S.race&&!isCourseCard(m)&&!isRwCard(m)' in fn_body(code, 'function bank('))
    g('4 one line per refused name', "refused.map(cardRefusal));" in code and "$('readStatus').innerHTML=said.map(esc).join('<br>');" in code)
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
    g('5 withdraw is refused while a course uses it, naming each race and start', 'const u=usesOf(m);' in ta and "' cannot be withdrawn: it is used in '" in ta)
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
      and "reason:'Auto, as saved with the course',live:" in fn_body(code, 'function autoUse(') and "' – use it?'" in code)
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
    g('A54: the start line under the Start line lists', "+lineInfo()+'</div>'+" in code and 'No start line yet: no start time is set, so auto finds no committee boat or Start Pin.' in code)
    g('A55: the scale bar in metres below 0.1 nm', "barNm<0.1?Math.round(barNm*1852)+' m'" in code)
    g('A56: a wind direction used only from 0 to 360, saved when the box is left', 'function twdOk(v)' in code and page.count('id="twdWarn"') == 1
      and "twdBad='';S.twd=v;buildLegs();};" in code and "twdBad='';S.twd=v;saveWind();};" in code)
    g('A49: no date label in the WhatsApp text', r".replace(/ on \S+ \d{1,2} \S+$/,'')" in code)
    g('A10: opening an old race never writes a choice: device-only laid choices from before .35 are not saved by a load, and a load-led save adds no auto choice',
      'S.laidLegacy[key])return;' in fn_body(code, 'function laidRec(') and "if(S.laidShape!==35)" in code
      and code.count('stamp(k,true);if(ln&&!ln[k])ln[k]=LOAD_WHY[') == 2 and 'if(!noFreeze)freezeFor(k);' in code)
    g('A54: section 3\'s start line note follows the wind box as section 4 does', "sMiss+'<div id=\"lineInfo\">'+lineInfo()+'</div>'+" in code
      and "if($('lineInfo'))$('lineInfo').innerHTML=lineInfo();" in fn_body(code, 'function buildLegs('))
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
    g('the options only with a start time and exactly one end, not on a Card mark start', "if(!startTime()||lineOff()||midLine())return '';" in eo
      and "function lineOff(r,st){return cardEndMode('s',r,st)==='card'||!!gsOf(r,st);}" in code
      and "if(!!cb===!!pin)return '';" in eo)
    g('the options write nothing until the RO acts (no save, stamp or commit in the offer)', not re.search(r'(commit|save|stamp|scheduleSave|saveCourses|sendOutbox)\(', eo))
    g('option 1 saves a typed position named for the missing end, and the line end of this start',"nm=w==='cb'?'Committee boat':'Start Pin'" in code
      and "S.lineAuto[k]=Object.assign({},S.lineAuto[k]||{},{[w]:'s:'+id});" in code and 'geoDest(ref,((brgM-varW())%360+360)%360,dist)' in code)
    g('option 2: the recorded end as midpoint, for the start and a start-line finish', "(midLine(r,st)||startLine(r,st,sel))" in code
      and "return midLine(r,st)||startLine(r,st,sel);}" in code)
    g('both saved with the course and read back', "{lineMid:Object.assign({},S.lineMid[k])}" in code and "{lineEst:estSaved(k)}" in code
      and 'S.lineMid[k]={w:lm.w,ref:lm.ref}' in code)
    g('a real end recorded later is offered, never taken', "' is now available – use it? '" in code)
    g('Copy for Sail Scoring says x-estimate; the WhatsApp text does not', "'  \"x-estimate\": '+JSON.stringify(lineEstNow(r,st).x)" in code
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
    g('both ends missing: offered only with a start time, no Card mark or Grassy start, no midpoint and no end found',
      "if(!startTime()||lineOff()||midLine())return '';" in bo and "if(endPick('cb').m||endPick('pin').m)return '';" in bo)
    g('suggestions are greyed placeholders only: the boxes keep what the RO typed', 'placeholder="200" value="\'+esc(d.dist)+\'"' in eo
      and 'placeholder="\'+ph+\'" value="\'+esc(d.brg)+\'"' in eo and 'd.dist=' not in code and 'd.brg=' not in code)
    g('starboard: committee boat 90 deg right of the pin looking upwind or to the first mark; pin = cb - 90; port swaps',
      "const turn=(w==='cb'?90:-90)*(d.port==='1'?-1:1)" in es and 'n(+S.twd)' in es and 'n(magOf(geo(have,f.m).brg,varW()))' in es)
    g('no wind or no first mark: a warning, no suggestion', "'No wind direction: type it in the wind box first" in es and "'No first mark yet: add the course first" in es)
    g('the first mark skips routing waypoints', 'if(m&&isRwCard(m)){rw=true;continue;}' in fn_body(code, 'function firstMarkOf('))
    g('the "from" list and the Start Pin list offer the full Fixed marks list', eo.count('fixedOpts(d.ref)') == 1 and bo.count('fixedOpts(d.at)') == 1
      and 'Object.keys(CARD.marks).forEach' in fn_body(code, 'function fixedOpts('))
    g('a Start Pin set at a mark: a typed position and this start\'s pin, the RO\'s choice, not an estimate (answer 2 corrected)', "name:'Start Pin',lat:src.lat,lon:src.lon,acc:0,time:t" in code
      and "S.linePinAt[k]={ref:'s:'+id,at};" in code and "S.lineAuto[k]=Object.assign({},S.lineAuto[k]||{},{pin:'s:'+id});" in code
      and "function setOf(m){return m?Object.values(S.linePinAt||{}).find(refHit(m))||null:null;}" in code
      and "function estOf(m){return m?estAll().find(refHit(m))||null:null;}" in code)
    g('its time defaults to the start time', "tt=String(d.ptime||'').trim()||startTime()" in code)
    g('one Undo withdraws every estimate of the start, committee boat first, after one confirmation', "sort((a,b)=>(a.w==='cb'?0:1)-(b.w==='cb'?0:1))" in code
      and code.count("reason:'estimate undone by the RO'") == 1)
    g('a recorded end while auto uses an estimate: offered, never taken', "re=e.how==='auto'?realEnd(w,e.m):null" in code
      and 'data-f="\'+esc(refFor(re))+\'">Use it</button>' in code)
    g('Grassy start: hand-built only, saved as startPt, read back, line not used, finish at Grassy Mid on Start line',
      "if(act==='grassy'){if(cardCfgNow())return;S.startPt[k]='Grassy Mid';" in code and "{startPt:S.startPt[k]}" in code
      and "if(rec.startPt==='Grassy Mid')S.startPt[k]='Grassy Mid'; else delete S.startPt[k];" in code
      and "return lineOff(r,st)?null:(midLine(r,st)||startLine(r,st,sel));" in code
      and "gsOf(r,st)&&finishMode(r,st)==='start'?cardEnd('Grassy Mid','Finish'):null" in code)
    cc = fn_body(code, 'function ccDoc(')
    g('Grassy start: the STAND-IN note beside Copy for Sail Scoring, never in the name', "measured from Grassy Mid (Grassy start chosen)');" in cc
      and 'gsOf' not in cc.split('const pre=')[1].split('const name=')[0])
    g('the new fields are written only when used, so other records save exactly as before',
      "...(S.startPt&&S.startPt[k]?{startPt:S.startPt[k]}:{})," in code and "...(S.linePinAt&&S.linePinAt[k]?{linePinAt:" in code)
    bl = fn_body(code, 'function buildLegs(')
    g('the midpoint is drawn as a 200 m line square to the first leg, drawing only', 'A=geoDest(sl.end,(b+90)%360,100), B=geoDest(sl.end,(b+270)%360,100)' in bl
      and "drawn:true},kind:'start',est:true}" in bl and '!g.a.drawn' in fn_body(code, 'function courseMarks('))
    g('the chart labels an estimated line', "ln.est?'Start line: estimate'" in code and "permanent:true,direction:'bottom',offset:[0,12],className:'estTip'" in code)
    g('decision 2a: an estimated end carries forward only within its race; a later race is offered it, never given it by auto',
      "&&!(m.race<r&&helpOf(m))).sort(" in fn_body(code, 'function candidates(') and "eo=!e.m&&e.how==='unset'?estEarlier(w):null" in code
      and "(estOf(eo)?'A start line estimate from Race '+eo.race:'A Start Pin set in Race '+eo.race)+' is available – use it? '" in code)
    g('T7: a helper end named by what the RO did, time last, in lists, notes and Check recorded marks; short on the drawings',
      "'Start Pin: '+p.at+' ('+fixWhen(m)+')'" in code and "' – estimate: '+e.m+' m at '+pad(e.brgM,3)+'°M from '+f+(f.endsWith(' '+w)?'':' ('+w+')')" in code
      and "'Start Pin ('+p.at+')'" in code and "' (est.)'" in code and "function fixText(m,w){if(helpOf(m))return helpLong(m);" in code
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
    g('while held the loaded day is hidden and every other control does nothing', 'body.dayHeld .wrap>.raceOnly,body.dayHeld #recCB,body.dayHeld #recCB~*,' in page
      and "['click','change','input','keydown'].forEach(ev=>document.addEventListener(ev,e=>{if(!dayHeld())return;" in code
      and "#day,#pull,#heldPull,#dayAnyway,#clear,#series,.modebar,#dayHeldNote" in code)
    g('the 30-second refresh never loads a day by itself while held', "!dayHeld()&&(reopenWait||pullOk&&$('day').value===todayISO()))pull(true);" in code)
    g('reopening the page when a day was loaded before says so when that was another day (changed by group 17)',
      "if(S.pulledDay){const was=S.pulledDay, now=$('day').value;" in code and "'The page was reopened: Race day is back to today, '" in code)
    g('T1: no comma before "time on the water"', "</select>, time on the water" not in code and code.count("</select> time on the water '") == 2)
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
      "f.endsWith(' '+w)?'':' ('+w+')'" in hl and "'°M from '+e.from+' ('+fixWhen(m)+')'" not in code)
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
      and "estsOf(k).concat(S.linePinAt[k]?[S.linePinAt[k]]:[],S.lineMid[k]?[S.lineMid[k]]:[]).some(e=>refIs(e.ref,m))" in lu
      and "['cb','pin','fcb','fpin'].some(w=>endPick(w,r,st).m===m)" in lu and "if(k===skip)return;" in lu)
    g('lineUsers looks at every start of the day',
      "['courses','startTimes','lineSel','lineAuto','lineEst','linePinAt','lineMid'].forEach(f=>" in fn_body(code, 'function startKeys('))
    g('a: Undo is refused, naming the starts, while any other start uses the estimate',
      "const others=[...new Set(its.reduce((a,i)=>a.concat(lineUsers(i.m,k)),[]))];" in code
      and "'Not undone: this estimate is also used by '+others.join(', ')+'. Undo would change '" in code
      and code.index("const others=[...new Set(") < code.index("await postFix({action:'withdraw',date:S.pulledDay,id:i.m.sid,reason:'estimate undone by the RO'}"))
    g('b: placing an end or setting the pin clears that end\'s "None" on the start',
      "if((S.lineSel[k]||{})[w]==='none')delete S.lineSel[k][w];" in code and "if((S.lineSel[k]||{}).pin==='none')delete S.lineSel[k].pin;" in code)
    g('c: a placed end\'s time on the water defaults to the start\'s own time, as the set pin does',
      "const tt=String(estDraft.time||'').trim()||startTime();" in code and "String(ref.time||have.time||'')" not in code
      and """data-f="time" type="text" inputmode="numeric" placeholder="'+esc(startTime())+'\"""" in code)
    g('d: one estimate record per end of a start; placing one end keeps the other',
      "S.lineEst[k]=Object.assign({},S.lineEst[k]||{},{[w]:rec});" in code
      and "function estsOf(k){const o=(S.lineEst||{})[k];return o?[o.cb,o.pin].filter(Boolean):[];}" in code
      and "function estOf(m){return m?estAll().find(refHit(m))||null:null;}" in code)
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
      "return [...new Set(out.concat(lineUsers(m)))];" in fn_body(code, 'function usesOf(')
      and "const u=usesOf(m);" in fn_body(code, 'async function typedAct('))


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
    g('1: the start time itself is still saved on every change', "$('startTime').onchange=e=>{S.startTimes[ckey(S.race,S.start)]=e.target.value;stamp();commit();};" in code)
    ra = fn_body(code, 'async function removeStartAsked(')
    g('2: the Remove Start button goes through removeStartAsked', "if(rm)rm.onclick=()=>removeStartAsked(S.start);" in code
      and "rm.onclick=()=>{removeStart(" not in code)
    g('2: the removed start\'s own placed ends and set pin are found', "estsOf(k).map(e=>({e,w:e.w})).concat(S.linePinAt[k]?[{e:S.linePinAt[k],w:'pin'}]:[])" in ra)
    g('2: refused, naming the starts, while any other start uses one of them',
      "const others=[...new Set(its.reduce((a,x)=>a.concat(lineUsers(x.m,k)),[]))];" in ra
      and "' not removed: its '" in ra and ra.index('const others=') < ra.index("action:'withdraw'"))
    g('2: each is withdrawn (kept, marked withdrawn) before the start is removed; a failed withdrawal removes nothing',
      "await postFix({action:'withdraw',date:S.pulledDay,id:x.m.sid,reason:'start removed by the RO'},OUTBOX_TIMEOUT_MS);" in ra
      and "catch(err){commit();say('Start '+(i+1)+' not removed: '" in ra
      and ra.index("action:'withdraw'") < ra.index('removeStart(i);'))


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
    print(f'\n{len(failed)} failed' if failed else '\nall passed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
