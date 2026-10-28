/* Sail Scoring connection, TEST COPY ONLY: Stage 1 read-only (Pat, 27 October 2026), Stage 2 the class list and the send.
   scripts/build_test.py adds this file to the test page (/course-test/) and nowhere else: the live page never loads it, and
   pages/course/course_v8.html does not name it. It adds the closed "Sail Scoring (test)" panel at the foot of the page and
   touches nothing else on it, apart from putting the Race day box back after the sign-in (as the RO would set it by hand).

   The page is a public OAuth client of Sail Scoring's authenticated public API (no secret): authorization code with PKCE
   (S256) and a random state checked on return. The redirect address is a fixed constant, never built from location.href,
   because the page is often opened with ?v=. The code is exchanged at the token endpoint from the browser; if the browser
   refuses that (CORS or anything else), the exact error is shown and nothing more is tried: no relay, no proxy.

   Reads: every read goes through ssApi, which refuses any method but GET. Writes (Stage 2 Part B): only through ssWrite,
   which knows exactly four requests (WRITES) and refuses each unless the review has just checked that send. The only
   other requests are to the token endpoint (the code exchange and the refresh) and to the revoke endpoint (Disconnect),
   all through tokenPost. Nothing is ever removed from Sail Scoring: no race or start is taken away.

   Tokens: localStorage, under a key naming the client and the workspace (STORE+'sailscoring|'+CLIENT_ID+'|tokens|'+slug),
   with STORE+'sailscoring|'+CLIENT_ID+'|in-use' naming the workspace in use. Never printed, never in saved race data.
   Refresh (Sail Scoring's rule): each refresh returns a new refresh token and the old one stops working; presenting a
   replaced one is treated as theft and ends every grant. So one refresh at a time across tabs (navigator.locks, or a lock
   in localStorage where that is missing), the new refresh token is stored and read back before the new access token is
   used, and a refresh that is refused or whose answer cannot be read clears the stored tokens: never sent again.

   Stage 2 Part A (STATUS A147, Pat 27 October 2026): the club's class list. A Sail Scoring fleet named
   "CLASS (RATING SYSTEM)", with anything after the bracket, belongs to the class CLASS (the text before the first "(",
   trimmed); a fleet with no "(" or nothing before it is not a class and is never offered. The scorer picks a series,
   taps "Use this series' classes" (one more GET of its fleets), checks the classes, and saves them with "Save as the
   club's class list". The page saves it (window.courseClassList, only on a test page, with the race key, in marks.php's
   classes.json) so every RO device reads it; this file never reaches marks.php itself. The saved list holds class names,
   fleet ids, names and scoring systems, the series and the time: no tokens.

   Stage 2 Part B (STATUS A148, Pat 28 October 2026): send the race day to Sail Scoring, after a review. The scorer picks
   the series at every send (nothing is preselected). One start on the page is one start in Sail Scoring. A page class
   matches the class of the same name (trimmed) among the PICKED series' fleets, by the rule above, with that series' own
   fleet ids; fleets with no bracket are not managed: never added, never taken off a start. Page Race n is the n-th race of
   the series on the race day, unless the day's record names its race; a missing race is created after the series' last
   race, with no name, its id and its starts' ids chosen here. A start is found by its id from the record, else by its
   fleets; a start none of whose classes is in the race yet is added to it, its id chosen here (Sail Scoring #708). Two
   page starts found as one Sail Scoring start are split: the one the record names keeps it (else the first on the page),
   and each other one's classes are taken off it and added as a new start, after every change to existing starts. When a
   class moves off a start (a split, or to another start), a fleet with no bracket on that start moves with it only if
   every competitor in that fleet is also entered in that class (the series' competitors); otherwise, or with no
   competitors, it stays, and the review says so. When the page creates a race or adds a start, a fleet with no bracket
   not on that race goes on the one new start with a class every competitor in that fleet is also entered in; for more
   than one such start, none, or no competitors, it is not added, and the review says so. It is
   given the page's classes (a managed class not raced that day is taken off it), the gun time, and the Copy
   for Sail Scoring document as its course (replacing any course). Stops, nothing sent: a class with no match in the
   series; course changes on this device not yet saved; a start with no gun time, no course, an INCOMPLETE course, no
   wind direction on its course's legs or no classes; one page start whose classes are in two Sail Scoring starts; a workspace other than ORC Ireland; a series whose name does not contain TESTING. A start or race in
   Sail Scoring but not on the page is named and left. Changing the classes or gun time of a start with finishes, and
   sending to a series other than the day's last one, each need their own tick. The record of the send (marks.php's
   sailscoring-DAY.json, through window.courseSailScoring) is saved before anything is created and again after. */
(function(){
'use strict';
const STORE='test-';   // every browser storage key starts with this (checked by scripts/build_test.py)
const CLIENT_ID='seKPxFYHkQKjsZiOcOfbJPKtAMDbszoT';
const REDIRECT_URI='https://tradboats.ie/course-test/';
const SCOPES='read races offline_access';
const ISSUER='https://app.sailscoring.ie/api/auth';
const AUTHORIZE='https://app.sailscoring.ie/api/auth/oauth2/authorize';
const TOKEN='https://app.sailscoring.ie/api/auth/oauth2/token';
const REVOKE='https://app.sailscoring.ie/api/auth/oauth2/revoke';
const API='https://app.sailscoring.ie/api/public/v1';
const EXPECTED_WS='ORC Ireland';
const LAPSED='Sail Scoring connection has lapsed: connect again';
const PENDING='pending';   // the tokens' workspace before GET /workspaces has named it
const PTR=STORE+'sailscoring|'+CLIENT_ID+'|in-use', AUTH=STORE+'sailscoring|'+CLIENT_ID+'|auth', LOCK=STORE+'sailscoring|'+CLIENT_ID+'|lock';
const WAIT_MS=20000;

const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sleep=ms=>new Promise(ok=>setTimeout(ok,ms));
const errText=e=>(e&&e.name?e.name+': ':'')+(e&&e.message!==undefined?e.message:String(e));
const b64url=bytes=>btoa(String.fromCharCode.apply(null,Array.from(bytes))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
function longDate(iso){try{const[y,m,d]=iso.split('-').map(Number);return new Date(y,m-1,d).toLocaleDateString('en-IE',{weekday:'short',day:'numeric',month:'short',year:'numeric'});}catch(e){return iso;}}
function lapsed(detail){const e=new Error(LAPSED);e.lapsed=true;e.detail=detail||'';return e;}

/* ---------- tokens on this device ---------- */
function readTokens(){
  try{const ws=localStorage.getItem(PTR);if(!ws)return null;
    const t=JSON.parse(localStorage.getItem(STORE+'sailscoring|'+CLIENT_ID+'|tokens|'+ws)||'null');
    return t&&typeof t.access==='string'?Object.assign(t,{ws}):null;}catch(_){return null;}}
// stored and read back before the access token is used; throws if this device would not keep them
function saveTokens(ws,t){
  const rec=JSON.stringify({access:t.access,refresh:t.refresh,expiresAt:t.expiresAt,scope:t.scope,workspace:t.workspace||null});
  localStorage.setItem(STORE+'sailscoring|'+CLIENT_ID+'|tokens|'+ws,rec);
  localStorage.setItem(PTR,ws);
  if(localStorage.getItem(STORE+'sailscoring|'+CLIENT_ID+'|tokens|'+ws)!==rec||localStorage.getItem(PTR)!==ws)
    throw new Error('this device did not keep the new tokens');}
function clearTokens(){
  try{const ws=localStorage.getItem(PTR);
    if(ws)localStorage.removeItem(STORE+'sailscoring|'+CLIENT_ID+'|tokens|'+ws);
    localStorage.removeItem(STORE+'sailscoring|'+CLIENT_ID+'|tokens|'+PENDING);
    localStorage.removeItem(PTR);}catch(_){}}
function fromTokenAnswer(j){
  if(!j||typeof j.access_token!=='string')throw new Error('Sail Scoring\'s answer had no access token');
  return{access:j.access_token,refresh:typeof j.refresh_token==='string'?j.refresh_token:'',
    expiresAt:Date.now()+1000*(Number(j.expires_in)||3600),scope:typeof j.scope==='string'?j.scope:''};}

/* ---------- the token and revoke endpoints: the only POSTs ---------- */
async function tokenPost(url,params){
  if(url!==TOKEN&&url!==REVOKE)throw new Error('Refused: no POST to '+url);
  const ac=new AbortController(), tm=setTimeout(()=>ac.abort(),WAIT_MS);
  let r;
  try{r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body:new URLSearchParams(params).toString(),cache:'no-store',credentials:'omit',signal:ac.signal});}
  catch(e){const err=new Error(errText(e));err.blocked=true;throw err;}
  finally{clearTimeout(tm);}
  let body=null;try{body=JSON.parse(await r.text());}catch(_){}
  return{status:r.status,ok:r.ok,body};}
const refusal=r=>'HTTP '+r.status+(r.body&&r.body.error?' ('+r.body.error+(r.body.error_description?': '+r.body.error_description:'')+')':'');

/* ---------- one refresh at a time, across tabs ---------- */
async function withLock(fn){
  if(navigator.locks&&navigator.locks.request)return navigator.locks.request(LOCK,{mode:'exclusive'},fn);
  // no Web Locks: a lock in localStorage, taken only if it reads back as ours, and given up after 45 s if a tab died holding it
  const me=Math.random().toString(36).slice(2), end=Date.now()+WAIT_MS*2;
  for(;;){
    let held=null;try{held=JSON.parse(localStorage.getItem(LOCK)||'null');}catch(_){}
    if(!held||!(held.until>Date.now())){
      try{localStorage.setItem(LOCK,JSON.stringify({me,until:Date.now()+45000}));}catch(_){throw new Error('could not take the refresh lock on this device');}
      await sleep(80);
      let now=null;try{now=JSON.parse(localStorage.getItem(LOCK)||'null');}catch(_){}
      if(now&&now.me===me)break;}
    if(Date.now()>end)throw new Error('another tab is refreshing the Sail Scoring connection: try again in a moment');
    await sleep(200);}
  try{return await fn();}
  finally{try{const h=JSON.parse(localStorage.getItem(LOCK)||'null');if(h&&h.me===me)localStorage.removeItem(LOCK);}catch(_){}}}

// a usable access token; failed: the access token the API has just refused (401), so it is refreshed even if not expired
async function freshAccess(failed){
  let t=readTokens();
  if(!t)throw new Error('Not connected to Sail Scoring.');
  if(!failed&&t.expiresAt-60000>Date.now())return t;
  return withLock(async()=>{
    t=readTokens();
    if(!t)throw lapsed('another tab cleared the connection');
    if(t.access!==failed&&t.expiresAt-60000>Date.now())return t;   // another tab refreshed while this one waited
    if(!t.refresh){clearTokens();throw lapsed('no refresh token was given (offline_access)');}
    if(navigator.onLine===false)throw new Error('No signal: Sail Scoring not reached.');   // nothing sent: the token stays good
    let r;
    try{r=await tokenPost(TOKEN,{grant_type:'refresh_token',refresh_token:t.refresh,client_id:CLIENT_ID});}
    catch(e){clearTokens();throw lapsed('the refresh answer could not be read: '+e.message);}   // it may have been used: never sent again
    if(!r.ok){clearTokens();throw lapsed('the refresh was refused: '+refusal(r));}
    let n;
    try{n=fromTokenAnswer(r.body);n.workspace=t.workspace;saveTokens(t.ws,n);}
    catch(e){clearTokens();throw lapsed(e.message);}
    return Object.assign(n,{ws:t.ws});});}

/* ---------- the API: GET only ---------- */
async function ssApi(method,path,token){
  if(method!=='GET')throw new Error('Refused: Stage 1 makes no '+method+' call to Sail Scoring (read-only).');
  if(!/^\/[A-Za-z0-9/_.\-]*(\?[A-Za-z0-9_.\-=&]*)?$/.test(path))throw new Error('Refused: '+path);
  const go=async tk=>{
    const ac=new AbortController(), tm=setTimeout(()=>ac.abort(),WAIT_MS);
    try{return await fetch(API+path,{method:'GET',headers:{Authorization:'Bearer '+tk},cache:'no-store',credentials:'omit',signal:ac.signal});}
    catch(e){throw new Error('Sail Scoring not reached: '+errText(e));}
    finally{clearTimeout(tm);}};
  let tk=token||(await freshAccess('')).access;
  let r=await go(tk);
  if(r.status===401&&!token){tk=(await freshAccess(tk)).access;r=await go(tk);}
  let body=null;try{body=await r.json();}catch(_){}
  if(!r.ok)throw new Error('Sail Scoring answered HTTP '+r.status+' to GET '+path+
    (body&&body.error?' ('+body.error+(body.message?': '+body.message:'')+')':''));
  return body;}

/* ---------- the panel ---------- */
const panel=document.createElement('details');
panel.className='sec setupOnly';panel.id='ssPanel';
panel.innerHTML='<summary><h2>Sail Scoring (test)</h2></summary>'+
  '<p class="cardnote">Test of the Sail Scoring connection. Sail Scoring is written only by Send, after its review, and only to a series whose name contains TESTING. A class list saved here sets the classes the class box offers on every device.</p>'+
  '<p class="status" id="ssState" role="status" aria-live="polite"></p>'+
  '<p class="status" id="ssDetail" hidden></p>'+
  '<p class="status" id="ssWs" hidden></p>'+
  '<p class="status" id="ssClassState"></p>'+
  '<button class="ghost" id="ssClassRemove" type="button" hidden>Remove saved class list</button>'+
  '<button class="ghost" id="ssConnect" type="button">Connect to Sail Scoring</button>'+
  '<button class="ghost" id="ssDisconnect" type="button" hidden>Disconnect</button>'+
  '<div id="ssData" hidden>'+
  '<div class="fields"><label>Series<select id="ssSeries"></select></label></div>'+
  '<h3>Fleets in this series</h3><div id="ssFleets"><p class="cardnote">Pick a series.</p></div>'+
  '<button class="ghost" id="ssUseClasses" type="button" hidden>Use this series\' classes</button>'+
  '<div id="ssClasses" hidden></div>'+
  '<h3 id="ssDayHead">Races on the race day</h3><div id="ssRaces"><p class="cardnote">Pick a series.</p></div>'+
  '<button class="ghost" id="ssReload" type="button">Read Sail Scoring again</button>'+
  '<h3>Send the race day to Sail Scoring</h3>'+
  '<div class="fields"><label>Send to series<select id="ssSendSeries"></select></label></div>'+
  '<button class="ghost" id="ssReviewBtn" type="button" disabled>Review the send</button>'+
  '<div id="ssReview" hidden></div>'+
  '</div>';
const foot=document.querySelector('.wrap>.foot');
if(foot)foot.parentNode.insertBefore(panel,foot);else document.body.appendChild(panel);

function say(msg,kind,detail){
  $('ssState').textContent=msg;$('ssState').className='status'+(kind?' '+kind:'');
  $('ssDetail').hidden=!detail;$('ssDetail').textContent=detail||'';$('ssDetail').className='status'+(kind?' '+kind:'');}
function showConnected(on){
  $('ssConnect').hidden=on;$('ssDisconnect').hidden=!on;$('ssData').hidden=!on;
  if(!on){$('ssWs').hidden=true;series=null;fleets={};racesBy={};}}
function fail(e){
  if(e&&e.lapsed){showConnected(false);say(LAPSED,'err',e.detail);return;}
  say(e&&e.message?e.message:errText(e),'err');}
const dayBox=()=>$('day');
const raceDay=()=>(dayBox()&&dayBox().value)||'';

/* ---------- what the connection reaches, and the series ---------- */
let series=null, fleets={}, racesBy={}, loading=false;
function showWorkspace(list){
  const w=$('ssWs'), names=list.map(x=>x.name);
  w.hidden=false;
  if(!list.length){w.className='status amberTxt';w.textContent='Test copy is connected to no workspace, expected '+EXPECTED_WS;return;}
  const ok=list.length===1&&String(list[0].name).trim()===EXPECTED_WS;
  w.className='status'+(ok?' ok':' amberTxt');
  w.textContent=ok?'Workspace: '+list[0].name+' ('+list[0].slug+')':'Test copy is connected to '+names.join(', ')+', expected '+EXPECTED_WS;}
async function loadAll(){
  if(loading)return;loading=true;
  try{
    say('Reading Sail Scoring…','');
    const ws=await ssApi('GET','/workspaces');
    showWorkspace(Array.isArray(ws&&ws.workspaces)?ws.workspaces:[]);
    const sl=await ssApi('GET','/series');
    series=Array.isArray(sl&&sl.series)?sl.series:[];
    const sel=$('ssSeries'), was=sel.value;
    sel.innerHTML='<option value="">Pick a series</option>'+series.map(s=>'<option value="'+esc(s.id)+'">'+esc(s.name+
      (s.startDate||s.endDate?' ('+(s.startDate||'?')+' to '+(s.endDate||'?')+')':'')+(s.archived?' · archived':'')+(s.asPublished?' · as published':''))+'</option>').join('');
    if(was&&series.some(s=>s.id===was))sel.value=was;   // only the RO's own pick, kept on Read again; never picked for them
    sendSeriesList();
    const t=readTokens();
    say('Connected to Sail Scoring.','ok',t&&!t.refresh?'Sail Scoring gave no refresh token: the connection lasts an hour.':'');
    if(sel.value)await loadSeries(sel.value);
  }catch(e){fail(e);}
  finally{loading=false;}}
async function loadSeries(id){
  hideClasses();
  if(!id){$('ssFleets').innerHTML=$('ssRaces').innerHTML='<p class="cardnote">Pick a series.</p>';return;}
  $('ssFleets').innerHTML=$('ssRaces').innerHTML='<p class="cardnote">Reading…</p>';
  try{
    const[f,r]=await Promise.all([ssApi('GET','/series/'+encodeURIComponent(id)+'/fleets'),ssApi('GET','/series/'+encodeURIComponent(id)+'/races')]);
    if($('ssSeries').value!==id)return;
    fleets[id]=Array.isArray(f&&f.fleets)?f.fleets:[];racesBy[id]=Array.isArray(r&&r.races)?r.races:[];
    showFleets(id);showRaces();$('ssUseClasses').hidden=false;
  }catch(e){$('ssFleets').innerHTML=$('ssRaces').innerHTML='';fail(e);}}
const cell=v=>v===null?'null':typeof v==='object'?JSON.stringify(v):String(v);
// every field the API returns, as it returns it: one column per field, in the order first seen
function showFleets(id){
  const list=fleets[id]||[];
  if(!list.length){$('ssFleets').innerHTML='<p class="cardnote">This series has no fleets.</p>';return;}
  const cols=[];list.forEach(f=>Object.keys(f).forEach(k=>{if(!cols.includes(k))cols.push(k);}));
  $('ssFleets').innerHTML='<div style="overflow-x:auto"><table style="border-collapse:collapse;font-size:.85rem;margin:6px 0">'+
    '<tr>'+cols.map(k=>'<th style="text-align:left;padding:4px 8px;border-bottom:1px solid var(--line)">'+esc(k)+'</th>').join('')+'</tr>'+
    list.map(f=>'<tr>'+cols.map(k=>'<td style="padding:4px 8px;border-bottom:1px solid var(--line);vertical-align:top;word-break:break-all">'+
      esc(k in f?cell(f[k]):'(absent)')+'</td>').join('')+'</tr>').join('')+'</table></div>';}
// the races of the picked series on the Race day box's date, each start's gun and fleets
function showRaces(){
  const id=$('ssSeries').value, day=raceDay();
  $('ssDayHead').textContent='Races on '+(day?longDate(day):'the race day');
  if(!id||!racesBy[id])return;
  const name=fid=>{const f=(fleets[id]||[]).find(x=>x.id===fid);return f?f.name:'unknown fleet '+fid;};
  const list=racesBy[id].filter(r=>r.date===day);
  if(!list.length){$('ssRaces').innerHTML='<p class="cardnote">No races on '+esc(day?longDate(day):'(no race day)')+' in this series</p>';return;}
  $('ssRaces').innerHTML=list.map(r=>'<div class="info"><b>Race '+esc(r.number)+(r.name?' – '+esc(r.name):'')+'</b>'+
    (r.starts&&r.starts.length?r.starts.map((s,i)=>'<div>Start '+(i+1)+': gun '+esc(s.startTime||'no time')+' · fleets: '+
      esc((s.fleetIds||[]).map(name).join(', ')||'none')+(s.course?' · course set ('+esc((s.course.legs||[]).length)+' legs)':'')+'</div>').join('')
      :'<div>No starts.</div>')+'</div>').join('');}

/* ---------- the club's class list (A147) ---------- */
const CL=()=>window.courseClassList||null;
const when=iso=>{try{return new Date(iso).toLocaleString('en-IE',{weekday:'short',day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});}catch(_){return iso;}};
function showClassState(){
  const c=CL(), l=c&&c.get(), el=$('ssClassState');
  el.className='status';
  el.textContent=!c?'Class list: not available on this copy of the page':
    l?'Class list: from '+l.series.name+', loaded '+when(l.loaded):'Class list: page defaults (none saved)';
  $('ssClassRemove').hidden=!(c&&l);}
// the fleets as classes: the class is the text before the first "(", trimmed; classes in the order their first fleet comes
function classesFrom(list){
  const classes=[], none=[];
  list.forEach(f=>{const n=String(f.name||''), i=n.indexOf('('), c=i>=0?n.slice(0,i).trim():'';
    if(!c){none.push(f);return;}
    let k=classes.find(x=>x.name===c); if(!k)classes.push(k={name:c,fleets:[]});
    k.fleets.push({id:f.id,name:n,scoringSystem:f.scoringSystem});});
  return{classes,none};}
// what marks.php would refuse, said before the Save button is offered
function classProblems(cs){
  const p=[];
  if(cs.length>30)p.push(cs.length+' classes: at most 30 can be saved');
  cs.forEach(c=>{if(c.name.length>40)p.push(c.name+': a class name can be at most 40 characters');
    if(/[<>]/.test(c.name))p.push(c.name+': a class name cannot hold < or >');
    if(c.fleets.length>60)p.push(c.name+': at most 60 fleets');
    c.fleets.forEach(f=>{if(typeof f.scoringSystem!=='string'||!f.scoringSystem.trim())p.push(f.name+': no scoring system');
      if(/[<>]/.test(f.name)||f.name.length>100)p.push(f.name+': a fleet name of at most 100 characters, without < or >');});});
  return p;}
let pending=null;   // the class list shown, waiting for Save or Cancel
function hideClasses(){pending=null;$('ssClasses').hidden=true;$('ssClasses').innerHTML='';$('ssUseClasses').hidden=true;}
async function useClasses(){
  const id=$('ssSeries').value, s=(series||[]).find(x=>x.id===id);
  if(!id||!s)return;
  const box=$('ssClasses');box.hidden=false;box.innerHTML='<p class="cardnote">Reading the fleets…</p>';
  let f;
  try{f=await ssApi('GET','/series/'+encodeURIComponent(id)+'/fleets');}
  catch(e){box.innerHTML='';box.hidden=true;fail(e);return;}
  if($('ssSeries').value!==id)return;
  const{classes,none}=classesFrom(Array.isArray(f&&f.fleets)?f.fleets:[]), probs=classProblems(classes);
  pending=classes.length&&!probs.length?{series:{id:s.id,name:s.name},loaded:new Date().toISOString(),classes}:null;
  box.innerHTML='<h3>Classes from '+esc(s.name)+'</h3>'+
    (classes.length?classes.map(c=>'<div class="info"><b>'+esc(c.name)+'</b>'+
      c.fleets.map(x=>'<div>'+esc(x.name)+' · '+esc(x.scoringSystem)+'</div>').join('')+'</div>').join('')
      :'<p class="cardnote">No fleet in this series has a class.</p>')+
    '<p><b>Not used as a class:</b> '+(none.length?esc(none.map(x=>x.name).join(', ')):'Every fleet has a class.')+'</p>'+
    (probs.length?'<p class="status err">Cannot be saved: '+esc(probs.join('; '))+'</p>':'')+
    (!CL()?'<p class="status err">This copy of the page cannot save a class list.</p>':'')+
    '<p class="status" id="ssClassSaid" hidden></p>'+
    (pending&&CL()?'<button class="ghost" id="ssClassSave" type="button">Save as the club\'s class list</button>':'')+
    '<button class="ghost" id="ssClassCancel" type="button">Cancel</button>';
  const sv=$('ssClassSave');
  if(sv)sv.onclick=async()=>{
    const said=$('ssClassSaid'), rec=pending;
    if(!rec)return;
    sv.disabled=true;said.hidden=false;said.className='status';said.textContent='Saving…';
    try{await CL().save(rec);hideClasses();$('ssUseClasses').hidden=false;
      $('ssClassState').textContent='Saved. Class list: from '+rec.series.name+', loaded '+when(rec.loaded);$('ssClassState').className='status ok';}
    catch(e){sv.disabled=false;said.className='status err';said.textContent='Not saved: '+errText(e)+(e&&e.text?' ('+e.text+')':'');}};
  $('ssClassCancel').onclick=()=>{hideClasses();$('ssUseClasses').hidden=false;};}
async function removeClasses(){
  const c=CL();if(!c||!c.get())return;
  if(!confirm('Remove the saved class list?\n\nThe class box goes back to the page defaults (Class 1 Spinnaker … Class 3 Non Spinnaker) on every device. A start that already holds a class keeps it.'))return;
  const el=$('ssClassState');el.className='status';el.textContent='Removing the class list…';
  try{await c.save(null);showClassState();}
  catch(e){el.className='status err';el.textContent='Not removed: '+errText(e)+(e&&e.text?' ('+e.text+')':'');}}

/* ---------- the send (A148) ---------- */
const PG=()=>window.courseSailScoring||null;
const SEND_TESTING='TESTING';
const isId=v=>typeof v==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v);
function newId(){
  if(crypto.randomUUID)return crypto.randomUUID();
  const b=crypto.getRandomValues(new Uint8Array(16));b[6]=b[6]&15|64;b[8]=b[8]&63|128;
  const h=Array.from(b,x=>x.toString(16).padStart(2,'0')).join('');
  return h.slice(0,8)+'-'+h.slice(8,12)+'-'+h.slice(12,16)+'-'+h.slice(16,20)+'-'+h.slice(20);}
async function sha(text){const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text));
  return Array.from(new Uint8Array(d),x=>x.toString(16).padStart(2,'0')).join('');}
const hm=t=>{const m=String(t||'').match(/^(\d{2}):(\d{2})(?::(\d{2}))?$/);return m?m[1]+':'+m[2]+(m[3]&&m[3]!=='00'?':'+m[3]:''):'';};
const sameSet=(a,b)=>a.length===b.length&&a.every(x=>b.includes(x));
const ssErr=(r,body)=>'HTTP '+r.status+(body&&body.error?' '+body.error:'')+(body&&body.message?': '+body.message:'')+
  (body&&Array.isArray(body.problems)&&body.problems.length?' ('+body.problems.map(x=>x.field+': '+x.message).join('; ')+')':'');

/* The writes: exactly these four requests. checked is set only by a review whose stops are all clear (the workspace
   ORC Ireland, the series named with TESTING, the series picked for this send), and holds every race and start the send
   may touch; it is cleared when the send ends. Anything else is refused before a request is made. */
const WRITES={races:['POST',/^\/series\/([0-9a-f-]{36})\/races$/],start:['PATCH',/^\/races\/([0-9a-f-]{36})\/starts\/([0-9a-f-]{36})$/],add:['POST',/^\/races\/([0-9a-f-]{36})\/starts$/],course:['PUT',/^\/races\/([0-9a-f-]{36})\/starts\/([0-9a-f-]{36})\/course\?replace=true$/]};
let checked=null;
async function ssWrite(op,path,body,key){
  const w=WRITES[op];
  if(!w||!checked||!checked.ok)throw new Error('Refused: '+op+' without a checked send');
  const m=path.match(w[1]);
  if(!m)throw new Error('Refused: '+op+' to '+path);
  if(op==='races'){
    if(m[1]!==checked.series||!body||!Array.isArray(body.races)||!body.races.every(x=>checked.newRaces.has(x.id)&&
      Array.isArray(x.starts)&&x.starts.every(y=>checked.newStarts.has(y.id))))throw new Error('Refused: races not checked for this send');}
  else if(op==='add'){if(!body||!checked.addStarts.has(m[1]+'|'+body.id))throw new Error('Refused: a start not checked to be added');}
  else if(!checked.starts.has(m[1]+'|'+m[2]))throw new Error('Refused: a start not checked for this send');
  const go=async tk=>{
    const ac=new AbortController(), tm=setTimeout(()=>ac.abort(),WAIT_MS);
    try{return await fetch(API+path,{method:w[0],headers:{Authorization:'Bearer '+tk,'Content-Type':'application/json','Idempotency-Key':key},
      body:JSON.stringify(body),cache:'no-store',credentials:'omit',signal:ac.signal});}
    catch(e){throw new Error('Sail Scoring not reached: '+errText(e));}
    finally{clearTimeout(tm);}};
  let tk=(await freshAccess('')).access;
  let r=await go(tk);
  if(r.status===401){tk=(await freshAccess(tk)).access;r=await go(tk);}   // the same Idempotency-Key: never done twice
  let res=null;try{res=await r.json();}catch(_){}
  if(!r.ok)throw new Error(ssErr(r,res));
  return res;}

function sendSeriesList(){
  const sel=$('ssSendSeries');
  sel.innerHTML='<option value="">Pick the series to send to</option>'+(series||[]).map(s=>'<option value="'+esc(s.id)+'">'+
    esc(s.name+(s.archived?' · archived':'')+(s.asPublished?' · as published':''))+'</option>').join('');
  sel.value='';$('ssReviewBtn').disabled=true;hideReview();}
function hideReview(){plan=null;$('ssReview').hidden=true;$('ssReview').innerHTML='';}
let plan=null;   // the send the review showed: what Send does, and nothing more

// fleet names, and each fleet's class (the A147 rule) in the picked series
function classMap(list){const{classes}=classesFrom(list), byName={}, fleetClass={};
  classes.forEach(c=>{byName[c.name]=c.fleets.map(f=>f.id);c.fleets.forEach(f=>fleetClass[f.id]=c.name);});
  return{byName,fleetClass,fleetName:Object.fromEntries(list.map(f=>[f.id,f.name]))};}
function legsOf(c){if(!c||!Array.isArray(c.legs)||!c.legs.length)return 'none';
  const nm=typeof c.distanceNm==='number'?c.distanceNm:c.legs.reduce((a,l)=>a+(+l.distanceNm||0),0);
  return c.legs.length+' leg'+(c.legs.length>1?'s':'')+', '+nm.toFixed(2)+' nm';}
function docLegs(d){const l=d.legs||[];return l.length+' leg'+(l.length>1?'s':'')+', '+l.reduce((a,x)=>a+(+x.distance||0),0).toFixed(2)+' nm';}

async function review(){
  hideReview();
  const P=PG(), box=$('ssReview'), sid=$('ssSendSeries').value, ser=(series||[]).find(x=>x.id===sid);
  if(!ser)return;
  box.hidden=false;box.innerHTML='<p class="cardnote">Reading Sail Scoring…</p>';
  if(!P){box.innerHTML='<p class="status err">This copy of the page cannot send to Sail Scoring.</p>';return;}
  const day=P.day();
  if(!day){box.innerHTML='<p class="status err">Nothing to review: tap Get latest marks for the race day in the Race day box first.</p>';return;}
  let ws,fl,rl,rec;
  try{[ws,fl,rl,rec]=await Promise.all([ssApi('GET','/workspaces'),ssApi('GET','/series/'+sid+'/fleets'),ssApi('GET','/series/'+sid+'/races'),P.load(day)]);}
  catch(e){box.innerHTML='';box.hidden=true;fail(e);return;}
  if($('ssSendSeries').value!==sid)return;
  const page=P.races(), heading=P.series(), stops=[], wsl=Array.isArray(ws&&ws.workspaces)?ws.workspaces:[];
  if(!(wsl.length===1&&String(wsl[0].name).trim()===EXPECTED_WS))stops.push('The test copy is connected to '+(wsl.map(x=>x.name).join(', ')||'no workspace')+', not '+EXPECTED_WS+'.');
  if(P.unsent())stops.push('This device has course changes not yet saved: save them first, then send.');
  if(!String(ser.name).includes(SEND_TESTING))stops.push('The series '+ser.name+' does not have '+SEND_TESTING+' in its name: this test copy sends only to a test series.');
  const fleetList=Array.isArray(fl&&fl.fleets)?fl.fleets:[], cm=classMap(fleetList);
  const races=(Array.isArray(rl&&rl.races)?rl.races:[]);
  const dayRaces=races.filter(r=>r.date===day).sort((a,b)=>a.number-b.number);
  const old=rec&&rec.series&&rec.series.id===sid?rec:null;      // a record of another series names nothing here
  const moved=rec&&rec.series&&rec.series.id!==sid?rec:null;
  const label=(n,c)=>c.length?c.join(', '):'none';
  const nameF=f=>cm.fleetClass[f]||cm.fleetName[f]||'unknown fleet';
  const clsOf=ids=>[...new Set(ids.map(nameF))];
  const claimed=new Set(), out=[], items=[];   // out: per page race; items: what Send does
  let compList=null;   // the series' competitors, read once, only when needed
  const comps=async()=>{if(!compList){const c=await ssApi('GET','/series/'+sid+'/competitors');compList=Array.isArray(c&&c.competitors)?c.competitors:[];}return compList;};
  for(const pr of page){
    const orec=old&&old.races.find(x=>x.race===pr.race);
    let R=orec?races.find(x=>x.id===orec.id):null, fresh=false, rid;
    if(!R&&!orec){const c=dayRaces[pr.race-1];
      if(c&&claimed.has(c.id))stops.push('Race '+pr.race+': Sail Scoring\'s race '+c.number+' on this date is already linked to another page race.');
      else if(c)R=c;}
    if(R){rid=R.id;claimed.add(R.id);}else{fresh=true;rid=orec?orec.id:newId();}
    const ro={race:pr.race,id:rid,fresh,number:R?R.number:null,starts:[],notOnPage:[],notes:[]};
    out.push(ro);
    // each page start: its classes, fleets, time and course document
    const ps=pr.starts.map(st=>{
      const where='Race '+pr.race+', Start '+st.start, d=st.doc||{};
      const p={start:st.start,classes:st.classes.map(c=>c.trim()),time:st.time,where,doc:d,want:[],notes:[]};
      if(!p.classes.length)stops.push(where+' has a course but no classes.');
      p.classes.forEach(c=>{if(!cm.byName[c])stops.push((/^class\b/i.test(c)?'':'Class ')+c+' ('+where+') has no matching class in '+ser.name+'.');else p.want.push(...cm.byName[c]);});
      if(!st.time)stops.push(where+' has no gun time.');
      if(d.block)stops.push(where+': no course to send ('+d.block+')');
      const inc=(d.warns||[]).filter(t=>/^INCOMPLETE/.test(t));
      if(inc.length)stops.push(where+': the course is INCOMPLETE: '+inc.join(' '));
      if(!d.block&&d.text){let lg=null;try{lg=JSON.parse(d.text).legs;}catch(_){}
        if(Array.isArray(lg)&&lg.some(l=>typeof l.windDirection!=='number'))stops.push(where+': no wind direction for its course: set the wind for this start or the day\'s wind, then review again.');}
      p.notes=(d.warns||[]).filter(t=>/^STAND-IN/.test(t));
      return p;});
    if(R){
      // the start each page start is: by the record's id, else by its fleets
      ps.forEach(p=>{const os=orec&&orec.starts.find(x=>x.start===p.start), byId=os&&R.starts.find(x=>x.id===os.id);
        const cand=R.starts.filter(x=>(x.fleetIds||[]).some(f=>p.want.includes(f)));
        if(byId)p.S=byId;
        else if(cand.length===1)p.S=cand[0];
        else if(!cand.length&&p.want.length)p.add=os?os.id:newId();   // none of its classes in the race yet: added (#708)
        else stops.push(p.where+': its classes are in '+(cand.length===2?'two':cand.length)+' starts in Sail Scoring (race '+R.number+', '+cand.map(x=>'start '+(R.starts.indexOf(x)+1)).join(' and ')+').');
        p.os=os&&p.S&&os.id===p.S.id?os:null;});
      // two page starts found as one Sail Scoring start: the one the record names keeps it, else the first on the page;
      // each other one's classes come off it and go to a new start (#708)
      R.starts.forEach(x=>{const on=ps.filter(q=>q.S===x);if(on.length<2)return;
        const keep=on.find(q=>q.os)||on[0];
        on.filter(q=>q!==keep).forEach(q=>{const os=orec&&orec.starts.find(y=>y.start===q.start);
          q.from=x;q.S=null;q.os=null;q.add=os&&os.id!==x.id?os.id:newId();});});
      // a fleet the page wants that sits in a Sail Scoring start no page start is
      ps.forEach(p=>{if(!p.S)return;R.starts.forEach(x=>{if(x===p.S||ps.some(q=>q.S===x))return;
        if((x.fleetIds||[]).some(f=>p.want.includes(f)))stops.push(p.where+': its classes are in two starts in Sail Scoring (race '+R.number+', start '+(R.starts.indexOf(p.S)+1)+' and start '+(R.starts.indexOf(x)+1)+').');});});
      R.starts.forEach((x,i)=>{if(!ps.some(q=>q.S===x))ro.notOnPage.push('Start '+(i+1)+' ('+(clsOf(x.fleetIds||[]).join(', ')||'no fleets')+', gun '+(hm(x.startTime)||'none')+')');});}
    else ps.forEach(p=>{const os=orec&&orec.starts.find(x=>x.start===p.start);p.newId=os?os.id:newId();});
    for(const p of ps){
      const hash=p.doc.text?await sha(p.doc.text):'', doc=p.doc.text?JSON.parse(p.doc.text):null;
      const st={start:p.start,where:p.where,notes:p.notes,hash,doc,want:p.want};
      if(R&&p.S){
        const cur=p.S.fleetIds||[], keep=cur.filter(f=>!cm.fleetClass[f]);   // fleets with no class: never taken off
        st.id=p.S.id;st.cur=cur;st.fleets=[...new Set(p.want.concat(keep))];
        st.fleetsChange=!sameSet(cur,st.fleets);st.timeChange=hm(p.S.startTime)!==hm(p.time);
        st.courseChange=!(p.os&&p.os.course&&p.os.course===hash);
        st.before={classes:clsOf(cur),time:hm(p.S.startTime)||'none',course:legsOf(p.S.course)};}
      else if(R&&p.add){st.id=p.add;st.fleets=p.want.slice();st.created=st.added=true;st.fleetsChange=st.timeChange=st.courseChange=true;
        if(p.from){st.fromId=p.from.id;st.moved=clsOf((p.from.fleetIds||[]).filter(f=>p.want.includes(f))).join(', ')+' moved from Sail Scoring start '+(R.starts.indexOf(p.from)+1);}}
      else if(!R){st.id=p.newId;st.fleets=p.want.slice();st.created=true;st.fleetsChange=st.timeChange=st.courseChange=true;}
      st.after={classes:clsOf(st.fleets||p.want),time:hm(p.time)||'none',course:doc?docLegs(doc):'none'};
      st.time=p.time;st.oldHash=p.os?p.os.course:'';
      ro.starts.push(st);}
    // a fleet with no bracket on a start a class moves off (Pat, 28 October 2026): it moves with that class only when every
    // competitor in it is also entered in a fleet of that class; otherwise, or with no competitors, it stays, and is named
    for(const src of ro.starts.filter(x=>x.cur)){
      const moving={};   // class -> the start its fleets go to
      src.cur.forEach(f=>{const c=cm.fleetClass[f];if(!c||src.fleets.includes(f))return;
        const to=ro.starts.find(q=>q!==src&&(q.fleets||[]).includes(f));if(to)moving[c]=to;});
      const names=Object.keys(moving), loose=src.fleets.filter(f=>!cm.fleetClass[f]);
      if(!names.length||!loose.length)continue;
      let comp;try{comp=await comps();}catch(e){box.innerHTML='';box.hidden=true;fail(e);return;}
      const n=R.starts.findIndex(x=>x.id===src.id)+1;
      for(const e of loose){
        const inE=comp.filter(x=>(x.fleetIds||[]).includes(e));
        const fit=inE.length?names.filter(c=>inE.every(x=>(x.fleetIds||[]).some(f=>cm.byName[c].includes(f)))):[];
        const en=cm.fleetName[e]||'unknown fleet';
        if(fit.length===1){const to=moving[fit[0]];src.fleets=src.fleets.filter(f=>f!==e);to.fleets=to.fleets.concat([e]);
          to.notes=to.notes.concat([en+' moves with '+fit[0]]);}
        else src.notes=src.notes.concat([en+' stays on Sail Scoring start '+n+'; check whether it should move with '+(fit.length?fit:names).join(' or ')]);}
      ro.starts.forEach(x=>{if(x.cur)x.fleetsChange=!sameSet(x.cur,x.fleets);x.after.classes=clsOf(x.fleets||x.want);});}
    // a fleet with no bracket, when the page creates a race or adds a start (Pat, 28 October 2026): added to the one new
    // start with a class every competitor in it is also entered in; for more than one, none, or no competitors, not added
    const made=ro.starts.filter(x=>x.created);
    const onRace=f=>ro.starts.some(x=>(x.fleets||[]).includes(f))||(!!R&&R.starts.some(x=>!ro.starts.some(q=>q.id===x.id)&&(x.fleetIds||[]).includes(f)));
    const free=made.length?fleetList.map(f=>f.id).filter(f=>!cm.fleetClass[f]&&!onRace(f)):[];
    if(free.length){
      let comp;try{comp=await comps();}catch(e){box.innerHTML='';box.hidden=true;fail(e);return;}
      for(const e of free){
        const inE=comp.filter(x=>(x.fleetIds||[]).includes(e)), en=cm.fleetName[e]||'unknown fleet';
        const fit=inE.length?made.map(x=>({x,cls:[...new Set(x.want.map(f=>cm.fleetClass[f]).filter(Boolean))]
          .filter(c=>inE.every(b=>(b.fleetIds||[]).some(f=>cm.byName[c].includes(f))))})).filter(o=>o.cls.length):[];
        if(fit.length===1){const x=fit[0].x;x.fleets=x.fleets.concat([e]);x.after.classes=clsOf(x.fleets);
          x.notes=x.notes.concat([en+' added with '+fit[0].cls.join(' and ')]);}
        else ro.notes.push(en+' not added; add it in Sail Scoring if it should race');}}}
  dayRaces.forEach(r=>{if(!claimed.has(r.id)&&!out.some(o=>o.id===r.id))out.push({extra:true,number:r.number,starts:r.starts||[]});});
  // finishes: a start with finishes whose classes or gun time would change needs its own tick
  let comp=null;
  for(const ro of out.filter(o=>!o.extra&&!o.fresh)){
    if(!ro.starts.some(s=>s.id&&!s.created&&(s.fleetsChange||s.timeChange)))continue;
    let fin;try{fin=await ssApi('GET','/races/'+ro.id+'/finishes');}catch(e){box.innerHTML='';box.hidden=true;fail(e);return;}
    const list=Array.isArray(fin&&fin.finishes)?fin.finishes:[];
    if(!list.length)continue;
    if(!comp){try{comp=await comps();}catch(e){box.innerHTML='';box.hidden=true;fail(e);return;}}
    const fleetsDone=new Set(), unknown=list.some(f=>!f.competitorId);
    list.forEach(f=>{const c=comp.find(x=>x.id===f.competitorId);if(c)(c.fleetIds||[]).forEach(x=>fleetsDone.add(x));else if(f.competitorId)fleetsDone.add('?');});
    ro.starts.forEach(s=>{if(s.cur&&(s.fleetsChange||s.timeChange)&&(unknown||fleetsDone.has('?')||s.cur.some(f=>fleetsDone.has(f))))s.finishes=true;});}
  if($('ssSendSeries').value!==sid)return;
  const work=out.filter(o=>!o.extra).some(o=>o.fresh||o.starts.some(s=>s.fleetsChange||s.timeChange||s.courseChange));
  const needFin=out.some(o=>(o.starts||[]).some(s=>s.finishes));
  plan={sid,ser,day,page:JSON.stringify(page),out,stops,old,moved,heading,work};
  const ch=(a,b,c)=>c?'<span class="caut">'+esc(a)+' → '+esc(b)+'</span>':esc(b)+' <small>(unchanged)</small>';
  box.innerHTML='<p><b>Message heading:</b> '+esc(heading||'(no series set for this day)')+' · <b>Sending to:</b> '+esc(ser.name)+'</p>'+
    (stops.length?'<div class="info"><p class="status err"><b>Nothing can be sent until these are put right:</b></p>'+stops.map(t=>'<p class="status err">'+esc(t)+'</p>').join('')+'</div>':'')+
    (moved?'<p class="status caut">This race day was sent to '+esc(moved.series.name)+' on '+esc(when(moved.sent))+'; sending to '+esc(ser.name)+' will create it there too.</p>'+
      '<label><input type="checkbox" id="ssMoveOk"> Send to '+esc(ser.name)+' as well</label>':'')+
    out.map(o=>o.extra?'<div class="info"><b>Sail Scoring race '+esc(o.number)+'</b><div>In Sail Scoring but not on the page: remove it in Sail Scoring if it should go.</div></div>':
      '<div class="info"><b>Race '+o.race+(o.fresh?' → a new race in '+esc(ser.name)+' (numbered by Sail Scoring)':' → Sail Scoring race '+esc(o.number))+'</b>'+
      o.starts.map(s=>'<div><b>Start '+s.start+(s.created?' (new)':'')+'</b>'+(s.moved?': '+esc(s.moved):'')+
        (s.created?'<div>Classes: '+esc(s.after.classes.join(', '))+'</div><div>Gun: '+esc(s.after.time)+'</div><div>Course: '+esc(s.after.course)+'</div>':
          (s.before?'<div>Classes: '+ch(s.before.classes.join(', ')||'none',s.after.classes.join(', '),s.fleetsChange)+'</div>'+
            '<div>Gun: '+ch(s.before.time,s.after.time,s.timeChange)+'</div><div>Course: '+ch(s.before.course,s.after.course,s.courseChange)+'</div>':''))+
        (s.finishes?'<div class="status err">has finishes</div>':'')+
        s.notes.map(t=>'<div class="cardnote caut">'+esc(t)+'</div>').join('')+'</div>').join('')+
      o.notOnPage.map(t=>'<div>'+esc(t)+': In Sail Scoring but not on the page: remove it in Sail Scoring if it should go.</div>').join('')+
      o.notes.map(t=>'<div class="cardnote caut">'+esc(t)+'</div>').join('')+'</div>').join('')+
    (needFin?'<label><input type="checkbox" id="ssFinOk"> Change the classes or gun time of the starts marked "has finishes"</label>':'')+
    (!work&&!stops.length?'<p class="status ok">Nothing to send.</p>':'')+
    '<p class="status" id="ssSendSaid" hidden></p><div id="ssResults"></div>'+
    '<button class="ghost" id="ssSendBtn" type="button" disabled>Send to Sail Scoring</button>'+
    '<button class="ghost" id="ssReviewCancel" type="button">Cancel</button>';
  const upd=()=>{const b=$('ssSendBtn');if(!b)return;
    b.disabled=!plan||!!plan.stops.length||!plan.work||(plan.moved&&!$('ssMoveOk').checked)||(needFin&&!$('ssFinOk').checked);
    b.style.opacity=b.disabled?'.4':'';b.style.cursor=b.disabled?'default':'';};   // the page's .ghost has no greyed look of its own
  if($('ssMoveOk'))$('ssMoveOk').onchange=upd;
  if($('ssFinOk'))$('ssFinOk').onchange=upd;
  upd();
  $('ssSendBtn').onclick=()=>{send().catch(e=>{say(errText(e),'err');});};
  $('ssReviewCancel').onclick=()=>{$('ssSendSeries').value='';$('ssReviewBtn').disabled=true;hideReview();};}

// the record of the send: every page race and start with its Sail Scoring id and the course last confirmed sent
function recordOf(pl,state,courseOf){
  return{series:{id:pl.ser.id,name:pl.ser.name},sent:pl.at,state,
    races:pl.out.filter(o=>!o.extra).map(o=>({race:o.race,id:o.id,starts:o.starts.map(s=>({start:s.start,id:s.id,course:courseOf(s)}))}))};}
async function send(){
  const pl=plan, P=PG(), said=$('ssSendSaid'), res=$('ssResults'), btn=$('ssSendBtn');
  if(!pl||pl.stops.length||!P)return;
  if(JSON.stringify(P.races())!==pl.page||P.day()!==pl.day){said.hidden=false;said.className='status err';said.textContent='The page has changed since the review: review again.';btn.disabled=true;btn.style.opacity='.4';return;}
  btn.disabled=true;btn.style.opacity='.4';$('ssReviewCancel').disabled=true;said.hidden=false;said.className='status';said.textContent='Sending…';
  pl.at=new Date().toISOString();
  const sendId=newId(), lines=[], line=(t,ok)=>{lines.push('<p class="status '+(ok?'ok':'err')+'">'+esc(t)+'</p>');res.innerHTML=lines.join('');};
  const races=pl.out.filter(o=>!o.extra), fresh=races.filter(o=>o.fresh), done=new Map();   // done: start id -> course hash now in Sail Scoring
  const added=races.filter(o=>!o.fresh).flatMap(o=>o.starts.filter(s=>s.added).map(s=>({o,s})));   // starts to add to races already there
  checked={ok:true,series:pl.sid,newRaces:new Set(fresh.map(o=>o.id)),newStarts:new Set(fresh.flatMap(o=>o.starts.map(s=>s.id))),
    starts:new Set(races.flatMap(o=>o.starts.map(s=>o.id+'|'+s.id))),addStarts:new Set(added.map(x=>x.o.id+'|'+x.s.id))};
  try{
    // 1. the record, with the ids about to be created, before anything is created: a repeat finds them by id
    if(fresh.length||added.length){
      try{await P.save(pl.day,recordOf(pl,'sending',s=>s.created?'':(s.oldHash||'')));}
      catch(e){said.className='status err';said.textContent='Nothing sent: the record of the send could not be saved first: '+errText(e)+(e&&e.text?' ('+e.text+')':'');return;}}
    // 2. the new races, with their starts
    if(fresh.length){
      try{await ssWrite('races','/series/'+pl.sid+'/races',{races:fresh.map(o=>({id:o.id,date:pl.day,starts:o.starts.map(s=>({id:s.id,fleetIds:s.fleets,startTime:hm(s.time)}))}))},sendId+':races');
        fresh.forEach(o=>{o.ok=true;line('Race '+o.race+': created, with '+o.starts.length+' start'+(o.starts.length>1?'s':'')+'.',true);});}
      catch(e){fresh.forEach(o=>line('Race '+o.race+': not created: '+e.message,false));}}
    // 3. starts already in Sail Scoring: a fleet moving between two starts leaves the one first (a fleet starts once per race)
    for(const o of races.filter(o=>!o.fresh)){
      const ch=o.starts.filter(s=>!s.added&&(s.fleetsChange||s.timeChange));
      for(const s of ch){const gone=s.cur.filter(f=>!s.fleets.includes(f));
        if(gone.length&&o.starts.some(q=>q!==s&&!q.added&&gone.some(f=>q.fleets.includes(f)))){
          try{await ssWrite('start','/races/'+o.id+'/starts/'+s.id,{fleetIds:s.cur.filter(f=>s.fleets.includes(f))},sendId+':leave:'+s.id);}
          catch(e){s.fail='Race '+o.race+', Start '+s.start+': classes not changed: '+e.message;}}}
      for(const s of ch){if(s.fail){line(s.fail,false);continue;}
        const body={};if(s.fleetsChange)body.fleetIds=s.fleets;if(s.timeChange)body.startTime=hm(s.time);
        try{await ssWrite('start','/races/'+o.id+'/starts/'+s.id,body,sendId+':start:'+s.id);
          line('Race '+o.race+', Start '+s.start+': '+[s.fleetsChange&&'classes',s.timeChange&&'gun time'].filter(Boolean).join(' and ')+' done.',true);}
        catch(e){s.fail=1;line('Race '+o.race+', Start '+s.start+': '+[s.fleetsChange&&'classes',s.timeChange&&'gun time'].filter(Boolean).join(' and ')+' failed: '+e.message,false);}}}
    // 4. starts added to races already in Sail Scoring, after any fleet has left its old start (a fleet starts once per race)
    for(const{o,s}of added){
      const src=s.fromId&&o.starts.find(q=>q.id===s.fromId);
      if(src&&src.fail){line('Race '+o.race+', Start '+s.start+': not added: its classes could not be taken off Sail Scoring\'s start first.',false);continue;}
      try{await ssWrite('add','/races/'+o.id+'/starts',{id:s.id,fleetIds:s.fleets,startTime:hm(s.time)},sendId+':add:'+s.id);
        s.ok=true;line('Race '+o.race+', Start '+s.start+': added.',true);}
      catch(e){line('Race '+o.race+', Start '+s.start+': not added: '+e.message,false);}}
    // 5. the courses
    for(const o of races){if(o.fresh&&!o.ok)continue;
      for(const s of o.starts){if(s.added&&!s.ok)continue;
        if(!s.courseChange){done.set(s.id,s.oldHash);continue;}
        try{await ssWrite('course','/races/'+o.id+'/starts/'+s.id+'/course?replace=true',s.doc,sendId+':course:'+s.id);
          done.set(s.id,s.hash);line('Race '+o.race+', Start '+s.start+': course done.',true);}
        catch(e){line('Race '+o.race+', Start '+s.start+': course failed: '+e.message,false);}}}
  }finally{checked=null;}
  // 6. the record again: what Sail Scoring now holds; a failed part is sent again by the next send
  try{await P.save(pl.day,recordOf(pl,'sent',s=>done.has(s.id)?done.get(s.id)||'':(s.created?'':(s.oldHash||''))));
    said.className='status ok';said.textContent='Sent to '+pl.ser.name+'. Review again to check: a repeat sends only what is still different.';}
  catch(e){said.className='status err';said.textContent='Sent, but the record of the send could not be saved: '+errText(e)+(e&&e.text?' ('+e.text+')':'')+'. Send again: nothing is doubled.';}
  plan=null;$('ssSendSeries').value='';$('ssReviewBtn').disabled=true;$('ssReviewCancel').disabled=false;$('ssReviewCancel').textContent='Close';}

/* ---------- connect, the return, disconnect ---------- */
async function connect(){
  if(location.origin+location.pathname.replace(/index\.html$/,'')!==REDIRECT_URI){
    say('Not connecting: Sail Scoring would send the sign-in back to '+REDIRECT_URI+', not to this copy of the page.','err');return;}
  if(!(window.crypto&&crypto.subtle)){say('Not connecting: this browser cannot make the PKCE code here.','err');return;}
  const verifier=b64url(crypto.getRandomValues(new Uint8Array(32)));
  const state=b64url(crypto.getRandomValues(new Uint8Array(16)));
  const challenge=b64url(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(verifier))));
  try{sessionStorage.setItem(AUTH,JSON.stringify({state,verifier,day:raceDay(),at:Date.now()}));
    if(JSON.parse(sessionStorage.getItem(AUTH)||'null').state!==state)throw new Error();}
  catch(_){say('Not connecting: this tab would not keep the sign-in details (session storage refused).','err');return;}
  const q={response_type:'code',client_id:CLIENT_ID,redirect_uri:REDIRECT_URI,scope:SCOPES,state,code_challenge:challenge,code_challenge_method:'S256'};
  location.assign(AUTHORIZE+'?'+Object.keys(q).map(k=>k+'='+encodeURIComponent(q[k])).join('&'));}

// back from Sail Scoring (?code=&state= or ?error=&state=): checked, exchanged, the address cleaned, the race day reopened
async function handleReturn(){
  const p=new URLSearchParams(location.search);
  if(!p.has('state')||!(p.has('code')||p.has('error')))return;
  let saved=null, ok=false;
  try{saved=JSON.parse(sessionStorage.getItem(AUTH)||'null');sessionStorage.removeItem(AUTH);}catch(_){}   // used once only
  panel.open=true;
  try{
    if(!saved||typeof saved.state!=='string'||p.get('state')!==saved.state){
      say('Not connected: the reply from Sail Scoring does not match a sign-in started in this tab. Nothing was exchanged.','err');return;}
    if(p.has('error')){say('Sail Scoring did not connect: '+p.get('error')+(p.get('error_description')?': '+p.get('error_description'):''),'err');return;}
    if(p.has('iss')&&p.get('iss')!==ISSUER){say('Not connected: the reply names '+p.get('iss')+' as its issuer, not '+ISSUER+'. Nothing was exchanged.','err');return;}
    say('Connecting to Sail Scoring…','');
    let r;
    try{r=await tokenPost(TOKEN,{grant_type:'authorization_code',code:p.get('code'),redirect_uri:REDIRECT_URI,client_id:CLIENT_ID,code_verifier:saved.verifier});}
    catch(e){say('Not connected: the browser refused the token exchange. Nothing was saved.','err','Error: '+e.message);return;}
    if(!r.ok){say('Not connected: Sail Scoring refused the token exchange: '+refusal(r),'err');return;}
    let t;
    try{t=fromTokenAnswer(r.body);clearTokens();saveTokens(PENDING,t);}   // the refresh token is kept before the access token is used
    catch(e){clearTokens();say('Not connected: '+e.message,'err');return;}
    try{
      const ws=await ssApi('GET','/workspaces',t.access), w=ws&&Array.isArray(ws.workspaces)&&ws.workspaces[0];
      if(w){t.workspace={id:w.id,slug:w.slug,name:w.name};saveTokens(String(w.slug||w.id),t);
        localStorage.removeItem(STORE+'sailscoring|'+CLIENT_ID+'|tokens|'+PENDING);}
    }catch(e){say('Connected, but the workspace could not be read: '+e.message,'err');}
    ok=true;
  }finally{
    history.replaceState(history.state,'',location.pathname+location.hash);
    const d=dayBox();
    if(saved&&saved.day&&d&&d.value!==saved.day){d.value=saved.day;d.dispatchEvent(new Event('change',{bubbles:true}));}
    if(ok&&readTokens()){showConnected(true);loadAll();}}}

async function disconnect(){
  say('Disconnecting…','');
  let note='';
  try{
    await withLock(async()=>{
      const t=readTokens();
      if(t){const tok=t.refresh||t.access;
        try{const r=await tokenPost(REVOKE,{token:tok,token_type_hint:t.refresh?'refresh_token':'access_token',client_id:CLIENT_ID});
          if(!r.ok)note='Sail Scoring did not confirm the revoke: '+refusal(r);}
        catch(e){note='The revoke could not be confirmed: '+e.message;}}
      clearTokens();});
  }catch(e){clearTokens();note=e.message;}
  showConnected(false);
  say('Disconnected from Sail Scoring.','',note);}

$('ssConnect').onclick=()=>{connect().catch(fail);};
$('ssDisconnect').onclick=()=>{disconnect();};
$('ssReload').onclick=()=>{loadAll();};
$('ssSeries').onchange=()=>{loadSeries($('ssSeries').value);};
$('ssUseClasses').onclick=()=>{useClasses();};
$('ssSendSeries').onchange=()=>{hideReview();$('ssReviewBtn').disabled=!$('ssSendSeries').value;};
$('ssReviewBtn').onclick=()=>{review().catch(fail);};
$('ssClassRemove').onclick=()=>{removeClasses();};
document.addEventListener('course-class-list',showClassState);
if(dayBox())dayBox().addEventListener('change',()=>{showRaces();hideReview();});
// read only when the panel is opened, so a closed panel sends nothing
panel.addEventListener('toggle',()=>{if(panel.open&&readTokens()&&!series)loadAll();});
showConnected(!!readTokens());
showClassState();
say(readTokens()?'Connected to Sail Scoring. Open this panel to read it.':'Not connected.','');
handleReturn().catch(fail);
})();
