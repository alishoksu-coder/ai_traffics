# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

for p in doc.paragraphs:
    if p.text.strip().startswith('1.1'):
        print(f"[{p.text.strip()}]")
