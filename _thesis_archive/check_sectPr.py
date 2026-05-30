# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

sectPr_xml = doc.sections[0]._sectPr.xml
print("Section 0 sectPr:")
print(sectPr_xml)
