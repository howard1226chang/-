from pathfinding import astar_search

def print_grid(grid, path=None, start=None, goal=None):
    path_set = set(path) if path else set()
    for y in range(len(grid)):
        row = []
        for x in range(len(grid[0])):
            if start == (x, y):
                row.append("S")
            elif goal == (x, y):
                row.append("G")
            elif (x, y) in path_set:
                row.append("*")
            elif grid[y][x] == 1:
                row.append("#")   # blocked
            else:
                row.append(".")
        print(" ".join(row))
    print()

grid = [
    [0,0,0,0,0,0],
    [0,1,1,1,1,0],
    [0,0,0,0,0,0],
]

# occupancy：中間那條路很擠（故意讓 A* 想繞開）
occ = [
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
    [0,5,5,5,5,0],   # 第 3 列（y=2）中間很擠
]

start = (0, 2)
goal  = (5, 2)

# 1) 不使用擁擠代價（純距離）
req_no = {
    "grid": grid,
    "grid_occupancy": occ,
    "start": start,
    "goal": goal,
    "use_crowd_cost": False
}
path_no = astar_search(req_no)

# 2) 使用擁擠代價（距離 + 擁擠）
req_yes = dict(req_no)
req_yes["use_crowd_cost"] = True
path_yes = astar_search(req_yes)

print("=== 不使用擁擠代價（純距離） ===")
print("path:", path_no)
print_grid(grid, path_no, start, goal)

print("=== 使用擁擠代價（距離+擁擠） ===")
print("path:", path_yes)
print_grid(grid, path_yes, start, goal)