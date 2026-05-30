# -*- coding: utf-8 -*-
import sys, io
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = 'doc.docx'
doc = Document(SRC)

target_level_2 = [
    '2.4 Инклюзивті маршруттау',
    '2.6 Жүйенің контейнерлік',
    '2.7 Клиенттік деңгей',
    '2.8 Серверлік деңгей',
    '2.9 ML болжау',
    '2.10 Интеллектуалды хабарламалар',
    '2.11 Жүйелік модульдер',
    '2.12 Модельдердің жауапкершілік',
    '3.6 Пайдаланушылармен тестілеу'
]

print("=== Adding Outline Levels ===")
for p in doc.paragraphs:
    t = p.text.strip()
    matched = False
    for target in target_level_2:
        if t.startswith(target):
            matched = True
            break
            
    if matched:
        pPr = p._p.get_or_add_pPr()
        # Check if it already has outlineLvl
        outlineLvl = pPr.find(qn('w:outlineLvl'))
        if outlineLvl is None:
            outlineLvl = OxmlElement('w:outlineLvl')
            pPr.append(outlineLvl)
        outlineLvl.set(qn('w:val'), '1') # 0 is Heading 1, 1 is Heading 2
        print(f"Set Outline Level 2 for: {t[:50]}...")

doc.save(SRC)
print("Finished setting outline levels")
