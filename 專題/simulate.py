import json
import time
import os

from agent import Agent
from map_system import MapSystem
from path_interface import agent_to_path_request, apply_path_to_agent
from pathfinding import astar_search
from fsm import State


def load_roles(filepath="roles.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        roles = json.load(f)

    required_fields = ["speed", "vision", "type", "reaction_time", "tolerance", "move_delay"]
    for name, info in roles.items():
        for field in required_fields:
            if field not in info:
                raise ValueError(f"角色 {name} 缺少欄位：{field}")
    return roles


def simulate(
    roles,
    case_name="default_case",
    agents=None,
    grid=None,
    steps=120,
    exit_pos=None,
    events=None,            # ✅ W18：事件表（全域+環境事件）
    stuck_replan=10,        # ✅ W17：連續 Wait 幾次就 replan
    sleep_s=0.05,
    end_when_all_arrived=True
):
    """
    事件驅動整合版（W18）+ 動態重新規劃（W17）
    - 全域事件：alarm/quake -> 丟給 FSM
    - 環境事件：block/clear -> 改 grid
    - Replan 觸發：
        1) 下一步路徑格變 BLOCKED/不可走
        2) 連續 Wait 太久
        3) try_move 失敗(視為 obstacle)
    """

    # ---------- default grid ----------
    if grid is None:
        grid = [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ]

    map_system = MapSystem(grid)

    # ---------- default exit ----------
    if exit_pos is None:
        exit_pos = (len(grid[0]) - 1, len(grid) - 1)  # 右下角

    # ---------- default agents ----------
    if agents is None:
        agents = [("一般人", 0, 0)]

    # ---------- default events (W18) ----------
    # 你可以在外部傳入 events；不傳就用預設 demo
    if events is None:
        events = [
            {"t": 0,  "type": "alarm", "data": {}},                 # 警報/地震廣播
            {"t": 30, "type": "block", "data": {"cell": (2, 1)}},   # 中途封路（示例）
            # {"t": 80, "type": "clear", "data": {"cell": (2, 1)}}, # 解除封路（可選）
        ]

    # ---------- init agents ----------
    agent_objs = []
    for name, x, y in agents:
        if name not in roles:
            raise KeyError(f"roles.json 找不到角色：{name}")

        a = Agent(name, roles[name], x, y)
        a.stuck_count = 0
        a.path = None
        a.path_index = 0

        agent_objs.append(a)
        map_system.occupy(x, y)

    log = []

    # ==============================
    # main simulation loop
    # ==============================
    for step in range(steps):

        # 取出本 step 的事件
        step_events = [e for e in events if e.get("t") == step]

        # ------------------------------
        # 2-1 全域事件（給 FSM）
        # ------------------------------
        global_event = None
        for e in step_events:
            if e.get("type") in ("alarm", "quake"):
                global_event = "alarm"   # FSM 用 alarm 足夠
                log.append({
                    "time": time.time(),
                    "name": "SYSTEM",
                    "x": None, "y": None,
                    "state": "EVENT",
                    "action": e.get("type")
                })

        # ------------------------------
        # 2-2 環境事件（改地圖）
        # ------------------------------
        for e in step_events:
            etype = e.get("type")
            if etype == "block":
                x, y = e["data"]["cell"]
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    grid[y][x] = 1  # 1 = BLOCKED
                    print(f"🚧 Blocked at step={step}: ({x},{y})")
                    log.append({
                        "time": time.time(),
                        "name": "SYSTEM",
                        "x": x, "y": y,
                        "state": "EVENT",
                        "action": "BlockCell"
                    })
            elif etype == "clear":
                x, y = e["data"]["cell"]
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    grid[y][x] = 0
                    print(f"✅ Cleared at step={step}: ({x},{y})")
                    log.append({
                        "time": time.time(),
                        "name": "SYSTEM",
                        "x": x, "y": y,
                        "state": "EVENT",
                        "action": "ClearCell"
                    })

        # 讓 MapSystem 如果有快取/依 grid 初始化的資訊能同步（你的 MapSystem 若不需要可留著）
        # 如果 MapSystem 沒有這個方法也沒關係：用 hasattr 保護
        if hasattr(map_system, "grid"):
            map_system.grid = grid

        # ------------------------------
        # agent loop
        # ------------------------------
        for a in agent_objs:

            # 已到出口
            if (a.x, a.y) == exit_pos:
                a.fsm.update("arrived", crowd_density=0.0)
                log.append(a.snapshot("Arrived"))
                continue

            # 擁擠度（先用本格 occupancy 當 proxy）
            crowd_density = min(1.0, map_system.occupancy[a.y][a.x] / 3.0)

            # FSM 更新（吃 global_event）
            a.fsm.update(global_event, crowd_density=crowd_density)

            # WAIT/IDLE：不移動
            if a.fsm.state in (State.IDLE, State.WAIT):
                log.append(a.snapshot("Wait"))
                continue

            # AVOID：強制清路徑，下一段會重規劃
            if a.fsm.state == State.AVOID:
                a.path = None
                a.path_index = 0

            # 需要路徑就規劃
            if a.path is None or a.path_index >= len(a.path):
                req = agent_to_path_request(
                    agent=a,
                    grid=grid,
                    grid_occupancy=map_system.occupancy,
                    goal=exit_pos
                )
                path = astar_search(req)
                apply_path_to_agent(a, path if path else None)

            # 決定下一步（路徑 or 隨機）
            if a.path is None or a.path_index >= len(a.path):
                nx, ny = a.choose_random_step()
            else:
                tx, ty = a.path[a.path_index]

                # --- W17：路徑失效偵測 → Replan ---
                # 1) 這格被封了  2) 或角色不可走（stairs/avoid 等）
                if grid[ty][tx] == 1 or (not map_system.is_walkable(tx, ty, a.role)):
                    a.path = None
                    a.path_index = 0
                    a.stuck_count = 0
                    log.append(a.snapshot("Replan"))
                    continue

                nx, ny = tx, ty
                a.path_index += 1

            # 邊界
            if not (0 <= nx < len(grid[0]) and 0 <= ny < len(grid)):
                log.append(a.snapshot("OutOfBounds"))
                continue

            # 目標格有人 → Wait（可觸發 Replan）
            if map_system.occupancy[ny][nx] > 0:
                a.fsm.update(None, crowd_density=1.0)
                a.stuck_count += 1
                log.append(a.snapshot("Wait"))

                # --- W17：連續 Wait 過久 → Replan ---
                if stuck_replan is not None and a.stuck_count >= stuck_replan:
                    a.path = None
                    a.path_index = 0
                    a.stuck_count = 0
                    log.append(a.snapshot("Replan"))
                continue

            # 嘗試移動：失敗 → obstacle → Replan
            ok = a.try_move(nx, ny, map_system)
            if not ok:
                a.fsm.update("obstacle", crowd_density=crowd_density)
                a.path = None
                a.path_index = 0
                a.stuck_count = 0
                log.append(a.snapshot("Blocked"))
            else:
                a.stuck_count = 0
                a.fsm.update("clear", crowd_density=crowd_density)
                log.append(a.snapshot("Step"))

        # 全員抵達就提前結束（demo 很好看）
        if end_when_all_arrived and all((ag.x, ag.y) == exit_pos for ag in agent_objs):
            print("🏁 All agents arrived. End simulation.")
            break

        time.sleep(sleep_s)

    # output log
    os.makedirs("logs", exist_ok=True)
    output_path = f"logs/simulation_log_{case_name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    print(f"✅ 模擬完成，輸出：{output_path}")