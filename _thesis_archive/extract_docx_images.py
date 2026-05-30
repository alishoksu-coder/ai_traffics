import zipfile
import os
from lxml import etree

doc_path = "диплом_Сулеймнов_Алишер_Втипо_45.docx"
extract_dir = "temp_word_extract"
os.makedirs(extract_dir, exist_ok=True)

with zipfile.ZipFile(doc_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

media_dir = os.path.join(extract_dir, "word", "media")
if os.path.exists(media_dir):
    images = os.listdir(media_dir)
    print(f"Found {len(images)} images in word/media:")
    for img in images:
        size = os.path.getsize(os.path.join(media_dir, img))
        print(f" - {img} ({size} bytes)")
else:
    print("No media directory found.")
