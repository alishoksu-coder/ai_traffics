# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

print("=== Checking Outline Levels ===")
for p in doc.paragraphs:
    t = p.text.strip()
    if t.startswith('2.3 Серверлік логика') or t.startswith('2.4 Инклюзивті'):
        if hasattr(p.paragraph_format, 'outline_level'):
            print(f"Text: {t[:50]}... | Outline Level: {p.paragraph_format.outline_level}")
        else:
            print(f"Text: {t[:50]}... | No outline_level attr")
