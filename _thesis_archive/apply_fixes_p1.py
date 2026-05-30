# -*- coding: utf-8 -*-
import sys, io, re, shutil
from docx import Document

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = 'Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted.docx'
BACKUP = 'Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted_PRE_FIXES_BACKUP.docx'

# Create a backup before major changes
shutil.copy2(SRC, BACKUP)
print(f"Created backup: {BACKUP}")

doc = Document(SRC)

# Text Replacements Dictionary
replacements = {
    "көл секторында": "көлік секторында",
    "краудсорсинг директорларынан": "краудсорсинг деректерінен",
    "1-кестеден көрінгендей, бiздiн усынылатын А.И. Трафик жуйесi бiркатар манызды функцияларда - болу, аномалия анактау, АI усыныстар, ауа-райс факторларын ескеру - колданыстағы базацестерден ерекшелендi. Функционалдық алшақтық (функционалдық алшақтық) .": "1-кестеде көрсетілгендей, ұсынылып отырған AI Traffic жүйесі қолданыстағы баламалардан бірнеше маңызды функцияларымен (аномалияларды анықтау, AI ұсыныстары, ауа райы факторларын ескеру) ерекшеленеді.",
    "Маршрутты жоспарлау процесі - машиналық оқыту алгоритмдерінің пост-хок талдауы - болжамды аналитикалық парадигмалар бізге мұны істеуге мүмкіндік береді.": "Маршрутты жоспарлау және көлік ағынын болжау процестерінде машиналық оқыту алгоритмдері мен аналитикалық модельдер кеңінен қолданылады.",
    "Сен ұсынған құрылым диплом үшін өте орынды, және оны төмендегідей ашып жазуға болады.": "Жүйе құрылымын төмендегідей толығырақ қарастыруға болады.",
    "2.4.0 Инклюзивті маршруттау": "2.5 Инклюзивті маршруттау",
    "SMA(t)=1ki=t-k+1tyi": "SMA(t) = (1/k) ∑ y_i",
    "Z=x-μσ": "Z = (x - μ) / σ",
    "MAE=1n∑∣yi-yi∣": "MAE = (1/n) ∑ |y_i - ŷ_i|",
    "J=(1-dr)SWf": "J = (1 - d_r) * (S_W / f)",
    "SQLite, ал бұлттық өзара әрекеттесу үшін Supabase": "локальді өңдеу үшін PostgreSQL, ал бұлттық өзара әрекеттесу үшін Supabase (PostgreSQL)",
    "SQLite": "PostgreSQL",
    "wttr.in": "OpenWeatherMap",
    "1.2 миллион": "симуляцияланған 1.2 миллион",
    "Render.com бұлттық платформасында deploy етілген": "Render.com бұлттық платформасында орналастырылған",
}

print("=== Text Replacements ===")
replace_counts = {k: 0 for k in replacements}

for p in doc.paragraphs:
    for old_text, new_text in replacements.items():
        if old_text in p.text:
            # Replace in runs to preserve formatting where possible
            for run in p.runs:
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)
                    replace_counts[old_text] += 1
            # If not replaced in runs (split across runs), replace in text and clear runs (lossy but works)
            if old_text in p.text:
                p.text = p.text.replace(old_text, new_text)
                replace_counts[old_text] += 1

for k, v in replace_counts.items():
    if v > 0:
        print(f"Replaced: '{k[:20]}...' -> {v} times")

doc.save(SRC)
print(f"Saved: {SRC}")
