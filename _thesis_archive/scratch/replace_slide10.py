import re

with open('../presentation.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_slide = """            <!-- 10. ML Модельдерін Бағалау -->
            <section>
                <div class="slide-card">
                    <h2 style="font-size: 2.8em;">10. ML Модельдерін Бағалау (Model Evaluation)</h2>
                    <p style="font-size: 1.1em; color: var(--secondary-text); margin-bottom: 30px;">
                        Жүйенің негізгі болжау ядросы ретінде әртүрлі машиналық оқыту алгоритмдері сыналды. Нәтижесінде ең жоғары дәлдік көрсеткен <strong>LSTM (Long Short-Term Memory)</strong> нейрондық желісі таңдалды.
                    </p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px;">
                        <div>
                            <table class="modern-table" style="width: 100%; font-size: 0.9em; margin-bottom: 20px;">
                                <tr>
                                    <th style="color: var(--accent-blue); padding: 15px;">Модель</th>
                                    <th style="padding: 15px;">MAE</th>
                                    <th style="padding: 15px;">RMSE</th>
                                    <th style="color: var(--accent-purple); padding: 15px;">Accuracy</th>
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
                                <tr style="background: rgba(124, 58, 237, 0.1); font-weight: bold; border-left: 4px solid var(--accent-purple);">
                                    <td style="color: var(--accent-purple);">LSTM (Таңдалған)</td>
                                    <td style="color: var(--accent-purple);">0.08</td>
                                    <td style="color: var(--accent-purple);">0.12</td>
                                    <td style="color: var(--accent-purple); font-size: 1.1em;">87.4%</td>
                                </tr>
                            </table>
                            <div class="info-box" style="padding: 20px; border-left: 5px solid var(--accent-blue);">
                                <h4 style="font-size: 1em; margin-bottom: 10px;"><i class="fa-solid fa-trophy" style="color: #f59e0b;"></i> Неліктен LSTM?</h4>
                                <ul style="font-size: 0.8em; padding-left: 20px; margin: 0;">
                                    <li style="margin-bottom: 8px;"><strong>Уақыттық қатарлар (Time-series):</strong> Өткен оқиғаларды (кептелістерді) есте сақтау қабілеті.</li>
                                    <li style="margin-bottom: 8px;"><strong>Ауа райы факторы:</strong> Ауа райының күрделі әсерлерін (қар, жаңбыр) тиімдірек өңдейді.</li>
                                    <li style="margin-bottom: 0;"><strong>Төмен қателік:</strong> MAE көрсеткіші небәрі 0.08, яғни болжам нақтылығы өте жоғары.</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="display: flex; flex-direction: column; gap: 20px;">
                            <div class="info-box" style="background: #f8fafc; padding: 25px; display: flex; align-items: center; justify-content: space-between;">
                                <div>
                                    <div style="font-size: 0.9em; color: #64748b; margin-bottom: 5px;">Оқыту датасеті</div>
                                    <div style="font-size: 1.5em; font-weight: bold; color: #0f172a;">20,000+</div>
                                    <div style="font-size: 0.8em; color: var(--accent-blue);">тарихи жазбалар</div>
                                </div>
                                <i class="fa-solid fa-database" style="font-size: 3em; color: #cbd5e1;"></i>
                            </div>
                            <div class="info-box" style="background: #f8fafc; padding: 25px; display: flex; align-items: center; justify-content: space-between;">
                                <div>
                                    <div style="font-size: 0.9em; color: #64748b; margin-bottom: 5px;">PyTorch фреймворкі</div>
                                    <div style="font-size: 1.5em; font-weight: bold; color: #0f172a;">Deep Learning</div>
                                    <div style="font-size: 0.8em; color: var(--accent-purple);">Екі қабатты LSTM архитектурасы</div>
                                </div>
                                <i class="fa-solid fa-layer-group" style="font-size: 3em; color: #cbd5e1;"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </section>"""

start_marker = '<!-- 10. Серверлік деңгей -->'
end_marker = '<!-- 11. Болжау Жүйесінің Архитектурасы (Prediction Pipeline) -->'

pattern = re.compile(re.escape(start_marker) + r'.*?' + re.escape(end_marker), re.DOTALL)
new_content = pattern.sub(new_slide + '\n' + end_marker, content)

if content == new_content:
    print('Error: Could not find the target section to replace.')
else:
    with open('../presentation.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Successfully updated presentation.html')
