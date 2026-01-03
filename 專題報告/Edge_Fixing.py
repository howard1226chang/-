class DynamicPathPlanner(PathPlanner):
    def __init__(self, grid_map, crowd_weight=0.5, replanning_threshold=0.5):
        """
        初始化動態路徑規劃器
        
        參數:
        - replanning_threshold: 重規劃閾值，當路徑代價變化超過此閾值時觸發重規劃
        """
        super().__init__(grid_map, crowd_weight)
        self.replanning_threshold = replanning_threshold
        self.dynamic_obstacles = set()  # 動態障礙物集合
        
    def add_dynamic_obstacle(self, position):
        """添加動態障礙物"""
        self.dynamic_obstacles.add(position)
        
    def remove_dynamic_obstacle(self, position):
        """移除動態障礙物"""
        if position in self.dynamic_obstacles:
            self.dynamic_obstacles.remove(position)
    
    def is_path_valid(self, path):
        """檢查路徑是否有效（沒有被動態障礙物阻擋）"""
        if not path:
            return False
        
        for node in path:
            if node in self.dynamic_obstacles:
                return False
        return True
    
    def calculate_path_cost(self, path):
        """計算路徑總代價"""
        if not path or len(path) < 2:
            return float('inf')
        
        total_cost = 0
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            total_cost += self.calculate_cost(current, next_node)
        
        return total_cost
    
    def should_replan(self, current_path, current_position):
        """判斷是否需要重新規劃路徑"""
        # 如果路徑被動態障礙物阻擋，需要重規劃
        if not self.is_path_valid(current_path):
            return True
        
        # 如果當前位置不在路徑上，需要重規劃
        if current_position not in current_path:
            return True
        
        # 計算剩餘路徑的代價
        current_index = current_path.index(current_position)
        remaining_path = current_path[current_index:]
        
        # 重新計算從當前位置到目標的路徑
        goal = current_path[-1]
        new_path = self.find_path(current_position, goal)
        
        if not new_path:
            return False  # 無法找到新路徑，保持原路徑
        
        # 比較新舊路徑代價
        old_cost = self.calculate_path_cost(remaining_path)
        new_cost = self.calculate_path_cost(new_path)
        
        # 如果新路徑比舊路徑更好（代價降低超過閾值），則重規劃
        return (old_cost - new_cost) / old_cost > self.replanning_threshold
    
    def update_and_replan(self, current_position, goal, current_path=None):
        """更新環境信息並在必要時重新規劃路徑"""
        if current_path is None or self.should_replan(current_path, current_position):
            # 考慮動態障礙物的臨時地圖
            temp_map = self.grid_map.copy()
            for obs_x, obs_y in self.dynamic_obstacles:
                if 0 <= obs_x < self.height and 0 <= obs_y < self.width:
                    temp_map[obs_x, obs_y] = 1  # 標記為障礙物
            
            # 暫時替換地圖進行路徑規劃
            original_map = self.grid_map
            self.grid_map = temp_map
            new_path = self.find_path(current_position, goal)
            self.grid_map = original_map  # 恢復原始地圖
            
            return new_path
        
        return current_path
