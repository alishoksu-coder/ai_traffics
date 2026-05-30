import json

with open("doc_text.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

queries = [
    "Zhasanda", "algorithmderge", "baskars", "automatics in thailand",
    "derekterge", "bagdarsham", "краудсорсинг", "Бейімделгіш",
    "ішек шаншуы", "Google Maps", "Waze", "2-кесте", "Қосынды",
    "LSTM", "README", "репозиторийде", "компоненттеріміз", "Ғылыми жаңалығы",
    "ЖИ", "AI", "колик", "жуйесi", "корингендей", "бiздiн", "усынылатын"
]

results = []
for i, line in enumerate(lines):
    for q in queries:
        if q.lower() in line.lower():
            results.append(f"Match [{q}] at line {i+1}: {line.strip()}")

with open("search_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
