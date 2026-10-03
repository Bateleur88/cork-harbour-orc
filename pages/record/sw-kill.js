/* Kill switch for the RIB page's service worker. Upload this file AS /record/sw.js, replacing the real one; do not
   just delete sw.js (a missing sw.js leaves the installed worker running). When a phone next opens /record/ with
   signal, its browser finds the changed sw.js, installs this, and this deletes the page's saved copies and unregisters
   itself: the page then loads from the network as it did before there was a worker. The page still registers sw.js on
   every open; while this file is in place, each such worker removes itself again at once. */
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil((async()=>{
  for(const k of await caches.keys())if(k.startsWith('record-'))await caches.delete(k);
  await self.registration.unregister();
})()));
