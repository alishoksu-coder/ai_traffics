import os, re
import json

d = r'c:\Users\user\Downloads\ai_traffic_fullstack\mobile\traffic_app\lib'
s = set()
for r, _, fs in os.walk(d):
    for f in fs:
        if f.endswith('.dart'):
            with open(os.path.join(r, f), 'r', encoding='utf-8') as file:
                text = file.read()
                matches = re.findall(r"'([^']*?[А-Яа-яЁё][^']*?)'", text)
                matches += re.findall(r'"([^"]*?[А-Яа-яЁё][^"]*?)"', text)
                for m in matches:
                    s.add(m)

with open('strings.json', 'w', encoding='utf-8') as f:
    json.dump(sorted(list(s)), f, ensure_ascii=False, indent=2)
