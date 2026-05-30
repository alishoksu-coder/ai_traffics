from docx import Document
from docx.oxml import parse_xml
import os

doc_path = "диплом_Сулеймнов_Алишер_Втипо_45_backup.docx"
output_path = "диплом_Сулеймнов_Алишер_Втипо_45.docx"

def omath(content):
    return f'<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">{content}</m:oMath>'

def m_r(text):
    # wrap text in run
    return f'<m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t>{text}</m:t></m:r>'

def m_r_i(text):
    # italic run for variables
    return f'<m:r><m:rPr><m:sty m:val="p"/><m:scr m:val="roman"/></m:rPr><m:t>{text}</m:t></m:r>'

def m_f(num, den):
    # fraction
    return f'<m:f><m:fPr><m:ctrlPr/></m:fPr><m:num>{num}</m:num><m:den>{den}</m:den></m:f>'

def m_sub(base, sub):
    # subscript
    return f'<m:sSub><m:sSubPr><m:ctrlPr/></m:sSubPr><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>'

def m_sup(base, sup):
    # superscript
    return f'<m:sSup><m:sSupPr><m:ctrlPr/></m:sSupPr><m:e>{base}</m:e><m:sup>{sup}</m:sup></m:sSup>'

def m_nary(char, sub, sup, e):
    # summation/integral etc
    return f'<m:nary><m:naryPr><m:chr m:val="{char}"/><m:limLoc m:val="undOvr"/><m:subHide m:val="{"off" if sub else "on"}"/><m:supHide m:val="{"off" if sup else "on"}"/><m:ctrlPr/></m:naryPr><m:sub>{sub}</m:sub><m:sup>{sup}</m:sup><m:e>{e}</m:e></m:nary>'

def m_rad(e):
    # square root
    return f'<m:rad><m:radPr><m:degHide m:val="on"/><m:ctrlPr/></m:radPr><m:deg></m:deg><m:e>{e}</m:e></m:rad>'

def m_d(e, beg="(", end=")"):
    # delimiters like parenthesis or brackets
    return f'<m:d><m:dPr><m:begChr m:val="{beg}"/><m:endChr m:val="{end}"/><m:ctrlPr/></m:dPr><m:e>{e}</m:e></m:d>'

def m_bar(e):
    # bar over (like mean)
    return f'<m:acc><m:accPr><m:chr m:val="¯"/><m:ctrlPr/></m:accPr><m:e>{e}</m:e></m:acc>'

def m_hat(e):
    # hat over
    return f'<m:acc><m:accPr><m:chr m:val="^"/><m:ctrlPr/></m:accPr><m:e>{e}</m:e></m:acc>'

# Now build the specific formulas
f_sma = omath(
    m_r("SMA") + m_d(m_r("t")) + m_r("=") + 
    m_f(m_r("1"), m_r("k")) + 
    m_nary("∑", m_r("i=t-k+1"), m_r("t"), m_sub(m_r("y"), m_r("i")))
)

f_ema = omath(
    m_r("EMA") + m_d(m_r("t")) + m_r("=") + m_r("α") + m_sub(m_r("y"), m_r("t")) + m_r("+") +
    m_d(m_r("1-α")) + m_r("EMA") + m_d(m_r("t-1"))
)

f_z = omath(
    m_r("Z=") + m_f(m_r("x-μ"), m_r("σ"))
)

f_cond1 = omath(
    m_d(m_sub(m_r("y"), m_r("t")) + m_r("-") + m_sub(m_r("y"), m_r("t-1")), "|", "|") + m_r(">25 және ") + m_sub(m_r("y"), m_r("t")) + m_r(">70")
)
f_cond1b = omath(
    m_d(m_sub(m_r("y"), m_r("t")) + m_r("-") + m_sub(m_r("y"), m_r("t-1")), "|", "|") + m_r(">25, ") + m_sub(m_r("y"), m_r("t")) + m_r(">70")
)

f_cond2 = omath(
    m_d(m_sub(m_r("y"), m_r("t")) + m_r("-") + m_sub(m_r("y"), m_r("t-k"))) + m_r(">35 немесе ") + m_sub(m_r("y"), m_r("t")) + m_r(">90")
)
f_cond3 = omath(
    m_d(m_sub(m_r("y"), m_r("t")) + m_r("-") + m_sub(m_r("y"), m_r("t-k"))) + m_r(">20")
)

f_v = omath(
    m_r("V") + m_d(m_r("t")) + m_r("=clamp") + m_d(
        m_r("B∙R") + m_d(m_r("h")) + m_r("∙L") + m_d(m_r("id")) + m_r("+W") + m_d(m_r("t")) + m_r("+N") + m_d(m_r("t")) + m_r("∙") + m_sub(m_r("W"), m_r("f")) + m_r("+J") + m_d(m_r("t")) + m_r(", 0, 100")
    )
)

f_w = omath(
    m_r("W") + m_d(m_r("t")) + m_r("=5sin") + m_d(m_r("0.1t"))
)

f_j = omath(
    m_r("J=") + m_d(m_r("1-") + m_f(m_r("d"), m_r("r"))) + m_r("S") + m_sub(m_r("W"), m_r("f"))
)

f_yhat = omath(
    m_sub(m_hat(m_r("y")), m_r("t+1")) + m_r("=") + m_sub(m_r("y"), m_r("t"))
)

# Linear regression
term1 = m_d(m_sub(m_r("x"), m_r("i")) + m_r("-") + m_bar(m_r("x")))
term2 = m_d(m_sub(m_r("y"), m_r("i")) + m_r("-") + m_bar(m_r("y")))
f_a = omath(
    m_sub(m_r("b"), m_r("1")) + m_r("=") + m_f(
        m_nary("∑", "", "", term1 + term2),
        m_nary("∑", "", "", m_sup(term1, m_r("2")))
    )
)

f_b = omath(
    m_sub(m_r("b"), m_r("0")) + m_r("=") + m_bar(m_r("y")) + m_r("-") + m_sub(m_r("b"), m_r("1")) + m_bar(m_r("x"))
)

f_yhat_pred = omath(
    m_hat(m_r("y")) + m_d(m_r("t+h")) + m_r("=") + m_sub(m_r("b"), m_r("1")) + m_d(m_sub(m_r("x"), m_r("last")) + m_r("+h")) + m_r("+") + m_sub(m_r("b"), m_r("0"))
)

f_mae = omath(
    m_r("MAE=") + m_f(m_r("1"), m_r("n")) + m_nary("∑", "", "", m_d(m_sub(m_r("y"), m_r("i")) + m_r("-") + m_sub(m_hat(m_r("y")), m_r("i")), "|", "|"))
)

f_rmse = omath(
    m_r("RMSE=") + m_rad(
        m_f(m_r("1"), m_r("n")) + m_nary("∑", "", "", m_sup(m_d(m_sub(m_r("y"), m_r("i")) + m_r("-") + m_sub(m_hat(m_r("y")), m_r("i"))), m_r("2")))
    )
)

f_access = omath(m_r("is_accessible = true, has_steps = false, surface_type IN ('asphalt', 'concrete')"))
f_cost = omath(m_r("cost(edge) = distance × time_weight × (1 + barrier_penalty)"))

formula_map = {
    4129: f_sma,
    1957: f_ema,
    813: f_z,
    1641: f_cond1,
    2130: f_cond2,
    1040: f_cond3,
    2192: f_sma,
    7076: f_v,
    1884: f_w,
    1521: f_j,
    787: f_yhat,
    2062: f_sma,
    2207: f_ema,
    1714: f_a,
    717: f_b,
    1746: f_yhat_pred,
    1689: f_mae,
    2342: f_rmse,
    1418: f_cond1b,
    2018: f_cond2,
    1086: f_cond3,
    3275: f_access,
    4752: f_cost
}

doc = Document(doc_path)
replaced_count = 0

for p in doc.paragraphs:
    for run in p.runs:
        if 'drawing' in run._element.xml or 'pict' in run._element.xml:
            blips = run._element.xpath('.//a:blip')
            for blip in blips:
                rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if rId:
                    part = doc.part.related_parts[rId]
                    size = len(part.blob)
                    if size in formula_map:
                        omml_xml = formula_map[size]
                        run.clear()
                        try:
                            omath_element = parse_xml(omml_xml)
                            p._p.append(omath_element)
                            replaced_count += 1
                        except Exception as e:
                            print(f"Error parsing xml for size {size}: {e}")

doc.save(output_path)
print(f"Total OMML formulas replaced: {replaced_count}")
