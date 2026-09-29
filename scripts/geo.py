"""Geodesy and INFOMAR raster sampling.

No third-party GIS stack: Vincenty and the UTM 29N projection are implemented here,
and GeoTIFF tiles are read directly, so the only dependencies are numpy, pandas and
tifffile. That keeps the audit reproducible on a plain Python install.

Depth convention: the INFOMAR grids store elevation relative to LAT, so a depth of
2.5 m appears as -2.5. Everything below returns depth (positive down).
"""
import math

import numpy as np
import tifffile

WGS84_A = 6378137.0
WGS84_F = 1 / 298.257223563


def vincenty(lat1, lon1, lat2, lon2):
    """Return (distance in nautical miles, initial bearing in degrees true)."""
    if abs(lat1 - lat2) < 1e-12 and abs(lon1 - lon2) < 1e-12:
        return 0.0, 0.0
    a, f = WGS84_A, WGS84_F
    b = a * (1 - f)
    L = math.radians(lon2 - lon1)
    U1 = math.atan((1 - f) * math.tan(math.radians(lat1)))
    U2 = math.atan((1 - f) * math.tan(math.radians(lat2)))
    sU1, cU1, sU2, cU2 = math.sin(U1), math.cos(U1), math.sin(U2), math.cos(U2)
    lam = L
    for _ in range(200):
        sl, cl = math.sin(lam), math.cos(lam)
        ss = math.hypot(cU2 * sl, cU1 * sU2 - sU1 * cU2 * cl)
        cs = sU1 * sU2 + cU1 * cU2 * cl
        sig = math.atan2(ss, cs)
        sa = cU1 * cU2 * sl / ss
        c2a = 1 - sa * sa
        c2sm = cs - 2 * sU1 * sU2 / c2a if c2a else 0.0
        C = f / 16 * c2a * (4 + f * (4 - 3 * c2a))
        prev = lam
        lam = L + (1 - C) * f * sa * (sig + C * ss * (c2sm + C * cs * (-1 + 2 * c2sm ** 2)))
        if abs(lam - prev) < 1e-13:
            break
    u2 = c2a * (a * a - b * b) / (b * b)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    ds = B * ss * (c2sm + B / 4 * (cs * (-1 + 2 * c2sm ** 2)
                                   - B / 6 * c2sm * (-3 + 4 * ss ** 2) * (-3 + 4 * c2sm ** 2)))
    s = b * A * (sig - ds)
    az = math.degrees(math.atan2(cU2 * math.sin(lam), cU1 * sU2 - sU1 * cU2 * math.cos(lam))) % 360
    return s / 1852.0, az


def utm29(lat, lon):
    """WGS84 -> UTM zone 29N (EPSG:32629), Krueger series. Metres."""
    a, f, k0 = WGS84_A, WGS84_F, 0.9996
    lon0 = math.radians(-9.0)
    e2 = f * (2 - f)
    n = f / (2 - f)
    A = a / (1 + n) * (1 + n ** 2 / 4 + n ** 4 / 64)
    al = [n / 2 - 2 * n ** 2 / 3 + 5 * n ** 3 / 16,
          13 * n ** 2 / 48 - 3 * n ** 3 / 5,
          61 * n ** 3 / 240]
    phi, lam = math.radians(lat), math.radians(lon) - lon0
    t = math.sinh(math.atanh(math.sin(phi)) - math.sqrt(e2) * math.atanh(math.sqrt(e2) * math.sin(phi)))
    xi = math.atan(t / math.cos(lam))
    eta = math.atanh(math.sin(lam) / math.hypot(1, t))
    E = 500000 + k0 * A * (eta + sum(al[j] * math.cos(2 * (j + 1) * xi) * math.sinh(2 * (j + 1) * eta)
                                     for j in range(3)))
    N = k0 * A * (xi + sum(al[j] * math.sin(2 * (j + 1) * xi) * math.cosh(2 * (j + 1) * eta)
                           for j in range(3)))
    return E, N


class Raster:
    """Read-only random access to a tiled, uncompressed float32 GeoTIFF."""

    def __init__(self, path, nodata=0.0):
        self.path = path
        with tifffile.TiffFile(path) as t:
            pg = t.pages[0]
            self.h, self.w = pg.shape
            tp = pg.tags['ModelTiepointTag'].value
            sc = pg.tags['ModelPixelScaleTag'].value
            self.x0, self.y0 = tp[3], tp[4]
            self.sx, self.sy = sc[0], sc[1]
            self.tl, self.tw = pg.tilelength, pg.tilewidth
            self.offsets = np.array(pg.tags['TileOffsets'].value, dtype=np.int64)
            self.counts = np.array(pg.tags['TileByteCounts'].value, dtype=np.int64)
        self.tcols = (self.w + self.tw - 1) // self.tw
        self.nodata = nodata
        self.fh = open(path, 'rb')
        self.cache = {}
        self.bounds = (self.x0, self.y0 - self.h * self.sy,
                       self.x0 + self.w * self.sx, self.y0)

    def _tile(self, ti):
        if ti not in self.cache:
            if len(self.cache) > 4000:
                self.cache.clear()
            self.fh.seek(self.offsets[ti])
            buf = self.fh.read(self.counts[ti])
            self.cache[ti] = np.frombuffer(buf, dtype='<f4').reshape(self.tl, self.tw)
        return self.cache[ti]

    def sample(self, E, N):
        """Depth in metres at a UTM 29N position, or None where there is no data."""
        col = int((E - self.x0) / self.sx)
        row = int((self.y0 - N) / self.sy)
        if not (0 <= col < self.w and 0 <= row < self.h):
            return None
        ti = (row // self.tl) * self.tcols + (col // self.tw)
        v = float(self._tile(ti)[row % self.tl, col % self.tw])
        if v == self.nodata or not np.isfinite(v):
            return None
        return -v  # stored as elevation relative to LAT


def sample_chord(rasters, lat1, lon1, lat2, lon2, spacing=5.0):
    """Sample a straight chord. rasters is [(name, Raster), ...] in priority order.

    Returns (chord length in metres, [(depth or None, source name or None), ...]).
    """
    E1, N1 = utm29(lat1, lon1)
    E2, N2 = utm29(lat2, lon2)
    L = math.hypot(E2 - E1, N2 - N1)
    n = max(2, int(L / spacing) + 1)
    out = []
    for i in range(n + 1):
        fr = i / n
        E, N = E1 + (E2 - E1) * fr, N1 + (N2 - N1) * fr
        hit = (None, None)
        for name, r in rasters:
            v = r.sample(E, N)
            if v is not None:
                hit = (v, name)
                break
        out.append(hit)
    return L, out


def chord_result(rasters, a, b, marks, spacing=5.0, criterion=1.5):
    """Test one directed chord. Returns a dict ready to be written as evidence."""
    L, pts = sample_chord(rasters, *marks[a], *marks[b], spacing=spacing)
    depths = [(d, i, src) for i, (d, src) in enumerate(pts) if d is not None]
    sources = {}
    for _, _, src in depths:
        sources[src] = sources.get(src, 0) + 1
    runs, cur = [], 0
    for d, _ in pts:
        if d is None:
            cur += 1
        else:
            if cur:
                runs.append(cur)
            cur = 0
    if cur:
        runs.append(cur)
    res = {'from': a, 'to': b, 'length_m': round(L, 1), 'samples': len(pts),
           'covered': len(depths), 'sources': sources, 'spacing_m': spacing,
           'criterion_m': criterion,
           'max_gap_samples': max(runs) if runs else 0,
           'max_gap_m': round((max(runs) if runs else 0) * L / (len(pts) - 1), 1)}
    if depths:
        mn, imn, _ = min(depths)
        res.update(min_depth_m=round(mn, 3),
                   below_criterion=sum(1 for d, _, _ in depths if d < criterion),
                   min_at_fraction=round(imn / (len(pts) - 1), 3))
        res['verdict'] = ('DEPTH FAIL' if res['below_criterion']
                          else 'PASS' if res['covered'] == res['samples']
                          else 'PASS - INCOMPLETE COVERAGE')
    else:
        res.update(min_depth_m=None, below_criterion=None, min_at_fraction=None,
                   verdict='NO COVERAGE')
    return res


def marks_from_workbook(marks_df):
    """{'No.8': (lat, lon)} keyed by the short id used in Numbered Legs."""
    out = {}
    df = marks_df.dropna(subset=['Decimal Lat'])
    for _, r in df.iterrows():
        out[str(r['Mark']).split('/')[0].strip()] = (r['Decimal Lat'], r['Decimal Lon'])
    return out
