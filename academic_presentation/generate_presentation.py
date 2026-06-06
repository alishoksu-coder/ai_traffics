import os

html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Traffic Monitoring & Forecasting - Defense Presentation</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&family=Outfit:wght@400;600;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #020617;
            --surface-color: rgba(15, 23, 42, 0.6);
            --card-border: rgba(51, 65, 85, 0.5);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyan: #06b6d4;
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --glow-cyan: rgba(6, 182, 212, 0.3);
            --glow-blue: rgba(59, 130, 246, 0.3);
            --glow-purple: rgba(139, 92, 246, 0.3);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            overflow: hidden;
            line-height: 1.6;
        }

        /* Subtle Grid Background & Radial Glows */
        .bg-layer {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            z-index: -1;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            background-position: center center;
        }
        
        .bg-layer::before {
            content: '';
            position: absolute;
            top: -10%; left: -10%; width: 50%; height: 50%;
            background: radial-gradient(circle, var(--glow-blue), transparent 60%);
            filter: blur(100px);
        }

        .bg-layer::after {
            content: '';
            position: absolute;
            bottom: -10%; right: -10%; width: 50%; height: 50%;
            background: radial-gradient(circle, var(--glow-purple), transparent 60%);
            filter: blur(100px);
        }

        /* Top Navigation */
        nav {
            position: fixed;
            top: 0; left: 0; width: 100%;
            height: 60px;
            background: rgba(2, 6, 23, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--card-border);
            display: flex;
            align-items: center;
            padding: 0 40px;
            z-index: 100;
            justify-content: space-between;
        }

        .nav-brand {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 1.2rem;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-dots {
            display: flex;
            gap: 8px;
        }

        .nav-dot {
            width: 10px; height: 10px;
            border-radius: 50%;
            background: var(--text-muted);
            cursor: pointer;
            transition: all 0.3s;
        }

        .nav-dot.active {
            background: var(--accent-cyan);
            box-shadow: 0 0 10px var(--accent-cyan);
            transform: scale(1.3);
        }

        .slide-counter {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: var(--text-muted);
        }

        /* Slides Container */
        .slides-container {
            height: 100vh;
            width: 100vw;
            transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
        }

        section {
            height: 100vh;
            width: 100vw;
            padding: 100px 60px 40px 60px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .content-wrapper {
            width: 100%;
            max-width: 1200px;
            max-height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        /* Typography */
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            margin-bottom: 20px;
            font-weight: 800;
        }

        h1 {
            font-size: 4rem;
            line-height: 1.1;
            margin-bottom: 30px;
            letter-spacing: -0.02em;
        }

        h2 {
            font-size: 2.8rem;
            color: var(--text-main);
            border-left: 6px solid var(--accent-cyan);
            padding-left: 20px;
            margin-bottom: 40px;
        }

        .text-gradient {
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        p, li {
            font-size: 1.2rem;
            color: var(--text-muted);
            margin-bottom: 15px;
        }

        /* Components */
        .glass-card {
            background: var(--surface-color);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            border-color: rgba(6, 182, 212, 0.4);
            box-shadow: 0 15px 40px rgba(6, 182, 212, 0.1);
        }

        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }

        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            background: rgba(59, 130, 246, 0.15);
            color: var(--accent-cyan);
            border: 1px solid rgba(59, 130, 246, 0.3);
            margin-right: 10px;
            margin-bottom: 10px;
        }

        ul.custom-list { list-style: none; }
        ul.custom-list li {
            position: relative;
            padding-left: 35px;
        }
        ul.custom-list li::before {
            content: '\\f101';
            font-family: 'Font Awesome 6 Free';
            font-weight: 900;
            position: absolute;
            left: 0;
            top: 2px;
            color: var(--accent-cyan);
        }

        /* Tables */
        .academic-table {
            width: 100%;
            border-collapse: collapse;
            background: var(--surface-color);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--card-border);
        }
        .academic-table th {
            background: rgba(2, 6, 23, 0.8);
            color: var(--text-main);
            padding: 15px;
            text-align: left;
            font-family: 'JetBrains Mono', monospace;
            border-bottom: 1px solid var(--card-border);
        }
        .academic-table td {
            padding: 15px;
            border-bottom: 1px solid rgba(51, 65, 85, 0.3);
            color: var(--text-muted);
        }
        .academic-table tr:last-child td { border-bottom: none; }
        .academic-table tr:hover td { background: rgba(255,255,255,0.02); }
        .highlight-cell { color: var(--accent-cyan) !important; font-weight: bold; }

        /* Diagrams */
        .flow-diagram {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            gap: 15px;
            margin: 30px 0;
        }
        .flow-node {
            background: var(--surface-color);
            border: 1px solid var(--accent-blue);
            padding: 15px 25px;
            border-radius: 12px;
            font-weight: 600;
            box-shadow: 0 0 15px var(--glow-blue);
            text-align: center;
        }
        .flow-arrow {
            color: var(--accent-cyan);
            font-size: 1.5rem;
        }
        
        .lstm-diagram {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }
        .lstm-block {
            width: 300px;
            text-align: center;
            padding: 15px;
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid var(--accent-purple);
            border-radius: 12px;
        }

        /* Animations */
        .fade-up {
            opacity: 0;
            transform: translateY(40px);
            transition: opacity 0.8s ease, transform 0.8s ease;
        }
        .fade-up.visible {
            opacity: 1;
            transform: translateY(0);
        }
        .delay-1 { transition-delay: 0.1s; }
        .delay-2 { transition-delay: 0.2s; }
        .delay-3 { transition-delay: 0.3s; }

        /* Mockup */
        .dashboard-mockup {
            border: 2px solid var(--card-border);
            border-radius: 12px;
            background: #0f172a;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }
        .mockup-header {
            height: 30px;
            background: #1e293b;
            display: flex;
            align-items: center;
            padding: 0 15px;
            gap: 6px;
        }
        .mockup-dot { width: 10px; height: 10px; border-radius: 50%; background: #ef4444; }
        .mockup-dot:nth-child(2) { background: #eab308; }
        .mockup-dot:nth-child(3) { background: #22c55e; }
    </style>
</head>
<body>
    <div class="bg-layer"></div>
    
    <nav>
        <div class="nav-brand">AI Traffic Defense</div>
        <div class="nav-dots" id="nav-dots"></div>
        <div class="slide-counter" id="slide-counter">1 / 18</div>
    </nav>

    <main class="slides-container" id="slides-container">
        
        <!-- 1. Титульный слайд -->
        <section>
            <div class="content-wrapper fade-up">
                <div style="margin-bottom: 20px;">
                    <span class="badge">PhD Dissertation Defense / IEEE Level</span>
                    <span class="badge">AI Traffic Monitoring & Forecasting</span>
                </div>
                <h1>Разработка AI-приложения для <br><span class="text-gradient">мониторинга и прогноза</span> <br>транспортных потоков</h1>
                <p style="font-size: 1.5rem; color: var(--text-main); margin-bottom: 40px;">в условиях городской среды</p>
                
                <div class="glass-card" style="display: inline-block; padding: 20px 30px;">
                    <h3 style="font-size: 1.1rem; color: var(--text-muted); margin-bottom: 10px;">Ключевой стек технологий:</h3>
                    <div>
                        <span class="badge" style="border-color: #3b82f6;">Python</span>
                        <span class="badge" style="border-color: #10b981;">Django</span>
                        <span class="badge" style="border-color: #3b82f6;">PostgreSQL</span>
                        <span class="badge" style="border-color: #ef4444;">PyTorch (LSTM)</span>
                        <span class="badge" style="border-color: #f59e0b;">Random Forest</span>
                        <span class="badge" style="border-color: #8b5cf6;">REST API</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- 2. Актуальность проблемы -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Актуальность проблемы</h2>
                <div class="grid-2">
                    <div class="glass-card fade-up delay-1">
                        <h3><i class="fa-solid fa-city text-gradient"></i> Вызовы мегаполисов</h3>
                        <ul class="custom-list">
                            <li>Экспоненциальный рост городского трафика.</li>
                            <li>Хроническая перегрузка дорожной сети.</li>
                            <li>Экологические и экономические издержки.</li>
                        </ul>
                    </div>
                    <div class="glass-card fade-up delay-2">
                        <h3><i class="fa-solid fa-chart-line text-gradient"></i> Ограничения текущих методов</h3>
                        <ul class="custom-list">
                            <li>Ограниченность ручного анализа и статических моделей.</li>
                            <li>Необходимость проактивного интеллектуального мониторинга.</li>
                            <li>Необходим переход к <strong>data-driven urban mobility</strong>.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- 3. Цель и задачи проекта -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Цель и задачи проекта</h2>
                <div class="glass-card fade-up delay-1" style="margin-bottom: 30px; border-left: 4px solid var(--accent-cyan);">
                    <h3 style="color: var(--text-main);">Цель исследования</h3>
                    <p>Разработать комплексное AI-приложение для сбора, мониторинга, анализа и прогноза транспортных потоков в городских условиях.</p>
                </div>
                <div class="grid-3">
                    <div class="glass-card fade-up delay-2"><i class="fa-solid fa-database text-gradient fa-2x mb-3"></i><br>Сбор и хранение данных о дорожном движении.</div>
                    <div class="glass-card fade-up delay-2"><i class="fa-solid fa-server text-gradient fa-2x mb-3"></i><br>Построение отказоустойчивой backend-системы.</div>
                    <div class="glass-card fade-up delay-2"><i class="fa-solid fa-brain text-gradient fa-2x mb-3"></i><br>Разработка ML-модуля для прогнозирования загрузки.</div>
                    <div class="glass-card fade-up delay-3"><i class="fa-solid fa-map-location-dot text-gradient fa-2x mb-3"></i><br>Визуализация показателей на интерактивной карте.</div>
                    <div class="glass-card fade-up delay-3"><i class="fa-solid fa-scale-balanced text-gradient fa-2x mb-3"></i><br>Сравнение baseline и нейросетевых ML-моделей.</div>
                    <div class="glass-card fade-up delay-3"><i class="fa-solid fa-cubes text-gradient fa-2x mb-3"></i><br>Подготовка архитектуры для масштабирования (IoT).</div>
                </div>
            </div>
        </section>

        <!-- 4. Объект и предмет исследования -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Объект и предмет исследования</h2>
                <div class="grid-2" style="margin-top: 50px;">
                    <div class="glass-card fade-up delay-1" style="text-align: center; padding: 60px 40px;">
                        <i class="fa-solid fa-road fa-4x mb-4" style="color: var(--accent-blue); margin-bottom: 20px;"></i>
                        <h3>Объект исследования</h3>
                        <p style="font-size: 1.4rem; color: var(--text-main);">Транспортные потоки<br>городской среды</p>
                    </div>
                    <div class="glass-card fade-up delay-2" style="text-align: center; padding: 60px 40px;">
                        <i class="fa-solid fa-network-wired fa-4x mb-4" style="color: var(--accent-purple); margin-bottom: 20px;"></i>
                        <h3>Предмет исследования</h3>
                        <p style="font-size: 1.4rem; color: var(--text-main);">Методы машинного обучения для анализа и прогнозирования загруженности дорог</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- 5. GAP-анализ -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">GAP-анализ систем мониторинга</h2>
                <div class="fade-up delay-1">
                    <table class="academic-table">
                        <thead>
                            <tr>
                                <th>Традиционные системы</th>
                                <th>Ограничения (GAP)</th>
                                <th>Предлагаемое AI-решение</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Статические правила светофоров</td>
                                <td>Слабая адаптивность к внезапным заторам</td>
                                <td class="highlight-cell">Динамический мониторинг через Data Pipeline</td>
                            </tr>
                            <tr>
                                <td>Реактивные карты (пост-фактум)</td>
                                <td>Отсутствие краткосрочного прогноза (30-60 мин)</td>
                                <td class="highlight-cell">ML-прогнозирование (LSTM / Moving Average)</td>
                            </tr>
                            <tr>
                                <td>Ручной анализ аналитиков</td>
                                <td>Долго, дорого, подвержено человеческому фактору</td>
                                <td class="highlight-cell">Автоматизированный Dashboard и API</td>
                            </tr>
                            <tr>
                                <td>Разрозненные датчики</td>
                                <td>Недостаточная интеграция данных в единую модель</td>
                                <td class="highlight-cell">Единая PostgreSQL архитектура + Feature Engineering</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- 6. Архитектура системы -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Архитектура системы</h2>
                <div class="flow-diagram fade-up delay-1">
                    <div class="flow-node"><i class="fa-solid fa-satellite-dish"></i><br>Data Sources<br><small>(IoT / Traffic API)</small></div>
                    <div class="flow-arrow"><i class="fa-solid fa-arrow-right"></i></div>
                    <div class="flow-node" style="border-color: #10b981;"><i class="fa-solid fa-server"></i><br>Backend API<br><small>(Django / DRF)</small></div>
                    <div class="flow-arrow"><i class="fa-solid fa-arrow-right"></i></div>
                    <div class="flow-node" style="border-color: #3b82f6;"><i class="fa-solid fa-database"></i><br>PostgreSQL<br><small>(Time-Series DB)</small></div>
                    <div class="flow-arrow"><i class="fa-solid fa-arrow-right"></i></div>
                    <div class="flow-node" style="border-color: #ef4444;"><i class="fa-solid fa-brain"></i><br>ML Module<br><small>(Forecasting)</small></div>
                    <div class="flow-arrow"><i class="fa-solid fa-arrow-right"></i></div>
                    <div class="flow-node" style="border-color: #8b5cf6;"><i class="fa-solid fa-desktop"></i><br>Dashboard<br><small>(City Analyst)</small></div>
                </div>
                <div class="glass-card fade-up delay-2" style="margin-top: 30px;">
                    <ul class="custom-list">
                        <li><strong>Backend API</strong> обеспечивает маршрутизацию данных и бизнес-логику.</li>
                        <li><strong>PostgreSQL</strong> надежно хранит историю временных рядов (Time-series records).</li>
                        <li><strong>ML-модуль</strong> асинхронно извлекает историю и строит прогноз на ближайший горизонт.</li>
                        <li><strong>Dashboard</strong> визуализирует аналитику для конечного пользователя.</li>
                    </ul>
                </div>
            </div>
        </section>

        <!-- 7. Стек технологий -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Технологический стек</h2>
                <div class="grid-3 fade-up delay-1">
                    <div class="glass-card">
                        <h3><i class="fa-brands fa-python"></i> Backend</h3>
                        <p>Django, Django REST Framework, Gunicorn, Nginx</p>
                    </div>
                    <div class="glass-card">
                        <h3><i class="fa-solid fa-database"></i> Database</h3>
                        <p>PostgreSQL, Psycopg2, Time-series optimization</p>
                    </div>
                    <div class="glass-card">
                        <h3><i class="fa-solid fa-network-wired"></i> ML Frameworks</h3>
                        <p>PyTorch, scikit-learn, Pandas, NumPy</p>
                    </div>
                    <div class="glass-card">
                        <h3><i class="fa-solid fa-microchip"></i> ML Models</h3>
                        <p>LSTM, Random Forest, Moving Average, Naive, Linear Reg.</p>
                    </div>
                    <div class="glass-card">
                        <h3><i class="fa-brands fa-html5"></i> Frontend / UI</h3>
                        <p>HTML5, CSS3, JavaScript, React, Chart.js / Leaflet</p>
                    </div>
                    <div class="glass-card">
                        <h3><i class="fa-solid fa-table"></i> Data</h3>
                        <p>Исторические записи трафика, Time-series traffic records</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- 8. Data Pipeline -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Data Pipeline & Feature Engineering</h2>
                <div class="flow-diagram fade-up delay-1" style="font-size: 0.9rem;">
                    <div class="flow-node">Raw Data</div> <div class="flow-arrow"><i class="fa-solid fa-angle-right"></i></div>
                    <div class="flow-node">Preprocessing</div> <div class="flow-arrow"><i class="fa-solid fa-angle-right"></i></div>
                    <div class="flow-node">Feature Eng.</div> <div class="flow-arrow"><i class="fa-solid fa-angle-right"></i></div>
                    <div class="flow-node">Train/Test Split</div> <div class="flow-arrow"><i class="fa-solid fa-angle-right"></i></div>
                    <div class="flow-node">Model Training</div> <div class="flow-arrow"><i class="fa-solid fa-angle-right"></i></div>
                    <div class="flow-node">Evaluation</div> <div class="flow-arrow"><i class="fa-solid fa-angle-right"></i></div>
                    <div class="flow-node">Forecast Output</div> <div class="flow-arrow"><i class="fa-solid fa-angle-right"></i></div>
                    <div class="flow-node">Dashboard View</div>
                </div>
                <div class="glass-card fade-up delay-2">
                    <h3>Ключевые извлекаемые признаки (Features)</h3>
                    <div class="grid-3">
                        <ul class="custom-list">
                            <li><span class="badge">timestamp</span> Время фиксации</li>
                            <li><span class="badge">segment_id</span> Идентификатор дороги</li>
                        </ul>
                        <ul class="custom-list">
                            <li><span class="badge">speed</span> Средняя скорость</li>
                            <li><span class="badge">traffic_level</span> Уровень загрузки</li>
                        </ul>
                        <ul class="custom-list">
                            <li><span class="badge">historical_window</span> Окно данных</li>
                            <li><span class="badge">time_features</span> Час, день недели</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- 9. ML-модуль -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">ML-модуль: Исследуемые модели</h2>
                <p class="fade-up delay-1">В рамках научного исследования был реализован и протестирован комплекс моделей прогнозирования:</p>
                <div class="grid-2 fade-up delay-2" style="margin-top: 20px;">
                    <div class="glass-card">
                        <h3>Базовые модели (Baselines)</h3>
                        <ul class="custom-list">
                            <li><strong>Naive Baseline:</strong> Прогноз равен последнему известному значению.</li>
                            <li><strong>Moving Average:</strong> Скользящая средняя за историческое окно. Эффективна для стабильных трендов.</li>
                            <li><strong>Linear Regression Trend:</strong> Выделение линейного тренда.</li>
                        </ul>
                    </div>
                    <div class="glass-card" style="border-left: 4px solid var(--accent-purple);">
                        <h3>Сложные модели (Advanced)</h3>
                        <ul class="custom-list">
                            <li><strong>Random Forest:</strong> Ансамблевая модель для выявления нелинейных связей (день недели + час).</li>
                            <li><strong>LSTM (Long Short-Term Memory):</strong> Нейросетевая архитектура, специально разработанная для анализа временных рядов и долгосрочных зависимостей.</li>
                        </ul>
                    </div>
                </div>
                <div class="glass-card fade-up delay-3" style="margin-top: 20px; border-color: var(--accent-cyan); background: rgba(6, 182, 212, 0.05);">
                    <p style="margin:0;"><strong>Научный подход:</strong> Цель состояла не в слепом внедрении нейросетей, а в честном сравнении. На коротких горизонтах сильный baseline (Moving Average) часто показывает лучшие метрики, тогда как потенциал LSTM раскрывается при увеличении объема данных и горизонта прогнозирования.</p>
                </div>
            </div>
        </section>

        <!-- 10. LSTM architecture -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Архитектура LSTM-модели</h2>
                <div class="grid-2 fade-up delay-1" style="align-items: center;">
                    <div class="lstm-diagram">
                        <div class="lstm-block"><strong>Input Sequence</strong><br><small>(Временное окно: t-N ... t)</small></div>
                        <i class="fa-solid fa-arrow-down flow-arrow"></i>
                        <div class="lstm-block" style="background: rgba(59, 130, 246, 0.2);"><strong>LSTM Layers</strong><br><small>(Извлечение временных паттернов)</small></div>
                        <i class="fa-solid fa-arrow-down flow-arrow"></i>
                        <div class="lstm-block" style="background: rgba(245, 158, 11, 0.2);"><strong>Hidden State</strong><br><small>(Контекстный вектор)</small></div>
                        <i class="fa-solid fa-arrow-down flow-arrow"></i>
                        <div class="lstm-block" style="background: rgba(16, 185, 129, 0.2);"><strong>Dense (Linear) Layer</strong><br><small>(Регрессионное преобразование)</small></div>
                        <i class="fa-solid fa-arrow-down flow-arrow"></i>
                        <div class="lstm-block" style="border-color: var(--accent-cyan);"><strong>Forecast Output</strong><br><small>(Прогноз на t+1)</small></div>
                    </div>
                    <div>
                        <div class="glass-card">
                            <h3>Обоснование выбора</h3>
                            <ul class="custom-list">
                                <li>LSTM сохраняет внутреннее состояние для учета <strong>временных зависимостей</strong>.</li>
                                <li>Модель способна обучаться на <strong>последовательностях</strong> (time-windows).</li>
                                <li><strong>Ограничение:</strong> требует значительного объема очищенных данных для предотвращения переобучения.</li>
                                <li>Чувствительна к <strong>гиперпараметрам</strong> (размер окна, количество слоев, learning rate).</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- 11. Метрики оценки -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Метрики оценки качества моделей</h2>
                <p class="fade-up delay-1">Для оценки точности регрессионных прогнозов использовались строгие математические метрики (использование обычной Accuracy для непрерывных величин некорректно).</p>
                
                <div class="grid-3 fade-up delay-2" style="margin-top: 30px;">
                    <div class="glass-card" style="text-align: center;">
                        <h1 style="margin-bottom: 10px; font-size: 3rem;">MAE</h1>
                        <h3>Mean Absolute Error</h3>
                        <p style="font-size: 1rem;">Показывает среднюю абсолютную ошибку прогноза. Интерпретируется линейно.</p>
                    </div>
                    <div class="glass-card" style="text-align: center;">
                        <h1 style="margin-bottom: 10px; font-size: 3rem;">RMSE</h1>
                        <h3>Root Mean Squared Error</h3>
                        <p style="font-size: 1rem;">Сильнее штрафует крупные отклонения и аномальные ошибки прогноза.</p>
                    </div>
                    <div class="glass-card" style="text-align: center;">
                        <h1 style="margin-bottom: 10px; font-size: 3rem;">Horizon</h1>
                        <h3>Горизонты оценки</h3>
                        <p style="font-size: 1rem;">Сравнение проводится по двум ключевым горизонтам планирования: <strong>30 и 60 минут</strong>.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- 12. Результаты экспериментов -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Результаты экспериментов</h2>
                <div class="fade-up delay-1">
                    <table class="academic-table" style="margin-bottom: 20px;">
                        <thead>
                            <tr>
                                <th>Модель (Model)</th>
                                <th>Горизонт (Horizon)</th>
                                <th>MAE</th>
                                <th>RMSE</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>Moving Average</td><td>30 min</td><td class="highlight-cell">1.54</td><td class="highlight-cell">2.95</td></tr>
                            <tr><td>Naive</td><td>30 min</td><td>1.74</td><td>3.82</td></tr>
                            <tr><td>LSTM</td><td>30 min</td><td>3.16</td><td>3.90</td></tr>
                            <tr><td>Trend LR</td><td>30 min</td><td>4.90</td><td>8.72</td></tr>
                            <tr style="border-top: 2px solid var(--card-border);"><td>Moving Average</td><td>60 min</td><td class="highlight-cell">1.65</td><td class="highlight-cell">3.27</td></tr>
                            <tr><td>Naive</td><td>60 min</td><td>1.80</td><td>4.04</td></tr>
                            <tr><td>LSTM</td><td>60 min</td><td>5.59</td><td>5.99</td></tr>
                            <tr><td>Trend LR</td><td>60 min</td><td>8.00+</td><td>8.72</td></tr>
                        </tbody>
                    </table>
                </div>
                <div class="glass-card fade-up delay-2">
                    <h3>Научные выводы по метрикам</h3>
                    <ul class="custom-list">
                        <li><strong>Moving Average</strong> показывает лучший результат на коротких горизонтах, являясь надежным baseline.</li>
                        <li><strong>LSTM</strong> пока уступает baseline, что типично при ограниченном датасете и требует fine-tuning гиперпараметров.</li>
                        <li>Научная ценность проекта — в создании <strong>полного цикла</strong> (сбор → хранение → ML-прогноз → визуализация), готового к внедрению более сложных моделей.</li>
                    </ul>
                </div>
            </div>
        </section>

        <!-- 13. Dashboard / интерфейс -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Dashboard: Интерфейс аналитика</h2>
                <div class="grid-2 fade-up delay-1" style="align-items: center;">
                    <div class="dashboard-mockup">
                        <div class="mockup-header">
                            <div class="mockup-dot"></div><div class="mockup-dot"></div><div class="mockup-dot"></div>
                        </div>
                        <div style="padding: 20px; display: grid; grid-template-columns: 2fr 1fr; gap: 15px; height: 350px;">
                            <div style="background: #1e293b; border-radius: 8px; border: 1px solid #334155; position: relative;">
                                <!-- Map Mockup -->
                                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 4px; font-size: 0.8rem;">City Map / Segments</div>
                                <div style="position: absolute; top: 40%; left: 30%; width: 12px; height: 12px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 10px #ef4444;"></div>
                                <div style="position: absolute; top: 60%; left: 50%; width: 12px; height: 12px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 10px #22c55e;"></div>
                                <div style="position: absolute; top: 30%; left: 70%; width: 12px; height: 12px; background: #eab308; border-radius: 50%; box-shadow: 0 0 10px #eab308;"></div>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 15px;">
                                <div style="background: rgba(59, 130, 246, 0.2); border: 1px solid var(--accent-blue); padding: 15px; border-radius: 8px; flex: 1;">
                                    <div style="font-size: 0.8rem; color: var(--text-muted);">Current Load</div>
                                    <div style="font-size: 1.8rem; font-weight: bold; color: #f8fafc;">78%</div>
                                </div>
                                <div style="background: rgba(139, 92, 246, 0.2); border: 1px solid var(--accent-purple); padding: 15px; border-radius: 8px; flex: 1;">
                                    <div style="font-size: 0.8rem; color: var(--text-muted);">Forecast +30m</div>
                                    <div style="font-size: 1.8rem; font-weight: bold; color: #ef4444;">85%</div>
                                </div>
                                <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; padding: 15px; border-radius: 8px; flex: 1;">
                                    <div style="font-size: 0.8rem; color: #fca5a5;"><i class="fa-solid fa-triangle-exclamation"></i> Alerts</div>
                                    <div style="font-size: 0.9rem;">Congestion ahead</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div>
                        <div class="glass-card">
                            <h3>Функционал Dashboard</h3>
                            <ul class="custom-list">
                                <li>Интерактивная карта (Road segments).</li>
                                <li>Текущая загруженность (Real-time).</li>
                                <li>Прогноз на 30/60 минут (ML Inference).</li>
                                <li>Графики изменения трафика.</li>
                                <li>Карточки аналитических метрик.</li>
                                <li>Система автоматических предупреждений (Alerts).</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- 14. SWOT-анализ -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">SWOT-анализ архитектуры</h2>
                <div class="grid-2 fade-up delay-1" style="gap: 20px;">
                    <div class="glass-card" style="border-top: 4px solid #22c55e;">
                        <h3 style="color: #22c55e;">S: Strengths (Сильные стороны)</h3>
                        <ul class="custom-list">
                            <li>Полный end-to-end data pipeline.</li>
                            <li>Интеграция Machine Learning модулей.</li>
                            <li>Современный web-dashboard интерфейс.</li>
                            <li>Расширяемая микросервисная архитектура.</li>
                        </ul>
                    </div>
                    <div class="glass-card" style="border-top: 4px solid #ef4444;">
                        <h3 style="color: #ef4444;">W: Weaknesses (Слабые стороны)</h3>
                        <ul class="custom-list">
                            <li>LSTM требует сложной дополнительной настройки.</li>
                            <li>Ограниченный исторический период данных.</li>
                            <li>Высокая зависимость от качества входных API-данных.</li>
                        </ul>
                    </div>
                    <div class="glass-card" style="border-top: 4px solid #3b82f6;">
                        <h3 style="color: #3b82f6;">O: Opportunities (Возможности)</h3>
                        <ul class="custom-list">
                            <li>Интеграция с городскими системами City IoT.</li>
                            <li>Real-time traffic control (светофоры).</li>
                            <li>Добавление признаков (погода, ДТП, мероприятия).</li>
                            <li>Ensemble models (LSTM + Moving Average).</li>
                        </ul>
                    </div>
                    <div class="glass-card" style="border-top: 4px solid #f59e0b;">
                        <h3 style="color: #f59e0b;">T: Threats (Угрозы)</h3>
                        <ul class="custom-list">
                            <li>Шумные или пропущенные данные с датчиков.</li>
                            <li>Сложности масштабирования нагрузки БД.</li>
                            <li>Непредсказуемое изменение транспортных паттернов.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- 15. Практическая значимость -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Практическая значимость</h2>
                <div class="grid-2 fade-up delay-1">
                    <div class="glass-card">
                        <i class="fa-solid fa-users-gear fa-3x mb-3 text-gradient" style="margin-bottom: 15px;"></i>
                        <h3>Для городских служб</h3>
                        <p>Инструмент предоставляет аналитикам удобную среду для мониторинга. Раннее выявление перегрузок позволяет проактивно регулировать трафик.</p>
                    </div>
                    <div class="glass-card">
                        <i class="fa-solid fa-lightbulb fa-3x mb-3 text-gradient" style="margin-bottom: 15px;"></i>
                        <h3>Основа для ITS</h3>
                        <p>Разработанная архитектура служит надежной платформой (backend + ML) для построения Интеллектуальной Транспортной Системы (ITS) мегаполиса.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- 16. Ограничения проекта -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Ограничения исследования</h2>
                <div class="glass-card fade-up delay-1" style="border-left: 5px solid #f59e0b;">
                    <h3>Академическая честность</h3>
                    <ul class="custom-list">
                        <li><strong>Эффективность моделей:</strong> Не все модели одинаково эффективны на имеющемся наборе данных. Baseline часто побеждает сложную нейросеть.</li>
                        <li><strong>Обобщающая способность:</strong> Короткий горизонт собранных исторических данных ограничивает способность LSTM-модели находить долгосрочные сезонные паттерны.</li>
                        <li><strong>Потребность в Tuning:</strong> LSTM архитектура требует дальнейшего fine-tuning и более глубокого Feature Engineering.</li>
                        <li><strong>Метрики:</strong> Использование Accuracy для задач регрессии (прогноз скорости) концептуально ограничено, приоритет отдан строгим MAE/RMSE.</li>
                    </ul>
                </div>
            </div>
        </section>

        <!-- 17. Roadmap -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Roadmap развития системы</h2>
                <div class="glass-card fade-up delay-1">
                    <div style="display: flex; flex-direction: column; gap: 20px;">
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <div class="badge" style="width: 80px; text-align: center;">Stage 1</div>
                            <p style="margin: 0;">Улучшение Feature Engineering и глубокий Hyperparameter tuning для LSTM.</p>
                        </div>
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <div class="badge" style="width: 80px; text-align: center;">Stage 2</div>
                            <p style="margin: 0;">Создание ансамблей (Ensemble): комбинация Moving Average + ML Predictors.</p>
                        </div>
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <div class="badge" style="width: 80px; text-align: center;">Stage 3</div>
                            <p style="margin: 0;">Подключение внешних факторов: API погоды, реестр ДТП, городские мероприятия.</p>
                        </div>
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <div class="badge" style="width: 80px; text-align: center; background: rgba(16, 185, 129, 0.2); border-color: #10b981; color: #10b981;">Final</div>
                            <p style="margin: 0;">Полноценный Real-time inference и Cloud Deployment системы.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- 18. Финальный слайд -->
        <section>
            <div class="content-wrapper">
                <h2 class="fade-up">Заключительные выводы</h2>
                <div class="grid-2 fade-up delay-1" style="align-items: center;">
                    <div class="glass-card" style="border-color: var(--accent-cyan); background: rgba(6, 182, 212, 0.05);">
                        <ul class="custom-list">
                            <li>Разработана полноценная архитектура AI-приложения.</li>
                            <li>Реализован и интегрирован ML-модуль прогнозирования.</li>
                            <li>Проведено строгое математическое сравнение моделей.</li>
                            <li>Подтверждена высокая важность baseline-моделей на практике.</li>
                            <li><strong>Итог:</strong> Система готова к интеграции с реальным городским IoT и дальнейшему масштабированию.</li>
                        </ul>
                    </div>
                    <div style="text-align: center;">
                        <h1 class="text-gradient">Спасибо <br>за внимание!</h1>
                        <p style="font-size: 1.5rem; color: var(--text-main);">Готов ответить на ваши вопросы.</p>
                        <div style="margin-top: 30px;">
                            <span class="badge">Сулейменов АЛИШЕР</span><br>
                            <span style="font-size: 0.9rem; color: var(--text-muted);">ЕҰУ, Дипломдық қорғау, 2026</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <script>
        // Slides Logic
        const slidesContainer = document.getElementById('slides-container');
        const slides = document.querySelectorAll('section');
        const navDotsContainer = document.getElementById('nav-dots');
        const counter = document.getElementById('slide-counter');
        
        let currentSlide = 0;
        let isAnimating = false;

        // Initialize Nav Dots
        slides.forEach((_, idx) => {
            const dot = document.createElement('div');
            dot.classList.add('nav-dot');
            if (idx === 0) dot.classList.add('active');
            dot.addEventListener('click', () => goToSlide(idx));
            navDotsContainer.appendChild(dot);
        });

        const dots = document.querySelectorAll('.nav-dot');

        function updateUI() {
            // Update container transform
            slidesContainer.style.transform = `translateY(-${currentSlide * 100}vh)`;
            
            // Update dots
            dots.forEach((dot, idx) => {
                dot.classList.toggle('active', idx === currentSlide);
            });
            
            // Update counter
            counter.innerText = `${currentSlide + 1} / ${slides.length}`;

            // Trigger animations
            const currentSection = slides[currentSlide];
            const animatedElements = currentSection.querySelectorAll('.fade-up');
            animatedElements.forEach(el => {
                // Reset and re-trigger
                el.classList.remove('visible');
                setTimeout(() => el.classList.add('visible'), 50);
            });
        }

        function goToSlide(index) {
            if (isAnimating || index < 0 || index >= slides.length) return;
            isAnimating = true;
            currentSlide = index;
            updateUI();
            setTimeout(() => isAnimating = false, 600); // Matches CSS transition duration
        }

        // Keyboard Navigation
        document.addEventListener('keydown', (e) => {
            if (['ArrowDown', 'ArrowRight', 'PageDown', ' '].includes(e.key)) {
                e.preventDefault();
                goToSlide(currentSlide + 1);
            }
            if (['ArrowUp', 'ArrowLeft', 'PageUp'].includes(e.key)) {
                e.preventDefault();
                goToSlide(currentSlide - 1);
            }
            if (e.key === 'Home') goToSlide(0);
            if (e.key === 'End') goToSlide(slides.length - 1);
        });

        // Mouse Wheel Navigation (Debounced)
        document.addEventListener('wheel', (e) => {
            if (isAnimating) return;
            if (e.deltaY > 50) goToSlide(currentSlide + 1);
            else if (e.deltaY < -50) goToSlide(currentSlide - 1);
        }, { passive: true });

        // Initial setup
        setTimeout(() => updateUI(), 100);
    </script>
</body>
</html>
"""

def generate():
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write("# AI Traffic - Academic Presentation\\n\\nOpen `index.html` in any modern browser to view the presentation.\\nNo build tools required. Built with Vanilla HTML/CSS/JS.")
        
    print("Presentation created successfully in index.html")

if __name__ == '__main__':
    generate()
