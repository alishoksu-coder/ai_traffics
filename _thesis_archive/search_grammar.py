# -*- coding: utf-8 -*-
import sys, io, re
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted.docx')

print("=== Text Search for Grammar ===")
for i, p in enumerate(doc.paragraphs):
    text = p.text
    if "А.И. Трафик" in text or "Маршрутты жоспарлау процесі" in text or "көл секторында" in text or "краудсорсинг директорларынан" in text or "Сен ұсынған" in text:
        print(f"Para {i}: {text}")
