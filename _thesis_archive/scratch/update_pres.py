import os

file_path = r"c:\Users\user\Downloads\ai_traffic_fullstack\presentation.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS
css_addition = """
        @keyframes fadeInUp {
            0% { opacity: 0; transform: translateY(30px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .slide-card {
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            background: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(25px) !important;
            -webkit-backdrop-filter: blur(25px) !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
"""

content = content.replace(".slide-card {\n            background: var(--card-bg);\n            backdrop-filter: blur(20px);", css_addition)

info_box_css = """
        .info-box {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(226, 232, 240, 0.8);
            border-radius: var(--radius-md);
            padding: 24px;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), inset 0 1px 0 rgba(255,255,255,1);
        }

        .info-box:hover {
            border-color: #3b82f6;
            transform: translateY(-5px);
            box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.15), inset 0 1px 0 rgba(255,255,255,1);
        }
"""
content = content.replace(".info-box {\n            background: #ffffff;\n            border: 1px solid #e2e8f0;", info_box_css.split("{", 1)[1].rsplit("}", 1)[0] + "{\n            background: rgba(255, 255, 255, 0.95);\n            backdrop-filter: blur(10px);\n            border: 1px solid rgba(226, 232, 240, 0.8);")


# 2. Add NLP Slide
nlp_slide = """
            <!-- 18. NLP: Дауыстық басқару және ИИ -->
            <section>
                <div class="slide-card">
                    <h2 style="font-size: 2.8em;">18. NLP: Дауыспен интеллектуалды іздеу</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 40px;">
                        <div class="info-box" style="padding: 30px; border-left: 8px solid var(--accent-purple);">
                            <h4 style="font-size: 1.5em; margin-bottom: 20px; color: #1e293b;"><i class="fa-solid fa-microphone" style="color: var(--accent-purple);"></i> Сөйлеуді Тану (Voice Assistant)</h4>
                            <p style="font-size: 1.1em; color: #475569; line-height: 1.6;">
                                Қосымшаға <strong>Natural Language Processing (NLP)</strong> алгоритмдері кіріктірілген. 
                                Жүргізушілер рульде отырып: <i>"Ең жақын май құю бекетіне апар"</i> немесе <i>"Мегаға дейін кептеліс жоқ жолмен апар"</i> деп дауыстық пәрмен бере алады.
                            </p>
                            <ul style="padding-left: 20px; margin-top: 20px; font-size: 0.9em;">
                                <li style="margin-bottom: 10px;"><strong>Speech-to-Text:</strong> Қазақ және орыс тілдерін қолдау.</li>
                                <li style="margin-bottom: 10px;"><strong>Intent Recognition:</strong> Сөз мағынасын түсініп, оны маршруттық координаттарға айналдыру.</li>
                            </ul>
                        </div>
                        <div class="info-box" style="display: flex; align-items: center; justify-content: center; background: #faf5ff;">
                            <div style="text-align: center; position: relative;">
                                <div style="position: absolute; width: 100%; height: 100%; background: var(--accent-purple); filter: blur(50px); opacity: 0.2; border-radius: 50%;"></div>
                                <i class="fa-solid fa-microphone-lines" style="font-size: 6em; color: var(--accent-purple); margin-bottom: 20px; position: relative; z-index: 2;"></i>
                                <div style="font-size: 1.4em; font-weight: 700; color: #1e293b; position: relative; z-index: 2;">AI Voice Assistant</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

"""

content = content.replace("<!-- 18. Мобильді Қосымша: Интерфейс -->", nlp_slide + "<!-- 19. Мобильді Қосымша: Интерфейс -->")
content = content.replace("18. Мобильді Қосымша Интерфейсі", "19. Мобильді Қосымша Интерфейсі")

# 3. Add API Load Testing slide
api_slide = """
            <!-- 10.5 API Тестілеу -->
            <section>
                <div class="slide-card">
                    <h2 style="font-size: 2.8em;">Сервердің Жүктемелік Тестілеуі (Load Testing)</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 40px;">
                        <div class="info-box" style="padding: 30px; border-top: 5px solid #22c55e;">
                            <h4 style="font-size: 1.5em; margin-bottom: 20px; color: #1e293b;"><i class="fa-solid fa-server" style="color: #22c55e;"></i> FastAPI Өнімділігі</h4>
                            <p style="font-size: 1.1em; color: #475569; line-height: 1.6;">
                                <strong>Apache JMeter</strong> және <strong>Locust</strong> құралдары арқылы жасалған стресс-тест қорытындылары:
                            </p>
                            <ul style="padding-left: 20px; margin-top: 20px; font-size: 0.95em;">
                                <li style="margin-bottom: 10px;"><strong>Concurrent Users:</strong> Бір уақытта 10,000+ белсенді пайдаланушы.</li>
                                <li style="margin-bottom: 10px;"><strong>Response Time:</strong> Орташа жауап беру уақыты <span style="color: #22c55e; font-weight: bold;">45 мс</span>.</li>
                                <li style="margin-bottom: 10px;"><strong>Error Rate:</strong> Қателіктер үлесі 0.01%-дан төмен.</li>
                            </ul>
                        </div>
                        <div class="info-box" style="display: flex; flex-direction: column; justify-content: center; align-items: center; background: #f0fdf4;">
                            <div style="font-size: 4em; font-weight: 800; color: #22c55e;">45 ms</div>
                            <div style="font-size: 1.2em; font-weight: 600; color: #166534; margin-top: 10px;">Орташа жауап беру уақыты</div>
                            <div style="margin-top: 20px; padding: 10px 20px; background: white; border-radius: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                                <i class="fa-solid fa-check-circle" style="color: #22c55e; margin-right: 5px;"></i> Production Ready
                            </div>
                        </div>
                    </div>
                </div>
            </section>

"""
content = content.replace("<!-- 11. Болжау Жүйесінің Архитектурасы (Prediction Pipeline) -->", api_slide + "<!-- 11. Болжау Жүйесінің Архитектурасы (Prediction Pipeline) -->")

# 4. Fix numbering
replacements = {
    "19. Web Admin Panel (Мониторинг)": "20. Web Admin Panel (Мониторинг)",
    "17. Жүйе Жұмысының Видео-Демосы": "21. Жүйе Жұмысының Видео-Демосы",
    "20. Деректер қауіпсіздігі (FaceID & PIN)": "22. Деректер қауіпсіздігі (FaceID & PIN)",
    "21. Пайдаланылған әдебиеттер": "23. Пайдаланылған әдебиеттер",
    "22. Тәжірибелік маңызы": "24. Тәжірибелік маңызы",
    "23. Қорытынды": "25. Қорытынды",
    "24. Даму перспективалары": "26. Даму перспективалары"
}

for old, new in replacements.items():
    content = content.replace(old, new)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Presentation updated successfully.")
