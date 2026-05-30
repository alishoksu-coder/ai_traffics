# -*- coding: utf-8 -*-
"""
PASS 2: Файлды қайта ашып, суреттер мен кестелерді нөмірлеу.
XML body ішінде тікелей жүру арқылы дұрыс орынға қосу.
"""
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from lxml import etree

FILE = 'Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted.docx'
doc = Document(FILE)
body = doc.element.body

# Сурет сипаттамалары
fig_descs = [
    'Навигациялық сервистерді салыстырмалы талдау',
    'Аномалия детекциясының статистикалық және эвристикалық тәсілдері',
    'AI Traffic жүйесінде қолданылатын технологиялар стегі',
    'AI Traffic жүйесінің деректер ағыны диаграммасы (DFD Level-0)',
    'AI Traffic жүйесінің компонент диаграммасы',
    'AI Traffic деректер қорының ER-диаграммасы',
    'AI Traffic жүйесінің архитектуралық диаграммасы',
    'REST API эндпоинттер спецификациясы',
    'AI Traffic серверлік модульдерінің UML класс диаграммасы',
    'AI Traffic мобильді қосымшасының Glassmorphism интерфейсі',
    'Мобильді қосымшаның негізгі экрандары',
    'Мобильді қосымшаның қосымша экрандары',
    'Google Maps интеграциясы: маршрут құру мен навигация',
    'Веб-Dashboard интерфейсі',
    'Веб-Dashboard аналитикалық графиктері',
    'Мобильді қосымшаның интерфейс скриншоты',
    'API жүктеме тестінің нәтижелері',
    'TipsScreen — аналитикалық мазмұны бар экран',
    'Аутентификация модулінің интерфейсі',
    'Веб-Dashboard диспетчерлік панелі',
    'Болжамдық модельдердің MAE/RMSE салыстыру графигі',
    'Қосымша А — код фрагменті (1)',
    'Қосымша А — код фрагменті (2)',
    'Қосымша А — код фрагменті (3)',
    'Қосымша А — код фрагменті (4)',
    'Қосымша А — код фрагменті (5)',
]

tbl_descs = [
    'Навигациялық сервистерді салыстыру',
    'Болжау алгоритмдерінің сипаттамасы',
    'AI Traffic жүйесінің сегменттер кестесі',
    'Мобильді қосымшаның модульдік құрылымы',
    'REST API эндпоинттер тізімі',
    'AI Traffic жүйесінің техникалық өнімділік метрикалары',
    'Болжамдық модельдердің дәлдігін салыстыру (horizon=30)',
    'Болжамдық модельдердің дәлдігі (horizon=60)',
    'Мобильді қосымшаның функционалдық тестілеуі',
    'AI Traffic жүйесінің мониторинг көрсеткіштері',
    'Экономикалық тиімділік көрсеткіштері',
    'Нәтижелерді халықаралық зерттеулермен салыстыру',
]

def make_caption_element(text, bold=False, italic=False, center=True):
    """XML деңгейінде подпись параграфы жасау."""
    nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    p = etree.SubElement(body, qn('w:p'))
    
    # Параграф properties (alignment)
    if center:
        pPr = etree.SubElement(p, qn('w:pPr'))
        jc = etree.SubElement(pPr, qn('w:jc'))
        jc.set(qn('w:val'), 'center')
    
    # Run
    r = etree.SubElement(p, qn('w:r'))
    rPr = etree.SubElement(r, qn('w:rPr'))
    
    # Font
    rFonts = etree.SubElement(rPr, qn('w:rFonts'))
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    
    # Size (12pt = 24 half-points)
    sz = etree.SubElement(rPr, qn('w:sz'))
    sz.set(qn('w:val'), '24')
    szCs = etree.SubElement(rPr, qn('w:szCs'))
    szCs.set(qn('w:val'), '24')
    
    if bold:
        b = etree.SubElement(rPr, qn('w:b'))
    if italic:
        i_el = etree.SubElement(rPr, qn('w:i'))
    
    # Text
    t = etree.SubElement(r, qn('w:t'))
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    
    return p

# ══════════════════════════════════════
# Мазмұн басталатын жерді табу
# ══════════════════════════════════════
# Кіріспе параграфын табу (CS=190 шамасында)
content_started = False
para_count = 0

print("PASS 2: XML body ішінде нөмірлеу")
print()

fig_num = 0
tbl_num = 0
elements = list(body)  # Snapshot of current body children

for elem in elements:
    if elem.tag == qn('w:p'):
        para_count += 1
        if para_count >= 190:
            content_started = True
    
    if not content_started:
        continue
    
    # ── СУРЕТ: <w:p> ішінде <w:drawing> бар ма? ──
    if elem.tag == qn('w:p'):
        drawings = elem.findall('.//' + qn('w:drawing'))
        if drawings:
            fig_num += 1
            desc = fig_descs[fig_num-1] if fig_num <= len(fig_descs) else ''
            label = f'Сурет {fig_num} – {desc}' if desc else f'Сурет {fig_num}'
            
            # Подпись параграфы жасау
            cap = make_caption_element(label, italic=True)
            
            # Суреттен КЕЙІН (астына) қою
            elem.addnext(cap)
            
            print(f"  Сурет {fig_num} – {desc[:50]}")
    
    # ── КЕСТЕ: <w:tbl> ──
    elif elem.tag == qn('w:tbl'):
        tbl_num += 1
        desc = tbl_descs[tbl_num-1] if tbl_num <= len(tbl_descs) else ''
        
        # Кесте N — бірінші жол
        cap1 = make_caption_element(f'Кесте {tbl_num}', bold=True)
        elem.addprevious(cap1)
        
        # Сипаттама — екінші жол
        if desc:
            cap2 = make_caption_element(desc)
            elem.addprevious(cap2)
        
        print(f"  Кесте {tbl_num} – {desc[:50]}")

print(f"\n  Жалпы: {fig_num} сурет, {tbl_num} кесте")

doc.save(FILE)
print(f"✅ Сақталды: {FILE}")
