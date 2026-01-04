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

events = [
    {"t": 0,  "type": "alarm", "data": {}},
    {"t": 30, "type": "block", "data": {"cell": (2, 1)}},
    {"t": 80, "type": "clear", "data": {"cell": (2, 1)}},
]

simulate(
    roles,
    case_name="case7_event_driven_demo",
    agents=[("一般人", 0, 1), ("學生", 0, 2), ("輪椅", 0, 3)],
    grid=grid,
    steps=250,
    exit_pos=(4, 2),
    events=events,
    stuck_replan=10
)