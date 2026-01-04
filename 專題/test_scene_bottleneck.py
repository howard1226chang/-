from simulate import simulate
import json

with open("roles.json", "r", encoding="utf-8") as f:
    roles = json.load(f)

# 右側只有一個出口通道（中間那格）
grid = [
    [0,0,0,0,1,1],
    [0,0,0,0,0,0],  # ← 這行中間是唯一能通向右側的通道
    [0,0,0,0,1,1],
    [0,0,0,0,1,1],
    [0,0,0,0,1,1],
]

simulate(
    roles,
    case_name="scene_bottleneck",
    agents=[
        ("一般人", 0, 0),
        ("學生", 0, 1),
        ("輪椅", 0, 2),
    ],
    grid=grid,
    steps=250
)
