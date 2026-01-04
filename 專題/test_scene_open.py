from simulate import simulate
import json

with open("roles.json", "r", encoding="utf-8") as f:
    roles = json.load(f)

grid = [
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
]

simulate(
    roles,
    case_name="scene_open",
    agents=[
        ("一般人", 0, 0),
        ("學生", 0, 1),
        ("輪椅", 0, 2),
    ],
    grid=grid,
    steps=200
)
