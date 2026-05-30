# -*- coding: utf-8 -*-
import sys, io, re
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

print("=== Sequence of Sections in Body ===")
for p in doc.paragraphs:
    t = p.text.strip()
    if '...' in t or len(t) > 150: # skip TOC and normal text
        continue
    m = re.match(r'^(2\.\d+(\.\d+)?|3\.\d+(\.\d+)?)\s+(.*)', t)
    if m:
        print(f"Para index: {m.group(0)}")
