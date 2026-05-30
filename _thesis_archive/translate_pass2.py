# -*- coding: utf-8 -*-
"""
Екінші тур аудармасы — қалған орыс тіліндегі мәтіндерді аудару
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document(r'c:\Users\user\Downloads\ai_traffic_fullstack\Сулейменов_Алишер_ВТШНИК_КАЗАҚША.docx')

# Remaining translations
REMAINING = {
    "[ Скриншот приложения 1: Главный экран (Light/Dark mode) с картой ]":
        "[ Қосымшаның 1-скриншоты: Картасы бар Басты экран (Light/Dark режимі) ]",
    "[ Скриншот приложения 2: Экран построенного маршрута (откуда/куда) ]":
        "[ Қосымшаның 2-скриншоты: Құрылған маршрут экраны (қайдан/қайда) ]",
    "[ Скриншот приложения 3: Экран AI Советов с подсказками (Tips UI) ]":
        "[ Қосымшаның 3-скриншоты: AI Кеңестер экраны (Tips UI) ]",
    "[ Скриншот сайта 1: Landing Page веб-интерфейса (index.html) ]":
        "[ Сайттың 1-скриншоты: Веб-интерфейстің Landing Page беті (index.html) ]",
    "[ Скриншот сайта 2: Интерактивная веб-карта с маркерами (map.html) ]":
        "[ Сайттың 2-скриншоты: Маркерлері бар интерактивті веб-карта (map.html) ]",
    "[ Скриншот сайта 3: Панель администратора (admin.html) ]":
        "[ Сайттың 3-скриншоты: Әкімші панелі (admin.html) ]",
    "[ Скриншот приложения 4: Экран аутентификации PIN/FaceID ]":
        "[ Қосымшаның 4-скриншоты: PIN/FaceID аутентификация экраны ]",
}

# Replace in literature section
LIT_REPLACE = {
    "Научное издательство ЕНУ": "ЕҰУ ғылыми баспасы",
}

translated = 0
for p in doc.paragraphs:
    text = p.text.strip()
    if not text:
        continue
    
    # Direct match
    if text in REMAINING:
        kz = REMAINING[text]
        if len(p.runs) == 1:
            p.runs[0].text = kz
        elif len(p.runs) > 1:
            p.runs[0].text = kz
            for r in p.runs[1:]:
                r.text = ""
        translated += 1
        continue
    
    # Partial replacements (литература)
    for ru, kz in LIT_REPLACE.items():
        if ru in text:
            for run in p.runs:
                if ru in run.text:
                    run.text = run.text.replace(ru, kz)
                    translated += 1

print(f"Қосымша аударылды: {translated} параграф")

# Save
dst = r'c:\Users\user\Downloads\ai_traffic_fullstack\Сулейменов_Алишер_ВТШНИК_КАЗАҚША.docx'
doc.save(dst)
print(f"✅ Сақталды: {dst}")
