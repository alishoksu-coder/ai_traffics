import os

def build_13_slide_presentation():
    html_content = """<!DOCTYPE html>
<html lang="kk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI Traffic - Дипломдық қорғау</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/reset.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/reveal.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/theme/simple.min.css" id="theme">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --navy: #0F172A;
            --blue: #2563EB;
            --purple: #7C3AED;
            --green: #10B981;
            --bg-light: #F8FAFC;
            --text-main: #334155;
            --text-muted: #64748B;
        }
        body { font-family: 'Inter', sans-serif; background-color: var(--bg-light); color: var(--navy); }
        .reveal { font-family: 'Inter', sans-serif; }
        .reveal h1, .reveal h2, .reveal h3, .reveal h4, .reveal h5, .reveal h6 { font-family: 'Inter', sans-serif !important; font-weight: 700; color: var(--navy); text-transform: none !important; }
        .reveal h2 { font-size: 1.4em !important; margin-bottom: 20px; color: var(--blue) !important; border-bottom: 2px solid var(--blue); padding-bottom: 10px; display: inline-block;}
        
        .slide-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.05);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
        
        .info-box {
            background: var(--bg-light);
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid var(--blue);
            text-align: left;
        }
        .info-box.purple { border-left-color: var(--purple); }
        .info-box.green { border-left-color: var(--green); }
        .info-box.navy { border-left-color: var(--navy); }
        
        .info-box h4 { margin-top: 0; font-size: 1.1em; margin-bottom: 15px; color: var(--navy); font-weight: 600;}
        .info-box p { font-size: 0.85em; color: var(--text-main); margin-bottom: 10px; line-height: 1.5; }
        
        ul.custom-list { list-style: none; padding: 0; margin: 0; text-align: left; }
        ul.custom-list li { margin-bottom: 12px; font-size: 0.85em; display: flex; align-items: flex-start; gap: 12px; line-height: 1.4; color: var(--text-main);}
        ul.custom-list li i { color: var(--blue); margin-top: 4px; font-size: 1.1em; flex-shrink: 0; }
        
        table.modern-table { width: 100%; border-collapse: collapse; font-size: 0.65em; text-align: left; margin-bottom: 20px;}
        table.modern-table th { background: var(--navy); color: white; padding: 12px; font-weight: 600;}
        table.modern-table td { padding: 12px; border-bottom: 1px solid #e2e8f0; }
        table.modern-table tr:nth-child(even) { background: #f1f5f9; }
        
        .diagram-container { display: flex; justify-content: center; align-items: center; padding: 20px; background: white; border-radius: 8px; border: 1px solid #e2e8f0; }
        .slide-number-badge {
            position: absolute; top: 20px; right: 20px; background: var(--navy); color: white;
            width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 0.8em; z-index: 100; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        svg text { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">

            <!-- 1. Титулдық слайд -->
            <section>
                <!-- Speaker notes: Құрметті мемлекеттік аттестаттау комиссиясының төрағасы және мүшелері! Назарларыңызға "Қалалық ортадағы көлік ағындарын бақылау мен болжауға арналған AI-қосымша әзірлеу" тақырыбындағы дипломдық жұмысымды ұсынамын. -->
                <div class="slide-card" style="text-align: center; padding: 50px 30px;">
                    <div style="font-size: 0.8em; color: var(--text-muted); margin-bottom: 30px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                        Л.Н. Гумилев атындағы Еуразия ұлттық университеті<br>Ақпараттық технологиялар факультеті
                    </div>
                    <h1 style="font-size: 2em; color: var(--navy); margin-bottom: 40px; line-height: 1.3;">
                        Қалалық ортадағы көлік ағындарын бақылау мен болжауға арналған <span style="color: var(--blue);">AI-қосымша</span> әзірлеу
                    </h1>

                    <div style="display: flex; justify-content: center; align-items: center; gap: 80px; margin-bottom: 40px; text-align: left;">
                        <div>
                            <p style="margin: 8px 0; font-size: 0.9em;"><strong>Мамандық:</strong> «Есептеу техникасы және бағдарламалық қамтамасыз ету»</p>
                            <p style="margin: 8px 0; font-size: 0.9em;"><strong>Орындаған:</strong> Сулейменов Алишер</p>
                            <p style="margin: 8px 0; font-size: 0.9em;"><strong>Ғылыми жетекші:</strong> Кусаинова Айнур</p>
                            <p style="margin: 8px 0; font-size: 0.9em; color: var(--text-muted);">Астана, 2026</p>
                        </div>
                        <div>
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://github.com/alishoksu-coder/ai_traffics" alt="QR GitHub" style="border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.6em; margin-top: 5px; color: var(--text-muted); text-align: center;">Жоба репозиторийі</div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 2. Тақырыптың өзектілігі -->
            <section>
                <!-- Speaker notes: Зерттеудің өзектілігі жаһандық урбанизация мен қалалардағы көлік кептелісінің артуымен тікелей байланысты. Кептеліс тек уақытты ғана емес, экологияға да үлкен зиян келтіреді. Сондықтан нақты уақыттағы мониторинг пен алдын ала болжау жүйелері қажет. -->
                <div class="slide-number-badge">2</div>
                <div class="slide-card">
                    <h2>Тақырыптың өзектілігі</h2>
                    <div class="grid-2" style="align-items: center;">
                        <ul class="custom-list">
                            <li><i class="fa-solid fa-city"></i><div><strong>Урбанизация және автокөлік санының өсуі:</strong> Қалалық инфрақұрылымға түсетін жүктеменің критикалық деңгейге жетуі.</div></li>
                            <li><i class="fa-solid fa-stopwatch"></i><div><strong>Экономикалық және уақыт жоғалту:</strong> Жүргізушілердің кептелісте өткізетін уақытының артуы (күніне орта есеппен 40-60 минут).</div></li>
                            <li><i class="fa-solid fa-leaf"></i><div><strong>Экологиялық зардаптар:</strong> Автокөліктердің бос жүрісі (idling) салдарынан атмосфераға бөлінетін CO2 шығарындыларының көбеюі.</div></li>
                            <li><i class="fa-solid fa-chart-line"></i><div><strong>Мониторинг қажеттілігі:</strong> Қолданыстағы жүйелерде алдын ала болжау мүмкіндігінің болмауы.</div></li>
                        </ul>
                        <div class="diagram-container" style="background: var(--bg-light); border:none; padding: 0;">
                            <img src="https://cdn-icons-png.flaticon.com/512/2324/2324391.png" style="width: 200px; opacity: 0.8;" alt="Traffic Concept">
                        </div>
                    </div>
                </div>
            </section>

            <!-- 3. Мәселе және GAP-талдау -->
            <section>
                <!-- Speaker notes: Қазіргі Yandex Maps немесе 2GIS сияқты жүйелер көбіне ағымдағы, яғни пост-фактум жағдайды көрсетеді. Біздің жобамыздың басты айырмашылығы - ол қысқа мерзімді болжауға, аномалияларды статистикалық анықтауға және What-If сценарийлерін модельдеуге бағытталған. -->
                <div class="slide-number-badge">3</div>
                <div class="slide-card">
                    <h2>Мәселе және GAP-талдау</h2>
                    <div class="info-box" style="border-left-width: 6px; margin-bottom: 25px;">
                        <p style="font-size: 0.95em; margin: 0; color: var(--navy); font-weight: 500;">
                            Қазіргі навигациялық жүйелер (Yandex, 2GIS, Google Maps) көбіне <strong>ағымдағы жағдайды көрсетеді</strong>, ал ұсынылған AI Traffic жүйесі <strong>қысқа мерзімді болжау</strong>, <strong>аномалияны анықтау</strong> және <strong>What-If сценарийлерін модельдеу</strong> арқылы ерекшеленеді.
                        </p>
                    </div>
                    
                    <table class="modern-table">
                        <tr>
                            <th>Функционалдық бағыт</th>
                            <th>Қазіргі жүйелер (Базалық деңгей)</th>
                            <th style="background: var(--blue);">AI Traffic (Дипломдық жоба)</th>
                        </tr>
                        <tr>
                            <td><strong>Трафик мониторингі</strong></td>
                            <td>Нақты уақыттағы көрсеткіштер (пост-фактум)</td>
                            <td><strong>30-60 минутқа алдын ала болжау</strong> (LSTM)</td>
                        </tr>
                        <tr>
                            <td><strong>Аномалияларды анықтау</strong></td>
                            <td>Пайдаланушылардың қолмен белгілеуі</td>
                            <td><strong>Статистикалық Z-Score</strong> арқылы автоматты анықтау</td>
                        </tr>
                        <tr>
                            <td><strong>Маршрутизация (Routing)</strong></td>
                            <td>Ең қысқа немесе ағымдағы ең жылдам жол</td>
                            <td><strong>Болжамдық traffic cost</strong> негізіндегі Dijkstra/A*</td>
                        </tr>
                        <tr>
                            <td><strong>Аналитикалық симуляция</strong></td>
                            <td>Жоқ</td>
                            <td><strong>Digital Twin</strong> (жол жабылғандағы ағынды есептеу)</td>
                        </tr>
                    </table>
                    <p style="font-size: 0.75em; color: var(--text-muted); margin-top: 10px;">
                        *Дипломдық жоба аясында негізгі акцент түсіндірілетін ML-модельдерге (Explainable AI) және алгоритмдік зерттеу бөліміне жасалды.
                    </p>
                </div>
            </section>

            <!-- 4. Зерттеу мақсаты мен міндеттері -->
            <section>
                <!-- Speaker notes: Жұмыстың мақсаты - LSTM нейрондық желісі негізінде қалалық трафикті бақылау және болжау жүйесін әзірлеу. Осы мақсатқа жету үшін деректер жинау, API жасау, ML модельді оқыту және оларды мобильді қосымшамен біріктіріп бағалау міндеттері қойылды. -->
                <div class="slide-number-badge">4</div>
                <div class="slide-card">
                    <h2>Зерттеу мақсаты мен міндеттері</h2>
                    <div class="info-box blue" style="background: rgba(37,99,235,0.05); margin-bottom: 25px;">
                        <h4 style="color: var(--blue);"><i class="fa-solid fa-bullseye"></i> Зерттеу мақсаты</h4>
                        <p style="font-weight: 500; font-size: 0.9em; margin: 0;">
                            LSTM нейрондық желісі негізінде қалалық трафикті нақты уақытта бақылауға және қысқа мерзімді (30-60 минут) болжауға арналған интеллектуалды жүйені әзірлеу.
                        </p>
                    </div>
                    
                    <h4 style="font-size: 1em; color: var(--navy); margin-bottom: 15px;"><i class="fa-solid fa-list-check" style="color: var(--blue); margin-right: 10px;"></i> Зерттеу міндеттері:</h4>
                    <div class="grid-2">
                        <ul class="custom-list">
                            <li><i class="fa-solid fa-database"></i><div>Трафик деректерін жинау және қалалық симуляциялық датасет құру.</div></li>
                            <li><i class="fa-solid fa-server"></i><div>PostgreSQL/PostGIS және FastAPI негізінде backend API әзірлеу.</div></li>
                            <li><i class="fa-solid fa-brain"></i><div>Уақыттық қатарларды болжау үшін LSTM және қосымша ML модельдерін іске асыру.</div></li>
                        </ul>
                        <ul class="custom-list">
                            <li><i class="fa-solid fa-mobile-screen"></i><div>Кроссплатформалық Flutter мобильді қосымшасы мен Web-интерфейсті құру.</div></li>
                            <li><i class="fa-solid fa-chart-bar"></i><div>Әзірленген модельдің дәлдігін MAE, RMSE және Accuracy метрикалары арқылы бағалау.</div></li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- 5. Зерттеу нысаны, пәні және ғылыми жаңалығы -->
            <section>
                <!-- Speaker notes: Зерттеу нысаны - қалалық көлік ағындары. Пәні - трафикті болжауға арналған ML алгоритмдері. Жұмыстың басты ғылыми жаңалығы - LSTM болжау, Z-score аномалияны анықтау және Digital Twin элементтерін бір қолданбалы кешенде біріктіру. -->
                <div class="slide-number-badge">5</div>
                <div class="slide-card">
                    <h2>Нысан, пән және ғылыми жаңалық</h2>
                    <div class="grid-3">
                        <div class="info-box navy" style="display: flex; flex-direction: column;">
                            <h4 style="color: var(--navy); border-bottom: 1px solid #e2e8f0; padding-bottom: 10px;"><i class="fa-solid fa-city"></i> Зерттеу нысаны</h4>
                            <p style="font-size: 0.9em; flex: 1;">Қалалық көлік инфрақұрылымы және автомобиль жолдарындағы <strong>көлік ағындары</strong>.</p>
                        </div>
                        <div class="info-box blue" style="display: flex; flex-direction: column;">
                            <h4 style="color: var(--blue); border-bottom: 1px solid #e2e8f0; padding-bottom: 10px;"><i class="fa-solid fa-network-wired"></i> Зерттеу пәні</h4>
                            <p style="font-size: 0.9em; flex: 1;">Көлік ағындарын талдау, болжау және аномалияларды анықтауға арналған <strong>AI/ML алгоритмдері мен нейрондық желілер</strong>.</p>
                        </div>
                        <div class="info-box green" style="display: flex; flex-direction: column;">
                            <h4 style="color: var(--green); border-bottom: 1px solid #e2e8f0; padding-bottom: 10px;"><i class="fa-solid fa-lightbulb"></i> Ғылыми жаңалық</h4>
                            <p style="font-size: 0.85em; flex: 1; margin-bottom:0;">
                                Кешенді қолданбалы жүйе ішінде бірнеше технологияны біріктіру: 
                                <br><br>
                                <strong>LSTM</strong> (уақыттық болжау) + <strong>Anomaly Detection</strong> (Z-Score) + <strong>Routing Cost</strong> (болжамдық салмақ) + <strong>Digital Twin</strong> элементтері.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 6. Деректер және симуляция моделі -->
            <section>
                <!-- Speaker notes: Қалалық нақты API қолжетімсіз болғандықтан, зерттеу кезеңінде тарихи және симуляциялық деректер генераторы әзірленді. Жүйе Астана қаласы бойынша 144 бақылау нүктесін қамтиды және ауа-райы, rush-hour сияқты факторларды ескере отырып деректерді дерекқорға жинайды. -->
                <div class="slide-number-badge">6</div>
                <div class="slide-card">
                    <h2>Деректер және симуляция моделі</h2>
                    
                    <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px; font-size: 0.8em; margin-bottom: 20px; color: #b45309; border-radius: 4px;">
                        <i class="fa-solid fa-circle-info"></i> <strong>Зерттеу деректері:</strong> Қалалық нақты ITS API қолжетімсіздігіне байланысты, зерттеу кезеңінде тарихи статистика негізіндегі математикалық симуляциялық модель қолданылды. Архитектура нақты API-мен тікелей интеграцияға дайын.
                    </div>

                    <div class="grid-2">
                        <ul class="custom-list">
                            <li><i class="fa-solid fa-location-dot"></i><div><strong>144 бақылау нүктесі:</strong> Жол сегменттері үшін кеңістіктік тор (Spatial Grid) құрылды.</div></li>
                            <li><i class="fa-solid fa-clock"></i><div><strong>Rush Hour Factor:</strong> Таңертеңгі және кешкі қарбалас уақыттардың математикалық профилі.</div></li>
                            <li><i class="fa-solid fa-cloud-rain"></i><div><strong>Weather Factor:</strong> Жауын-шашынның трафик жылдамдығына әсер ету коэффициенті.</div></li>
                            <li><i class="fa-solid fa-fire-flame-curved"></i><div><strong>Congestion Hotspots:</strong> Тұрақты кептеліс жиналатын ошақтарды модельдеу.</div></li>
                        </ul>
                        
                        <div class="diagram-container" style="padding: 10px;">
                            <svg width="100%" height="100%" viewBox="0 0 300 200">
                                <rect x="10" y="80" width="60" height="40" rx="5" fill="#0f172a" stroke="none"/>
                                <text x="40" y="100" font-size="8" fill="white" text-anchor="middle">144 Points</text>
                                <text x="40" y="110" font-size="6" fill="#94a3b8" text-anchor="middle">(Simulation)</text>

                                <rect x="110" y="30" width="80" height="30" fill="#f1f5f9" stroke="#64748b"/>
                                <text x="150" y="48" font-size="8" text-anchor="middle">Weather Factor</text>

                                <rect x="110" y="140" width="80" height="30" fill="#f1f5f9" stroke="#64748b"/>
                                <text x="150" y="158" font-size="8" text-anchor="middle">Rush Hour Factor</text>

                                <rect x="110" y="80" width="80" height="40" rx="5" fill="#2563eb"/>
                                <text x="150" y="100" font-size="8" fill="white" text-anchor="middle">Data Pipeline</text>
                                <text x="150" y="110" font-size="6" fill="white" text-anchor="middle">& Feature Eng.</text>

                                <rect x="230" y="80" width="60" height="40" rx="5" fill="#10b981"/>
                                <text x="260" y="100" font-size="8" fill="white" text-anchor="middle">PostgreSQL</text>
                                <text x="260" y="110" font-size="8" fill="white" text-anchor="middle">Database</text>

                                <!-- Arrows -->
                                <path d="M 70 100 L 110 100" fill="none" stroke="#64748b" marker-end="url(#arrow)"/>
                                <path d="M 150 60 L 150 80" fill="none" stroke="#64748b" marker-end="url(#arrow)"/>
                                <path d="M 150 140 L 150 120" fill="none" stroke="#64748b" marker-end="url(#arrow)"/>
                                <path d="M 190 100 L 230 100" fill="none" stroke="#64748b" marker-end="url(#arrow)"/>
                            </svg>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 7. Жүйенің жалпы архитектурасы -->
            <section>
                <!-- Speaker notes: Жүйенің архитектурасы бірнеше қабаттан тұрады. Клиенттік бөлік Flutter және Vue.js арқылы жасалған. Олар FastAPI арқылы Python AI Pipeline-мен және PostgreSQL базасымен байланысады. Real-time үшін WebSocket қолданылады. -->
                <div class="slide-number-badge">7</div>
                <div class="slide-card">
                    <h2>Жүйенің жалпы архитектурасы</h2>
                    <p style="font-size: 0.85em; color: var(--text-main); margin-bottom: 20px;">
                        Қосымша микросервистік тәсіл негізінде заманауи стекпен (Flutter/Dart + FastAPI/Python + PostgreSQL) құрылған.
                    </p>
                    <div class="diagram-container" style="height: 350px;">
                        <svg width="100%" height="100%" viewBox="0 0 800 300">
                            <!-- Client -->
                            <rect x="50" y="80" width="120" height="50" rx="5" fill="#3b82f6" stroke="none"/>
                            <text x="110" y="105" font-size="12" fill="white" text-anchor="middle">Flutter Mobile</text>
                            <text x="110" y="120" font-size="10" fill="#bfdbfe" text-anchor="middle">(User App)</text>

                            <rect x="50" y="160" width="120" height="50" rx="5" fill="#8b5cf6" stroke="none"/>
                            <text x="110" y="185" font-size="12" fill="white" text-anchor="middle">Web Dashboard</text>
                            <text x="110" y="200" font-size="10" fill="#ddd6fe" text-anchor="middle">(Admin Panel)</text>

                            <!-- Backend / API -->
                            <rect x="250" y="100" width="140" height="90" rx="5" fill="#0f172a" stroke="none"/>
                            <text x="320" y="140" font-size="14" font-weight="bold" fill="white" text-anchor="middle">FastAPI Backend</text>
                            <text x="320" y="160" font-size="10" fill="#94a3b8" text-anchor="middle">REST + WebSocket</text>

                            <!-- AI / DB -->
                            <rect x="470" y="60" width="140" height="70" rx="5" fill="#10b981" stroke="none"/>
                            <text x="540" y="95" font-size="12" font-weight="bold" fill="white" text-anchor="middle">Python AI Pipeline</text>
                            <text x="540" y="115" font-size="10" fill="#d1fae5" text-anchor="middle">LSTM / PyTorch</text>

                            <rect x="470" y="160" width="140" height="70" rx="5" fill="#f59e0b" stroke="none"/>
                            <text x="540" y="195" font-size="12" font-weight="bold" fill="white" text-anchor="middle">PostgreSQL + PostGIS</text>
                            <text x="540" y="215" font-size="10" fill="#fef3c7" text-anchor="middle">Spatial Database</text>

                            <!-- Arrows -->
                            <path d="M 170 105 L 250 130" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
                            <path d="M 170 185 L 250 160" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
                            
                            <path d="M 390 120 L 470 95" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)" marker-start="url(#arrow)"/>
                            <path d="M 390 170 L 470 195" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)" marker-start="url(#arrow)"/>
                            
                            <path d="M 540 130 L 540 160" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)" marker-start="url(#arrow)"/>
                        </svg>
                    </div>
                </div>
            </section>

            <!-- 8. LSTM арқылы трафикті болжау алгоритмі -->
            <section>
                <!-- Speaker notes: Бұл жобаның басты ғылыми өзегі - LSTM алгоритмі. Уақыттық қатарлар PyTorch арқылы өңделеді. Модель параметрлері: hidden size 64, 2 қабат, және lookback window 12 қадамнан тұрады. -->
                <div class="slide-number-badge">8</div>
                <div class="slide-card">
                    <h2>LSTM арқылы трафикті болжау алгоритмі</h2>
                    <div class="grid-2">
                        <div>
                            <ul class="custom-list">
                                <li><i class="fa-solid fa-microchip"></i><div><strong>Неге LSTM таңдалды?</strong> Уақыттық қатарлармен (time-series) жақсы жұмыс істейді, өткен жағдайды (күрделі тәуелділіктерді) есте сақтайды.</div></li>
                                <li><i class="fa-solid fa-code"></i><div><strong>Фреймворк:</strong> PyTorch (<code>nn.LSTM</code>).</div></li>
                                <li><i class="fa-solid fa-sliders"></i><div><strong>Гиперпараметрлер:</strong>
                                    <ul style="margin-top: 5px; margin-left: 0px; padding-left: 20px; list-style-type: circle;">
                                        <li>Hidden size: 64</li>
                                        <li>Layers: 2 қабат</li>
                                        <li>Dropout: 0.2</li>
                                        <li>Lookback window: 12 қадам</li>
                                        <li>Loss / Optimizer: MSELoss, Adam</li>
                                    </ul></div>
                                </li>
                            </ul>
                        </div>
                        <div class="diagram-container" style="flex-direction: column;">
                            <div style="font-size: 0.8em; font-weight: bold; margin-bottom: 10px; color: var(--navy);">LSTM Processing Pipeline</div>
                            <svg width="100%" height="200" viewBox="0 0 300 200">
                                <rect x="20" y="85" width="50" height="30" rx="3" fill="#cbd5e1" stroke="none"/>
                                <text x="45" y="103" font-size="8" text-anchor="middle">Input Seq.</text>
                                
                                <rect x="100" y="80" width="40" height="40" rx="3" fill="#3b82f6" stroke="none"/>
                                <text x="120" y="103" font-size="8" fill="white" text-anchor="middle">LSTM 1</text>
                                
                                <rect x="170" y="80" width="40" height="40" rx="3" fill="#3b82f6" stroke="none"/>
                                <text x="190" y="103" font-size="8" fill="white" text-anchor="middle">LSTM 2</text>
                                
                                <rect x="240" y="85" width="40" height="30" rx="3" fill="#10b981" stroke="none"/>
                                <text x="260" y="103" font-size="8" fill="white" text-anchor="middle">FC Layer</text>

                                <!-- Arrows -->
                                <path d="M 70 100 L 100 100" fill="none" stroke="#64748b" marker-end="url(#arrow)"/>
                                <path d="M 140 100 L 170 100" fill="none" stroke="#64748b" marker-end="url(#arrow)"/>
                                <path d="M 210 100 L 240 100" fill="none" stroke="#64748b" marker-end="url(#arrow)"/>
                                
                                <text x="260" y="135" font-size="7" fill="#10b981" font-weight="bold" text-anchor="middle">Prediction</text>
                                <text x="260" y="145" font-size="7" fill="#10b981" text-anchor="middle">(30-60 min)</text>
                                <path d="M 260 115 L 260 125" fill="none" stroke="#10b981" marker-end="url(#arrow)"/>
                            </svg>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 9. Қосымша алгоритмдер -->
            <section>
                <!-- Speaker notes: Трафик өте күрделі процесс болғандықтан, тек бір модель жеткіліксіз. Біз деректерді тегістеу үшін EMA, трендті тез бағалау үшін Linear Regression, аномалиялар үшін Z-Score және маршрутты табу үшін Dijkstra алгоритмдерін біріктірдік. -->
                <div class="slide-number-badge">9</div>
                <div class="slide-card">
                    <h2>Қосымша алгоритмдер кешені</h2>
                    <p style="font-size: 0.85em; color: var(--text-main); margin-bottom: 20px;">
                        Неге бірнеше алгоритм қолданылды? Қалалық трафик — күрделі стохастикалық жүйе, бір ғана модель барлық жағдайды (шуыл, аномалия, навигация) қамти алмайды.
                    </p>
                    <div class="grid-2">
                        <div class="info-box" style="border-left-color: #f59e0b;">
                            <h4 style="color: #f59e0b;"><i class="fa-solid fa-filter"></i> EMA (Exponential Moving Avg)</h4>
                            <p>GPS және сенсор деректеріндегі жоғары жиілікті <strong>шуды тегістеу (сглаживание)</strong> үшін қолданылады.</p>
                        </div>
                        <div class="info-box" style="border-left-color: #0ea5e9;">
                            <h4 style="color: #0ea5e9;"><i class="fa-solid fa-chart-line"></i> Linear Regression</h4>
                            <p>Кептеліс деңгейінің <strong>өсу немесе кему трендін</strong> лезде (LSTM-сіз) бағалау үшін.</p>
                        </div>
                        <div class="info-box" style="border-left-color: #ef4444;">
                            <h4 style="color: #ef4444;"><i class="fa-solid fa-triangle-exclamation"></i> Z-Score (Anomaly Detection)</h4>
                            <p>Жылдамдықтың нормадан күрт ауытқуын анықтап, <strong>ЖКО немесе жол жабылуын (резкие скачки)</strong> тіркейді.</p>
                        </div>
                        <div class="info-box purple">
                            <h4 style="color: var(--purple);"><i class="fa-solid fa-route"></i> Dijkstra / A* Algorithm</h4>
                            <p>Графтар теориясы негізінде, болжамдық <strong>Predicted Cost</strong> (қашықтық + трафик салмағы) арқылы ең тиімді маршрутты есептеу.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 10. Модельдерді салыстыру және бағалау -->
            <section>
                <!-- Speaker notes: Модельдердің дәлдігі симуляциялық деректер базасында тексерілді. Нәтижесінде LSTM алгоритмі орташа абсолютті қателік (MAE) мен дәлдік (Accuracy) бойынша Linear Regression мен Random Forest-ті артта қалдырды. -->
                <div class="slide-number-badge">10</div>
                <div class="slide-card">
                    <h2>Модельдерді салыстыру және бағалау</h2>
                    <p style="font-size: 0.85em; color: var(--text-main); margin-bottom: 20px;">
                        Алгоритмдердің тиімділігі тарихи және симуляциялық датасет негізінде бағаланды.
                    </p>
                    
                    <table class="modern-table" style="font-size: 0.9em;">
                        <tr>
                            <th>Модель</th>
                            <th>MAE (Орташа қателік) ↓</th>
                            <th>RMSE ↓</th>
                            <th>Accuracy (Дәлдік) ↑</th>
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
                            <td style="color: var(--green); font-weight: bold;">LSTM (Ұсынылған)</td>
                            <td style="color: var(--green); font-weight: bold;">0.08</td>
                            <td style="color: var(--green); font-weight: bold;">0.12</td>
                            <td style="color: var(--green); font-weight: bold;">87.4%</td>
                        </tr>
                    </table>

                    <div class="grid-2" style="margin-top: 20px;">
                        <ul class="custom-list">
                            <li><i class="fa-solid fa-check" style="color: var(--green);"></i><div><strong>MAE (Mean Absolute Error)</strong> — модельдің нақты мәннен орташа ауытқуы (төмен болған сайын жақсы).</div></li>
                            <li><i class="fa-solid fa-check" style="color: var(--green);"></i><div>LSTM алгоритмі уақыттық қатарлардың динамикасын басқа модельдерге қарағанда <strong>~6% дәлірек</strong> таниды.</div></li>
                        </ul>
                        <div style="font-size: 0.75em; background: #f8fafc; padding: 10px; border-left: 3px solid #64748b; color: var(--text-muted);">
                            *Ескерту: Бағалау кезеңінде нақты қалалық трафик сенсорлары емес, жүйенің өз генераторы арқылы жиналған тарихи/симуляциялық деректер қолданылды.
                        </div>
                    </div>
                </div>
            </section>

            <!-- 11. Бағдарламаны іске асыру -->
            <section>
                <!-- Speaker notes: Бағдарламалық қамтамасыз ету екі негізгі бөліктен тұрады: Жүргізушілерге арналған интерактивті мобильді қосымша және операторларға арналған Web Admin панелі. Олар нақты уақыт режимінде деректерді көрсетеді. -->
                <div class="slide-number-badge">11</div>
                <div class="slide-card">
                    <h2>Бағдарламаны іске асыру (Implementation)</h2>
                    <div class="grid-2" style="align-items: center;">
                        <ul class="custom-list">
                            <li><i class="fa-solid fa-mobile-screen"></i><div><strong>Мобильді карта (Flutter):</strong> Жүргізушілерге арналған интерактивті интерфейс, ағымдағы кептеліс деңгейін көрсетеді.</div></li>
                            <li><i class="fa-solid fa-route"></i><div><strong>Смарт-Маршрут:</strong> Predicted cost арқылы ең тиімді бағытты сызу.</div></li>
                            <li><i class="fa-solid fa-desktop"></i><div><strong>Web Admin Panel (Vue.js):</strong> Қалалық диспетчерлерге арналған Live Map.</div></li>
                            <li><i class="fa-solid fa-chart-pie"></i><div><strong>Метрикалар Dashboard-ы:</strong> Жалпы қалалық жүктеме мен модель дәлдігін бақылау тақтасы.</div></li>
                        </ul>
                        <div style="display: flex; gap: 15px; justify-content: center;">
                            <!-- CSS Wireframe Mobile -->
                            <div style="width: 130px; height: 260px; border-radius: 15px; border: 3px solid #0f172a; background: #f1f5f9; display: flex; flex-direction: column; overflow: hidden;">
                                <div style="height: 30px; background: var(--blue); color: white; font-size: 0.6em; display: flex; align-items: center; justify-content: center; font-weight: bold;">AI Traffic Mobile</div>
                                <div style="flex: 1; padding: 10px; display: flex; flex-direction: column; gap: 10px;">
                                    <div style="background: white; border-radius: 5px; height: 40px; border-left: 3px solid var(--green); padding: 5px; font-size: 0.5em;">Трафик: Қалыпты<br>Болжам: 30 мин өзгеріссіз</div>
                                    <div style="background: #cbd5e1; flex: 1; border-radius: 5px; display: flex; align-items: center; justify-content: center;"><i class="fa-solid fa-map-location-dot" style="font-size: 2em; color: white;"></i></div>
                                </div>
                            </div>
                            <!-- CSS Wireframe Web -->
                            <div style="width: 180px; height: 160px; border-radius: 8px; border: 2px solid #0f172a; background: #f1f5f9; display: flex; flex-direction: column; overflow: hidden; align-self: center;">
                                <div style="height: 20px; background: #0f172a; color: white; font-size: 0.5em; display: flex; align-items: center; padding-left: 10px;">Admin Dashboard</div>
                                <div style="flex: 1; padding: 10px; display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
                                    <div style="background: white; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 0.6em; font-weight: bold; color: var(--blue);">Live Map</div>
                                    <div style="background: white; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 0.6em; font-weight: bold; color: var(--purple);">Analytics</div>
                                    <div style="grid-column: span 2; background: white; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 0.6em; color: #ef4444;"><i class="fa-solid fa-triangle-exclamation"></i> 2 Аномалия</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 12. Тестілеу нәтижелері -->
            <section>
                <!-- Speaker notes: Кешенді тестілеу барысында барлық модульдердің дұрыс жұмыс істейтіні расталды. Backend API жауап береді, LSTM болжам жасайды, және аномалиялар уақтылы анықталады. -->
                <div class="slide-number-badge">12</div>
                <div class="slide-card">
                    <h2>Тестілеу және жүйенің жұмыс нәтижелері</h2>
                    <div class="info-box green" style="background: rgba(16,185,129,0.05); margin-bottom: 20px;">
                        <h4 style="color: var(--green); margin-bottom: 5px;"><i class="fa-solid fa-server"></i> Интеграциялық тестілеу сәтті аяқталды</h4>
                        <p style="margin: 0;">Барлық микросервистер мен алгоритмдер бірыңғай экожүйеде штаттық режимде жұмыс істейтіні дәлелденді.</p>
                    </div>

                    <table class="modern-table">
                        <tr>
                            <th>Модуль / Компонент</th>
                            <th>Тестілеу нәтижесі (Статус)</th>
                        </tr>
                        <tr>
                            <td><strong>Backend API (FastAPI)</strong></td>
                            <td><i class="fa-solid fa-circle-check" style="color: var(--green);"></i> Іске қосылды, HTTP сұрауларға тұрақты жауап береді</td>
                        </tr>
                        <tr>
                            <td><strong>Деректер жинау (Data Layer)</strong></td>
                            <td><i class="fa-solid fa-circle-check" style="color: var(--green);"></i> 144 сегменттен тарихи деректер БД-ға (PostgreSQL) жиналды</td>
                        </tr>
                        <tr>
                            <td><strong>AI Prediction (LSTM)</strong></td>
                            <td><i class="fa-solid fa-circle-check" style="color: var(--green);"></i> Жаңа жазбалар негізінде 30 минуттық болжам жасайды</td>
                        </tr>
                        <tr>
                            <td><strong>Anomaly Detection (Z-Score)</strong></td>
                            <td><i class="fa-solid fa-circle-check" style="color: var(--green);"></i> Жылдамдықтың күрт төмендеуін (апатты) тіркейді</td>
                        </tr>
                        <tr>
                            <td><strong>Mobile / Web UI</strong></td>
                            <td><i class="fa-solid fa-circle-check" style="color: var(--green);"></i> Деректерді WebSocket арқылы қабылдап, картада көрсетеді</td>
                        </tr>
                    </table>
                </div>
            </section>

            <!-- 13. Қорытынды және болашақ даму -->
            <section>
                <!-- Speaker notes: Қорытындылай келе, қойылған мақсат орындалып, AI Traffic жүйесі құрылды. Болашақта жүйені нақты ITS камераларымен және сенсорларымен байланыстырып, басқа қалаларға масштабтауды жоспарлап отырмыз. Назарларыңызға рақмет! -->
                <div class="slide-number-badge">13</div>
                <div class="slide-card">
                    <h2>Қорытынды және болашақ даму</h2>
                    
                    <div class="info-box navy" style="margin-bottom: 20px;">
                        <h4 style="color: var(--navy);"><i class="fa-solid fa-flag-checkered"></i> Нәтиже:</h4>
                        <p style="font-weight: 500; color: var(--navy); margin: 0;">
                            AI Traffic жүйесі қалалық трафикті бақылауға, LSTM арқылы қысқа мерзімді болжауға, аномалияларды статистикалық анықтауға және маршрутты интеллектуалды таңдауға мүмкіндік беретін толыққанды архитектура ретінде іске асырылды.
                        </p>
                    </div>

                    <h4 style="font-size: 1em; color: var(--blue); margin-bottom: 15px;"><i class="fa-solid fa-rocket"></i> Болашақ даму бағыттары (Future Work):</h4>
                    <div class="grid-2">
                        <ul class="custom-list">
                            <li><i class="fa-solid fa-arrow-right"></i><div><strong>Real ITS API:</strong> Қалалық нақты бейнебақылау камералары мен сенсорлар деректеріне қосылу.</div></li>
                            <li><i class="fa-solid fa-arrow-right"></i><div><strong>Масштабтау:</strong> Жүйені тек бір қала емес, бірнеше қалаларға (Multi-city) бейімдеу.</div></li>
                        </ul>
                        <ul class="custom-list">
                            <li><i class="fa-solid fa-arrow-right"></i><div><strong>Model Retraining:</strong> Жаңа деректер түскен сайын модельді автоматты түрде қайта оқыту (MLOps).</div></li>
                            <li><i class="fa-solid fa-arrow-right"></i><div><strong>Push-хабарламалар:</strong> Жолдағы төтенше жағдайлар туралы жүргізушілерге лезде ескерту.</div></li>
                        </ul>
                    </div>
                </div>
            </section>

        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/reveal.min.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            slideNumber: false,
            transition: 'fade',
            width: 1200,
            height: 700,
            margin: 0.1,
            minScale: 0.2,
            maxScale: 2.0
        });
    </script>
</body>
</html>"""
    with open('presentation.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("presentation.html has been successfully generated with exactly 13 PhD-style scientific slides!")

if __name__ == "__main__":
    build_13_slide_presentation()
