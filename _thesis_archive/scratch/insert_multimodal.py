import codecs

with codecs.open('../presentation.html', 'r', 'utf-8') as f:
    content = f.read()

marker = '<!-- 11.5 Цифрлық егіз (Digital Twin) -->'

# Find the start of 11.5
start_idx = content.find(marker)
if start_idx == -1:
    print("Could not find marker 11.5")
    exit(1)

# Find the next </section> after marker
end_idx = content.find('</section>', start_idx)
if end_idx == -1:
    print("Could not find </section> after marker")
    exit(1)

insert_idx = end_idx + len('</section>')

new_slide = """

            <!-- 12. AI-Экожүйе: Multimodal & Smart Parking -->
            <section>
                <div class="slide-card">
                    <h2 style="font-size: 2.8em;">12. AI-Экожүйе: Multimodal & Smart Parking</h2>
                    <p style="font-size: 1.1em; color: var(--secondary-text); margin-bottom: 30px;">
                        Қосымша тек навигатор емес, толыққанды <strong>Smart City экожүйесі</strong>. ИИ болжамдары маршруттарды біріктіріп, қалалық паркингтерді басқаруға көмектеседі.
                    </p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px;">
                        <!-- Multimodal Routing -->
                        <div class="info-box" style="border-top: 5px solid #10b981; padding: 25px;">
                            <h4 style="font-size: 1.3em; margin-bottom: 15px;"><i class="fa-solid fa-person-biking" style="color: #10b981;"></i> Мультимодальді Маршруттар</h4>
                            <div style="font-size: 0.85em; background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #10b981;">
                                <strong>Сценарий:</strong> «Егер алда 60 минуттық кептеліс болжамдалса, жүйе көлікті тұраққа қойып, соңғы 2 шақырымды <strong>электросамокатпен</strong> жүруді ұсынады (20 минут үнемдеу)».
                            </div>
                            <ul style="font-size: 0.8em; padding-left: 20px;">
                                <li style="margin-bottom: 10px;">Экологияны жақсартуға үлес (CO2 азайту).</li>
                                <li style="margin-bottom: 10px;">Психологиялық "Антистресс" режимі.</li>
                                <li style="color: var(--accent-blue);"><i class="fa-solid fa-link"></i> Endpoint: <code>/traffic/multimodal_analysis</code></li>
                            </ul>
                        </div>
                        
                        <!-- Smart Parking -->
                        <div class="info-box" style="border-top: 5px solid #3b82f6; padding: 25px;">
                            <h4 style="font-size: 1.3em; margin-bottom: 15px;"><i class="fa-solid fa-square-parking" style="color: #3b82f6;"></i> Smart Parking</h4>
                            <div style="font-size: 0.85em; background: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #3b82f6;">
                                <strong>Динамикалық статус:</strong> Паркингтегі бос орындар саны қазіргі емес, <strong>сіз жеткен кездегі (мысалы 30 мин кейін)</strong> трафик жүктемесіне байланысты AI арқылы болжанады.
                            </div>
                            <ul style="font-size: 0.8em; padding-left: 20px;">
                                <li style="margin-bottom: 10px;">Astana Park орындарын интеллектуалды бөлу.</li>
                                <li style="margin-bottom: 10px;">Орын іздеу уақытын 40%-ға қысқарту.</li>
                                <li style="color: var(--accent-purple);"><i class="fa-solid fa-link"></i> Endpoint: <code>/parking?horizon=30</code></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>"""

new_file = content[:insert_idx] + new_slide + content[insert_idx:]

with codecs.open('../presentation.html', 'w', 'utf-8') as f:
    f.write(new_file)
print("Successfully inserted Multimodal slide.")
