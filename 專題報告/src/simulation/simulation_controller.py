import numpy as np
from ..pathfinding.dynamic_path_planner import DynamicPathPlanner

class SimulationController:
    def __init__(self, grid_map, time_step=0.1):
        """
        初始化模擬控制器
        
        參數:
        - grid_map: 環境地圖
        - time_step: 模擬時間步長（秒）
        """
        self.grid_map = grid_map
        self.time_step = time_step
        self.current_time = 0.0
        self.path_planner = DynamicPathPlanner(grid_map)
        
        # 事件隊列，格式為 (觸發時間, 事件類型, 事件數據)
        self.event_queue = []
        
        # 代理列表，每個代理包含位置、目標、當前路徑等信息
        self.agents = []
        
        # 統計數據
        self.stats = {
            "evacuation_time": 0,
            "congestion_points": [],
            "path_changes": 0
        }
    
    def add_agent(self, agent_id, position, goal):
        """添加代理（人員）"""
        path = self.path_planner.find_path(position, goal)
        self.agents.append({
            "id": agent_id,
            "position": position,
            "goal": goal,
            "path": path,
            "current_path_index": 0,
            "evacuated": False,
            "speed": 1.0,  # 每個時間步可以移動的網格數
            "path_changes": 0
        })
    
    def add_event(self, time, event_type, data):
        """添加事件到隊列"""
        self.event_queue.append((self.current_time + time, event_type, data))
        self.event_queue.sort()  # 按時間排序
    
    def update_agent_positions(self):
        """更新所有代理的位置"""
        # 收集所有代理的當前位置，用於更新擁擠度地圖
        positions = [agent["position"] for agent in self.agents if not agent["evacuated"]]
        self.path_planner.update_crowd_density(positions)
        
        for agent in self.agents:
            if agent["evacuated"]:
                continue
                
            # 如果已經到達目標
            if agent["position"] == agent["goal"]:
                agent["evacuated"] = True
                continue
                
            # 檢查是否需要重新規劃路徑
            new_path = self.path_planner.update_and_replan(
                agent["position"], agent["goal"], agent["path"])
                
            if new_path and new_path != agent["path"]:
                agent["path"] = new_path
                agent["current_path_index"] = 0
                agent["path_changes"] += 1
                self.stats["path_changes"] += 1
            
            # 沿著路徑移動
            if agent["path"] and agent["current_path_index"] < len(agent["path"]) - 1:
                # 根據速度移動
                steps = min(int(agent["speed"]), len(agent["path"]) - 1 - agent["current_path_index"])
                agent["current_path_index"] += steps
                agent["position"] = agent["path"][agent["current_path_index"]]
    
    def process_events(self):
        """處理當前時間步的事件"""
        while self.event_queue and self.event_queue[0][0] <= self.current_time:
            _, event_type, data = self.event_queue.pop(0)
            
            if event_type == "add_obstacle":
                x, y = data
                self.path_planner.add_dynamic_obstacle((x, y))
                
            elif event_type == "remove_obstacle":
                x, y = data
                self.path_planner.remove_dynamic_obstacle((x, y))
                
            elif event_type == "change_agent_goal":
                agent_id, new_goal = data
                for agent in self.agents:
                    if agent["id"] == agent_id:
                        agent["goal"] = new_goal
                        agent["path"] = self.path_planner.find_path(agent["position"], new_goal)
                        agent["current_path_index"] = 0
                        break
    
    def step(self):
        """執行一個模擬時間步"""
        self.process_events()
        self.update_agent_positions()
        
        # 更新模擬時間
        self.current_time += self.time_step
        
        # 檢查是否所有代理都已疏散
        all_evacuated = all(agent["evacuated"] for agent in self.agents)
        if all_evacuated:
            self.stats["evacuation_time"] = self.current_time
            
        # 識別擁擠點
        congestion_threshold = 5.0  # 擁擠度閾值
        congestion_points = []
        for i in range(self.path_planner.height):
            for j in range(self.path_planner.width):
                if self.path_planner.crowd_density[i, j] > congestion_threshold:
                    congestion_points.append((i, j, self.path_planner.crowd_density[i, j]))
        
        self.stats["congestion_points"] = congestion_points
        
        return all_evacuated
    
    def run_simulation(self, max_time=1000.0):
        """運行完整模擬"""
        while self.current_time < max_time:
            all_evacuated = self.step()
            if all_evacuated:
                break
                
        return self.stats
    
    def get_simulation_state(self):
        """獲取當前模擬狀態，用於可視化或導出到Unity"""
        state = {
            "time": self.current_time,
            "agents": [],
            "congestion_map": self.path_planner.crowd_density.tolist()
        }
        
        for agent in self.agents:
            state["agents"].append({
                "id": agent["id"],
                "position": agent["position"],
                "goal": agent["goal"],
                "path": agent["path"],
                "evacuated": agent["evacuated"]
            })
            
        return state

