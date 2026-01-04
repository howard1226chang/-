import json
import random
import time
from fsm import FSM
from map_system import is_walkable, print_map
from map_system import PASSABLE, BLOCKED, DANGER, STAIRS

# 載入角色資料
with open("roles.json", "r", encoding="utf-8") as f:
    roles = json.load(f)

def simulate(role_name):
    role = roles[role_name]
    fsm = FSM(role_name)

    x, y = 0, 0
    print_map()
    print(f"\n[{role_name}] 起點：({x},{y})\n")

    fsm.update("alarm")  # 觸發避難開始

    for step in range(10):
        if fsm.state == "Arrived":
            break

        dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        nx, ny = x + dx, y + dy

        if is_walkable(nx, ny, role):
            x, y = nx, ny
            print(f"→ 移動到 ({x},{y})")
        else:
            print(f"× 遇到障礙 ({nx},{ny})")
            fsm.update("obstacle")
            continue

        # 假設 (4,4) 是出口
        if (x, y) == (4, 4):
            fsm.update("arrived")
        else:
            fsm.update("clear")

        time.sleep(0.3)

# 測試不同角色
simulate("一般人")
print("\n---------------------------\n")
simulate("輪椅")
