import re

def merge_presentation():
    with open('presentation.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where <div class="slides"> begins and where its direct children (<section>) are
    slides_div_match = re.search(r'(<div class="slides">\s*)', content)
    if not slides_div_match:
        print("Cannot find <div class='slides'>")
        return
        
    slides_start = slides_div_match.end()
    
    # Find all sections (slides)
    # Using regex to find <section>...</section> pairs without nesting them recursively
    # Since Reveal.js sections usually aren't nested in this specific file except for vertical slides,
    # but let's assume they are simple <section> tags.
    # Actually, a better way is to split by </section>
    sections_raw = re.findall(r'<section>.*?</section>', content, re.DOTALL)
    
    if len(sections_raw) < 30:
        print(f"Found only {len(sections_raw)} sections. Something is wrong.")
        return

    # Extract contents of slide-card for each slide
    slide_contents = []
    for sec in sections_raw:
        # Find inner content of <div class="slide-card">
        card_match = re.search(r'<div class="slide-card"[^>]*>(.*?)</div>\s*</section>', sec, re.DOTALL)
        if card_match:
            slide_contents.append(card_match.group(1).strip())
        else:
            # Maybe it doesn't have slide-card
            inner_match = re.search(r'<section>(.*?)</section>', sec, re.DOTALL)
            slide_contents.append(inner_match.group(1).strip() if inner_match else "")

    print(f"Parsed {len(slide_contents)} slide contents.")

    # We want 15 slides. Let's construct them.
    # Slide 1: Keep original, but replace QR with the one from the end.
    # Slide 37 has the big QR: <img src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https://github.com/alishoksu-coder/ai_traffics"
    
    slide1_html = slide_contents[0]
    slide1_html = re.sub(
        r'https://api\.qrserver\.com/v1/create-qr-code/\?size=150x150&data=https://alishoksu-coder\.github\.io/ai_traffics/',
        r'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://github.com/alishoksu-coder/ai_traffics',
        slide1_html
    )

    new_sections = []
    
    def wrap_section(content, is_grid=True):
        if is_grid:
            return f"""
            <section>
                <div class="slide-card" style="width: 98%; padding: 30px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start;">
                        {content}
                    </div>
                </div>
            </section>
            """
        else:
            return f"""
            <section>
                <div class="slide-card" style="width: 98%; padding: 30px;">
                    {content}
                </div>
            </section>
            """

    def shrink_headers(html_str):
        # make h2 -> h3, h4 -> h5 etc so it fits better side by side
        html_str = re.sub(r'<h2([^>]*)>', r'<h3\1 style="font-size: 1.5em; margin-bottom: 10px;">', html_str)
        html_str = re.sub(r'</h2>', r'</h3>', html_str)
        return html_str

    # Slide 1: Title
    new_sections.append(wrap_section(slide1_html, is_grid=False))

    # Slide 2: 1. Өзектілігі, Мәселелер және Аналогтар
    # Merge: 2 (index 1) + 3 (index 2) + 8 (index 7) + 9 (index 8)
    left_col = shrink_headers(slide_contents[1]) + "\n" + shrink_headers(slide_contents[2])
    right_col = shrink_headers(slide_contents[7]) + "\n" + shrink_headers(slide_contents[8])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 3: 2. Мақсат, Міндеттер және Зерттеу нысаны
    # Merge: 4 (index 3) + 5 (index 4) + 6 (index 5)
    left_col = shrink_headers(slide_contents[3]) + "\n" + shrink_headers(slide_contents[5])
    right_col = shrink_headers(slide_contents[4])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 4: 3. Технологиялар мен Жүйелік Архитектура
    # Merge: 7 (index 6) + 10 (index 9) + 11 (index 10) + 21 (index 20)
    left_col = shrink_headers(slide_contents[6]) + "\n" + shrink_headers(slide_contents[20])
    right_col = shrink_headers(slide_contents[9]) + "\n" + shrink_headers(slide_contents[10])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 5: 4. ML Болжау Архитектурасы және LSTM Нейрондық Желісі
    # Merge: 13 (index 12) + 19 (index 18) + 22 (index 21) + 24 (index 23)
    left_col = shrink_headers(slide_contents[21]) + "\n" + shrink_headers(slide_contents[23])
    right_col = shrink_headers(slide_contents[12]) + "\n" + shrink_headers(slide_contents[18])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 6: 5. Модельдерді Бағалау және Нәтижелері
    # Merge: 12 (index 11) + 20 (index 19) + 26 (index 25)
    left_col = shrink_headers(slide_contents[25])
    right_col = shrink_headers(slide_contents[11]) + "\n" + shrink_headers(slide_contents[19])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 7: 6. «Цифрлық Егіз» (Digital Twin) және Симулятор
    # Merge: 14 (index 13) + 18 (index 17)
    left_col = shrink_headers(slide_contents[13])
    right_col = shrink_headers(slide_contents[17])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 8: 7. Аномалияларды Анықтау және Жол Апаттары
    # Merge: 16 (index 15) + 17 (index 16)
    left_col = shrink_headers(slide_contents[15])
    right_col = shrink_headers(slide_contents[16])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 9: 8. AI-Экожүйесі (Multimodal & Smart Parking)
    # Merge: 15 (index 14)
    new_sections.append(wrap_section(shrink_headers(slide_contents[14]), is_grid=False))

    # Slide 10: 9. Деректер: Оқыту, Белгілер және Қауіпсіздік
    # Merge: 23 (index 22) + 25 (index 24) + 33 (index 32)
    left_col = shrink_headers(slide_contents[22]) + "\n" + shrink_headers(slide_contents[32])
    right_col = shrink_headers(slide_contents[24])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 11: 10. Мобильді Интерфейс, Дауыспен іздеу және Краудсорсинг
    # Merge: 27 (index 26) + 28 (index 27) + 29 (index 28) + 30 (index 29)
    left_col = shrink_headers(slide_contents[26]) + "\n" + shrink_headers(slide_contents[28])
    right_col = shrink_headers(slide_contents[27]) + "\n" + shrink_headers(slide_contents[29])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 12: 11. Web Admin Panel (Мониторинг)
    # Keep: 31 (index 30)
    new_sections.append(wrap_section(shrink_headers(slide_contents[30]), is_grid=False))

    # Slide 13: 12. Видео-Демонстрация
    # Keep: 32 (index 31)
    new_sections.append(wrap_section(shrink_headers(slide_contents[31]), is_grid=False))

    # Slide 14: 13. Тәжірибелік маңызы және Даму перспективалары
    # Merge: 35 (index 34) + 37 (index 36)
    left_col = shrink_headers(slide_contents[34])
    right_col = shrink_headers(slide_contents[36])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Slide 15: 14. Қорытынды және Әдебиеттер
    # Merge: 36 (index 35) + 34 (index 33)
    left_col = shrink_headers(slide_contents[35])
    right_col = shrink_headers(slide_contents[33])
    new_sections.append(wrap_section(f"<div>{left_col}</div><div>{right_col}</div>"))

    # Reconstruct presentation.html
    # Find exact start of sections
    start_idx = content.find('<section>')
    # Find exact end of sections
    end_idx = content.rfind('</section>') + len('</section>')

    final_content = content[:start_idx] + "\n".join(new_sections) + "\n" + content[end_idx:]

    # Remove the large font sizes inline to prevent breaking side-by-side
    final_content = re.sub(r'font-size:\s*2\.\d+em;', 'font-size: 1.4em;', final_content)

    with open('presentation.html', 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print("Done! Merged into 15 slides.")

if __name__ == '__main__':
    merge_presentation()
