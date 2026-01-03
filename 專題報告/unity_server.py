"""
Python 模擬伺服器 - 將路徑規劃結果傳送給 Unity
"""
import socket
import json
import time
import threading
import numpy as np
from src.pathfinding.path_planner import PathPlanner
from src.pathfinding.dynamic_path_planner import DynamicPathPlanner

class UnitySimulationServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.running = False

        # 模擬參數
        self.map_width = 20
        self.map_height = 20
        self.agent_count = 10

        # 初始化地圖和路徑規劃器
        self.grid_map = self.create_map()
        self.path_planner = DynamicPathPlanner(self.grid_map, crowd_weight=0.5)

        # 代理狀態
        self.agents = []
        self.exit_positions = [(self.map_width - 2, self.map_height - 1),
                               (self.map_width - 1, self.map_height - 2)]

        # 模擬時間
        self.time_step = 0.1
        self.current_time = 0.0

    def create_map(self):
        """創建地圖，0=可通行，1=障礙物"""
        grid_map = np.zeros((self.map_height, self.map_width), dtype=int)

        # 邊緣牆壁
        for x in range(self.map_width):
            grid_map[0, x] = 1
            grid_map[self.map_height - 1, x] = 1
        for y in range(self.map_height):
            grid_map[y, 0] = 1
            grid_map[y, self.map_width - 1] = 1

        # 出口（設為可通行）
        grid_map[self.map_height - 1, self.map_width - 2] = 0
        grid_map[self.map_height - 2, self.map_width - 1] = 0

        # 內部牆（中間有門）
        for i in range(5, 15):
            if i != 10:  # 門的位置
                grid_map[10, i] = 1

        return grid_map

    def init_agents(self):
        """初始化代理"""
        self.agents = []
        for i in range(self.agent_count):
            # 隨機起始位置（避開牆壁）
            while True:
                x = np.random.randint(2, self.map_width - 2)
                y = np.random.randint(2, self.map_height - 2)
                if self.grid_map[y, x] == 0:
                    break

            # 選擇最近的出口作為目標
            goal = self.exit_positions[0]

            # 計算路徑
            path = self.path_planner.find_path((y, x), (goal[1], goal[0]))

            if path:
                print(f"代理 {i}: 起點({y},{x}) -> 終點({goal[1]},{goal[0]}), 路徑長度: {len(path)}")
            else:
                print(f"警告: 代理 {i} 無法找到路徑！起點({y},{x}) -> 終點({goal[1]},{goal[0]})")

            self.agents.append({
                'id': i,
                'x': float(x),
                'y': float(y),
                'goal': goal,
                'path': path if path else [],
                'path_index': 0,
                'evacuated': False,
                'speed': 0.5 + np.random.random() * 0.5  # 0.5 ~ 1.0
            })

        print(f"初始化 {self.agent_count} 個代理完成")

    def update_simulation(self):
        """更新模擬一個時間步"""
        # 收集所有代理位置用於擁擠度計算
        positions = [(int(a['y']), int(a['x'])) for a in self.agents if not a['evacuated']]
        self.path_planner.update_crowd_density(positions)

        for agent in self.agents:
            if agent['evacuated']:
                continue

            # 檢查是否到達出口
            dist_to_exit = min(
                abs(agent['x'] - ex[0]) + abs(agent['y'] - ex[1])
                for ex in self.exit_positions
            )
            if dist_to_exit < 1.0:
                agent['evacuated'] = True
                print(f"代理 {agent['id']} 已疏散")
                continue

            # 沿路徑移動
            if agent['path'] and agent['path_index'] < len(agent['path']):
                target = agent['path'][agent['path_index']]
                target_x, target_y = target[1], target[0]  # 轉換座標

                # 計算移動方向
                dx = target_x - agent['x']
                dy = target_y - agent['y']
                dist = np.sqrt(dx*dx + dy*dy)

                if dist > 0.1:
                    # 移動
                    move_dist = agent['speed'] * self.time_step
                    agent['x'] += (dx / dist) * move_dist
                    agent['y'] += (dy / dist) * move_dist
                else:
                    # 到達路徑點，移動到下一個
                    agent['path_index'] += 1

            # 定期重新規劃路徑
            if np.random.random() < 0.05:  # 5% 機率重新規劃
                current_pos = (int(agent['y']), int(agent['x']))
                goal_pos = (agent['goal'][1], agent['goal'][0])
                new_path = self.path_planner.find_path(current_pos, goal_pos)
                if new_path:
                    agent['path'] = new_path
                    agent['path_index'] = 0

        self.current_time += self.time_step

    def get_state_json(self):
        """獲取當前狀態的 JSON"""
        state = {
            'time': self.current_time,
            'agents': [
                {
                    'id': a['id'],
                    'x': a['x'],
                    'y': a['y'],
                    'evacuated': a['evacuated']
                }
                for a in self.agents
            ],
            'all_evacuated': all(a['evacuated'] for a in self.agents)
        }
        return json.dumps(state)

    def start_server(self):
        """啟動伺服器"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.running = True

        print(f"伺服器啟動於 {self.host}:{self.port}")
        print("等待 Unity 連接...")

        while self.running:
            try:
                self.client_socket, addr = self.server_socket.accept()
                print(f"Unity 已連接: {addr}")

                # 初始化代理
                self.init_agents()
                self.current_time = 0.0

                # 開始模擬循環
                self.simulation_loop()

            except Exception as e:
                print(f"錯誤: {e}")

    def simulation_loop(self):
        """模擬主循環"""
        try:
            print("開始模擬循環...")
            frame_count = 0
            while self.running and self.client_socket:
                # 更新模擬
                try:
                    self.update_simulation()
                except Exception as e:
                    print(f"更新模擬時發生錯誤: {e}")
                    import traceback
                    traceback.print_exc()
                    break

                # 發送狀態給 Unity
                try:
                    state_json = self.get_state_json()
                    message = state_json + "\n"
                    self.client_socket.send(message.encode('utf-8'))

                    frame_count += 1
                    if frame_count % 50 == 0:  # 每 50 幀輸出一次
                        print(f"已發送 {frame_count} 幀，時間: {self.current_time:.2f}s")

                except Exception as e:
                    print(f"發送資料時發生錯誤: {e}")
                    import traceback
                    traceback.print_exc()
                    break

                # 檢查是否全部疏散
                if all(a['evacuated'] for a in self.agents):
                    print(f"所有代理已疏散！總時間: {self.current_time:.2f} 秒")
                    time.sleep(2)
                    break

                # 控制更新頻率
                time.sleep(self.time_step)

        except (ConnectionResetError, BrokenPipeError) as e:
            print(f"Unity 斷開連接: {e}")
        except Exception as e:
            print(f"模擬錯誤: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            print("模擬循環結束")

    def stop(self):
        """停止伺服器"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        print("伺服器已停止")


if __name__ == "__main__":
    server = UnitySimulationServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n收到中斷信號")
        server.stop()
