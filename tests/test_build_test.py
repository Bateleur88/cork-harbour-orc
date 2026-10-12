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
    report('5 copy: the leg table line format unchanged', "g.parts.forEach(pt=>ss.push(pt.nm.toFixed(2)+' '+pad(magOf(pt.brg),3)));" in code)
    report('5 copy: the leg table copy code unchanged',
           "await navigator.clipboard.writeText(ssText);$('ssCopy').textContent='Copied';"
           "setTimeout(()=>$('ssCopy').textContent='Copy legs for SailScoring',1500);" in code and
           "ssText=lines.join('\\n');" in fn_body(code, 'function setSS('))
    cd = fn_body(code, 'function ccDoc(')
    report('5 copy: ccDoc found', bool(cd))
    report("5 copy: ccDoc takes the leg table's legs and figures",
           'legPts(r,st)' in cd and 'g.parts.forEach' in cd and 'pt.nm.toFixed(2)' in cd and 'magOf(pt.brg)' in cd)
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
        got = hashlib.sha256(body.encode()).hexdigest()
        g(head.split()[1].rstrip('(') + ' unchanged from 2026-10-06.29' + (' apart from its routing waypoint line' if
          head == 'function ccDoc(' else ''), got == want)
    g('card marks are added only by tap, import or a saved row (four callers)', code.count('pushCardMark(') == 5,
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
    g('1 the WhatsApp date is the Race day box, never S.date',
      "const head=[series.name,$('day').value?longDate($('day').value):''].filter(Boolean).join(' – ')||'Course';" in bl
      and 'S.date' not in bl)
    g('1 the heading follows the Race day box at once', "$('day').addEventListener('change',()=>render());" in code)
    g('2 routing waypoints are not carried either', 'm.race<S.race&&!isCourseCard(m)&&!isRwCard(m)' in fn_body(code, 'function bank('))
    g('4 one line per refused name', "concat(refused.map(cardRefusal));" in code and "$('readStatus').innerHTML=said.map(esc).join('<br>');" in code)
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
    g('9 a far typed or pasted position is left out of the magnetic variation',
      'const near=S.marks.filter(m=>!farNm(m)), ms=near.length?near:[{lat:51.8,lon:-8.3}];' in fn_body(code, 'function varW('))


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
    print(f'\n{len(failed)} failed' if failed else '\nall passed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
