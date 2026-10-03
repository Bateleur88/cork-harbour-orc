/* Service worker for the RIB page (/record/). A phone that has opened the page once with signal can open it again
   without: the page and /marks/key.js are kept in a cache and used only when the network fails, answers with a server
   error (5xx) or has not answered within 3 seconds. Nothing else is handled: marks.php, the page's version check,
   Google Fonts and every other request go to the network exactly as if there were no worker.
   The saved page is only ever replaced by a response that contains the PAGE_VERSION marker, so an error or
   maintenance page that comes back as 200 is shown but never saved.
   The page registers this file as sw.js?v=PAGE_VERSION, so each page version installs its own worker with its own
   cache, "record-" + the version; a new worker deletes the older ones when it takes over.
   Scope: /record/ only, the folder this file is served from. If it misbehaves, upload sw-kill.js in its place. */
const CACHE='record-'+(new URL(location.href).searchParams.get('v')||'0');
const PAGE=new URL('./',location.href).href, PAGE_PATH=new URL(PAGE).pathname;   // …/record/
const KEY=new URL('/marks/key.js',location.href).href;
const MARK="const PAGE_VERSION='";
const WAIT=3000;
const isPage=async res=>res.ok&&(await res.clone().text()).includes(MARK);

self.addEventListener('install',e=>e.waitUntil((async()=>{
  const c=await caches.open(CACHE), res=await fetch(PAGE,{cache:'reload'});
  if(!await isPage(res))throw new Error('page not saved');           // no copy of the page, no install: the old worker stays
  await c.put(PAGE,res);
  await c.add(new Request(KEY,{cache:'reload'})).catch(()=>{});     // the page also keeps the last key itself
  await self.skipWaiting();
})()));
self.addEventListener('activate',e=>e.waitUntil((async()=>{
  for(const k of await caches.keys())if(k.startsWith('record-')&&k!==CACHE)await caches.delete(k);
  await self.clients.claim();
})()));
self.addEventListener('fetch',e=>{
  const r=e.request, u=new URL(r.url);
  const page=r.mode==='navigate'&&u.origin===location.origin&&(u.pathname===PAGE_PATH||u.pathname===PAGE_PATH+'index.html');
  const key=page?PAGE:(r.method==='GET'&&r.url===KEY?KEY:'');
  if(!key)return;                                                    // not ours: the browser fetches it as normal
  const net=fetch(r).then(async res=>{
    if(res.type==='basic'&&!res.redirected&&(page?await isPage(res):res.ok))await (await caches.open(CACHE)).put(key,res.clone());
    return res;});
  e.waitUntil(net.catch(()=>{}));                                    // an answer after the 3 s still refreshes the copy
  e.respondWith((async()=>{
    let res;
    try{res=await Promise.race([net,new Promise(ok=>setTimeout(ok,WAIT))]);}catch(_){}
    if(res&&res.status<500)return res;                               // answered in time: the network's answer, as without a worker
    return (await caches.match(key,{cacheName:CACHE}))||res||net;    // nothing saved: the server's error, or wait for the network
  })());
});
