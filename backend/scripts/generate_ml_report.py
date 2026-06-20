import os
import pandas as pd

def generate_report():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    reports_dir = os.path.join(backend_dir, "reports")
    csv_path = os.path.join(reports_dir, "metrics_summary.csv")
    
    if not os.path.exists(csv_path):
        print(f"Metrics not found at {csv_path}. Run evaluate_models.py first.")
        return
        
    df = pd.read_csv(csv_path)
    
    report = []
    report.append("# Валидация ML-моделей прогнозирования трафика\n")
    
    report.append("## 1. Введение и Методология\n")
    report.append("В рамках дипломной работы было проведено сравнение архитектуры **LSTM** с простыми baseline-моделями "
                  "(Наивный прогноз, Скользящее среднее, Линейная регрессия, Random Forest). "
                  "Это необходимо для доказательства целесообразности использования нейросетей "
                  "в задаче прогнозирования загруженности перекрестков (0-100).\n")
    
    report.append("### Метрики оценки:")
    report.append("- **MAE (Mean Absolute Error):** Средняя абсолютная ошибка в единицах загруженности (0-100). Показывает типичное отклонение прогноза от факта.")
    report.append("- **RMSE (Root Mean Square Error):** Квадратичная ошибка. Сильнее штрафует за крупные промахи (например, внезапные пробки).")
    report.append("- **MAPE:** Процентная ошибка.\n")
    
    report.append("### Горизонты прогноза:")
    report.append("- **30 минут (h=2):** Краткосрочный прогноз для маршрутизации водителей в пути.")
    report.append("- **60 минут (h=4):** Среднесрочный прогноз для планирования поездок.\n")
    
    report.append("## 2. Результаты экспериментов\n")
    report.append("Оценка проводилась на тестовой выборке (последние 20% хронологических данных локального датасета).\n")
    
    report.append("### Таблица метрик\n")
    markdown_table = df.to_markdown(index=False, floatfmt=".2f")
    report.append(markdown_table + "\n")
    
    report.append("## 3. Анализ и Выводы\n")
    
    # Analyze who won
    df_30 = df[df['Horizon_min'] == 30]
    best_30_mae_model = df_30.loc[df_30['MAE'].idxmin()]['Model']
    
    if best_30_mae_model == "LSTM":
        report.append(f"**Победитель:** LSTM показал наилучшие результаты ({best_30_mae_model}), "
                      f"успешно улавливая нелинейные зависимости и паттерны времени.\n")
    elif best_30_mae_model in ["Random Forest"]:
        report.append(f"**Победитель:** Ансамблевые деревья ({best_30_mae_model}) превзошли LSTM. "
                      f"Это частое явление на табличных данных с явными категориальными "
                      f"временными признаками (час, день недели).\n")
    else:
        report.append(f"**Победитель:** Простая модель ({best_30_mae_model}) оказалась точнее LSTM. "
                      f"В условиях недостатка обучающих данных или сильной зашумленности "
                      f"простые эвристики работают надежнее, так как не склонны к переобучению.\n")
                      
    report.append("### Ограничения текущей реализации LSTM:")
    report.append("1. **Отсутствие пространственного контекста:** Текущая LSTM анализирует каждый перекресток изолированно. Она не знает, что пробка на соседней улице повлияет на неё через 10 минут.")
    report.append("2. **Размер датасета:** Нейросети требуют огромного количества данных для обобщения. На локальной выборке они могут проигрывать Random Forest.")
    report.append("3. **Внешние факторы:** В модели сейчас используется только базовый множитель погоды. Не хватает данных об авариях, дорожных работах и массовых мероприятиях.\n")
    
    report.append("## 4. Перспективы развития (Future Work)\n")
    report.append("Для достижения state-of-the-art результатов в дипломе предлагается следующий шаг развития — "
                  "использование пространственно-временных графовых нейросетей (**STGCN** - Spatial-Temporal Graph Convolutional Networks). "
                  "Они позволят одновременно учитывать исторический тренд (Temporal) и влияние соседних узлов графа дорог (Spatial).")
                  
    report_path = os.path.join(reports_dir, "ML_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"Report generated successfully at {report_path}")

if __name__ == "__main__":
    generate_report()
