from simulate import simulate
import json

with open("roles.json", "r", encoding="utf-8") as f:
    roles = json.load(f)

simulate(
    roles,
    case_name="case5_astar_interface",
    agents=[
        ("輪椅", 0, 0),
        ("一般人", 1, 0),
        ("學生", 0, 2),
    ],
    grid=[
        [0,0,3,0],
        [0,1,0,0],
        [0,0,0,0]
    ],
    steps=120
)
