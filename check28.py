# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

doc = Document('Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted.docx')

# Check section 2.8 area
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if '2.8' in t or 'контейнерлік' in t.lower():
        print(f"Para {i}: [{p.style.name}] {t[:120]}")
        # Show surrounding
        for j in range(max(0,i-1), min(len(doc.paragraphs), i+8)):
            print(f"  {j}: {doc.paragraphs[j].text.strip()[:100]}")
        print()

# Also verify chapter 3 is still there
print("\n=== Chapter 3 check ===")
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if i > 900 and (t.startswith('3.') or t.startswith('AI Traffic жүйесін тестілеу')):
        if len(t) < 100:
            print(f"Para {i}: {t}")
