import re

def rebuild():
    with open('presentation.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Extract before and after slides
    start_tag = '<div class="slides">'
    start_idx = html.find(start_tag)
    
    # finding the matching end div for slides is tricky, let's use regex to find the end of slides.
    # Usually it's followed by </div> </div> <script src=...
    end_idx = html.find('</div>\n    </div>\n\n    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/')
    if end_idx == -1:
        end_idx = html.rfind('</div>', 0, html.find('<script src='))
    
    prefix = html[:start_idx + len(start_tag)] + '\n'
    suffix = '\n' + html[end_idx:]
    
    # We will build the new slides
    slides = []

    # Slide 1: Титул + позиционирование
    slides.append('''
        <!-- Speaker notes: Құрметті комиссия, назарларыңызға қалалық ортадағы көлік ағындарын бақылауға және болжауға арналған AI-қосымша әзірлеу тақырыбындағы дипломдық жобаны ұсынамын. -->
        <section>
            <div class="slide-card">
                <h1 style="font-size: 1.5em; color: var(--accent-blue); margin-bottom: 20px;">Қалалық ортадағы көлік ағындарын бақылау мен болжауға арналған AI-қосымша әзірлеу</h1>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 30px;">
                    <div style="text-align: left; font-size: 0.8em; line-height: 1.5;">
                        <p><strong>Орындаған:</strong> Сулейменов Алишер</p>
                        <p><strong>Ғылыми жетекші:</strong> Кусаинова Айнұр</p>
                        <p><strong>Мамандығы:</strong> Есептеу техникасы және бағдарламалық қамтамасыз ету</p>
                    </div>
                    <div class="info-box" style="background: rgba(37,99,235,0.05); border-left: 4px solid var(--accent-blue); max-width: 40%; font-size: 0.75em; text-align: left;">
                        <strong>Аналогтарды талдау:</strong> Нарықтағы навигаторлар ағымдағы жағдайды ғана көрсетеді, ал ұсынылған AI Traffic жүйесі LSTM моделі арқылы 30–60 минуттық болжам жасауға бағытталған.
                    </div>
                    <div>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://github.com/alishoksu/ai_traffics" alt="QR" style="border-radius: 10px; width: 120px; height: 120px;">
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 2: Өзектілік және аналогтарды қысқаша талдау (Slide 2 с графиком)
    slides.append('''
        <!-- Speaker notes: Зерттеудің өзектілігі қалалық кептеліс индексінің жыл сайын өсуімен негізделеді. Экрандағы иллюстрациялық тренд көрсеткіштері болжамдық жүйеге қажеттілікті көрсетеді. Аналогтармен салыстырғанда біздің жүйе алдын ала болжау мен инклюзивті маршруттауды ұсынады. -->
        <section>
            <div class="slide-card">
                <h2>1. Өзектілігі және аналогтарды талдау</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                    <div class="info-box" style="text-align: center;">
                        <h4 style="font-size: 0.9em; margin-bottom: 10px;">Жол кептелісі индексінің өсуі (аналитикалық бағалау)</h4>
                        <!-- SVG Chart representing the trend -->
                        <svg viewBox="0 0 400 250" style="width:100%; height:auto;">
                            <polyline fill="none" stroke="var(--accent-blue)" stroke-width="4" points="50,200 150,170 250,100 350,50" />
                            <circle cx="50" cy="200" r="6" fill="var(--accent-purple)"/>
                            <circle cx="150" cy="170" r="6" fill="var(--accent-purple)"/>
                            <circle cx="250" cy="100" r="6" fill="var(--accent-purple)"/>
                            <circle cx="350" cy="50" r="6" fill="var(--accent-purple)"/>
                            <text x="40" y="220" font-size="12">2022</text>
                            <text x="140" y="220" font-size="12">2023</text>
                            <text x="240" y="220" font-size="12">2024</text>
                            <text x="340" y="220" font-size="12">2025</text>
                            <text x="10" y="125" font-size="12" transform="rotate(-90 10,125)">Кептеліс индексі</text>
                            <text x="200" y="240" font-size="12" text-anchor="middle">Жылдар</text>
                        </svg>
                        <p style="font-size: 0.6em; color: var(--secondary-text); margin-top: 5px;">Көрсеткіштер қалалық трафиктің өсу тенденциясын және болжамдық жүйеге қажеттілікті негіздейді.</p>
                    </div>
                    <div class="info-box">
                        <h4 style="font-size: 0.9em; margin-bottom: 10px;">Жүйелерді салыстыру</h4>
                        <table class="modern-table" style="font-size: 0.65em; width: 100%;">
                            <tr>
                                <th style="color: var(--accent-blue);">Функция</th>
                                <th>Yandex Maps</th>
                                <th>2GIS</th>
                                <th>Google Maps</th>
                                <th style="color: var(--accent-blue);">AI Traffic</th>
                            </tr>
                            <tr><td>Жол жағдайын көрсету</td><td>Иә</td><td>Иә</td><td>Иә</td><td>Иә</td></tr>
                            <tr><td>30–60 мин. AI болжам</td><td>Жоқ</td><td>Шектеулі</td><td>Шектеулі</td><td><strong style="color: var(--accent-blue);">Иә</strong></td></tr>
                            <tr><td>Қалалық әкімшілік dashboard</td><td>Жоқ</td><td>Жоқ</td><td>Жоқ</td><td><strong style="color: var(--accent-blue);">Иә</strong></td></tr>
                            <tr><td>Инклюзивті маршрут</td><td>Жоқ</td><td>Жоқ</td><td>Жоқ</td><td><strong style="color: var(--accent-blue);">Иә</strong></td></tr>
                            <tr><td>Аномалияны анықтау</td><td>Иә</td><td>Жоқ</td><td>Иә</td><td><strong style="color: var(--accent-blue);">Иә</strong></td></tr>
                            <tr><td>Жергілікті дерекке бейімделу</td><td>Жоғары</td><td>Жоғары</td><td>Орташа</td><td><strong style="color: var(--accent-blue);">Жоғары</strong></td></tr>
                        </table>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 3: Проблема → Себеп → AI шешім
    slides.append('''
        <!-- Speaker notes: Қалалық трафиктің негізгі проблемасы - уақыт жоғалту мен экологиялық зардап. Оның себебі деректердің бөлінуі мен болжамның жоқтығында. Біздің шешім - AI-модельге негізделген кешенді жүйе. -->
        <section>
            <div class="slide-card">
                <h2>2. Мәселені қою және шешу жолдары</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 30px;">
                    <div class="info-box" style="border-top: 4px solid #ef4444;">
                        <h4 style="color: #ef4444;"><i class="fa-solid fa-triangle-exclamation"></i> Проблема</h4>
                        <ul style="font-size: 0.8em; padding-left: 15px;">
                            <li>Қалалық кептелістердің артуы</li>
                            <li>Уақыт пен экономикалық жоғалту</li>
                            <li>Экологиялық шығарындылар көлемінің өсуі</li>
                            <li>Авариялық тәуекелдер</li>
                        </ul>
                    </div>
                    <div class="info-box" style="border-top: 4px solid #f59e0b;">
                        <h4 style="color: #f59e0b;"><i class="fa-solid fa-magnifying-glass-chart"></i> Себеп</h4>
                        <ul style="font-size: 0.8em; padding-left: 15px;">
                            <li>Деректердің әртүрлі көздерде бөлінуі</li>
                            <li>Real-time мониторингтің жеткіліксіздігі</li>
                            <li>Болашақ кептелістерді алдын ала болжау алгоритмдерінің жоқтығы</li>
                        </ul>
                    </div>
                    <div class="info-box" style="border-top: 4px solid #10b981;">
                        <h4 style="color: #10b981;"><i class="fa-solid fa-lightbulb"></i> AI Шешім</h4>
                        <ul style="font-size: 0.8em; padding-left: 15px;">
                            <li>LSTM AI-болжау моделі</li>
                            <li>Real-time FastAPI платформасы</li>
                            <li>Flutter мобильді қосымшасы</li>
                            <li>Әкімшілік Web Dashboard</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 4: Зерттеудің мақсаты мен міндеттері
    slides.append('''
        <!-- Speaker notes: Зерттеудің басты мақсаты — қалалық трафикті нақты уақытта бақылауға және болжауға мүмкіндік беретін жүйе құру. Ол үшін 5 негізгі міндет қойылды: деректерді жинаудан бастап, модельдерді бағалауға дейін. -->
        <section>
            <div class="slide-card">
                <h2>3. Зерттеудің мақсаты мен міндеттері</h2>
                <div style="display: grid; grid-template-columns: 1fr 1.5fr; gap: 30px; margin-top: 20px;">
                    <div class="info-box" style="background: rgba(37,99,235,0.05); border-left: 4px solid var(--accent-blue); display: flex; flex-direction: column; justify-content: center;">
                        <h4 style="color: var(--accent-blue); margin-bottom: 15px;"><i class="fa-solid fa-bullseye"></i> Мақсаты</h4>
                        <p style="font-size: 0.9em; line-height: 1.6;">LSTM нейрондық желісі мен Digital Twin тұжырымдамасы негізінде қалалық трафикті нақты уақыт режимінде бақылауға және болжауға арналған кешенді AI-жүйесін әзірлеу.</p>
                    </div>
                    <div class="info-box">
                        <h4 style="margin-bottom: 15px;"><i class="fa-solid fa-list-check"></i> Міндеттері</h4>
                        <ol style="font-size: 0.8em; line-height: 1.6; padding-left: 20px;">
                            <li>Қалалық трафик деректерін жинау және құрылымдау.</li>
                            <li>Уақыттық қатарларды болжауға арналған ML/LSTM моделін әзірлеу.</li>
                            <li>FastAPI + PostgreSQL/PostGIS негізінде серверлік архитектура құру.</li>
                            <li>Flutter мобильді қосымшасы және Web Admin панелін әзірлеу.</li>
                            <li>Модель нәтижелерін MAE/RMSE арқылы бағалау және визуализациялау.</li>
                        </ol>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 5: Зерттеу нысаны, пәні және әдістері
    slides.append('''
        <!-- Speaker notes: Зерттеу нысаны ретінде қалалық көлік инфрақұрылымы, ал пәні ретінде нейрондық желілерді қолдану процесі алынды. Зерттеуде статистикалық талдау, машиналық оқыту және жүйелік архитектураны жобалау әдістері қолданылды. -->
        <section>
            <div class="slide-card">
                <h2>4. Зерттеу нысаны, пәні және әдістері</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
                    <div class="info-box">
                        <h4 style="color: var(--accent-purple);"><i class="fa-solid fa-city"></i> Зерттеу нысаны</h4>
                        <p style="font-size: 0.85em;">Қалалық көлік инфрақұрылымы және көлік ағындарын басқару жүйелері.</p>
                    </div>
                    <div class="info-box">
                        <h4 style="color: var(--accent-blue);"><i class="fa-solid fa-network-wired"></i> Зерттеу пәні</h4>
                        <p style="font-size: 0.85em;">Көлік кептелісін болжау және бақылау мақсатында машиналық оқыту алгоритмдері мен нейрондық желілерді (LSTM) қолдану процесі.</p>
                    </div>
                </div>
                <div class="info-box" style="margin-top: 20px;">
                    <h4 style="color: #10b981;"><i class="fa-solid fa-vial"></i> Зерттеу әдістері</h4>
                    <ul style="font-size: 0.8em; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <li>Деректерді интеллектуалды талдау (Data Mining)</li>
                        <li>Машиналық оқыту (Machine Learning)</li>
                        <li>Уақыттық қатарларды статистикалық талдау</li>
                        <li>Микросервистік жүйелерді архитектуралық жобалау</li>
                    </ul>
                </div>
            </div>
        </section>
    ''')

    # Slide 6: Ғылыми жаңалық
    slides.append('''
        <!-- Speaker notes: Бұл жұмыстың негізгі ғылыми жаңалығы - LSTM, EMA және Z-score әдістерін біріктіретін гибридті аналитикалық pipeline ұсынуында. Сондай-ақ, инклюзивті маршруттауға арналған жаңа cost функциясы жасалды. -->
        <section>
            <div class="slide-card">
                <h2>5. Ғылыми жаңалық</h2>
                <div style="display: grid; grid-template-columns: 1fr; gap: 15px; margin-top: 20px;">
                    <div class="info-box" style="display: flex; align-items: center; border-left: 4px solid var(--accent-purple);">
                        <i class="fa-solid fa-microchip" style="font-size: 2em; color: var(--accent-purple); margin-right: 20px;"></i>
                        <p style="font-size: 0.9em; margin: 0;">Қалалық трафикті real-time деректер негізінде <strong>30–60 минутқа болжау моделі</strong> ұсынылды.</p>
                    </div>
                    <div class="info-box" style="display: flex; align-items: center; border-left: 4px solid var(--accent-blue);">
                        <i class="fa-solid fa-layer-group" style="font-size: 2em; color: var(--accent-blue); margin-right: 20px;"></i>
                        <p style="font-size: 0.9em; margin: 0;">LSTM, EMA және Z-score әдістерін біріктіретін <strong>гибридті аналитикалық pipeline</strong> құрылды.</p>
                    </div>
                    <div class="info-box" style="display: flex; align-items: center; border-left: 4px solid #10b981;">
                        <i class="fa-solid fa-route" style="font-size: 2em; color: #10b981; margin-right: 20px;"></i>
                        <p style="font-size: 0.9em; margin: 0;">Инклюзивті және антистресс маршруттау үшін арнайы <strong>traffic-aware cost function</strong> қолданылды.</p>
                    </div>
                    <div class="info-box" style="display: flex; align-items: center; border-left: 4px solid #f59e0b;">
                        <i class="fa-solid fa-city" style="font-size: 2em; color: #f59e0b; margin-right: 20px;"></i>
                        <p style="font-size: 0.9em; margin: 0;">Қалалық әкімшілікке арналған <strong>digital twin / what-if сценарийлерін</strong> модельдеу мүмкіндігі қарастырылды.</p>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 7: Жүйенің жалпы архитектурасы
    slides.append('''
        <!-- Speaker notes: Жүйенің архитектурасы 5 қабаттан тұрады: Клиенттік деңгей, API шлюзі, AI аналитикалық қабаты, Деректер базасы және сыртқы сервистер интеграциясы. Деректер ағыны логикалық түрде бөлінген. -->
        <section>
            <div class="slide-card">
                <h2>6. Жүйенің жалпы архитектурасы</h2>
                <div class="info-box" style="margin-top: 15px; padding: 20px; text-align: center;">
                    <svg viewBox="0 0 800 400" style="width: 100%; height: auto; max-height: 400px;">
                        <!-- Client Layer -->
                        <rect x="50" y="50" width="150" height="100" rx="10" fill="rgba(37,99,235,0.1)" stroke="var(--accent-blue)" stroke-width="2"/>
                        <text x="125" y="80" text-anchor="middle" font-size="14" font-weight="bold" fill="var(--primary-text)">Client Layer</text>
                        <text x="125" y="105" text-anchor="middle" font-size="12">Flutter Mobile App</text>
                        <text x="125" y="125" text-anchor="middle" font-size="12">Vue.js Dashboard</text>
                        
                        <!-- API Layer -->
                        <rect x="250" y="50" width="150" height="100" rx="10" fill="rgba(124,58,237,0.1)" stroke="var(--accent-purple)" stroke-width="2"/>
                        <text x="325" y="80" text-anchor="middle" font-size="14" font-weight="bold" fill="var(--primary-text)">API Layer</text>
                        <text x="325" y="105" text-anchor="middle" font-size="12">FastAPI REST</text>
                        <text x="325" y="125" text-anchor="middle" font-size="12">WebSockets / Auth</text>
                        
                        <!-- AI Layer -->
                        <rect x="450" y="50" width="150" height="100" rx="10" fill="rgba(16,185,129,0.1)" stroke="#10b981" stroke-width="2"/>
                        <text x="525" y="80" text-anchor="middle" font-size="14" font-weight="bold" fill="var(--primary-text)">AI Layer</text>
                        <text x="525" y="105" text-anchor="middle" font-size="12">LSTM Model</text>
                        <text x="525" y="125" text-anchor="middle" font-size="12">Z-score / EMA</text>
                        
                        <!-- DB Layer -->
                        <rect x="350" y="220" width="150" height="100" rx="10" fill="rgba(245,158,11,0.1)" stroke="#f59e0b" stroke-width="2"/>
                        <text x="425" y="250" text-anchor="middle" font-size="14" font-weight="bold" fill="var(--primary-text)">Data Layer</text>
                        <text x="425" y="275" text-anchor="middle" font-size="12">PostgreSQL</text>
                        <text x="425" y="295" text-anchor="middle" font-size="12">PostGIS</text>
                        
                        <!-- External Layer -->
                        <rect x="150" y="220" width="150" height="100" rx="10" fill="rgba(100,116,139,0.1)" stroke="#64748b" stroke-width="2"/>
                        <text x="225" y="250" text-anchor="middle" font-size="14" font-weight="bold" fill="var(--primary-text)">External Services</text>
                        <text x="225" y="275" text-anchor="middle" font-size="12">Google Maps API</text>
                        <text x="225" y="295" text-anchor="middle" font-size="12">Weather API</text>
                        
                        <!-- Arrows -->
                        <!-- Client <-> API -->
                        <path d="M 200 100 L 240 100" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)" marker-start="url(#arrow)"/>
                        <!-- API <-> AI -->
                        <path d="M 400 100 L 440 100" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)" marker-start="url(#arrow)"/>
                        <!-- API <-> DB -->
                        <path d="M 325 150 L 325 200 L 400 200 L 400 220" stroke="var(--primary-text)" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
                        <!-- AI <-> DB -->
                        <path d="M 525 150 L 525 200 L 450 200 L 450 220" stroke="var(--primary-text)" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
                        <!-- External -> API -->
                        <path d="M 225 220 L 225 180 L 300 180 L 300 150" stroke="var(--primary-text)" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
                        
                        <defs>
                            <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
                                <path d="M0,0 L0,6 L9,3 z" fill="var(--primary-text)" />
                            </marker>
                        </defs>
                    </svg>
                    <p style="font-size: 0.7em; color: var(--secondary-text); margin-top: 10px;">User GPS → API → DB → AI Model → Prediction → Mobile/Web UI</p>
                </div>
            </div>
        </section>
    ''')

    # Slide 8: Data Flow Diagram
    slides.append('''
        <!-- Speaker notes: Деректер ағыны Data Flow Diagram арқылы көрсетілген. Қолданушы мен сыртқы көздерден келген шикі деректер өңделіп, модель арқылы болжам нәтижесіне айналады. -->
        <section>
            <div class="slide-card">
                <h2>7. Data Flow Diagram (Level 0)</h2>
                <div class="info-box" style="margin-top: 20px; display: flex; justify-content: center; align-items: center; padding: 30px;">
                    <svg viewBox="0 0 700 300" style="width: 100%; max-height: 350px;">
                        <!-- External Entities -->
                        <rect x="20" y="120" width="100" height="60" rx="5" fill="#f1f5f9" stroke="#64748b" stroke-width="2"/>
                        <text x="70" y="155" text-anchor="middle" font-size="12">Пайдаланушы / GPS</text>
                        
                        <rect x="580" y="40" width="100" height="60" rx="5" fill="#f1f5f9" stroke="#64748b" stroke-width="2"/>
                        <text x="630" y="75" text-anchor="middle" font-size="12">Mobile App</text>
                        
                        <rect x="580" y="200" width="100" height="60" rx="5" fill="#f1f5f9" stroke="#64748b" stroke-width="2"/>
                        <text x="630" y="235" text-anchor="middle" font-size="12">Web Admin</text>
                        
                        <!-- Processes -->
                        <circle cx="220" cy="150" r="45" fill="rgba(37,99,235,0.1)" stroke="var(--accent-blue)" stroke-width="2"/>
                        <text x="220" y="145" text-anchor="middle" font-size="11">Деректерді</text>
                        <text x="220" y="160" text-anchor="middle" font-size="11">өңдеу (API)</text>

                        <circle cx="450" cy="150" r="45" fill="rgba(124,58,237,0.1)" stroke="var(--accent-purple)" stroke-width="2"/>
                        <text x="450" y="145" text-anchor="middle" font-size="11">AI Болжау</text>
                        <text x="450" y="160" text-anchor="middle" font-size="11">Модулі</text>
                        
                        <!-- Datastore -->
                        <line x1="300" y1="50" x2="400" y2="50" stroke="#f59e0b" stroke-width="2"/>
                        <line x1="300" y1="80" x2="400" y2="80" stroke="#f59e0b" stroke-width="2"/>
                        <text x="350" y="70" text-anchor="middle" font-size="12" fill="#d97706">PostgreSQL DB</text>

                        <!-- Arrows -->
                        <path d="M 120 150 L 170 150" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>
                        <text x="145" y="140" text-anchor="middle" font-size="10">Raw Data</text>

                        <path d="M 220 105 L 220 65 L 295 65" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>
                        <text x="260" y="55" text-anchor="middle" font-size="10">Save</text>

                        <path d="M 405 65 L 450 65 L 450 105" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>
                        <text x="425" y="55" text-anchor="middle" font-size="10">History</text>

                        <path d="M 265 150 L 400 150" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>
                        <text x="330" y="140" text-anchor="middle" font-size="10">Features Extracted</text>

                        <path d="M 490 130 L 575 80" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>
                        <text x="540" y="100" text-anchor="middle" font-size="10" transform="rotate(-30 540,100)">Prediction</text>

                        <path d="M 490 170 L 575 220" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>
                        <text x="540" y="200" text-anchor="middle" font-size="10" transform="rotate(30 540,200)">Analytics</text>
                    </svg>
                </div>
            </div>
        </section>
    ''')

    # Slide 9: Prediction Function Flowchart
    slides.append('''
        <!-- Speaker notes: Бұл блок-схема болжау функциясының ішкі жұмысын сипаттайды. Сұраныс түскенде, дерекқордан соңғы уақыттық жазбалар алынып, қажетті фичалар жасалып, LSTM моделіне беріледі. -->
        <section>
            <div class="slide-card">
                <h2>8. Болжау функциясының жұмыс алгоритмі</h2>
                <div class="info-box" style="margin-top: 10px; display: flex; justify-content: center;">
                    <svg viewBox="0 0 400 450" style="width: auto; height: 450px;">
                        <rect x="150" y="10" width="100" height="30" rx="15" fill="#f8fafc" stroke="var(--primary-text)" stroke-width="2"/>
                        <text x="200" y="30" text-anchor="middle" font-size="12">Start</text>
                        <path d="M 200 40 L 200 60" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="100" y="60" width="200" height="40" fill="#eff6ff" stroke="var(--accent-blue)" stroke-width="1"/>
                        <text x="200" y="85" text-anchor="middle" font-size="12">segment_id және time қабылдау</text>
                        <path d="M 200 100 L 200 120" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="100" y="120" width="200" height="40" fill="#fdf4ff" stroke="var(--accent-purple)" stroke-width="1"/>
                        <text x="200" y="145" text-anchor="middle" font-size="12">Соңғы N жазбаны DB-дан алу</text>
                        <path d="M 200 160 L 200 180" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="70" y="180" width="260" height="40" fill="#f0fdf4" stroke="#10b981" stroke-width="1"/>
                        <text x="200" y="205" text-anchor="middle" font-size="12">Feature eng: speed, weather, hour</text>
                        <path d="M 200 220 L 200 240" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="100" y="240" width="200" height="40" fill="#eff6ff" stroke="var(--accent-blue)" stroke-width="1"/>
                        <text x="200" y="265" text-anchor="middle" font-size="12">Normalization / Preprocessing</text>
                        <path d="M 200 280 L 200 300" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="100" y="300" width="200" height="40" fill="#fdf4ff" stroke="var(--accent-purple)" stroke-width="1"/>
                        <text x="200" y="325" text-anchor="middle" font-size="12">LSTM модель inference</text>
                        <path d="M 200 340 L 200 360" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="100" y="360" width="200" height="40" fill="#fffbeb" stroke="#f59e0b" stroke-width="1"/>
                        <text x="200" y="385" text-anchor="middle" font-size="12">Prediction score қайтару (API)</text>
                        <path d="M 200 400 L 200 420" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="150" y="420" width="100" height="30" rx="15" fill="#f8fafc" stroke="var(--primary-text)" stroke-width="2"/>
                        <text x="200" y="440" text-anchor="middle" font-size="12">End</text>
                    </svg>
                </div>
            </div>
        </section>
    ''')

    # Slide 10: Routing Algorithm Flowchart
    slides.append('''
        <!-- Speaker notes: Смарт-маршруттау алгоритмі A* әдісіне негізделген. Біздің ерекшелік - маршрут құнын есептеуде қашықтыққа қосымша кептеліс, кедергілер және стресс деңгейі пенализация ретінде қосылады. -->
        <section>
            <div class="slide-card">
                <h2>9. Смарт-маршруттау алгоритмі</h2>
                <div class="info-box" style="margin-top: 10px; display: flex; justify-content: center;">
                    <svg viewBox="0 0 500 400" style="width: auto; height: 400px;">
                        <rect x="200" y="10" width="100" height="30" rx="15" fill="#f8fafc" stroke="var(--primary-text)" stroke-width="2"/>
                        <text x="250" y="30" text-anchor="middle" font-size="12">Start</text>
                        <path d="M 250 40 L 250 60" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="150" y="60" width="200" height="40" fill="#eff6ff" stroke="var(--accent-blue)" stroke-width="1"/>
                        <text x="250" y="85" text-anchor="middle" font-size="12">A / B нүктелерін алу</text>
                        <path d="M 250 100 L 250 120" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="150" y="120" width="200" height="40" fill="#fdf4ff" stroke="var(--accent-purple)" stroke-width="1"/>
                        <text x="250" y="145" text-anchor="middle" font-size="12">Road Graph құру</text>
                        <path d="M 250 160 L 250 180" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="50" y="180" width="400" height="50" fill="#f0fdf4" stroke="#10b981" stroke-width="1"/>
                        <text x="250" y="200" text-anchor="middle" font-size="12">Cost есептеу: dist + traffic_weight +</text>
                        <text x="250" y="220" text-anchor="middle" font-size="12">barrier_penalty + stress_penalty</text>
                        <path d="M 250 230 L 250 250" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="150" y="250" width="200" height="40" fill="#fffbeb" stroke="#f59e0b" stroke-width="1"/>
                        <text x="250" y="275" text-anchor="middle" font-size="12">A* / Dijkstra алгоритмі</text>
                        <path d="M 250 290 L 250 310" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="150" y="310" width="200" height="40" fill="#eff6ff" stroke="var(--accent-blue)" stroke-width="1"/>
                        <text x="250" y="335" text-anchor="middle" font-size="12">Ең тиімді маршрутты UI-да көрсету</text>
                        <path d="M 250 350 L 250 370" stroke="var(--primary-text)" stroke-width="2" marker-end="url(#arrow)"/>

                        <rect x="200" y="370" width="100" height="30" rx="15" fill="#f8fafc" stroke="var(--primary-text)" stroke-width="2"/>
                        <text x="250" y="390" text-anchor="middle" font-size="12">End</text>
                    </svg>
                </div>
            </div>
        </section>
    ''')

    # Slide 11: ML модельдері және олардың рөлі
    slides.append('''
        <!-- Speaker notes: Біздің шешімде бірнеше модельдер комбинациясы қолданылады. Негізгі уақыттық болжау LSTM-ге жүктелген, ал Random Forest және LR трендтер мен салыстыру базасын қамтамасыз етеді. -->
        <section>
            <div class="slide-card">
                <h2>10. ML модельдері және олардың рөлі</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                    <div class="info-box" style="border-left: 4px solid var(--accent-purple);">
                        <h4 style="color: var(--accent-purple);"><i class="fa-solid fa-brain"></i> Негізгі модель</h4>
                        <p style="font-size: 0.8em;"><strong>LSTM:</strong> Уақыттық қатарлардың ұзақ мерзімді тәуелділігін сақтау және динамикалық болжау жасайтын негізгі алгоритм.</p>
                    </div>
                    <div class="info-box" style="border-left: 4px solid var(--accent-blue);">
                        <h4 style="color: var(--accent-blue);"><i class="fa-solid fa-code-compare"></i> Baseline модельдер</h4>
                        <p style="font-size: 0.8em;"><strong>Random Forest:</strong> LSTM нәтижелерін тексеруге арналған салыстырмалы/baseline модель.<br>
                        <strong>Linear Regression:</strong> Трафиктің жалпы локальді трендін бағалау.</p>
                    </div>
                    <div class="info-box" style="border-left: 4px solid #10b981;">
                        <h4 style="color: #10b981;"><i class="fa-solid fa-wave-square"></i> Тегістеу (Smoothing)</h4>
                        <p style="font-size: 0.8em;"><strong>EMA (Exponential Moving Average):</strong> Деректердегі кездейсоқ шуылдарды тегістеу және сигналды тазарту.</p>
                    </div>
                    <div class="info-box" style="border-left: 4px solid #ef4444;">
                        <h4 style="color: #ef4444;"><i class="fa-solid fa-triangle-exclamation"></i> Аномалия детекторы</h4>
                        <p style="font-size: 0.8em;"><strong>Z-Score:</strong> Стандартты ауытқуды есептеу арқылы шұғыл ДТП немесе тосқауылдарды автоматты анықтау.</p>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 12: Dataset және feature engineering
    slides.append('''
        <!-- Speaker notes: Деректер жиынтығын дайындау барысында бірнеше факторлар (уақыт, апта күні, метео-жағдай) ескеріліп, feature engineering жасалды. Бұл модельдің дәлдігін арттыруға негіз болды. -->
        <section>
            <div class="slide-card">
                <h2>11. Dataset және Feature Engineering</h2>
                <div class="info-box" style="margin-top: 20px;">
                    <h4 style="font-size: 1.1em; color: var(--accent-blue); margin-bottom: 15px;">Модельге берілетін кіріс белгілері (Features)</h4>
                    <ul style="font-size: 0.8em; line-height: 1.8;">
                        <li><strong>Historical Traffic Speed:</strong> Соңғы N уақыттық терезелердегі орташа жылдамдық.</li>
                        <li><strong>Temporal Features:</strong> Тәулік уақыты (Hour), Апта күні (Weekday), Мереке күндері көрсеткіштері.</li>
                        <li><strong>Spatial Features:</strong> Жол сегментінің ID-і және оның көршілес сегменттермен байланысы.</li>
                        <li><strong>Weather Factors:</strong> Температура, жауын-шашын мөлшері (модельде математикалық коэффициент ретінде пенализация жасайды).</li>
                    </ul>
                </div>
                <p style="font-size: 0.75em; color: var(--secondary-text); text-align: center; margin-top: 15px;">* Деректерді өңдеу Min-Max Scaling арқылы нормаланды.</p>
            </div>
        </section>
    ''')

    # Slide 13: Модельдерді салыстыру және метрикалар
    slides.append('''
        <!-- Speaker notes: Тәжірибелік тестілеу барысында бірнеше модельдердің нәтижелері салыстырылды. Нормаланған шкалада LSTM моделі қателік деңгейін төмендетіп, ең жоғары дәлдікті көрсетті. -->
        <section>
            <div class="slide-card">
                <h2>12. Модельдерді салыстыру және метрикалар</h2>
                <p style="font-size: 0.7em; color: var(--secondary-text); margin-bottom: 15px;">* Метрикалар нормаланған шкалада (0-1) есептелді.</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="info-box">
                        <table class="modern-table" style="font-size: 0.75em; width: 100%;">
                            <tr>
                                <th style="color: var(--accent-blue);">Модель</th>
                                <th>MAE</th>
                                <th>RMSE</th>
                            </tr>
                            <tr><td>Naive Approach</td><td>0.28</td><td>0.35</td></tr>
                            <tr><td>Moving Average</td><td>0.22</td><td>0.29</td></tr>
                            <tr><td>Trend LR</td><td>0.18</td><td>0.24</td></tr>
                            <tr><td>Random Forest</td><td>0.11</td><td>0.16</td></tr>
                            <tr style="background: rgba(16, 185, 129, 0.1);">
                                <td style="color: #047857; font-weight: bold;">LSTM (Proposed)</td>
                                <td style="color: #047857; font-weight: bold;">0.08</td>
                                <td style="color: #047857; font-weight: bold;">0.12</td>
                            </tr>
                        </table>
                    </div>
                    <div class="info-box" style="display: flex; justify-content: center; align-items: flex-end; padding-top: 30px;">
                        <!-- Simple bar chart via SVG -->
                        <svg viewBox="0 0 300 200" style="width: 100%; height: auto;">
                            <!-- MAE Bars -->
                            <rect x="30" y="40" width="30" height="140" fill="#94a3b8"/>
                            <rect x="80" y="90" width="30" height="90" fill="#94a3b8"/>
                            <rect x="130" y="125" width="30" height="55" fill="var(--accent-blue)"/>
                            <rect x="180" y="160" width="30" height="20" fill="#10b981"/>
                            
                            <!-- Labels -->
                            <text x="45" y="195" text-anchor="middle" font-size="10">Naive</text>
                            <text x="95" y="195" text-anchor="middle" font-size="10">LR</text>
                            <text x="145" y="195" text-anchor="middle" font-size="10">RF</text>
                            <text x="195" y="195" text-anchor="middle" font-size="10" font-weight="bold" fill="#10b981">LSTM</text>
                            
                            <!-- Values -->
                            <text x="45" y="35" text-anchor="middle" font-size="10">0.28</text>
                            <text x="95" y="85" text-anchor="middle" font-size="10">0.18</text>
                            <text x="145" y="120" text-anchor="middle" font-size="10">0.11</text>
                            <text x="195" y="155" text-anchor="middle" font-size="10" font-weight="bold" fill="#10b981">0.08</text>
                            
                            <text x="150" y="10" text-anchor="middle" font-size="12" font-weight="bold">MAE Салыстыру (Төменірек - Жақсырақ)</text>
                        </svg>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 14: Аномалияларды анықтау: Z-score
    slides.append('''
        <!-- Speaker notes: Жүйеде Z-score алгоритмі арқылы статистикалық аномалияларды (мысалы, күрт кептелістерді) автоматты түрде анықтау механизмі іске асырылды. -->
        <section>
            <div class="slide-card">
                <h2>13. Аномалияларды анықтау: Z-score</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 20px;">
                    <div class="info-box">
                        <h4 style="color: #ef4444; margin-bottom: 15px;"><i class="fa-solid fa-bolt"></i> Статистикалық Ауытқу</h4>
                        <p style="font-size: 0.85em; line-height: 1.6;">
                            Z-score әдісі ағымдағы трафик индексінің тарихи орташа мәннен қанша стандартты ауытқуға (σ) алшақтағанын есептейді.<br><br>
                            Егер <strong>|Z| > 3</strong> болса, жүйе мұны "аномалия" (мысалы, ДТП немесе жол жабылуы) деп тіркейді және баламалы маршруттарды қайта есептеуді іске қосады.
                        </p>
                    </div>
                    <div class="info-box" style="display: flex; justify-content: center; align-items: center; background: #eff6ff;">
                        <!-- Inline graphic representation of Z-score anomaly -->
                        <svg viewBox="0 0 300 150" style="width: 100%;">
                            <path d="M 10 100 Q 50 100 100 100 T 200 100 T 290 100" fill="none" stroke="var(--accent-blue)" stroke-width="2"/>
                            <path d="M 10 100 L 80 100 L 150 20 L 180 100 L 290 100" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="5,5"/>
                            <circle cx="150" cy="20" r="5" fill="#ef4444"/>
                            <text x="150" y="10" text-anchor="middle" font-size="10" fill="#ef4444">Anomaly (Z > 3)</text>
                            <text x="200" y="120" font-size="10" fill="var(--accent-blue)">Қалыпты тренд</text>
                        </svg>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 15: Мобильді қосымша интерфейсі
    slides.append('''
        <!-- Speaker notes: Flutter негізінде жасалған мобильді клиент пайдаланушыға интерактивті карта, 30 минуттық болжам және инклюзивті маршруттарды ұсынады. -->
        <section>
            <div class="slide-card">
                <h2>14. Мобильді қосымша интерфейсі</h2>
                <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 30px; margin-top: 20px;">
                    <div class="info-box">
                        <ul style="font-size: 0.85em; line-height: 1.8;">
                            <li><i class="fa-brands fa-flutter" style="color: #0284c7;"></i> <strong>Технология:</strong> Flutter (Cross-platform)</li>
                            <li><i class="fa-solid fa-map-location-dot" style="color: var(--accent-blue);"></i> <strong>UI/UX:</strong> Интерактивті карта және нақты уақыттағы трафик қабаттары.</li>
                            <li><i class="fa-solid fa-clock-rotate-left" style="color: var(--accent-purple);"></i> <strong>Болжау:</strong> Таңдалған маршрут бойынша 30-60 минут алға AI болжам.</li>
                            <li><i class="fa-solid fa-universal-access" style="color: #10b981;"></i> <strong>Инклюзивтілік:</strong> Кедергісіз бағыттарды таңдау мүмкіндігі (баспалдақтарды айналып өту).</li>
                        </ul>
                    </div>
                    <div class="info-box" style="text-align: center; background: #f8fafc; padding: 10px;">
                        <div style="width: 140px; height: 280px; background: white; border: 4px solid #333; border-radius: 20px; margin: 0 auto; position: relative;">
                            <div style="background: var(--accent-blue); height: 50%; border-radius: 15px 15px 0 0;"></div>
                            <div style="padding: 10px; font-size: 0.5em; text-align: left;">
                                <p style="font-weight:bold;">Маршрут табылды</p>
                                <p style="color:#ef4444;">15 мин кептеліс күтілуде</p>
                                <div style="background: #10b981; color: white; padding: 5px; border-radius: 5px; text-align: center;">Баламалы маршрут</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 16: Web Admin Dashboard
    slides.append('''
        <!-- Speaker notes: Қалалық әкімшілікке арналған Web Admin панелі жалпы көлік ағынының жағдайын бақылауға және аномалияларды басқаруға арналған. -->
        <section>
            <div class="slide-card">
                <h2>15. Web Admin Dashboard</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                    <div class="info-box">
                        <h4 style="color: var(--accent-blue); margin-bottom: 10px;"><i class="fa-solid fa-desktop"></i> Әкімшілік Бақылау</h4>
                        <p style="font-size: 0.8em;">Vue.js негізіндегі веб-интерфейс қалалық қызметтер үшін арналған.</p>
                        <ul style="font-size: 0.8em; margin-top: 10px;">
                            <li>Қала бойынша жалпы кептеліс индексі.</li>
                            <li>Аномалиялық нүктелерді тіркеу (ДТП).</li>
                            <li>API жүктемесін және сервер статусын бақылау.</li>
                        </ul>
                    </div>
                    <div class="info-box" style="display: flex; justify-content: center; align-items: center; background: #f1f5f9; border: 2px dashed #cbd5e1;">
                        <p style="font-size: 0.8em; color: #64748b;"><i class="fa-solid fa-chart-line"></i> Dashboard Analytics View</p>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 17: Digital Twin / What-if simulation
    slides.append('''
        <!-- Speaker notes: Жүйенің ерекшелігі - Digital Twin. Бұл арқылы белгілі бір көшені жаппас бұрын, оның бүкіл трафикке әсерін симуляциялауға болады. -->
        <section>
            <div class="slide-card">
                <h2>16. Digital Twin / What-if Simulation</h2>
                <div style="display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px; margin-top: 20px;">
                    <div class="info-box" style="border-left: 4px solid #f59e0b;">
                        <h4 style="color: #f59e0b;"><i class="fa-solid fa-code-branch"></i> Симуляция логикасы</h4>
                        <p style="font-size: 0.8em; line-height: 1.6;">Жолдың жабылуын виртуалды түрде үлгілеу (simulate_closure API). Модель ағынның көршілес көшелерге қалай таралатынын және жаңа кептеліс ошақтарының қайда пайда болатынын есептейді.</p>
                    </div>
                    <div class="info-box" style="display: flex; align-items: center; justify-content: center;">
                        <svg viewBox="0 0 300 150" style="width: 100%;">
                            <!-- Road Network -->
                            <line x1="50" y1="75" x2="250" y2="75" stroke="#94a3b8" stroke-width="8"/>
                            <line x1="150" y1="20" x2="150" y2="130" stroke="#94a3b8" stroke-width="8"/>
                            
                            <!-- Closure mark -->
                            <circle cx="100" cy="75" r="10" fill="#ef4444"/>
                            <text x="100" y="60" text-anchor="middle" font-size="10" fill="#ef4444">Closed</text>
                            
                            <!-- Rerouted Traffic Flow -->
                            <path d="M 50 75 L 80 40 L 150 40 L 150 20" stroke="var(--accent-blue)" stroke-width="3" fill="none" stroke-dasharray="4,4" marker-end="url(#arrow)"/>
                            <text x="120" y="30" font-size="10" fill="var(--accent-blue)">Rerouted Flow</text>
                        </svg>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 18: Деректер қауіпсіздігі
    slides.append('''
        <!-- Speaker notes: Пайдаланушы мен жүйенің қауіпсіздігі JWT токендері және биометриялық авторизация арқылы қамтамасыз етіледі. -->
        <section>
            <div class="slide-card">
                <h2>17. Деректер қауіпсіздігі</h2>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 30px;">
                    <div class="info-box" style="text-align: center;">
                        <i class="fa-solid fa-shield-halved" style="font-size: 2em; color: var(--accent-blue); margin-bottom: 10px;"></i>
                        <h4 style="font-size: 0.9em;">API Қорғанысы</h4>
                        <p style="font-size: 0.75em;">JWT (JSON Web Tokens) негізіндегі авторизация және endpoint-терді қорғау.</p>
                    </div>
                    <div class="info-box" style="text-align: center;">
                        <i class="fa-solid fa-fingerprint" style="font-size: 2em; color: var(--accent-purple); margin-bottom: 10px;"></i>
                        <h4 style="font-size: 0.9em;">Биометрия</h4>
                        <p style="font-size: 0.75em;">Мобильді қосымшада FaceID / TouchID арқылы қауіпсіз кіру.</p>
                    </div>
                    <div class="info-box" style="text-align: center;">
                        <i class="fa-solid fa-database" style="font-size: 2em; color: #10b981; margin-bottom: 10px;"></i>
                        <h4 style="font-size: 0.9em;">Деректердің құпиялылығы</h4>
                        <p style="font-size: 0.75em;">GPS тректерді анонимизациялау және парольдерді хэштеу (Bcrypt).</p>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 19: Практикалық маңыз
    slides.append('''
        <!-- Speaker notes: Практикалық тұрғыда жоба әкімдікке инфрақұрылымды жақсартуға, жүргізушілерге уақыт үнемдеуге, ал қоғамға экологиялық және инклюзивті орта құруға көмектеседі. -->
        <section>
            <div class="slide-card">
                <h2>18. Практикалық маңыз</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                    <div class="info-box" style="border-left: 4px solid var(--accent-blue);">
                        <h4 style="color: var(--accent-blue);"><i class="fa-solid fa-building-columns"></i> Қала әкімдігі үшін</h4>
                        <p style="font-size: 0.8em;">Кептеліс ошақтарын бақылау, жол жөндеу жоспарларын бағалау және инфрақұрылымды оңтайландыру.</p>
                    </div>
                    <div class="info-box" style="border-left: 4px solid #f59e0b;">
                        <h4 style="color: #f59e0b;"><i class="fa-solid fa-car"></i> Жүргізушілер үшін</h4>
                        <p style="font-size: 0.8em;">Уақыт үнемдеу, маршрутты алдын ала таңдау және болжамды кептелістерден аулақ болу.</p>
                    </div>
                    <div class="info-box" style="border-left: 4px solid var(--accent-purple);">
                        <h4 style="color: var(--accent-purple);"><i class="fa-solid fa-wheelchair"></i> Инклюзивті қоғам үшін</h4>
                        <p style="font-size: 0.8em;">Барлық пайдаланушыларға арналған barrier-free (кедергісіз) маршруттар.</p>
                    </div>
                    <div class="info-box" style="border-left: 4px solid #10b981;">
                        <h4 style="color: #10b981;"><i class="fa-solid fa-leaf"></i> Экология үшін</h4>
                        <p style="font-size: 0.8em;">Бос жүріс уақытын азайту арқылы көмірқышқыл газының (CO2) шығарындыларын төмендету.</p>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 20: Қорытынды
    slides.append('''
        <!-- Speaker notes: Қорытындылай келе, қойылған барлық міндеттер орындалды. Тәжірибелік тестілеуде жүйе қалалық трафик динамикасын тиімді сипаттайтынын дәлелдеді. -->
        <section>
            <div class="slide-card">
                <h2>19. Қорытынды</h2>
                <div class="info-box" style="margin-top: 20px; background: rgba(37,99,235,0.05);">
                    <ul style="font-size: 0.85em; line-height: 1.8;">
                        <li><i class="fa-solid fa-check" style="color: #10b981; margin-right: 10px;"></i> Зерттеу барысында алға қойылған <strong>барлық міндеттер толығымен орындалды</strong>.</li>
                        <li><i class="fa-solid fa-check" style="color: #10b981; margin-right: 10px;"></i> Микросервистік архитектура (FastAPI, PostGIS) және мобильді клиент (Flutter) интеграцияланды.</li>
                        <li><i class="fa-solid fa-check" style="color: #10b981; margin-right: 10px;"></i> LSTM моделі тәжірибелік тестілеуде <strong>жоғары нәтиже көрсетті</strong> және қателік деңгейі төмендеді.</li>
                        <li><i class="fa-solid fa-check" style="color: #10b981; margin-right: 10px;"></i> Әзірленген жүйе қалалық трафик динамикасын нақты сипаттауға мүмкіндік береді.</li>
                    </ul>
                </div>
            </div>
        </section>
    ''')

    # Slide 21: Даму перспективалары
    slides.append('''
        <!-- Speaker notes: Болашақта жүйені IoT бағдаршамдарымен тікелей біріктіріп, қаланы автоматты басқару деңгейіне жеткізу жоспарлануда. -->
        <section>
            <div class="slide-card">
                <h2>20. Даму перспективалары</h2>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px;">
                    <div class="info-box" style="text-align: center; border-top: 4px solid var(--accent-blue);">
                        <i class="fa-solid fa-traffic-light" style="font-size: 2em; color: var(--accent-blue); margin-bottom: 10px;"></i>
                        <h4 style="font-size: 0.9em;">Smart Traffic Lights</h4>
                        <p style="font-size: 0.75em;">Бағдаршамдарды нақты уақытта IoT арқылы автоматты басқару.</p>
                    </div>
                    <div class="info-box" style="text-align: center; border-top: 4px solid var(--accent-purple);">
                        <i class="fa-solid fa-bus" style="font-size: 2em; color: var(--accent-purple); margin-bottom: 10px;"></i>
                        <h4 style="font-size: 0.9em;">Қоғамдық Көлік</h4>
                        <p style="font-size: 0.75em;">Автобустардың маршруттарын кептеліске қарай динамикалық өзгерту.</p>
                    </div>
                    <div class="info-box" style="text-align: center; border-top: 4px solid #10b981;">
                        <i class="fa-solid fa-video" style="font-size: 2em; color: #10b981; margin-bottom: 10px;"></i>
                        <h4 style="font-size: 0.9em;">Computer Vision</h4>
                        <p style="font-size: 0.75em;">Бейнебақылау камераларынан трафикті тікелей талдау (YOLOv8).</p>
                    </div>
                </div>
            </div>
        </section>
    ''')

    # Slide 22: Назарларыңызға рақмет
    slides.append('''
        <!-- Speaker notes: Назарларыңызға рақмет, сұрақтарыңызға жауап беруге дайынмын. -->
        <section>
            <div class="slide-card" style="text-align: center; padding: 60px 20px;">
                <i class="fa-solid fa-graduation-cap" style="font-size: 4em; color: var(--accent-blue); margin-bottom: 20px;"></i>
                <h1 style="font-size: 2.5em; color: var(--primary-text); margin-bottom: 10px;">Назарларыңызға рақмет!</h1>
                <p style="font-size: 1.2em; color: var(--secondary-text);">Сұрақтарыңызға жауап беруге дайынмын.</p>
            </div>
        </section>
    ''')

    new_html = prefix + "".join(slides) + suffix

    with open('presentation.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

if __name__ == '__main__':
    rebuild()
