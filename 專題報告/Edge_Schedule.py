import heapq
import numpy as np

class PathPlanner:
    def __init__(self, grid_map, crowd_weight=0.5):
        """
        初始化路徑規劃器
        
        參數:
        - grid_map: 2D網格地圖，0表示可通行，1表示障礙物
        - crowd_weight: 擁擠度權重係數
        """
        self.grid_map = grid_map
        self.crowd_density = np.zeros_like(grid_map, dtype=float)  # 初始化擁擠度地圖
        self.crowd_weight = crowd_weight
        self.height, self.width = grid_map.shape
        
    def update_crowd_density(self, positions):
        """更新擁擠度地圖"""
        # 重置擁擠度地圖
        self.crowd_density = np.zeros_like(self.grid_map, dtype=float)
        
        # 根據當前人員位置更新擁擠度
        for x, y in positions:
            if 0 <= x < self.height and 0 <= y < self.width:
                # 在位置周圍增加擁擠度
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.height and 0 <= ny < self.width:
                            # 距離越近，擁擠度越高
                            distance = np.sqrt(dx**2 + dy**2)
                            if distance > 0:
                                self.crowd_density[nx, ny] += 1.0 / distance
    
    def heuristic(self, a, b):
        """計算兩點之間的曼哈頓距離"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(self, node):
        """獲取相鄰節點"""
        x, y = node
        neighbors = []
        
        # 上下左右四個方向
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.height and 0 <= ny < self.width and 
                self.grid_map[nx, ny] == 0):  # 確保是可通行區域
                neighbors.append((nx, ny))
                
        return neighbors
    
    def calculate_cost(self, current, neighbor):
        """計算從當前節點到鄰居節點的代價"""
        # 基本移動代價
        base_cost = 1.0
        
        # 擁擠度代價
        crowd_cost = self.crowd_density[neighbor] * self.crowd_weight
        
        return base_cost + crowd_cost
    
    def find_path(self, start, goal):
        """使用改進的A*算法尋找路徑"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        open_set_hash = {start}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            open_set_hash.remove(current)
            
            if current == goal:
                # 重建路徑
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]  # 反轉路徑
            
            for neighbor in self.get_neighbors(current):
                # 計算到鄰居的臨時g分數
                temp_g_score = g_score[current] + self.calculate_cost(current, neighbor)
                
                # 如果找到更好的路徑
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + self.heuristic(neighbor, goal)
                    
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)
        
        return None  # 沒有找到路徑
