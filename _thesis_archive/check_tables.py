# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted.docx')

for i, tbl in enumerate(doc.tables):
    try:
        headers = [c.text.strip() for c in tbl.rows[0].cells]
        first_row_data = [c.text.strip() for c in tbl.rows[1].cells] if len(tbl.rows) > 1 else []
        print(f"Table {i}:")
        print(f"  Headers: {headers}")
        print(f"  Row 1: {first_row_data}")
        print()
    except Exception as e:
        print(f"Table {i} error: {e}")
