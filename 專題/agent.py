import random
import time
from fsm import FSM, State

class Agent:
    def __init__(self, name, role_data, x=0, y=0):
        self.name = name
        self.role = role_data  # 保留完整角色屬性
        self.speed = role_data["speed"]
        self.vision = role_data["vision"]
        self.type = role_data["type"]
        self.reaction_time = role_data["reaction_time"]
        self.tolerance = role_data["tolerance"]
        self.move_delay = role_data["move_delay"]
        # 位置與狀態
        self.x = x
        self.y = y
        self.log = []
        self.fsm = FSM(self)
        
        self.path = None
        self.path_index = 0

    # 🧭 基礎移動邏輯
    def try_move(self, nx, ny, map_system):
        """嘗試移動至 (nx, ny)，若可行則更新地圖與位置"""
        if map_system.is_walkable(nx, ny, self.role):
            map_system.leave(self.x, self.y)
            self.x, self.y = nx, ny
            map_system.occupy(nx, ny)
            self.log.append(f"Moved to ({nx},{ny})")
            return True
        else:
            self.log.append(f"Blocked at ({nx},{ny})")
            return False

    def choose_random_step(self):
        """隨機選一個方向嘗試前進"""
        dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        return self.x + dx, self.y + dy

    def move_toward_exit(self):
        """模擬向出口移動"""
        self.log.append(f"{self.name} 正在以速度 {self.speed} 向出口移動")
        print(f"{self.name} is moving toward exit at speed {self.speed}")

    # 🧩 社會互動邏輯    
    def distance_to(self, other):
        """曼哈頓距離"""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def find_nearest_adult(self, agents):
        """找最近的成人（type 為 adult）"""
        adults = [a for a in agents if a.type == "adult" and a.name != self.name]
        if not adults:
            return None
        return min(adults, key=lambda a: self.distance_to(a))

    def move_toward(self, target, map_system):
        """向指定角色移動"""
        dx = 1 if target.x > self.x else -1 if target.x < self.x else 0
        dy = 1 if target.y > self.y else -1 if target.y < self.y else 0
        nx, ny = self.x + dx, self.y + dy

        if map_system.is_walkable(nx, ny, self.role):
            map_system.leave(self.x, self.y)
            self.x, self.y = nx, ny
            map_system.occupy(nx, ny)
            msg = f"跟隨 {target.name} 移動到 ({nx},{ny})"
            self.log.append(msg)
            print(msg)
        else:
            self.log.append("跟隨失敗，路被擋住")

    # 📸 狀態記錄
    def snapshot(self, action):
        """回傳當下角色狀態的紀錄 dict"""
        return {
            "time": time.time(),
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "state": self.fsm.state.value,
            "action": action
        }

    # 🔁 更新邏輯（每回合呼叫一次）
    def update(self, map_system, agents, crowd_density=0.0, event=None):
        """根據 FSM 狀態與環境更新角色行為"""
        if self.fsm.state == State.ARRIVED:
            return

        # 若擁擠超過容忍度 → 等待
        if crowd_density > self.tolerance or map_system.is_crowded(self.x, self.y):
            self.log.append("等待中（擁擠區）")
            self.fsm.update("wait", crowd_density)
            return

        # 小孩偏好跟隨成人
        if self.type == "child":
            target = self.find_nearest_adult(agents)
            if target:
                self.move_toward(target, map_system)
                return

        # 一般隨機移動邏輯
        nx, ny = self.choose_random_step()
        if self.try_move(nx, ny, map_system):
            self.fsm.update("clear", crowd_density)
        else:
            self.fsm.update("obstacle", crowd_density)