import json

import data

with open("json/goals.json", 'w', encoding='utf-8') as f:
    json.dump(data.goals, f)

with open("json/teachers.json", 'w', encoding='utf-8') as f:
    json.dump(data.teachers, f)
