# pathfinding.py
import heapq

def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct(came_from, start, goal):
    cur = goal
    path = []
    while cur != start:
        path.append(cur)
        cur = came_from.get(cur)
        if cur is None:
            return None
    path.reverse()
    return path

def astar_search(request):
    grid = request["grid"]
    occ = request["grid_occupancy"]
    start = request["start"]
    goal = request["goal"]

    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {}
    g = {start: 0}

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == goal:
            return reconstruct(came_from, start, goal)

        x, y = current
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)

            # bounds
            if not (0 <= nx < len(grid[0]) and 0 <= ny < len(grid)):
                continue

            cell = grid[ny][nx]
            if cell == 1:  # BLOCKED
                continue

            # stairs 限制（3 代表 STAIRS）
            if cell == 3:
                if not request.get("can_use_stairs", True):
                    continue
                if "stairs" in request.get("avoid", []):
                    continue

            # 擁擠度成本：人越多越貴（至少 1）
            use_crowd = request.get("use_crowd_cost", True)
            step_cost = 1 + occ[ny][nx] if use_crowd else 1

            new_g = g[current] + step_cost

            if neighbor not in g or new_g < g[neighbor]:
                g[neighbor] = new_g
                priority = new_g + heuristic(neighbor, goal)
                heapq.heappush(open_list, (priority, neighbor))
                came_from[neighbor] = current

    return None