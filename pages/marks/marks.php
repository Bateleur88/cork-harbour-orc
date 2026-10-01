<?php
/*
 * Laid-mark and course store for the RIB record page and the RO course page.
 * Marks go in data/marks-YYYY-MM-DD.json, built courses in data/courses-YYYY-MM-DD.json.
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
 */
function race_key() {                 // '' if key.js is missing, unreadable, too short or still the placeholder
  $f = dirname(__FILE__) . '/key.js';
  $s = is_file($f) ? @file_get_contents($f) : false;
  if ($s === false || !preg_match("/RACE_KEY\\s*=\\s*'([^'\\\\]{6,})'/", $s, $m) || $m[1] === 'CHANGE_ME') return '';
  return $m[1];
}
define('RACE_KEY', race_key());
define('MAX_FIXES', 2000);            // per day, stops runaway files

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function out($code, $data) {
  if (function_exists('http_response_code')) http_response_code($code);
  else header('X-Status: ' . $code, true, $code);
  echo json_encode($data);
  exit;
}
function arg($arr, $k, $def) { return (is_array($arr) && isset($arr[$k])) ? $arr[$k] : $def; }
function same($a, $b) { return function_exists('hash_equals') ? hash_equals($a, $b) : ($a === $b); }
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
  $d = arg($_GET, 'date', '');
  if (!valid_date($d)) out(400, array('ok' => false, 'error' => 'bad date'));
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
$d      = arg($in, 'date', '');
$id     = arg($in, 'id', '');
if (!valid_date($d)) out(400, array('ok' => false, 'error' => 'bad date'));

/* ---------- POST action "course": save one built course (race|start) or one race's start groups (_starts|race) ---------- */
if ($action === 'course') {
  $k    = arg($in, 'key', '');
  $data = arg($in, 'data', null);
  if (!is_string($k) || !preg_match('/^(\d{1,2}\|\d{1,2}|_starts(\|[1-9])?)$/D', $k)) out(400, array('ok' => false, 'error' => 'bad course name'));
  if (!is_array($data) || strlen(json_encode($data)) > 50000) out(400, array('ok' => false, 'error' => 'bad course'));
  $f  = $dir . '/courses-' . $d . '.json';
  $lh = lock_data($dir);
  $c  = load_json($f);
  if (!isset($c[$k]) && count($c) >= 200) out(429, array('ok' => false, 'error' => 'too many courses'));
  $c[$k] = array('data' => $data, 'updated' => time());
  save_json($f, $c);
  flock($lh, LOCK_UN); fclose($lh);
  out(200, array('ok' => true));
}

if (!is_string($id) || !preg_match('/^[a-z0-9]{4,40}$/i', $id)) out(400, array('ok' => false, 'error' => 'bad id'));

$rec = null;
if ($action === 'add') {
  $race = (int)arg($in, 'race', 0);
  $name = trim(strip_tags((string)arg($in, 'name', '')));
  $ser  = trim(strip_tags((string)arg($in, 'series', '')));
  $lat  = (float)arg($in, 'lat', 999);
  $lon  = (float)arg($in, 'lon', 999);
  $acc  = (float)arg($in, 'acc', -1);
  $time = (float)arg($in, 'time', 0);
  if ($race < 1 || $race > 9 || $name === '' || strlen($name) > 80 || strlen($ser) > 120
      || $lat < -90 || $lat > 90 || $lon < -180 || $lon > 180 || $acc < 0 || $acc > 10000 || $time <= 0)
    out(400, array('ok' => false, 'error' => 'bad fix'));
  $rec = array('id' => $id, 'series' => $ser, 'date' => $d, 'race' => $race, 'name' => $name,
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
} elseif ($action !== 'delete') {
  out(400, array('ok' => false, 'error' => 'bad action'));
}

$f     = $dir . '/marks-' . $d . '.json';
$lh    = lock_data($dir);
$marks = load_json($f);

if ($action === 'add') {
  if (!isset($marks[$id]) && count($marks) >= MAX_FIXES) out(429, array('ok' => false, 'error' => 'day full'));
  if (isset($marks[$id]) && is_array($marks[$id])) {   // a re-post (the RO page moving a fix to another race) keeps who recorded it
    foreach (array('device', 'recorder') as $k)
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
