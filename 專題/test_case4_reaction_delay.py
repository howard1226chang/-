from simulate import simulate
import json

with open("roles.json", "r", encoding="utf-8") as f:
    roles = json.load(f)

simulate(
    roles,
    case_name="case4_reaction_delay",
    agents=[
        ("老師", 0, 0),
        ("學生", 1, 0),
        ("輪椅", 2, 0),
    ],
    grid=[
        [0,0,0,0],
        [0,1,0,0],
        [0,0,0,0]
    ],
    steps=200   # 拉長時間，確保都會進 Evacuate
)