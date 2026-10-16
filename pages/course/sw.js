/* Service worker for the course page (/course/; STATUS A65). A device that has opened the page once with signal can
   open it again without: the page and its key.js are kept in a cache and used only when the network fails, answers
   with a server error (5xx) or has not answered within 3 seconds. Nothing else is handled: marks.php, the page's
   version check, Google Fonts, Leaflet, map tiles and every other request go to the network exactly as if there were
   no worker.
   Own version only: the page registers this file as sw.js?v=PAGE_VERSION, and this worker keeps a page only if its
   PAGE_VERSION is exactly that version, when installing (from ./?v=<version>) and whenever it refreshes the copy, so
   an older page cached by the host can never become or replace the saved copy.
   A navigation whose ?v= names another version (the page reloading to a newer one it found on the server) waits up to
   10 seconds for the network before the saved copy is used; the page then deals with it.
   Cache names: "coursepage|<folder>|<version>". A new worker deletes only older caches of its own folder, so the live
   copy (/course/) and the test copy (/course-test/) never touch each other's, and no name starts with "record-" (the
   RIB worker deletes those).
   Scope: this folder only. If it misbehaves, upload sw-kill.js in its place. */
const VERSION=new URL(location.href).searchParams.get('v')||'';
const PAGE=new URL('./',location.href).href, PAGE_PATH=new URL(PAGE).pathname;   // …/course/
const KEY=new URL('/marks/key.js',location.href).href;                         // a test build names /marks-test/key.js
const CACHE='coursepage|'+PAGE_PATH+'|'+VERSION;
const WAIT=3000, OTHER_WAIT=10000;
const ownCache=k=>{const p=k.split('|');return p.length===3&&p[0]==='coursepage'&&p[1]===PAGE_PATH;};
// the page, and exactly this worker's version of it
const isOwn=async res=>{if(!res.ok||!VERSION)return false;
  const m=(await res.clone().text()).match(/const PAGE_VERSION='([^']+)'/);return !!m&&m[1]===VERSION;};

self.addEventListener('install',e=>e.waitUntil((async()=>{
  const res=await fetch(PAGE+'?v='+encodeURIComponent(VERSION),{cache:'reload'});
  if(res.type!=='basic'||!await isOwn(res))throw new Error('page not saved');   // not its own version: no install
  const c=await caches.open(CACHE);
  await c.put(PAGE,res);
  await c.add(new Request(KEY,{cache:'reload'})).catch(()=>{});                 // the page also keeps the last key itself
  await self.skipWaiting();
})()));
self.addEventListener('activate',e=>e.waitUntil((async()=>{
  for(const k of await caches.keys())if(ownCache(k)&&k!==CACHE)await caches.delete(k);
  await self.clients.claim();
})()));
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  const u=new URL(r.url);
  const page=r.mode==='navigate'&&u.origin===location.origin&&(u.pathname===PAGE_PATH||u.pathname===PAGE_PATH+'index.html');
  const key=page?PAGE:(r.url===KEY?KEY:'');
  if(!key)return;                                                     // not ours: the browser fetches it as normal
  const v=page?u.searchParams.get('v'):null, wait=v!==null&&v!==VERSION?OTHER_WAIT:WAIT;
  const net=fetch(r).then(async res=>{
    if(res.type==='basic'&&!res.redirected&&(page?await isOwn(res):res.ok))await (await caches.open(CACHE)).put(key,res.clone());
    return res;});
  e.waitUntil(net.catch(()=>{}));                                     // an answer after the wait still refreshes the copy
  e.respondWith((async()=>{
    let res;
    try{res=await Promise.race([net,new Promise(ok=>setTimeout(ok,wait))]);}catch(_){}
    if(res&&res.status<500)return res;                                // answered in time: the network's answer
    return (await caches.match(key,{cacheName:CACHE}))||res||net;     // nothing saved: the server's error, or wait for the network
  })());
});
