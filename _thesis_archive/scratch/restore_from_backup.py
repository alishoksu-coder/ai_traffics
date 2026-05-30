# -*- coding: utf-8 -*-
"""
Restore page numbering from backup.
The backup has the correct structure:
- Sections 0-4: no page numbers (title pages)
- Section 5 (Kirispe): PAGE field, center aligned
- Sections 6-92: linked to previous (inherit page numbers)
- Section 93: no page numbers

We just copy the backup file to the main file.
"""
import shutil
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = 'диплом_Сулеймнов_Алишер_Втипо_45_backup.docx'
dst = 'диплом_Сулеймнов_Алишер_Втипо_45_restored.docx'

shutil.copy2(src, dst)
print(f"Copied backup to {dst}")

# Verify
import docx
doc = docx.Document(dst)
print(f"Sections: {len(doc.sections)}")

# Check section 5 footer XML to confirm PAGE field exists
footer_xml = doc.sections[5].footer._element.xml
has_page = 'PAGE' in footer_xml
print(f"Section 5 has PAGE field: {has_page}")

# Print the actual footer XML of section 5 to see the page number format
print("\nSection 5 footer XML:")
print(footer_xml[:1000])
