from docx import Document
from docx.shared import Pt
import os

doc_path = "диплом_Сулеймнов_Алишер_Втипо_45.docx"
output_path = "диплом_Сулеймнов_Алишер_Втипо_45_fixed.docx"

doc = Document(doc_path)

# Map image byte sizes to their text formulas
formula_map = {
    4129: "SMA(t) = (1/k) ∑ y_i",
    1957: "EMA(t) = α y_t + (1 - α) EMA(t-1)",
    813: "Z = (x - μ) / σ",
    1641: "| y_t - y_{t-1} | > 25 және y_t > 70",
    2130: "(y_t - y_{t-k}) > 35 немесе y_t > 90",
    1040: "(y_t - y_{t-k}) > 20",
    2192: "SMA(t) = (1/k) ∑ y_i",
    7076: "V(t) = clamp(B ∙ R(h) ∙ L(id) + W(t) + N(t) ∙ W_f + J(t), 0, 100)",
    1884: "W(t) = 5sin(0.1t)",
    1521: "J = (1 - d/r)SW_f",
    787: "ŷ_{t+1} = y_t",
    2062: "SMA(t) = (1/k) ∑ y_i",
    2207: "EMA(t) = α y_t + (1 - α) EMA(t - 1)",
    1714: "a = ∑(x_i - x̄)(y_i - ȳ) / ∑(x_i - x̄)²",
    717: "b = ȳ - a x̄",
    1746: "ŷ(t + h) = a(x_last + h) + b",
    1689: "MAE = (1/n) ∑ |y_i - ŷ_i|",
    2342: "RMSE = √((1/n) ∑(y_i - ŷ_i)²)",
    1418: "| y_t - y_{t-1} | > 25, y_t > 70",
    2018: "(y_t - y_{t-k}) > 35 немесе y_t > 90",
    1086: "(y_t - y_{t-k}) > 20",
    3275: "is_accessible = true, has_steps = false, surface_type IN ('asphalt', 'concrete')",
    4752: "cost(edge) = distance × time_weight × (1 + barrier_penalty)"
}

replaced_count = 0

for p in doc.paragraphs:
    for run in p.runs:
        # Check if run contains a drawing
        if 'drawing' in run._element.xml or 'pict' in run._element.xml:
            # Find blip elements
            blips = run._element.xpath('.//a:blip')
            for blip in blips:
                rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if rId:
                    part = doc.part.related_parts[rId]
                    size = len(part.blob)
                    if size in formula_map:
                        formula_text = formula_map[size]
                        # Clear the run (removes the image)
                        run.clear()
                        # Add the text formula
                        run.text = formula_text
                        # Style it to look like a formula
                        run.font.name = 'Cambria Math'
                        run.font.italic = True
                        run.font.size = Pt(14)
                        replaced_count += 1
                        pass

doc.save(output_path)
print(f"Total formulas replaced: {replaced_count}")
