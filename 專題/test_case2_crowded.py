from simulate import simulate
import json

with open("roles.json", "r", encoding="utf-8") as f:
    roles = json.load(f)

simulate(roles, case_name="case2_crowded", agents=[
    ("老人", 0, 0),
    ("小孩", 1, 0),
    ("一般人", 2, 0)
], grid=[
    [0,0,0],
    [1,1,0],
    [0,0,0]
])
