# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

print("=== Checking XML for Outline Levels ===")
for p in doc.paragraphs:
    t = p.text.strip()
    if t.startswith('2.3 Серверлік логика') or t.startswith('2.4 Инклюзивті'):
        if p._p.pPr is not None:
            print(f"Text: {t[:50]}...\nXML: {p._p.pPr.xml}")
