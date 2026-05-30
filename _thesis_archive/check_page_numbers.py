# -*- coding: utf-8 -*-
import sys, io
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = Document('doc.docx')

for i, section in enumerate(doc.sections):
    print(f"=== Section {i} ===")
    # Find the paragraph that corresponds to the start of this section
    # doc.sections doesn't directly map to paragraphs, but we can look at page breaks or section breaks in the document XML.
    pass

# Let's count page breaks
page_breaks = 0
for p in doc.paragraphs:
    if 'w:br' in p._p.xml and 'type="page"' in p._p.xml:
        page_breaks += p._p.xml.count('type="page"')
    if 'w:sectPr' in p._p.xml:
        print(f"Section break found at paragraph starting with: {p.text[:50]}")

print(f"Total page breaks found: {page_breaks}")

# Also let's check the footer xml of Section 0 and Section 1
print("\nSection 0 Footer XML:")
if not doc.sections[0].footer.is_linked_to_previous:
    print(doc.sections[0].footer._element.xml[:500])

print("\nSection 1 Footer XML:")
try:
    print(doc.sections[1].footer._element.xml[:500])
except Exception as e:
    print(e)
