import re

file_path = "presentation.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    (
        '<!-- NEW SLIDE: Specific Problems Solved (1.1) -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.2em;">Қазақстан үшін маңызды мәселелер</h2>',
        '<!-- 2. Қазақстан үшін маңызды мәселелер -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.2em;">2. Қазақстан үшін маңызды мәселелер</h2>'
    ),
    (
        '<!-- 8. Жүйенің Контейнерлік Архитектурасы -->\n            <section>\n                <div class="slide-card container-slide">\n                    <h2 style="font-size: 2em; text-align: center; margin-bottom: 15px;">8. Жүйенің Контейнерлік',
        '<!-- 3. Жүйенің Контейнерлік Архитектурасы -->\n            <section>\n                <div class="slide-card container-slide">\n                    <h2 style="font-size: 2em; text-align: center; margin-bottom: 15px;">3. Жүйенің Контейнерлік'
    ),
    (
        '<!-- 11.5 Цифрлық егіз (Digital Twin) -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">11.5 «Цифрлық Егіз» (Digital Twin) Режимі</h2>',
        '<!-- 4. Цифрлық егіз (Digital Twin) -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">4. «Цифрлық Егіз» (Digital Twin) Режимі</h2>'
    ),
    (
        '<!-- 13. Z-Score Аномалиялар және AR-Интеграция -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">13. Аномалияларды Анықтау & AR Интеграциясы</h2>',
        '<!-- 5. Аномалияларды Анықтау & AR Интеграциясы -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">5. Аномалияларды Анықтау & AR Интеграциясы</h2>'
    ),
    (
        '<!-- 12. Аномалияларды анықтау (Z-Score) -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">12. Жол апаттары мен аномалияларды детекторлау</h2>',
        '<!-- 6. Жол апаттары мен аномалияларды детекторлау -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">6. Жол апаттары мен аномалияларды детекторлау</h2>'
    ),
    (
        '<!-- 14. ML Алгоритм: LSTM Нейрондық Желісі -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">14. ML Алгоритм: LSTM Нейрондық Желісі</h2>',
        '<!-- 7. ML Алгоритм: LSTM Нейрондық Желісі -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">7. ML Алгоритм: LSTM Нейрондық Желісі</h2>'
    ),
    (
        '<!-- 17. Болжамдау Метрикалары -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.5em;">17. Болжаудың Математикалық Метрикалары</h2>',
        '<!-- 8. Болжамдау Метрикалары -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.5em;">8. Болжаудың Математикалық Метрикалары</h2>'
    ),
    (
        '<!-- 18. NLP: Дауыстық басқару және ИИ -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">18. NLP: Дауыспен интеллектуалды іздеу</h2>',
        '<!-- 9. NLP: Дауыстық басқару және ИИ -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">9. NLP: Дауыспен интеллектуалды іздеу</h2>'
    ),
    (
        '<!-- 19. Web Admin: Қалалық Мониторинг -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">20. Web Admin Panel (Мониторинг)</h2>',
        '<!-- 10. Web Admin: Қалалық Мониторинг -->\n            <section>\n                <div class="slide-card">\n                    <h2 style="font-size: 2.8em;">10. Web Admin Panel (Мониторинг)</h2>'
    ),
]

for old_str, new_str in replacements:
    if old_str in content:
        content = content.replace(old_str, new_str)
    else:
        print(f"Warning: Could not find \n{old_str}\n")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
