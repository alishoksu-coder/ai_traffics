from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = Document()
p = doc.add_paragraph()

math_xml = f'''
<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:r>
    <m:rPr><m:scr m:val="roman"/></m:rPr>
    <m:t>SMA(t) = 1/k ∑ y_i</m:t>
  </m:r>
</m:oMath>
'''
omath = parse_xml(math_xml)
p._p.append(omath)

doc.save("test_omml.docx")
