PASSABLE, BLOCKED, DANGER, STAIRS = 0, 1, 2, 3

GRID_W = 5
GRID_H = 5

grid = [
    [0, 0, 0, 1, 0],
    [0, 3, 0, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 2, 1, 0, 0],
    [0, 0, 0, 0, 0]
]

# occupancy: 2D array same size as grid, counts people in each cell
occupancy = [[0 for _ in range(GRID_W)] for __ in range(GRID_H)]

def in_bounds(x, y):
    return 0 <= x < GRID_W and 0 <= y < GRID_H

def cell_type(x, y):
    if not in_bounds(x, y):
        return None
    return grid[y][x]

def is_walkable(x, y, role_dict):
    """根據角色屬性判斷指定格子是否可通行（不考慮是否被其他人佔據）"""
    if not in_bounds(x, y):
        return False
    c = grid[y][x]
    if c == BLOCKED:
        return False
    # 若格子為 stairs，檢查角色能否走樓梯
    if c == STAIRS and not role_dict.get("can_use_stairs", True):
        return False
    # 若角色有 avoid_terrain 設定（list），若 cell match 則不可行
    avoid = role_dict.get("avoid_terrain", [])
    if c == STAIRS and "stairs" in avoid:
        return False
    return True

def print_map():
    symbols = {PASSABLE: "⬜", BLOCKED: "⬛", DANGER: "⚠️ ", STAIRS: "↗️ "}
    for y in range(GRID_H):
        row = ""
        for x in range(GRID_W):
            row += symbols[grid[y][x]] + " "
        print(row)

def add_occupant(x, y):
    if in_bounds(x, y):
        occupancy[y][x] += 1

def remove_occupant(x, y):
    if in_bounds(x, y) and occupancy[y][x] > 0:
        occupancy[y][x] -= 1

def occupancy_count(x, y):
    if in_bounds(x, y):
        return occupancy[y][x]
    return 0

class MapSystem:
    def __init__(self, grid):
        self.grid = grid
        self.h = len(grid)
        self.w = len(grid[0]) if self.h > 0 else 0
        self.occupancy = [[0 for _ in range(self.w)] for __ in range(self.h)]

    def is_walkable(self, x, y, role_dict):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return False
        c = self.grid[y][x]
        if c == BLOCKED:
            return False
        if c == STAIRS and not role_dict.get("can_use_stairs", True):
            return False
        avoid = role_dict.get("avoid_terrain", [])
        if c == STAIRS and "stairs" in avoid:
            return False
        return True

    def occupy(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.occupancy[y][x] += 1

    def leave(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h and self.occupancy[y][x] > 0:
            self.occupancy[y][x] -= 1

    def is_crowded(self, x, y, threshold=0):
        return self.occupancy[y][x] > threshold
