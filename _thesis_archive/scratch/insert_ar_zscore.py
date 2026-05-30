import codecs

with codecs.open('../presentation.html', 'r', 'utf-8') as f:
    content = f.read()

marker = '<!-- 12. AI-Экожүйе: Multimodal & Smart Parking -->'

# Find the start of 12
start_idx = content.find(marker)
if start_idx == -1:
    print("Could not find marker 12")
    exit(1)

# Find the next </section> after marker
end_idx = content.find('</section>', start_idx)
if end_idx == -1:
    print("Could not find </section> after marker")
    exit(1)

insert_idx = end_idx + len('</section>')

new_slide = """

            <!-- 13. Z-Score Аномалиялар және AR-Интеграция -->
            <section>
                <div class="slide-card">
                    <h2 style="font-size: 2.8em;">13. Аномалияларды Анықтау & AR Интеграциясы</h2>
                    <p style="font-size: 1.1em; color: var(--secondary-text); margin-bottom: 30px;">
                        Жүйенің инновациялық модульдері кептелістердің табиғатын (қалыпты "час пик" немесе күтпеген апат) ажыратуға және оны заманауи форматта визуалдауға мүмкіндік береді.
                    </p>
                    
                    <div style="display: grid; grid-template-columns: 1.1fr 1fr; gap: 30px;">
                        <!-- Z-Score Anomaly Detection -->
                        <div class="info-box" style="border-top: 5px solid #ef4444; padding: 25px;">
                            <h4 style="font-size: 1.3em; margin-bottom: 15px;"><i class="fa-solid fa-chart-line" style="color: #ef4444;"></i> Z-Score Аномалия Детекторы</h4>
                            <div style="font-size: 0.85em; background: rgba(239, 68, 68, 0.05); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #ef4444;">
                                Статистикалық <strong>Z-Score</strong> алгоритмі қалыпты көлік ағынын күтпеген жағдайлардан (ДТП, ауа райы аномалиясы) автоматты түрде ажыратады.
                            </div>
                            <ul style="font-size: 0.8em; padding-left: 20px;">
                                <li style="margin-bottom: 8px;"><strong>Смарт-ескертулер:</strong> Жай кептеліс үшін емес, тек ауытқу болғанда ғана "Участок нестабилен" деген Push-хабарлама келеді.</li>
                                <li style="margin-bottom: 8px;">Статистикалық нормадан (Mean + 3 StdDev) ауытқуды іздеу.</li>
                                <li style="color: var(--accent-blue);"><i class="fa-solid fa-bell"></i> Endpoint: <code>/traffic/recommendation</code></li>
                            </ul>
                        </div>
                        
                        <!-- AR Visualization -->
                        <div class="info-box" style="border-top: 5px solid #a855f7; padding: 25px;">
                            <h4 style="font-size: 1.3em; margin-bottom: 15px;"><i class="fa-solid fa-vr-cardboard" style="color: #a855f7;"></i> AR-Интеграцияға Дайындық</h4>
                            <div style="font-size: 0.85em; background: rgba(168, 85, 247, 0.05); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #a855f7;">
                                Жүйе <strong>Толықтырылған Шындық (AR)</strong> қосымшаларына арнап көшелердің 3D-кеңістіктегі дағдарыс нүктелерін береді.
                            </div>
                            <ul style="font-size: 0.8em; padding-left: 20px;">
                                <li style="margin-bottom: 8px;">Камера арқылы қызылмен подсветить етілетін <code>"critical"</code> зоналар (мысалы: 3 км/сағ).</li>
                                <li style="margin-bottom: 8px;">Көлік камераларымен немесе смартфонмен тікелей жұмыс жасау мүмкіндігі.</li>
                                <li style="color: var(--accent-purple);"><i class="fa-solid fa-map-pin"></i> Endpoint: <code>/traffic/ar_points</code></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>"""

new_file = content[:insert_idx] + new_slide + content[insert_idx:]

with codecs.open('../presentation.html', 'w', 'utf-8') as f:
    f.write(new_file)
print("Successfully inserted AR & Z-Score slide.")
