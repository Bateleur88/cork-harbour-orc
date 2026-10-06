<?php
/*
 * Laid-mark and course store for the RIB record page and the RO course page.
 * Marks go in data/marks-YYYY-MM-DD.json, built courses in data/courses-YYYY-MM-DD.json.
 * The series name, one for the whole series and set from the RO page, goes in data/series.json. Fixes no longer
 * carry a series: a "series" sent by a page not yet reloaded is ignored, never a reason to refuse the fix.
 * Courses are keyed race|start; each race's start groups are _starts|race. The older day-wide _starts
 * (one set of groups for every race of the day) is still accepted, from pages not yet reloaded.
 * Upload it as /marks/marks.php. It creates a "data" folder next to itself.
 * The race key is not in this file or the repository. It is read from key.js next to this file, the same
 * file both pages load, so the key is set in one place. Copy key.example.js to key.js, set the key, and
 * upload it with this file. Without a usable key.js every request is refused.
 * Written to run on old and new PHP alike (5.3 upwards).
 *
 * Fixes from the RIB page also carry "device" (a random id per phone) and "recorder" (an optional
 * typed name, may be ""). Older fixes, and fixes added from the RO page, have neither: read a
 * missing field as unattributed. Neither field is ever a reason to refuse a fix.
 * Fixes from the RIB page also carry "tap": when the Record button was tapped (ms, the phone's clock),
 * so the age of the position ("time", the position's own time) can be measured exactly. Older fixes and
 * the RO page's have none. A tap that is not a number within a day of "time" is dropped, never refused.
 *
 * Course history: before a course save replaces a version, the replaced version is kept in
 * data/courses-history-YYYY-MM-DD.json (never inside the courses file, which old pages read key by key): per race|start
 * (and _starts|race) the first version of the day and the last HISTORY_KEEP replaced versions, the whole file capped at
 * HISTORY_MAX_BYTES (oldest non-first versions dropped first). A save identical to the current version writes nothing.
 * A course save may carry "by", an optional name (text, cut to 40 characters), stored with that version; old pages send
 * none and an older marks.php ignores it. Read with GET ?type=coursehistory&date= and the race key.
 *
 * Review decisions (the scoring record: use-as, do-not-use, accept, revoke) go in data/decisions-YYYY-MM-DD.json,
 * append-only, keyed by the record id the page makes, at most MAX_DECISIONS a day. They are WRITTEN only with the RO key,
 * sent in the X-RO-Key header and read as text from data/ro-key.php (never run, never taken from the URL), and READ with
 * GET ?type=decisions&date= and the race key. key.js is public, so names and notes in decisions are effectively readable
 * by anyone with the race key: no personal details in notes.
 */
function race_key() {                 // '' if key.js is missing, unreadable, too short or still the placeholder
  $f = dirname(__FILE__) . '/key.js';
  $s = is_file($f) ? @file_get_contents($f) : false;
  if ($s === false || !preg_match("/RACE_KEY\\s*=\\s*'([^'\\\\]{6,})'/", $s, $m) || $m[1] === 'CHANGE_ME') return '';
  return $m[1];
}
define('RACE_KEY', race_key());
define('MAX_FIXES', 2000);            // per day, stops runaway files
define('MAX_DECISIONS', 2000);        // review decisions per day
define('HISTORY_KEEP', 5);            // replaced course versions kept per race|start, besides the first of the day
define('HISTORY_MAX_BYTES', 5242880); // the whole history file, 5 MB
define('NAME_MAX', 40);               // "by" on a course save and "who" on a decision, in characters
define('NOTE_MAX', 200);              // a decision's note, in characters
/* The RO key, for decision writes only: data/ro-key.php, read as TEXT (never run), holding exactly one
   return '...'; with 16-64 letters, digits, - or _. '' if missing, unreadable, malformed or still CHANGE_ME.
   Web access to data/ is denied by its .htaccess, and a PHP file prints nothing even if it were fetched. */
function ro_key() {
  $f = dirname(__FILE__) . '/data/ro-key.php';
  $s = is_file($f) ? @file_get_contents($f) : false;
  if ($s === false || strpos(ltrim($s), '<?php') !== 0) return '';
  if (preg_match_all("/\\breturn\\s*'([^'\\\\]*)'\\s*;/", $s, $m) !== 1) return '';
  $k = $m[1][0];
  if ($k === 'CHANGE_ME' || !preg_match('/^[A-Za-z0-9_-]{16,64}$/D', $k)) return '';
  return $k;
}
function name_text($v, $max) {        // one line of text, at most $max characters; null if not valid UTF-8 text
  if (!is_string($v)) return null;
  $v = preg_replace('/\s+/u', ' ', trim($v));
  if (!is_string($v) || preg_match('/[\x00-\x1f\x7f<>]/', $v)) return null;
  return preg_match('/^.{0,' . (int)$max . '}\z/us', $v) ? $v : null;
}

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function out($code, $data) {
  if (function_exists('http_response_code')) http_response_code($code);
  else header('X-Status: ' . $code, true, $code);
  echo json_encode($data);
  exit;
}
function arg($arr, $k, $def) { return (is_array($arr) && isset($arr[$k])) ? $arr[$k] : $def; }
function same($a, $b) {               // constant-time compare, also on PHP 5.3-5.5 (no hash_equals before 5.6)
  if (function_exists('hash_equals')) return hash_equals($a, $b);
  if (strlen($a) !== strlen($b)) return false;
  $r = 0;
  for ($i = 0, $n = strlen($a); $i < $n; $i++) $r |= ord($a[$i]) ^ ord($b[$i]);
  return $r === 0;
}
function valid_date($d) { return is_string($d) && preg_match('/^\d{4}-\d{2}-\d{2}$/', $d); }

/* ---------- safe writes ----------
   A day file is never rewritten in place. The new contents go to a .tmp file, which is renamed over the
   old one only once fully written, so a failed encode or an interrupted write leaves yesterday's file whole.
   Writers lock a separate file, because the lock on a renamed-over file would no longer guard anything.
   Locks are released when the request ends, including through out(). */
function lock_data($dir) {
  $lh = @fopen($dir . '/.write.lock', 'c');
  if (!$lh || !flock($lh, LOCK_EX)) out(500, array('ok' => false, 'error' => 'cannot lock data folder'));
  return $lh;
}
function load_json($f) {             // an unreadable file stops the write rather than being replaced
  if (!file_exists($f)) return array();
  $raw = @file_get_contents($f);
  if ($raw === false) out(500, array('ok' => false, 'error' => 'cannot read ' . basename($f)));
  if (trim($raw) === '') return array();
  $j = json_decode($raw, true);
  if (!is_array($j)) out(500, array('ok' => false, 'error' => basename($f) . ' is damaged, not overwritten'));
  return $j;
}
function save_json($f, $data) {
  $json = json_encode((object)$data);
  if (!is_string($json)) out(500, array('ok' => false, 'error' => 'could not encode, nothing written'));
  $tmp = $f . '.tmp';
  $th  = @fopen($tmp, 'wb');
  $ok  = $th && fwrite($th, $json) === strlen($json) && fflush($th);
  if ($ok && function_exists('fsync')) $ok = fsync($th);      // PHP 8.1+
  if ($th) fclose($th);
  if (!$ok || !@rename($tmp, $f)) { @unlink($tmp); out(500, array('ok' => false, 'error' => 'could not write, ' . basename($f) . ' unchanged')); }
}

/* the history file kept under HISTORY_MAX_BYTES: the oldest version that is not a first of the day goes first */
function history_cap(&$h) {
  while (strlen(json_encode((object)$h)) > HISTORY_MAX_BYTES) {
    $bk = null; $bi = 0; $bt = 0;
    foreach ($h as $k => $list) for ($i = 1, $n = count($list); $i < $n; $i++) {
      $t = (int)arg($list[$i], 'replaced', 0);
      if ($bk === null || $t < $bt) { $bk = $k; $bi = $i; $bt = $t; }
    }
    if ($bk === null) return;
    array_splice($h[$bk], $bi, 1);
  }
}
function bad_decision($why) { out(400, array('ok' => false, 'error' => 'bad decision: ' . $why)); }
function ref_ok($v) { return is_string($v) && preg_match('/^[sl]:[A-Za-z0-9|_. -]{1,80}$/D', $v); }
function int_field($r, $k, $lo, $hi) { $v = arg($r, $k, null); if (!is_int($v) || $v < $lo || $v > $hi) bad_decision($k); return $v; }
/* A review record as the page sends it, checked field by field; anything malformed is refused with 400 and nothing is
   written. Shapes (any other field is refused):
     use-as      id ref race start role from who [client_when] [note]
                 from: for cb, pin, fcb, fpin the line end replaced ('auto', 'none' or a fix ref); for windward, leeward,
                 gybe the course rows replaced, [{row, ref}, ...] (1 to 100)
     accept      id ref race start role who [client_when] [note]
     do-not-use  id ref who note [race start] [client_when]   (the fix for the whole day; note is the reason; race and
                 start, if sent, only say where it was decided)
     revoke      id ref revokes who [client_when] [note]       (race, start and role are copied from the record undone)
   who and note may not contain < or > (refused, "bad decision: who" or "bad decision: note"). from is what the page
   says it replaced: only its format is checked. The server adds when (its own time, the one that counts) and series
   (from series.json). */
function decision_record($r) {
  if (!is_array($r) || !count($r) || array_values($r) === $r) bad_decision('not a record');
  $a = arg($r, 'action', '');
  $allowed = array('use-as' => array('id', 'ref', 'action', 'race', 'start', 'role', 'from', 'who', 'client_when', 'note'),
                   'accept' => array('id', 'ref', 'action', 'race', 'start', 'role', 'who', 'client_when', 'note'),
                   'do-not-use' => array('id', 'ref', 'action', 'race', 'start', 'who', 'client_when', 'note'),
                   'revoke' => array('id', 'ref', 'action', 'revokes', 'who', 'client_when', 'note'));
  if (!is_string($a) || !isset($allowed[$a])) bad_decision('action');
  foreach ($r as $k => $v) if (!in_array($k, $allowed[$a], true)) bad_decision('field ' . $k);
  $o = array('id' => arg($r, 'id', null), 'ref' => arg($r, 'ref', null), 'action' => $a);
  if (!is_string($o['id']) || !preg_match('/^[A-Za-z0-9]{8,40}$/D', $o['id'])) bad_decision('id');
  if (!is_string($o['ref']) || !preg_match('/^s:[A-Za-z0-9]{4,40}$/D', $o['ref'])) bad_decision('ref');
  if ($a === 'use-as' || $a === 'accept' || ($a === 'do-not-use' && (array_key_exists('race', $r) || array_key_exists('start', $r)))) {
    $o['race'] = int_field($r, 'race', 1, 9);
    $o['start'] = int_field($r, 'start', 0, 9);
  }
  if ($a === 'use-as' || $a === 'accept') {
    $o['role'] = arg($r, 'role', null);
    if (!in_array($o['role'], array('cb', 'pin', 'fcb', 'fpin', 'windward', 'leeward', 'gybe'), true)) bad_decision('role');
  }
  if ($a === 'use-as') {
    $f = arg($r, 'from', null);
    if (in_array($o['role'], array('cb', 'pin', 'fcb', 'fpin'), true)) {
      if (!($f === 'auto' || $f === 'none' || ref_ok($f))) bad_decision('from');
    } else {
      if (!is_array($f) || array_values($f) !== $f || count($f) < 1 || count($f) > 100) bad_decision('from');
      foreach ($f as $row) {
        if (!is_array($row) || count($row) !== 2 || !isset($row['row'], $row['ref'])
            || !is_int($row['row']) || $row['row'] < 0 || $row['row'] > 99 || !ref_ok($row['ref'])) bad_decision('from');
      }
    }
    $o['from'] = $f;
  }
  if ($a === 'revoke') {
    $o['revokes'] = arg($r, 'revokes', null);
    if (!is_string($o['revokes']) || !preg_match('/^[A-Za-z0-9]{8,40}$/D', $o['revokes']) || $o['revokes'] === $o['id']) bad_decision('revokes');
  }
  $o['who'] = name_text(arg($r, 'who', null), NAME_MAX);
  if ($o['who'] === null || $o['who'] === '') bad_decision('who');
  if (array_key_exists('client_when', $r)) {
    $cw = $r['client_when'];
    if (!(is_int($cw) || is_float($cw)) || $cw <= 0 || $cw > 1e14) bad_decision('client_when');
    $o['client_when'] = $cw;
  }
  if (array_key_exists('note', $r) || $a === 'do-not-use') {
    $n = arg($r, 'note', null);
    if (!is_string($n) || preg_match('/[\x00-\x09\x0b-\x1f\x7f<>]/', $n) || !preg_match('/^.{0,' . NOTE_MAX . '}\z/us', $n)) bad_decision('note');
    if ($a === 'do-not-use' && trim($n) === '') bad_decision('note: the reason is required for do-not-use');
    $o['note'] = $n;
  }
  return $o;
}

if (RACE_KEY === '') out(500, array('ok' => false, 'error' => 'server key not configured'));   // never compare '' with ''
$key = arg($_SERVER, 'HTTP_X_RACE_KEY', arg($_GET, 'key', ''));
if (!is_string($key) || !same(RACE_KEY, $key)) out(403, array('ok' => false, 'error' => 'bad key'));

$dir = dirname(__FILE__) . '/data';
if (!is_dir($dir) && !@mkdir($dir, 0755, true)) out(500, array('ok' => false, 'error' => 'cannot create data folder'));
if (!is_writable($dir)) out(500, array('ok' => false, 'error' => 'data folder not writable'));
if (!file_exists($dir . '/.htaccess')) {
  @file_put_contents($dir . '/.htaccess',
    "<IfModule mod_authz_core.c>\n  Require all denied\n</IfModule>\n<IfModule !mod_authz_core.c>\n  Deny from all\n</IfModule>\n");
}

/* ---------- GET: all fixes (or all built courses) for a day ---------- */
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
  if (arg($_GET, 'type', '') === 'series') {
    $f = $dir . '/series.json';
    $s = array();
    if (file_exists($f)) { $j = json_decode(file_get_contents($f), true); if (is_array($j)) $s = $j; }
    out(200, array('ok' => true, 'name' => (string)arg($s, 'name', ''), 'updated' => (int)arg($s, 'updated', 0)));
  }
  $d = arg($_GET, 'date', '');
  if (!valid_date($d)) out(400, array('ok' => false, 'error' => 'bad date'));
  if (arg($_GET, 'type', '') === 'coursehistory') {
    $f = $dir . '/courses-history-' . $d . '.json';
    $h = array();
    if (file_exists($f)) { $j = json_decode(file_get_contents($f), true); if (is_array($j)) $h = $j; }
    out(200, array('ok' => true, 'date' => $d, 'history' => (object)$h));
  }
  if (arg($_GET, 'type', '') === 'decisions') {
    $f = $dir . '/decisions-' . $d . '.json';
    $r = array();
    if (file_exists($f)) { $j = json_decode(file_get_contents($f), true); if (is_array($j)) $r = $j; }
    out(200, array('ok' => true, 'date' => $d, 'decisions' => array_values($r)));
  }
  if (arg($_GET, 'type', '') === 'courses') {
    $f = $dir . '/courses-' . $d . '.json';
    $c = array();
    if (file_exists($f)) { $j = json_decode(file_get_contents($f), true); if (is_array($j)) $c = $j; }
    out(200, array('ok' => true, 'date' => $d, 'courses' => (object)$c));
  }
  $f = $dir . '/marks-' . $d . '.json';
  $marks = array();
  if (file_exists($f)) { $j = json_decode(file_get_contents($f), true); if (is_array($j)) $marks = $j; }
  out(200, array('ok' => true, 'date' => $d, 'marks' => array_values($marks)));
}

/* ---------- POST: add or delete one fix ---------- */
if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, array('ok' => false, 'error' => 'method'));
$in = json_decode(file_get_contents('php://input'), true);
if (!is_array($in)) out(400, array('ok' => false, 'error' => 'bad body'));

$action = arg($in, 'action', 'add');

/* ---------- POST action "series": the series name, one for the whole series; "" clears it ---------- */
if ($action === 'series') {
  $name = arg($in, 'name', null);
  if (!is_string($name)) out(400, array('ok' => false, 'error' => 'bad series'));
  $name = preg_replace('/\s+/u', ' ', trim(strip_tags($name)));    // null if not valid UTF-8
  if (!is_string($name)) out(400, array('ok' => false, 'error' => 'bad series'));
  if (!preg_match('/^.{0,60}\z/us', $name)) out(400, array('ok' => false, 'error' => 'series name too long'));
  $lh = lock_data($dir);
  save_json($dir . '/series.json', array('name' => $name, 'updated' => time()));
  flock($lh, LOCK_UN); fclose($lh);
  out(200, array('ok' => true, 'name' => $name));
}

$d      = arg($in, 'date', '');
$id     = arg($in, 'id', '');
if (!valid_date($d)) out(400, array('ok' => false, 'error' => 'bad date'));

/* ---------- POST action "course": save one built course (race|start) or one race's start groups (_starts|race) ---------- */
if ($action === 'course') {
  $k    = arg($in, 'key', '');
  $data = arg($in, 'data', null);
  if (!is_string($k) || !preg_match('/^(\d{1,2}\|\d{1,2}|_starts(\|[1-9])?)$/D', $k)) out(400, array('ok' => false, 'error' => 'bad course name'));
  if (!is_array($data) || strlen(json_encode($data)) > 50000) out(400, array('ok' => false, 'error' => 'bad course'));
  $by = name_text(arg($in, 'by', null), 10000);     // optional: who saved this version; cut to NAME_MAX, else dropped
  $by = ($by !== null && preg_match('/^.{0,' . NAME_MAX . '}/us', $by, $mm)) ? trim($mm[0]) : '';
  $f  = $dir . '/courses-' . $d . '.json';
  $hf = $dir . '/courses-history-' . $d . '.json';
  $lh = lock_data($dir);
  $c  = load_json($f);
  if (!isset($c[$k]) && count($c) >= 200) out(429, array('ok' => false, 'error' => 'too many courses'));
  $old = (isset($c[$k]) && is_array($c[$k])) ? $c[$k] : null;
  if ($old !== null && json_encode(arg($old, 'data', null)) === json_encode($data)) {   // nothing changed: nothing written
    flock($lh, LOCK_UN); fclose($lh);
    out(200, array('ok' => true, 'unchanged' => true));
  }
  if ($old !== null) {
    // the version being replaced goes into the history FIRST; if that cannot be written (damaged history file, failed
    // write) load_json/save_json stop here with 500 and the course is not saved either, so a course is never replaced
    // without its earlier version being kept
    $h = load_json($hf);
    $list = (isset($h[$k]) && is_array($h[$k])) ? array_values($h[$k]) : array();
    $last = count($list) ? $list[count($list) - 1] : null;
    if (!$last || json_encode(arg($last, 'data', null)) !== json_encode(arg($old, 'data', null))) {   // not twice in a row
      $e = array('data' => arg($old, 'data', null), 'updated' => (int)arg($old, 'updated', 0), 'replaced' => time());
      if (isset($old['by']) && is_string($old['by']) && $old['by'] !== '') $e['by'] = $old['by'];
      if ($by !== '') $e['replaced_by'] = $by;
      $list[] = $e;
      if (count($list) > 1 + HISTORY_KEEP) $list = array_merge(array($list[0]), array_slice($list, -HISTORY_KEEP));
      $h[$k] = $list;
      history_cap($h);
      save_json($hf, $h);
    }
  }
  $rec = array('data' => $data, 'updated' => time());
  if ($by !== '') $rec['by'] = $by;
  $c[$k] = $rec;
  save_json($f, $c);
  flock($lh, LOCK_UN); fclose($lh);
  out(200, array('ok' => true));
}

/* ---------- POST action "decision": one review record, append-only, with the RO key ---------- */
if ($action === 'decision') {
  $rk = ro_key();
  if ($rk === '') out(403, array('ok' => false, 'error' => 'RO key not set on the server (data/ro-key.php: 16-64 letters, digits, - or _)'));
  $hk = arg($_SERVER, 'HTTP_X_RO_KEY', '');                 // the header only, never a URL parameter
  if (!is_string($hk) || !same($rk, $hk)) out(403, array('ok' => false, 'error' => 'bad RO key'));
  $rec = decision_record(arg($in, 'record', null));        // refuses anything malformed with 400, before any write
  $f   = $dir . '/decisions-' . $d . '.json';
  $lh  = lock_data($dir);
  $all = load_json($f);
  if (isset($all[$rec['id']])) {                           // a retry of the same record: nothing written
    $prev = $all[$rec['id']];
    unset($prev['when'], $prev['series']);
    if ($rec['action'] === 'revoke') unset($prev['race'], $prev['start'], $prev['role']);
    if (json_encode($prev) === json_encode($rec)) { flock($lh, LOCK_UN); fclose($lh); out(200, array('ok' => true, 'duplicate' => true)); }
    out(409, array('ok' => false, 'error' => 'a different record already has this id'));
  }
  if (count($all) >= MAX_DECISIONS) out(429, array('ok' => false, 'error' => 'too many decisions for this day'));
  $marks = load_json($dir . '/marks-' . $d . '.json');
  if (!isset($marks[substr($rec['ref'], 2)])) out(400, array('ok' => false, 'error' => 'no such fix on this day'));
  if ($rec['action'] === 'revoke') {
    $t = isset($all[$rec['revokes']]) ? $all[$rec['revokes']] : null;
    if (!$t || $t['action'] === 'revoke') out(400, array('ok' => false, 'error' => 'nothing to revoke with that id'));
    if ($t['ref'] !== $rec['ref']) out(400, array('ok' => false, 'error' => 'revoke names a different fix'));
    foreach ($all as $x) if (isset($x['revokes']) && $x['revokes'] === $rec['revokes']) out(400, array('ok' => false, 'error' => 'already revoked'));
    foreach (array('race', 'start', 'role') as $f2) if (isset($t[$f2])) $rec[$f2] = $t[$f2];   // what it undoes
  }
  $sj = json_decode((string)@file_get_contents($dir . '/series.json'), true);
  $rec['series'] = is_array($sj) ? (string)arg($sj, 'name', '') : '';
  $rec['when'] = time();
  $all[$rec['id']] = $rec;
  save_json($f, $all);
  flock($lh, LOCK_UN); fclose($lh);
  out(200, array('ok' => true));
}

if (!is_string($id) || !preg_match('/^[a-z0-9]{4,40}$/i', $id)) out(400, array('ok' => false, 'error' => 'bad id'));

$rec = null;
if ($action === 'add') {
  $race = (int)arg($in, 'race', 0);
  $name = trim(strip_tags((string)arg($in, 'name', '')));
  $lat  = (float)arg($in, 'lat', 999);
  $lon  = (float)arg($in, 'lon', 999);
  $acc  = (float)arg($in, 'acc', -1);
  $time = (float)arg($in, 'time', 0);
  if ($race < 1 || $race > 9 || $name === '' || strlen($name) > 80
      || $lat < -90 || $lat > 90 || $lon < -180 || $lon > 180 || $acc < 0 || $acc > 10000 || $time <= 0)
    out(400, array('ok' => false, 'error' => 'bad fix'));
  $rec = array('id' => $id, 'date' => $d, 'race' => $race, 'name' => $name,
               'lat' => round($lat, 7), 'lon' => round($lon, 7), 'acc' => round($acc, 1),
               'time' => $time, 'received' => time());
  // who recorded it: kept only if well formed, otherwise dropped silently
  $dev = arg($in, 'device', null);
  if (is_string($dev) && preg_match('/^[A-Za-z0-9-]{1,64}$/', $dev)) $rec['device'] = $dev;
  $who = arg($in, 'recorder', null);
  if (is_string($who)) {
    $who = trim(strip_tags($who));
    $rec['recorder'] = preg_match('/^.{0,60}/us', $who, $mm) ? trim($mm[0]) : '';   // cut on a character, not a byte
  }
  // when Record was tapped: kept only if a number within a day of the position's time, otherwise dropped silently
  $tap = arg($in, 'tap', null);
  if ((is_int($tap) || is_float($tap)) && $tap > 0 && abs($tap - $time) < 86400000) $rec['tap'] = (float)$tap;
} elseif ($action !== 'delete') {
  out(400, array('ok' => false, 'error' => 'bad action'));
}

$f     = $dir . '/marks-' . $d . '.json';
$lh    = lock_data($dir);
$marks = load_json($f);

if ($action === 'add') {
  if (!isset($marks[$id]) && count($marks) >= MAX_FIXES) out(429, array('ok' => false, 'error' => 'day full'));
  if (isset($marks[$id]) && is_array($marks[$id])) {   // a re-post (the RO page moving a fix to another race) keeps who recorded it, and when
    foreach (array('device', 'recorder', 'tap') as $k)
      if (!isset($rec[$k]) && isset($marks[$id][$k])) $rec[$k] = $marks[$id][$k];
  }
  $marks[$id] = $rec;                 // same id twice (a retry) just overwrites
} else {
  unset($marks[$id]);
}

save_json($f, $marks);
flock($lh, LOCK_UN);
fclose($lh);
out(200, array('ok' => true));
