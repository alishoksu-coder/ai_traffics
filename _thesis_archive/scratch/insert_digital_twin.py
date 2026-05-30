import codecs

with codecs.open('../presentation.html', 'r', 'utf-8') as f:
    content = f.read()

marker11 = '<!-- 11. Болжау Жүйесінің Архитектурасы (Prediction Pipeline) -->'

# Find the start of 11
start_idx = content.find(marker11)
if start_idx == -1:
    print("Could not find marker 11")
    exit(1)

# Find the next </section> after marker11
end_idx = content.find('</section>', start_idx)
if end_idx == -1:
    print("Could not find </section> after marker 11")
    exit(1)

insert_idx = end_idx + len('</section>')

new_slide = """

            <!-- 11.5 Цифрлық егіз (Digital Twin) -->
            <section>
                <div class="slide-card">
                    <h2 style="font-size: 2.8em;">11.5 «Цифрлық Егіз» (Digital Twin) Режимі</h2>
                    <p style="font-size: 1.1em; color: var(--secondary-text); margin-bottom: 30px;">
                        Жүйе тек трафикті бақылап қана қоймай, <strong>What-If (Не болса, егер...)</strong> сценарийлерін модельдеуге мүмкіндік береді. Бұл қала әкімдігі мен диспетчерлерге арналған стратегиялық құрал.
                    </p>
                    
                    <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 40px;">
                        <div class="info-box" style="border-top: 5px solid var(--accent-purple);">
                            <h4 style="font-size: 1.3em; margin-bottom: 20px;"><i class="fa-solid fa-code-merge" style="color: var(--accent-purple);"></i> Жолды жасанды жабу симуляциясы</h4>
                            <div style="background: #0f172a; border-radius: 12px; padding: 20px; margin-bottom: 20px; font-family: 'JetBrains Mono', monospace; font-size: 0.85em; color: #38bdf8;">
                                <span style="color: #cbd5e1;">POST</span> /traffic/simulate_closure<br>
                                {<br>
                                &nbsp;&nbsp;<span style="color: #a3e635;">"lat"</span>: 51.1283,<br>
                                &nbsp;&nbsp;<span style="color: #a3e635;">"lon"</span>: 71.4304,<br>
                                &nbsp;&nbsp;<span style="color: #a3e635;">"duration_min"</span>: 120<br>
                                }
                            </div>
                            <ul style="font-size: 0.85em; padding-left: 20px;">
                                <li style="margin-bottom: 10px;"><strong>Жол жөндеу жұмыстары:</strong> Көшенің бір бөлігін жапқанда, балама маршруттардың жүктемесін алдын ала көру.</li>
                                <li style="margin-bottom: 10px;"><strong>Марафондар мен мерекелер:</strong> Қала орталығындағы іс-шаралардың трафикке әсерін есептеу.</li>
                                <li style="margin-bottom: 0;"><strong>Төтенше жағдайлар (ДТП):</strong> Апат болған кезде трафикті қалай дұрыс бағыттау керектігін анықтау.</li>
                            </ul>
                        </div>
                        
                        <div style="display: flex; flex-direction: column; gap: 20px;">
                            <div class="info-box" style="background: rgba(59, 130, 246, 0.05); padding: 25px; border-left: 5px solid var(--accent-blue); display: flex; align-items: center; justify-content: space-between;">
                                <div>
                                    <div style="font-size: 0.9em; color: #64748b; margin-bottom: 5px;">Модельдеу дәлдігі</div>
                                    <div style="font-size: 1.8em; font-weight: bold; color: var(--accent-blue);">92%</div>
                                </div>
                                <i class="fa-solid fa-bullseye" style="font-size: 3em; color: rgba(59, 130, 246, 0.3);"></i>
                            </div>
                            
                            <div class="info-box" style="background: rgba(16, 185, 129, 0.05); padding: 25px; border-left: 5px solid #10b981; display: flex; align-items: center; justify-content: space-between;">
                                <div>
                                    <div style="font-size: 0.9em; color: #64748b; margin-bottom: 5px;">Динамикалық қайта есептеу</div>
                                    <div style="font-size: 1.8em; font-weight: bold; color: #10b981;">Нақты уақыт</div>
                                </div>
                                <i class="fa-solid fa-bolt" style="font-size: 3em; color: rgba(16, 185, 129, 0.3);"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </section>"""

new_file = content[:insert_idx] + new_slide + content[insert_idx:]

with codecs.open('../presentation.html', 'w', 'utf-8') as f:
    f.write(new_file)
print("Successfully inserted Digital Twin slide.")
