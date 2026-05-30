# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

print("=== Checking Existing Styles ===")
for p in doc.paragraphs:
    t = p.text.strip()
    if t.startswith('2.3 Серверлік логика') or t.startswith('2.3.1 Traffic Simulator') or t.startswith('3.1 Интерфейс'):
        print(f"Text: {t[:50]}... | Style: {p.style.name}")
