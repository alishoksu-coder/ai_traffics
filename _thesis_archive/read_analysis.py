import docx
import os

doc_path = os.path.abspath("diploma_analysis_Suleimenov.docx")
try:
    doc = docx.Document(doc_path)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
    
    with open("analysis_text.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    print("Successfully extracted analysis text.")
except Exception as e:
    print(f"Error: {e}")
