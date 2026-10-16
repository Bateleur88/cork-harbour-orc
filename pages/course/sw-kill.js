/* Kill switch for the course page's service worker (STATUS A65). Upload this file AS sw.js in the page's folder
   (/course/sw.js, or /course-test/sw.js for the test copy), replacing the real one; do not just delete sw.js (a missing
   sw.js leaves the installed worker running). When a device next opens the page with signal, its browser finds the
   changed sw.js, installs this, and this deletes this folder's saved copies ("coursepage|<folder>|…", never another
   folder's and never the RIB page's) and unregisters itself: the page then loads from the network as it did before
   there was a worker. A page that registers sw.js on opening installs this again, and it removes itself again at once. */
const PAGE_PATH=new URL('./',location.href).pathname;
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil((async()=>{
  for(const k of await caches.keys()){const p=k.split('|');if(p.length===3&&p[0]==='coursepage'&&p[1]===PAGE_PATH)await caches.delete(k);}
  await self.registration.unregister();
})()));
