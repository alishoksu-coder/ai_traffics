# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

print("=== Checking if TOC is a field ===")
toc_found = False
for p in doc.paragraphs:
    if "TOC" in p._p.xml:
        toc_found = True
        break
        
print(f"Is there a dynamic TOC field? {toc_found}")
