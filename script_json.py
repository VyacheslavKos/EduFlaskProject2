import json

import data

with open("goals.json", 'w', encoding='utf-8') as f:
    json.dump(data.goals, f)

with open("teachers.json", 'w', encoding='utf-8') as f:
    json.dump(data.teachers, f)
