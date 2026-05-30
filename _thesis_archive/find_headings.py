# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

for i, p in enumerate(doc.paragraphs):
    if p.text.strip() in ['Кіріспе', 'Мазмұны', 'Нормативтік сілтемелер', 'Анықтамалар']:
        print(f"Para {i}: {p.text.strip()}")
