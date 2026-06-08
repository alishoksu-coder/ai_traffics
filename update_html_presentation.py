import os

def update_presentation():
    with open('presentation.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    title_end_index = -1
    for i in range(len(lines)):
        # Look for the end of the title slide, which is the FIRST </section>
        if '</section>' in lines[i]:
            title_end_index = i
            break
            
    last_section_index = -1
    for i in range(len(lines) - 1, -1, -1):
        if '</section>' in lines[i]:
            last_section_index = i
            break

    if title_end_index == -1 or last_section_index == -1:
        print("Error: Could not find <section> boundaries.")
        return

    new_slides = """
            <!-- 2. Актуальность & Аналоги (Relevance & Analogs) -->
            <section>
                <div class="slide-card">
                    <h2>1. Өзектілігі және қолданыстағы шешімдерді талдау</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 20px;">
                        <div>
                            <div class="info-box" style="margin-bottom: 20px;">
                                <h4 style="font-size: 1.1em; color: var(--accent-blue);"><i class="fa-solid fa-triangle-exclamation"></i> Мәселенің өзектілігі</h4>
                                <ul style="font-size: 0.85em;">
                                    <li>Қазақстанның ірі қалаларында көлік кептелісі критикалық деңгейге жетті.</li>
                                    <li>Қолданыстағы жүйелер (Сергек) тек айыппұлға бағытталған.</li>
                                    <li>Нақты уақыттағы динамикалық болжау және «Цифрлық Егіз» архитектурасы жоқ.</li>
                                </ul>
                            </div>
                            
                            <div class="info-box">
                                <h4 style="font-size: 1.1em; color: var(--accent-purple);"><i class="fa-solid fa-scale-balanced"></i> Аналогтармен салыстыру</h4>
                                <table class="modern-table" style="font-size: 0.7em; width: 100%;">
                                    <tr>
                                        <th style="color: var(--accent-blue);">Параметр</th>
                                        <th>2GIS</th>
                                        <th>Сергек</th>
                                        <th style="color: var(--accent-blue);">AI Traffic (Біз)</th>
                                    </tr>
                                    <tr>
                                        <td>AI Болжау (60 мин)</td>
                                        <td>Шектеулі</td>
                                        <td>Жоқ</td>
                                        <td><strong>Жоғары (LSTM)</strong></td>
                                    </tr>
                                    <tr>
                                        <td>Аномалия детекторы</td>
                                        <td>Жоқ</td>
                                        <td>Жартылай</td>
                                        <td><strong>Автоматты (Z-Score)</strong></td>
                                    </tr>
                                    <tr>
                                        <td>Антистресс/Кедергісіз</td>
                                        <td>Жоқ</td>
                                        <td>Жоқ</td>
                                        <td><strong>Толық қолдау</strong></td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                        <div class="info-box" style="display: flex; flex-direction: column; justify-content: center; align-items: center; background: #eff6ff;">
                            <h4 style="font-size: 1em; color: var(--primary-text); margin-bottom: 15px;">Астана қаласының ағымдағы кептеліс картасы (Мысал)</h4>
                            <img src="road_graph.png" alt="Traffic Map" style="max-width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                            <p style="font-size: 0.7em; color: var(--secondary-text); margin-top: 10px; text-align: center;">Қызыл аймақтар - критикалық кептеліс нүктелері</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 3. Мақсат және Зерттеу міндеттері (Merged 2 and 4) -->
            <section>
                <div class="slide-card">
                    <h2>2. Жұмыс мақсаты және зерттеу міндеттері</h2>
                    <div class="info-box" style="margin-top: 10px; background: rgba(37, 99, 235, 0.05); border-left: 4px solid var(--accent-blue);">
                        <h4 style="font-size: 1.1em; color: var(--accent-blue);"><i class="fa-solid fa-bullseye"></i> Зерттеу мақсаты</h4>
                        <p style="font-size: 0.9em;">LSTM нейрондық желілік архитектурасы негізінде қалалық трафикті нақты уақыт режимінде мониторингтеуге және кептелісті алдын ала болжауға мүмкіндік беретін кешенді интеллектуалды AI-жүйесін әзірлеу.</p>
                    </div>

                    <h4 style="font-size: 1.1em; color: var(--primary-text); margin-top: 25px;"><i class="fa-solid fa-list-check"></i> Негізгі міндеттер (Architecture & Software Engineering)</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                        <div class="info-box" style="padding: 15px;">
                            <h5 style="color: var(--accent-blue); margin-bottom: 5px;">1. Backend & DB</h5>
                            <p style="font-size: 0.75em; margin: 0;">Backend (FastAPI, PostGIS) және интеграциялық API шлюздерін жобалау.</p>
                        </div>
                        <div class="info-box" style="padding: 15px;">
                            <h5 style="color: var(--accent-purple); margin-bottom: 5px;">2. AI & ML</h5>
                            <p style="font-size: 0.75em; margin: 0;">Уақыттық қатарларды талдау үшін LSTM (PyTorch) моделін оқыту.</p>
                        </div>
                        <div class="info-box" style="padding: 15px;">
                            <h5 style="color: #10b981; margin-bottom: 5px;">3. Frontend & Mobile</h5>
                            <p style="font-size: 0.75em; margin: 0;">Cross-platform Мобильді қосымша (Flutter) және Web Dashboard жасау.</p>
                        </div>
                        <div class="info-box" style="padding: 15px;">
                            <h5 style="color: #f59e0b; margin-bottom: 5px;">4. Digital Twin</h5>
                            <p style="font-size: 0.75em; margin: 0;">Кептеліс «Цифрлық Егізін» және смарт-маршруттауды іске асыру.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 4. Архитектура және ML Функциялары (Side-by-side) -->
            <section>
                <div class="slide-card">
                    <h2>3. Жүйе Архитектурасы және ML Алгоритмдері</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 10px;">
                        <div class="info-box">
                            <h4 style="font-size: 1.1em; color: var(--accent-blue); margin-bottom: 15px;"><i class="fa-solid fa-code"></i> ML Алгоритмі (Функциялар)</h4>
                            
                            <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0;">
                                <strong style="color: var(--accent-purple); font-family: monospace; font-size: 0.9em;">predict_future(history)</strong>
                                <p style="font-size: 0.75em; margin: 5px 0 0 0;">Кіріс: Соңғы 12 нүкте. Процесс: PyTorch тензорлары. Шығыс: 60 минутқа болжам.</p>
                            </div>
                            
                            <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0;">
                                <strong style="color: var(--accent-purple); font-family: monospace; font-size: 0.9em;">predict_ema(series)</strong>
                                <p style="font-size: 0.75em; margin: 5px 0 0 0;">Экспоненциалды жылжымалы орташа мән. Күрт өзгерістерге жылдам реакция.</p>
                            </div>

                            <div>
                                <strong style="color: var(--accent-purple); font-family: monospace; font-size: 0.9em;">detect_anomaly(series)</strong>
                                <p style="font-size: 0.75em; margin: 5px 0 0 0;">Z-Score арқылы ауытқуды іздейді. 'Critical' деңгейінде дабыл қағады.</p>
                            </div>
                        </div>
                        <div class="info-box" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                            <h4 style="font-size: 1.1em; color: var(--primary-text); margin-bottom: 15px;"><i class="fa-solid fa-sitemap"></i> Жүйелік Архитектура</h4>
                            <img src="diag_architecture.png" alt="Architecture" style="max-width: 100%; border-radius: 8px;">
                        </div>
                    </div>
                </div>
            </section>

            <!-- 5. Болжау Нәтижелері және Математика (Side-by-side) -->
            <section>
                <div class="slide-card">
                    <h2>4. Модель нәтижелері және Математикалық негіздеме</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 10px;">
                        <div class="info-box">
                            <h4 style="font-size: 1.1em; color: var(--accent-blue); margin-bottom: 15px;"><i class="fa-solid fa-square-root-variable"></i> Метрикалар мағынасы</h4>
                            
                            <div style="margin-bottom: 15px; padding: 10px; background: #f8fafc; border-radius: 8px;">
                                <strong style="color: #10b981;">MAE (Mean Absolute Error)</strong>
                                <p style="font-size: 0.75em; margin: 5px 0 0 0;">Болжам мен нақты деректің абсолютті ауытқуы. MAE = 0.08 дегеніміз модель 8% ғана қателеседі деген сөз.</p>
                            </div>
                            
                            <div style="margin-bottom: 15px; padding: 10px; background: #f8fafc; border-radius: 8px;">
                                <strong style="color: #f59e0b;">RMSE (Root Mean Square Error)</strong>
                                <p style="font-size: 0.75em; margin: 5px 0 0 0;">Жалған және өте үлкен аномалияларды (шұғыл кептелістерді) қаттырақ жазалайтын метрика.</p>
                            </div>

                            <div style="padding: 10px; background: #f8fafc; border-radius: 8px;">
                                <strong style="color: #ef4444;">Linear Regression Trend</strong>
                                <p style="font-size: 0.75em; margin: 5px 0 0 0;">a = Σ(x-mx)(y-my) / Σ(x-mx)². Локальді өсу/кему бағытын анықтайды.</p>
                            </div>
                        </div>
                        <div class="info-box">
                            <h4 style="font-size: 1.1em; color: var(--primary-text); margin-bottom: 15px;"><i class="fa-solid fa-chart-pie"></i> Эксперимент Нәтижелері</h4>
                            <table class="modern-table" style="font-size: 0.7em; width: 100%; margin-bottom: 15px;">
                                <tr>
                                    <th style="color: var(--accent-blue);">Модель</th>
                                    <th>MAE</th>
                                    <th>RMSE</th>
                                    <th>Accuracy</th>
                                </tr>
                                <tr>
                                    <td>Linear Regression</td>
                                    <td>0.18</td>
                                    <td>0.24</td>
                                    <td>72.1%</td>
                                </tr>
                                <tr>
                                    <td>Random Forest</td>
                                    <td>0.11</td>
                                    <td>0.16</td>
                                    <td>81.5%</td>
                                </tr>
                                <tr style="background: rgba(16, 185, 129, 0.1);">
                                    <td style="color: #047857; font-weight: bold;">LSTM (Ұсынылған)</td>
                                    <td style="color: #047857; font-weight: bold;">0.08</td>
                                    <td style="color: #047857; font-weight: bold;">0.12</td>
                                    <td style="color: #047857; font-weight: bold;">87.4%</td>
                                </tr>
                            </table>
                            <img src="mae_rmse_chart.png" alt="Metrics" style="max-width: 100%; border-radius: 8px;">
                        </div>
                    </div>
                </div>
            </section>

            <!-- 6. Инновация: Цифрлық егіз -->
            <section>
                <div class="slide-card">
                    <h2>5. Инновациялық шешімдер: Digital Twin</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 10px;">
                        <div class="info-box">
                            <ul class="icon-list" style="margin: 0;">
                                <li style="margin-bottom: 15px; font-size: 0.8em;"><i class="fa-solid fa-clone" style="color: #3b82f6;"></i> <strong>What-If Симуляторы (Digital Twin):</strong> Жол жөндеу немесе апат кезінде трафик ағынының қалай өзгеретінін алдын ала симуляциялау.</li>
                                <li style="margin-bottom: 15px; font-size: 0.8em;"><i class="fa-solid fa-person-walking" style="color: #8b5cf6;"></i> <strong>Multimodal Analysis:</strong> Кептеліс критикалық деңгейге жеткенде, баламалы транспорт түрлерін ұсынады.</li>
                                <li style="margin-bottom: 15px; font-size: 0.8em;"><i class="fa-solid fa-wheelchair" style="color: #ec4899;"></i> <strong>Инклюзивті бағыттау:</strong> «Кедергісіз орта» режимі баспалдақтар мен кедергілерді айналып өтеді.</li>
                                <li style="margin-bottom: 0px; font-size: 0.8em;"><i class="fa-solid fa-cloud-sun-rain" style="color: #22c55e;"></i> <strong>Ауа-райы интеграциясы:</strong> Метео-деректер көлік ағынының жылдамдығына математикалық коэффициент ретінде әсер етеді.</li>
                            </ul>
                        </div>
                        <div class="info-box" style="display: flex; justify-content: center; align-items: center; background: #eff6ff;">
                            <img src="lstm_architecture.png" alt="Twin" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        </div>
                    </div>
                </div>
            </section>

            <!-- 7. Қорытынды -->
            <section>
                <div class="slide-card" style="text-align: center;">
                    <h2>6. Қорытынды және Практикалық Маңызы</h2>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 40px; margin-bottom: 40px;">
                        <div class="info-box" style="border-top: 4px solid var(--accent-blue);">
                            <i class="fa-solid fa-chart-line" style="font-size: 2em; color: var(--accent-blue); margin-bottom: 15px;"></i>
                            <h4 style="font-size: 1em;">Экономикалық</h4>
                            <p style="font-size: 0.7em;">Кептелістегі уақытты 20%-ға қысқарту.</p>
                        </div>
                        <div class="info-box" style="border-top: 4px solid #10b981;">
                            <i class="fa-solid fa-leaf" style="font-size: 2em; color: #10b981; margin-bottom: 15px;"></i>
                            <h4 style="font-size: 1em;">Экологиялық</h4>
                            <p style="font-size: 0.7em;">CO2 шығарындыларын азайту.</p>
                        </div>
                        <div class="info-box" style="border-top: 4px solid #ef4444;">
                            <i class="fa-solid fa-users" style="font-size: 2em; color: #ef4444; margin-bottom: 15px;"></i>
                            <h4 style="font-size: 1em;">Әлеуметтік</h4>
                            <p style="font-size: 0.7em;">Инклюзивті орта және қауіпсіздік.</p>
                        </div>
                    </div>
                    <h3 style="color: var(--accent-blue); font-size: 1.8em; margin-top: 30px;">Назарларыңызға рақмет!</h3>
                </div>
            </section>
"""
    
    # We keep everything up to the end of the first </section>
    new_content_lines = lines[:title_end_index + 1]
    # Add new slides
    new_content_lines.append(new_slides)
    # Add everything after the last </section>
    new_content_lines.extend(lines[last_section_index + 1:])
    
    with open('presentation.html', 'w', encoding='utf-8') as f:
        f.writelines(new_content_lines)
        
    print("Success: presentation.html updated successfully!")

if __name__ == '__main__':
    update_presentation()
