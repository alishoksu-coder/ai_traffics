import zipfile
import xml.etree.ElementTree as ET

def extract_docx_text(path):
    with zipfile.ZipFile(path, 'r') as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    texts = []
    for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        line = ''
        for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
            if t.text:
                line += t.text
        if line.strip():
            texts.append(line.strip())
    return '\n'.join(texts)

text1 = extract_docx_text('AI_Traffic_Diploma_FINAL_Suleimenov_1.docx')
with open('extracted_final.txt', 'w', encoding='utf-8') as f:
    f.write(text1)

text2 = extract_docx_text('Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted.docx')
with open('extracted_gost.txt', 'w', encoding='utf-8') as f:
    f.write(text2)

print(f"Final doc: {len(text1)} chars, {len(text1.splitlines())} lines")
print(f"GOST doc: {len(text2)} chars, {len(text2.splitlines())} lines")
