# -*- coding: utf-8 -*-
import sys, io, re
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = 'doc.docx'
doc = Document(SRC)

lvl0_re = re.compile(r'^([1-9]\s+[А-ЯҮҰҚӨӘІҢҒA-Z]|Кіріспе|Қорытынды|Пайдаланылған әдебиеттер тізімі|Қосымша\s+[А-Я])')
lvl1_re = re.compile(r'^[1-9]\.\d+\s+[А-ЯҮҰҚӨӘІҢҒA-Z]')
lvl2_re = re.compile(r'^[1-9]\.\d+\.\d+\s+[А-ЯҮҰҚӨӘІҢҒA-Z]')

print("=== Setting Outline Levels for Entire Document ===")
count = 0
for p in doc.paragraphs:
    t = p.text.strip()
    # Skip empty lines, lines that are too long to be headers, and lines that look like the static TOC
    if not t or len(t) > 150 or t.endswith('.') or t.startswith('Кесте ') or t.startswith('Сурет ') or '...' in t:
        continue
        
    lvl = None
    if lvl2_re.match(t):
        lvl = '2'
    elif lvl1_re.match(t):
        lvl = '1'
    elif lvl0_re.match(t):
        lvl = '0'
        
    if lvl is not None:
        pPr = p._p.get_or_add_pPr()
        outlineLvl = pPr.find(qn('w:outlineLvl'))
        if outlineLvl is None:
            outlineLvl = OxmlElement('w:outlineLvl')
            pPr.append(outlineLvl)
        outlineLvl.set(qn('w:val'), lvl)
        count += 1
        print(f"Set Level {lvl} for: {t[:50]}...")

doc.save(SRC)
print(f"Finished. Total headers updated: {count}")
