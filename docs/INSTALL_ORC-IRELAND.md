# Installing the race tools on orc-ireland.org

For John Kelly. Prepared 16 October 2026 from the versions running on tradboats.ie that day.

This package replaces the old install on orc-ireland.org (course page PAGE_VERSION 2026-09-22.1, never used). It is a clean install: delete every old file first, then upload this package. No backup of the old install is needed.

What you get:

- **Course page** (race officer): `/course/`, PAGE_VERSION 2026-10-06.37.
- **RIB page** (laid-mark recording on the phones): `/record/`, PAGE_VERSION 2026-10-06.1, with its service worker `sw.js`.
- **marks.php**: `/marks/marks.php`, the store both pages read and write.
- **Race data**: three real race days from tradboats.ie, 27 September, 4 October and 11 October 2026, and the series name "Autumn League".

Every file, with its size and SHA-256, is in `MANIFEST.txt`.

This install is separate from tradboats.ie. The two sites share no data: a fix recorded on one never appears on the other.


## The site: what was checked

The package uses the same folder layout as tradboats.ie, at the top of the site, which is also where the old install is:

    https://orc-ireland.org/course/
    https://orc-ireland.org/record/
    https://orc-ireland.org/marks/          (marks.php, key.js, data/)

No rebuild is needed for this layout. Don't edit the files by hand: the pages name `/marks/` directly.

Pat checked orc-ireland.org from his browser on 16 October 2026:

- **HTTPS works.** Phones only give a web page their GPS position over HTTPS, and the RIB page's offline copy (its service worker) works only over HTTPS. Always open the pages with `https://`.
- **nginx in front of Apache, and `.htaccess` is honoured:** `https://orc-ireland.org/marks/data/series.json` returns Apache's 403 Forbidden. `/marks/data/` is protected by its `.htaccess`; Step 15 checks it again after the upload.
- **marks.php answers** (the old install's): `marks.php?date=2026-10-16` returned 200 with `{"ok":true,"date":"2026-10-16","marks":[]}`, not cached (Age 0, Cache-Control: no-store).
- **No Content-Security-Policy header**, so nothing blocks what the course page loads from outside: its map from `unpkg.com` (Leaflet), map tiles from `tile.openstreetmap.de` and `tiles.openseamap.org`, and the font from Google Fonts (both pages). No cross-site (CORS) setting is needed.
- **The host caches pages:** `/course/` came back with Age 6846 (served from the host's cache, almost two hours old). After uploading, clear the site's cache (Step 13).

The site also needs, as on any host:

1. **PHP 5.3 or newer.** marks.php was tested on 16 October 2026 with PHP 8.4.26 and PHP 5.5.38, and every test passed. tradboats.ie runs PHP 5.5.38 on Apache.
2. **PHP can write to `/marks/data/`.** marks.php writes a new file for each race day, and replaces files by writing a `.tmp` file next to them and renaming it. The folder and the files in it must be writable by the user PHP runs as. On most shared hosts that is your FTP user, and folder 755 with files 644 is enough. If saving fails with "data folder not writable", make the folder 775 or ask your host.
3. **File locking.** marks.php locks `data/.write.lock` while it writes, so two phones saving at once never damage a file. Ordinary hosting does this; a data folder on a network share may not.
4. **The `X-Race-Key` header reaches PHP.** Both pages send the key in this header. Step 17 proves it.


## Part A – Delete the old install

Step 1 – On every phone, tablet and PC that has opened the old pages on orc-ireland.org, clear the site's stored data:
- **Chrome on Android:** open `https://orc-ireland.org/`, tap the icon left of the address, then **Site settings**, then **Delete data** (or **Clear & reset**).
- **Chrome on a PC:** open the site, click the icon left of the address, then **Site settings**, then **Delete data**.
- **iPhone (Safari):** Settings, Safari, Advanced, Website Data, find orc-ireland.org and delete it.

You should see: the site's data gone. This removes the old pages' saved copies, any old service worker, any old key kept on the device, and any old course kept on the device, so none of it can reach the new install.

Step 2 – In your FTP program (or the hosting file manager), delete the old files in `/course/`, `/record/` and `/marks/`, including everything in `/marks/data/` and the old `/marks/key.js`. **Keep the folders** `/course/`, `/record/`, `/marks/` and `/marks/data/` themselves. Also delete any other file the old install put on the site, for example a `course_v8.html`, `record.html`, `sw.js` or `ro-key.php` anywhere else.

You should see: the four folders still there, and empty.

Step 3 – Make sure your FTP program shows hidden files (names starting with a dot), then check there is no old `.htaccess` or `.write.lock` left in `/marks/data/`.

You should see: nothing old left.


## Part B – Upload the new files

Upload in **Binary** mode, so nothing changes the line endings. The folder `upload/` in this package is laid out exactly as the site.

Step 4 – Upload `upload/course/index.html` into `/course/`.

Step 5 – Upload `upload/record/index.html` and `upload/record/sw.js` into `/record/`.

Step 6 – Upload `upload/marks/marks.php` into `/marks/`.

Step 7 – Upload the 11 files in `upload/marks/data/` into `/marks/data/`, including the hidden `.htaccess` and `.write.lock`. `.write.lock` is empty (0 bytes); some FTP programs skip empty or hidden files, so check both arrived.

You should see: 11 files in `/marks/data/`, with the sizes in `MANIFEST.txt`.

Step 8 – Make sure `/marks/data/` and its files are writable by PHP (point 2 above).

Step 9 – Download `/course/index.html` back from the server by FTP to a new folder on your PC and check its SHA-256. In PowerShell:

    Get-FileHash C:\path\to\index.html

You should see: `D0D1CF39820A6C7D6122AF664C4C64FB3A53E044687A2D377ACEBD6F743988EB`. Do the same for `/record/index.html`, `/record/sw.js` and `/marks/marks.php` against `MANIFEST.txt`.

Don't upload `spare/sw-kill.js`. It is only for an emergency (see "If the RIB page misbehaves" below).


## Part C – Set your own key

The pages and marks.php share one key, the race key. Only someone whose page has it can save a fix or a course. You choose your own; it is never Pat's tradboats.ie key, and Pat doesn't need to know it.

Step 10 – Choose a key: at least 6 characters, letters and digits only, no spaces or quote marks. Use something long and random, for example 24 letters and digits from a password generator.

Step 11 – Copy `templates/key.example.js` to a new file named `key.js` and open it in a plain text editor (Notepad). Change the last line from

    window.RACE_KEY='CHANGE_ME';

to your key, keeping the quote marks and the semicolon:

    window.RACE_KEY='your-key-here';

Save it as plain text.

Step 12 – Upload `key.js` into `/marks/`, next to marks.php.

Things to know about the key:

- `key.js` is loaded by both pages in the browser, so anyone who opens the pages can read it. It keeps out passers-by and stray requests, not someone determined. Treat it as shared with your race officers, not as a password.
- To change it later, upload a new `key.js` and clear the site's cache (Step 13). Each page reads key.js every time it opens, and again if marks.php refuses the key it has, so devices pick up the new key without being reset.
- While `key.js` is missing, or still says `CHANGE_ME`, marks.php refuses every request ("server key not configured").
- Don't put `key.js` in email or chat threads that others can see, and never commit it to a repository.
- The review-decisions feature and its separate RO key (`ro-key.php`) are not used. Don't install one.


## Part D – Clear the site's cache, then check the version

Do this before anything else. The host keeps copies of pages (Pat saw `/course/` served from the cache almost two hours old), so until the cache is cleared, browsers may be given the old pages, the old `sw.js` or no `key.js`.

Step 13 – Clear the site's cache: in the hosting control panel (the host's cache, for example "Purge cache" or "Clear cache" for nginx or Varnish), and, if the site runs WordPress with a caching plugin, in that plugin too. Clear everything, not only one page.

You should see: the panel or plugin says the cache was cleared.

Step 14 – On a PC, open `https://orc-ireland.org/course/` in a **private window**, press Ctrl+U and search the page source for `PAGE_VERSION`.

You should see: `PAGE_VERSION='2026-10-06.37'` and nearby `MARKS_BASE='/marks/', STORE=''`. If it shows `2026-09-22.1`, or anything else, the cache still holds the old page: repeat Step 13, or ask your host, and don't go on until it shows .37. Close the private window.


## Part E – Checks (nothing is written)

These checks only read. Don't tap anything that is not in the steps.

Step 15 – In a browser, open `https://orc-ireland.org/marks/data/series.json`.

You should see: "403 Forbidden", **not** the text `{"name":"Autumn League",…}`. If you can read the text, stop: the data folder is not protected. Tell your host and Pat before anything else.

Step 16 – Open `https://orc-ireland.org/marks/marks.php`.

You should see: `{"ok":false,"error":"bad key"}`. That means the new marks.php runs and your key.js is in place. If it says "server key not configured", key.js is missing, misnamed, or still has `CHANGE_ME`. If you see PHP code or a download, PHP is not running.

Step 17 – In a normal window, open `https://orc-ireland.org/course/` and press Ctrl+Shift+R. Set **Race day** to 11/10/2026 and tap **Get latest marks**.

You should see: "2 recorded fixes · 1 typed position for Sun 11 Oct 2026 · updated hh:mm". This proves the key reaches marks.php (point 4) and the data is in place. If it says the key was refused, check key.js (Step 11) and clear the cache again (Step 13).

Step 18 – Tap **Race 1**, then **Start 1**.

You should see:
- under the Committee boat list: "Committee boat – estimate: 200 m at 260°M from Start Pin R1 11:09";
- Total **7.62**;
- no "A newer fix", "now available" or "Auto now gives" line.

Step 19 – Tap **Start 2**, then **Start 3**.

You should see: the same committee boat line on each, Total **11.37** for Start 2 and **11.37** for Start 3, and no such line. Race 1 reads 7.62 / 11.37 / 11.37.

Step 20 – Set Race day to 04/10/2026, tap Get latest marks, then Race 1, Start 1.

You should see: "16 recorded fixes for Sun 4 Oct 2026" and Total **5.10**.

Step 21 – Look at the line under Get latest marks.

You should see: no "Saving N course changes held on this device" line. Loading old days on a cleared device writes nothing.

Step 22 – On a phone, open `https://orc-ireland.org/record/` with signal, and allow location when asked.

You should see: "Who's recording?", the Race 1 to 3 buttons, "Record mark here", **no** "Series name" box, and at the foot "© 2026 Pat Tanner ORC Ireland". Don't tap Record mark here: that would save a fix to today's race day.

These checks do not prove that PHP can write to `/marks/data/`. That is first proved by the first real save. If you want to prove it before race day, ask Pat for a test write that can be removed afterwards.


## Part F – Every device, before it is used

Do this on every phone, tablet and PC that you or your race officers will use, with signal:

Step 23 – If the device ever opened the old pages, clear the site's data, as in Step 1. This matters most for the RIB page: if the old RIB page installed a service worker (an offline copy of itself), the phone may keep showing the old page until that copy is removed or the new page has been opened once with signal.

Step 24 – Close every tab of the course page and the RIB page, then open them again from `https://orc-ireland.org/course/` and `https://orc-ireland.org/record/`.

You should see: on the course page, 11 October Race 1 Start 1 reads "Committee boat – estimate: 200 m at 260°M from Start Pin R1 11:09" (Steps 17 and 18). On the RIB page, the "© 2026 Pat Tanner ORC Ireland" footer and no Series name box (Step 22). If not, the device still has an old page: clear the site data again and reopen with signal.


## Race-day precautions (as they stand for course page .37)

1. On the committee boat, don't reload or close the course page while the signal is poor; if it must be reopened, wait for signal first. (The course page cannot yet open with no signal unless the browser has it in its own cache. The RIB page can.)
2. Once a start has gone, don't tap Undo on its start line.
3. Don't tap Remove Start in a race that already has a course; leave an unused start empty (until Remove Start is confirmed in a live race).

Also: glance at the series name at the top of Setup before building the first course of the day. It is one name for every day and every device on this site.


## If the RIB page misbehaves

Upload `spare/sw-kill.js` **as** `/record/sw.js`, replacing the real one, and clear the site's cache (Step 13). Don't just delete `sw.js`: a missing sw.js leaves the installed worker running. When each phone next opens `/record/` with signal, the offline copy is removed and the page loads from the network as normal. To go back, upload the real `upload/record/sw.js` again and clear the cache.


## The race data in this package

From tradboats.ie, as it stood after the 16 October 2026 cleanup (Pat's backup of that day):

- 27 September 2026: `courses-2026-09-27.json`, `marks-2026-09-27.json` (no course history that day)
- 4 October 2026: `courses-2026-10-04.json`, `courses-history-2026-10-04.json`, `marks-2026-10-04.json`
- 11 October 2026: `courses-2026-10-11.json`, `courses-history-2026-10-11.json`, `marks-2026-10-11.json`
- `series.json`: "Autumn League"

The marks files hold the RIB recorders' names as they typed them, and a random id for each phone. Never edit these files by hand: they are the recorded marks, and every course is built from them.
