# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

print("=== Checking Styles of Headings ===")
for p in doc.paragraphs:
    t = p.text.strip()
    if t.startswith('2.4 Инклюзивті маршруттау') or \
       t.startswith('2.5 Мобильді клиент') or \
       t.startswith('2.6 Жүйенің контейнерлік') or \
       t.startswith('2.7 Клиенттік деңгей') or \
       t.startswith('2.12 Модельдердің'):
        print(f"Text: {t[:50]}... | Style: {p.style.name}")
