# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

for i, p in enumerate(doc.paragraphs[50:200]):
    print(f"[{i+50}] {p.text.strip()[:60]}")
