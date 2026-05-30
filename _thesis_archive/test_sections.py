# -*- coding: utf-8 -*-
import sys, io
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

# Find Кіріспе
kirispe_para = None
for p in doc.paragraphs:
    if p.text.strip() == 'Кіріспе':
        kirispe_para = p
        break

if kirispe_para:
    print("Found Кіріспе")
    # To insert a section break before a paragraph, we actually add a sectPr to the PREVIOUS paragraph.
    # But wait, Word defines sections at the end of the section text. 
    # The last paragraph of a section contains the sectPr for that section.
    # So we find the paragraph BEFORE Кіріспе and add a sectPr to it.
    prev_p = kirispe_para._p.getprevious()
    if prev_p is not None:
        pPr = prev_p.get_or_add_pPr()
        sectPr = OxmlElement('w:sectPr')
        
        # copy page size/margins from document default or existing sections to avoid breaking layout
        # For simplicity, we just add a basic Next Page break
        type_el = OxmlElement('w:type')
        type_el.set(qn('w:val'), 'nextPage')
        sectPr.append(type_el)
        
        pPr.append(sectPr)
        print("Added section break before Кіріспе")

doc.save('test_sections.docx')
print("Saved test_sections.docx")
