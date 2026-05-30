"""
Apply reference formatting to Suleimenov diploma.
Margins, fonts, paragraph styles, formula numbering + explanations.
"""
import win32com.client
import os

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

doc_path = os.path.abspath("Suleimenov_Alisher_VTIPO-45_REPORT_GOST.docx")
doc = word.Documents.Open(doc_path)

# Helper: cm to points (1 cm = 28.3465 pt)
def cm2pt(cm):
    return cm * 28.3465

# ===== 1. PAGE MARGINS =====
for i in range(1, doc.Sections.Count + 1):
    sec = doc.Sections(i)
    ps = sec.PageSetup
    ps.LeftMargin = cm2pt(3.0)
    ps.RightMargin = cm2pt(1.5)
    ps.TopMargin = cm2pt(2.0)
    ps.BottomMargin = cm2pt(2.0)
    ps.HeaderDistance = cm2pt(1.25)
    ps.FooterDistance = cm2pt(1.25)

print("1/5 Margins set.")

# ===== 2. BODY TEXT FORMATTING =====
total_paras = doc.Paragraphs.Count
for i in range(1, total_paras + 1):
    para = doc.Paragraphs(i)
    text = para.Range.Text.strip()
    if not text:
        continue

    is_heading = False
    is_caption = False

    # Check bold
    try:
        all_bold = (para.Range.Bold == -1)  # -1 means all bold
    except:
        all_bold = False

    if all_bold and len(text) < 150:
        is_heading = True

    lower_text = text.lower()
    if lower_text.startswith("сурет ") or lower_text.startswith("кесте "):
        is_caption = True

    # Apply font
    para.Range.Font.Name = "Times New Roman"
    para.Range.Font.Size = 14
    para.Format.SpaceAfter = 0
    para.Format.SpaceBefore = 0
    para.Format.LineSpacingRule = 0  # Single

    if is_heading:
        para.Format.Alignment = 1  # Center
        para.Format.FirstLineIndent = 0
    elif is_caption:
        para.Format.Alignment = 1  # Center
        para.Format.FirstLineIndent = 0
    else:
        para.Format.Alignment = 3  # Justify
        para.Format.FirstLineIndent = cm2pt(1.25)

    if i % 100 == 0:
        print(f"  formatting para {i}/{total_paras}")

print("2/5 Paragraph formatting applied.")

# ===== 3. FORMULA NUMBERING =====
formula_num = 0
formula_indices = []

for i in range(1, doc.Paragraphs.Count + 1):
    para = doc.Paragraphs(i)
    text = para.Range.Text.strip()

    has_formula = False
    for marker in ["Σ(", "σ ", "b0 =", "b1 =", "SMA =", "EMA =",
                    "Z =", "ŷ =", "MAE =", "RMSE =", "y_pred"]:
        if marker in text:
            has_formula = True
            break

    if has_formula and len(text) < 250:
        formula_num += 1
        para.Format.Alignment = 1  # Center
        para.Format.FirstLineIndent = 0

        # Add (N) at end
        rng = para.Range
        rng.Collapse(0)
        rng.MoveEnd(1, -1)
        rng.Collapse(0)
        rng.InsertAfter(f"  ({formula_num})")

        formula_indices.append((i, formula_num, text))

print(f"3/5 Numbered {formula_num} formulas.")

# ===== 4. ADD EXPLANATIONS =====
explanations = {
    "SMA =": "мұндағы SMA – қарапайым жылжымалы орташа мән; n – терезе өлшемі (кезеңдер саны); xᵢ – i-ші кезеңдегі трафик жүктемесінің мәні.",
    "EMA =": "мұндағы EMA – экспоненциалды жылжымалы орташа; α – тегістеу коэффициенті (0 < α ≤ 1); xₜ – ағымдағы кезеңдегі мән; EMAₜ₋₁ – алдыңғы кезеңдегі EMA мәні.",
    "Z =": "мұндағы Z – стандартталған ауытқу (Z-score); x – ағымдағы мән; μ – орташа мән; σ – стандартты ауытқу.",
    "b0 =": "мұндағы b₀ – регрессия теңдеуінің бос мүшесі; b₁ – көлбеу коэффициенті; x̄ – тәуелсіз айнымалының орташа мәні; ȳ – тәуелді айнымалының орташа мәні.",
    "MAE =": "мұндағы MAE – орташа абсолютті қателік; n – бақылаулар саны; yᵢ – нақты мән; ŷᵢ – болжамды мән.",
    "RMSE =": "мұндағы RMSE – орташа квадраттық қателіктің түбірі; n – бақылаулар саны; yᵢ – нақты мән; ŷᵢ – болжамды мән.",
    "ŷ =": "мұндағы ŷ – болжамды мән; T – шешім ағаштарының саны; fₜ(x) – t-ші ағаштың болжамы.",
}

inserted = 0
for (para_idx, fnum, text) in reversed(formula_indices):
    expl = None
    for key, val in explanations.items():
        if key in text:
            expl = val
            break

    if expl:
        adj_idx = para_idx + inserted
        target = doc.Paragraphs(adj_idx)
        rng = target.Range
        rng.Collapse(0)
        rng.InsertAfter(expl + "\n")

        new_p = doc.Paragraphs(adj_idx + 1)
        new_p.Range.Font.Name = "Times New Roman"
        new_p.Range.Font.Size = 14
        new_p.Format.Alignment = 3
        new_p.Format.FirstLineIndent = cm2pt(1.25)
        new_p.Format.SpaceAfter = 0
        new_p.Format.LineSpacingRule = 0
        inserted += 1

print(f"4/5 Added {inserted} explanations.")

# ===== 5. SAVE =====
out = os.path.abspath("Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted.docx")
doc.SaveAs(out)
doc.Close()
word.Quit()
print("5/5 DONE! Saved: Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted.docx")
