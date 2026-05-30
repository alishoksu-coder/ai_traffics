# -*- coding: utf-8 -*-
import sys, io
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = 'doc.docx'
doc = Document(SRC)

fixes = {
    "Жол қозғалысын басқару саласының өзектілігі": "1.1 Көлік ағындарын бақылау саласының өзектілігі",
    "Навигация сервисі жайлы салыстырмалы ақпарат": "1.3 Навигациялық сервистерді салыстырмалы талдау",
    "Навигация жүйелерді  салыстырмалы талдау": "", # This looks like an accidental extra header
    "Астана қаласынын көлік қозғалысы": "1.4 Трафикті болжау үшін машиналық оқыту әдістері",
    "API жүктеме тестілеу": "3.2 API жүктеме тестілеу"
}

count = 0
for p in doc.paragraphs:
    t = p.text.strip()
    
    # Text replacements
    for old, new in fixes.items():
        if t == old:
            if new == "":
                p.text = "" # remove it
            else:
                p.text = new
                t = new # update t for the next check
            print(f"Replaced header text: {old} -> {new}")
            
    # Also set Outline Level 1 if it matches our new texts
    if t in ["1.1 Көлік ағындарын бақылау саласының өзектілігі", 
             "1.3 Навигациялық сервистерді салыстырмалы талдау",
             "1.4 Трафикті болжау үшін машиналық оқыту әдістері",
             "3.2 API жүктеме тестілеу"]:
        pPr = p._p.get_or_add_pPr()
        outlineLvl = pPr.find(qn('w:outlineLvl'))
        if outlineLvl is None:
            outlineLvl = OxmlElement('w:outlineLvl')
            pPr.append(outlineLvl)
        outlineLvl.set(qn('w:val'), '1')
        print(f"Set Outline Level 1 for: {t}")
        count += 1

doc.save(SRC)
print(f"Finished fixing broken headers. Total updated: {count}")
