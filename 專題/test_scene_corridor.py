from simulate import simulate
import json

with open("roles.json", "r", encoding="utf-8") as f:
    roles = json.load(f)

# 1 = BLOCKED，做出一條只有中間能走的走廊
grid = [
    [0,1,1,1,1,1],
    [0,0,0,0,0,0],
    [0,1,1,1,1,1],
    [0,1,1,1,1,1],
    [0,1,1,1,1,1],
]

simulate(
    roles,
    case_name="scene_corridor",
    agents=[
        ("一般人", 0, 0),
        ("學生", 0, 1),
        ("輪椅", 0, 2),
    ],
    grid=grid,
    steps=200
)
