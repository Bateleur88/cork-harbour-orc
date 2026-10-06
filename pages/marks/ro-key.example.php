<?php
/* RO key for marks.php: only review decision writes (the scoring record) need it, sent by the RO page in the
   X-RO-Key header. Fixes, courses and the series name stay on the race key in key.js.
   Place a copy on the server as data/ro-key.php, in the data folder next to marks.php (not next to marks.php itself),
   with CHANGE_ME replaced by the RO key: 16 to 64 characters, letters, digits, - or _ only, no spaces or quote marks.
   marks.php reads this file as text and never runs it; web access to data/ is denied by its .htaccess.
   While the file is missing, malformed or still holds CHANGE_ME, every decision write is refused with
   "RO key not set on the server". Never commit or share the real file: the repository is public, and backups of
   data/ contain it, so keep them outside the repository. */
return 'CHANGE_ME';
