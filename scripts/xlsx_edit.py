"""Surgical edits to the master workbook.

Why not openpyxl: an early attempt to write geometry into Numbered Legs through a
full library re-save produced a file Excel repaired with

    Removed Records: Cell information from /xl/worksheets/sheet11.xml part

That workbook (v3.1) is invalid and must never be reused. Everything since has
been done by editing the sheet XML in place and copying every other part of the
zip through byte for byte, so a change to one cell cannot disturb anything else.

Usage:

    from xlsx_edit import Workbook
    wb = Workbook('master_v3_14.xlsx')
    wb.set_cell('Marks', 59, 'H', 'RCYC Autumn League SI 2026, para 36')
    wb.append_readme('Some change v3.15 (1 Oct 2026)', 'What changed, why, and the baseline hash.')
    wb.save('master_v3_15.xlsx')

Then always: reopen, diff against the previous version, and run audit_workbook.py.
Never declare an edit successful because the write returned without error.
"""
import re
import zipfile
from xml.sax.saxutils import escape

READ_ME_SHEET = 'Read Me'


class Workbook:
    def __init__(self, path):
        self.path = path
        self.zin = zipfile.ZipFile(path)
        self.parts = {}
        wbxml = self.zin.read('xl/workbook.xml').decode('utf-8')
        rels = self.zin.read('xl/_rels/workbook.xml.rels').decode('utf-8')
        self.sheets = {}
        for m in re.finditer(r'<(?:x:)?sheet name="([^"]+)"[^>]*r:id="([^"]+)"', wbxml):
            name, rid = m.group(1), m.group(2)
            t = re.search(r'Target="([^"]+)"[^>]*Id="%s"' % rid, rels) or \
                re.search(r'Id="%s"[^>]*Target="([^"]+)"' % rid, rels)
            target = t.group(1).lstrip('/')
            self.sheets[name] = target if target.startswith('xl/') else 'xl/' + target

    def _xml(self, sheet):
        part = self.sheets[sheet]
        if part not in self.parts:
            self.parts[part] = self.zin.read(part).decode('utf-8')
        return part, self.parts[part]

    def set_cell(self, sheet, row, col, value, numeric=False):
        """Replace one cell. Row numbers are worksheet rows: data row i of a
        pandas frame is row i + 2."""
        part, s = self._xml(sheet)
        m = re.search(r'<x:row r="%d"[^>]*>.*?</x:row>' % row, s, re.S)
        if not m:
            raise KeyError(f'{sheet} row {row} not found')
        old = m.group(0)
        style = re.search(r'<x:c r="A%d"( s="\d+")?' % row, old)
        style = (style.group(1) or '') if style else ''
        if numeric:
            cell = f'<x:c r="{col}{row}"{style} t="n"><x:v>{value}</x:v></x:c>'
        else:
            cell = (f'<x:c r="{col}{row}"{style} t="inlineStr">'
                    f'<x:is><x:t xml:space="preserve">{escape(str(value))}</x:t></x:is></x:c>')
        pat = re.compile(r'<x:c r="%s%d"(?: s="\d+")?(?: t="[^"]*")?(?:\s*/>|>.*?</x:c>)' % (col, row), re.S)
        if pat.search(old):
            new = pat.sub(lambda _: cell, old, count=1)
        else:  # cell absent: insert in column order
            cols = re.findall(r'<x:c r="([A-Z]+)%d"' % row, old)
            before = [c for c in cols if (len(c), c) < (len(col), col)]
            if not before:
                new = old.replace('>', '>' + cell, 1)
            else:
                anchor = before[-1]
                apat = re.compile(r'<x:c r="%s%d"(?: s="\d+")?(?: t="[^"]*")?(?:\s*/>|>.*?</x:c>)'
                                  % (anchor, row), re.S)
                new = apat.sub(lambda mm: mm.group(0) + cell, old, count=1)
        assert s.count(old) == 1
        self.parts[part] = s.replace(old, new)

    def append_row(self, sheet, values, style_from_row=2):
        """Append one row of inline strings after the last row of a sheet."""
        part, s = self._xml(sheet)
        last = max(int(r) for r in re.findall(r'<x:row r="(\d+)"', s))
        n = last + 1
        st = re.search(r'<x:row r="%d"[^>]*>.*?<x:c r="A%d"( s="\d+")?' % (style_from_row, style_from_row), s, re.S)
        st = (st.group(1) or '') if st else ''
        cells = ''.join(
            f'<x:c r="{chr(65 + i)}{n}"{st} t="inlineStr"><x:is>'
            f'<x:t xml:space="preserve">{escape(str(v))}</x:t></x:is></x:c>'
            for i, v in enumerate(values))
        self.parts[part] = s.replace('</x:sheetData>', f'<x:row r="{n}">{cells}</x:row></x:sheetData>')
        return n

    def append_readme(self, key, text):
        """Add a change record. Every release must add one, citing the baseline hash."""
        return self.append_row(READ_ME_SHEET, [key, text])

    def save(self, out):
        with zipfile.ZipFile(out, 'w') as z:
            for info in self.zin.infolist():
                data = self.parts.get(info.filename)
                z.writestr(info, data.encode('utf-8') if data is not None else self.zin.read(info.filename),
                           compress_type=info.compress_type)
        return out


def cell_diff(before, after):
    """Every differing cell between two workbooks: [(sheet, coordinate, old, new)]."""
    import openpyxl
    wa = openpyxl.load_workbook(before)
    wb = openpyxl.load_workbook(after)
    out = []
    for ws in wb.worksheets:
        src = wa[ws.title] if ws.title in wa.sheetnames else None
        for row in ws.iter_rows():
            for c in row:
                old = None
                if src is not None and c.row <= src.max_row and c.column <= src.max_column:
                    old = src.cell(row=c.row, column=c.column).value
                if old != c.value:
                    out.append((ws.title, c.coordinate, old, c.value))
    return out
