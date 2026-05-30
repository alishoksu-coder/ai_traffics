# -*- coding: utf-8 -*-
import sys, io, re
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

print("=== Headings in doc.docx ===")
for p in doc.paragraphs:
    if p.style.name.startswith('Heading'):
        print(f"{p.style.name}: {p.text.strip()}")
    elif re.match(r'^(1|2|3)\.\d+(\.\d+)?\s+[А-ЯҮҰҚӨӘІҢҒ]', p.text.strip()):
        print(f"Possible heading: {p.text.strip()[:100]}")
