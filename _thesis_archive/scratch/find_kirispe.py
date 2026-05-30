import docx
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = docx.Document('диплом_Сулеймнов_Алишер_Втипо_45.docx')

sect_idx = 0
for p in doc.paragraphs:
    if p.text.strip().upper() == 'КІРІСПЕ':
        print(f"'Кіріспе' found in section roughly near this paragraph.")
        print(f"Current paragraph style: {p.style.name}")
        break
    if 'w:sectPr' in p._p.xml:
        sect_idx += 1

print(f"Estimated section index for 'Кіріспе': {sect_idx}")
print(f"Total sections: {len(doc.sections)}")
