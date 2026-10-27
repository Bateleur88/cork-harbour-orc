/* Sail Scoring connection, Stage 1: read-only, TEST COPY ONLY (Pat, 27 October 2026).
   scripts/build_test.py adds this file to the test page (/course-test/) and nowhere else: the live page never loads it, and
   pages/course/course_v8.html does not name it. It adds the closed "Sail Scoring (test)" panel at the foot of the page and
   touches nothing else on it, apart from putting the Race day box back after the sign-in (as the RO would set it by hand).

   The page is a public OAuth client of Sail Scoring's authenticated public API (no secret): authorization code with PKCE
   (S256) and a random state checked on return. The redirect address is a fixed constant, never built from location.href,
   because the page is often opened with ?v=. The code is exchanged at the token endpoint from the browser; if the browser
   refuses that (CORS or anything else), the exact error is shown and nothing more is tried: no relay, no proxy.

   Read-only: every API call goes through ssApi, which refuses any method but GET. The only other requests are to the token
   endpoint (the code exchange and the refresh) and to the revoke endpoint (Disconnect), all through tokenPost.

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
   fleet ids, names and scoring systems, the series and the time: no tokens. */
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
  '<p class="cardnote">Test of the Sail Scoring connection. Nothing is ever sent to Sail Scoring. A class list saved here sets the classes the class box offers on every device.</p>'+
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
  say('Disconnected','',note);}

$('ssConnect').onclick=()=>{connect().catch(fail);};
$('ssDisconnect').onclick=()=>{disconnect();};
$('ssReload').onclick=()=>{loadAll();};
$('ssSeries').onchange=()=>{loadSeries($('ssSeries').value);};
$('ssUseClasses').onclick=()=>{useClasses();};
$('ssClassRemove').onclick=()=>{removeClasses();};
document.addEventListener('course-class-list',showClassState);
if(dayBox())dayBox().addEventListener('change',showRaces);
// read only when the panel is opened, so a closed panel sends nothing
panel.addEventListener('toggle',()=>{if(panel.open&&readTokens()&&!series)loadAll();});
showConnected(!!readTokens());
showClassState();
say(readTokens()?'Connected to Sail Scoring. Open this panel to read it.':'Not connected.','');
handleReturn().catch(fail);
})();
