from simulate import simulate
import json

with open("roles.json", "r", encoding="utf-8") as f:
    roles = json.load(f)

grid = [
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,1,1,1,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
]

simulate(
    roles,
    case_name="case6_replan_block",
    agents=[("一般人", 0, 1), ("輪椅", 0, 3)],
    grid=grid,
    steps=200,
    block_step=30,
    block_cell=(2, 1),   # 你也可以換別格
    stuck_replan=10
)