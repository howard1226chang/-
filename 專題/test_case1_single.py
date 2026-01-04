from simulate import simulate
import json
import os
BASE = os.path.dirname(__file__)
with open(os.path.join(BASE, "roles.json"), "r", encoding="utf-8") as f:
    roles = json.load(f)

simulate(roles, case_name="case1_single", agents=[
    ("一般人", 0, 0)
], grid=[
    [0,0,0],
    [0,0,0],
    [0,0,0]
])