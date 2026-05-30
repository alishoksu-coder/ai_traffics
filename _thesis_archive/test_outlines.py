# -*- coding: utf-8 -*-
import sys, io, re
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = 'doc.docx'
doc = Document(SRC)

# Regex patterns
# Note: some headings might have spaces or weird characters.
lvl0_re = re.compile(r'^([1-9]\s+[А-ЯҮҰҚӨӘІҢҒA-Z]|Кіріспе|Қорытынды|Пайдаланылған әдебиеттер тізімі|Қосымша\s+[А-Я])')
lvl1_re = re.compile(r'^[1-9]\.\d+\s+[А-ЯҮҰҚӨӘІҢҒA-Z]')
lvl2_re = re.compile(r'^[1-9]\.\d+\.\d+\s+[А-ЯҮҰҚӨӘІҢҒA-Z]')

print("=== Simulating Outline Level Assignment ===")
for p in doc.paragraphs:
    t = p.text.strip()
    if not t or len(t) > 150 or t.endswith('.') or t.startswith('Кесте ') or t.startswith('Сурет '):
        continue
        
    lvl = None
    if lvl2_re.match(t):
        lvl = '2' # Heading 3
    elif lvl1_re.match(t):
        lvl = '1' # Heading 2
    elif lvl0_re.match(t):
        lvl = '0' # Heading 1
        
    if lvl is not None:
        print(f"Level {lvl}: {t}")
