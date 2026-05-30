# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

texts_to_check = [
    "Render.com", "CI/CD",
    "accuracy", "87%", 
    "ИКЖ", "ITS", "ББЖ", "ТҚБЖ", "ASGI", "JWT",
    "ЖИ", "AI", "Жасанды интеллект",
    "19 сегмент", "144",
    "Z-score", "μ", "σ"
]

print("=== Audit Results ===")
for p in doc.paragraphs:
    t = p.text
    for term in texts_to_check:
        if term in t:
            print(f"Found {term} in: {t[:80]}...")
