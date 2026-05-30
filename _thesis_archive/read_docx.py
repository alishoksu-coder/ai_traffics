import docx
import json

doc = docx.Document("Suleimenov_Alisher_VTIPO-45_REPORT_GOST.docx")
lines = []
for p in doc.paragraphs:
    if p.text.strip():
        lines.append(p.text.strip())

with open("doc_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
