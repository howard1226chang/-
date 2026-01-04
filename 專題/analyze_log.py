import json
import csv
import os
from collections import defaultdict

def load_log(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def analyze_events(events, exit_pos=None):
    """
    統計：
    - wait_count: action == "Wait"
    - move_count: action == "Step" or action == "Moved" (兼容不同寫法)
    - blocked_count: action == "Blocked"
    - arrived: action == "Arrived" 或最後位置==exit_pos（可選）
    """
    stats = defaultdict(lambda: {
        "wait_count": 0,
        "move_count": 0,
        "blocked_count": 0,
        "arrived": 0,
        "final_x": None,
        "final_y": None,
        "final_state": None,
    })

    for e in events:
        name = e.get("name", "UNKNOWN")
        action = e.get("action", "")
        state = e.get("state", "")

        # 記錄最後狀態/位置
        stats[name]["final_x"] = e.get("x")
        stats[name]["final_y"] = e.get("y")
        stats[name]["final_state"] = state

        if action == "Wait":
            stats[name]["wait_count"] += 1
        elif action in ("Step", "Moved"):
            stats[name]["move_count"] += 1
        elif action == "Blocked":
            stats[name]["blocked_count"] += 1
        elif action == "Arrived":
            stats[name]["arrived"] = 1

    # 如果沒有 Arrived action，也可用最後位置判斷是否到出口（可選）
    if exit_pos is not None:
        ex, ey = exit_pos
        for name in stats:
            if stats[name]["final_x"] == ex and stats[name]["final_y"] == ey:
                stats[name]["arrived"] = 1

    return stats

def write_csv(output_csv, case_name, stats_dict):
    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    header = ["case", "name", "wait_count", "move_count", "blocked_count", "arrived",
              "final_x", "final_y", "final_state"]
    file_exists = os.path.exists(output_csv)

    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(header)
        for name, s in stats_dict.items():
            w.writerow([
                case_name, name,
                s["wait_count"], s["move_count"], s["blocked_count"], s["arrived"],
                s["final_x"], s["final_y"], s["final_state"]
            ])

def print_table(case_name, stats_dict):
    print(f"\n== {case_name} ==")
    print(f"{'角色':<6} | {'Move':>4} | {'Wait':>4} | {'Blocked':>7} | {'Arrived':>7} | {'Final':>10}")
    print("-" * 60)
    for name in sorted(stats_dict.keys()):
        s = stats_dict[name]
        final_pos = f"({s['final_x']},{s['final_y']})"
        print(f"{name:<6} | {s['move_count']:>4} | {s['wait_count']:>4} | {s['blocked_count']:>7} | {s['arrived']:>7} | {final_pos:>10}")

def main():
    # 你可以在這裡換成你想分析的 log
    log_files = [
        "logs/simulation_log_case1_single.json",
        "logs/simulation_log_case2_crowded.json",
        "logs/simulation_log_case3_wheelchair.json",
    ]

    output_csv = "logs/summary_stats.csv"

    for path in log_files:
        if not os.path.exists(path):
            print(f"找不到：{path}（略過）")
            continue

        case_name = os.path.splitext(os.path.basename(path))[0].replace("simulation_log_", "")
        events = load_log(path)
        stats = analyze_events(events, exit_pos=None)  # 若你有固定出口座標，可填 exit_pos=(x,y)

        print_table(case_name, stats)
        write_csv(output_csv, case_name, stats)

    print(f"\n✅ 統計完成，CSV 輸出：{output_csv}")

if __name__ == "__main__":
    main()
