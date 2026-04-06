"""
Python 模擬伺服器 - 將路徑規劃結果傳送給 Unity
"""
import socket
import json
import time
import threading
import numpy as np

# 使用新的資料夾結構導入
from src.pathfinding.path_planner import PathPlanner
from src.pathfinding.dynamic_path_planner import DynamicPathPlanner
from Time_Event_Control import SimulationController

class UnitySimulationServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.is_running = False
        
        # 模擬參數
        self.grid_map = None
        self.path_planner = None
        self.simulation_controller = None
        self.agents = []
        self.exits = []
        
        print(f"[Server] Initializing Unity Simulation Server...")
    
    def start(self):
        """啟動伺服器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            self.is_running = True
            
            print(f"[Server] ✓ Unity Simulation Server started on {self.host}:{self.port}")
            print(f"[Server] Waiting for Unity client...")
            
            self.client_socket, addr = self.server_socket.accept()
            print(f"[Server] ✓ Client connected from {addr}")
            
            # 處理客戶端請求
            self.handle_client()
            
        except Exception as e:
            print(f"[Server] ✗ Start error: {e}")
            self.cleanup()
    
    def handle_client(self):
        """處理客戶端訊息"""
        buffer = ""
        
        while self.is_running:
            try:
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    print("[Server] Client disconnected")
                    break
                
                buffer += data
                
                # 處理完整的訊息（以換行符分隔）
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.process_message(line.strip())
                        
            except Exception as e:
                print(f"[Server] Handle error: {e}")
                break
        
        self.cleanup()
    
    def process_message(self, message):
        """處理接收到的訊息"""
        try:
            print(f"[Server] Received: {message[:100]}...")
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'init':
                response = self.handle_init(data)
            elif command == 'update':
                response = self.handle_update(data)
            elif command == 'get_paths':
                response = self.handle_get_paths(data)
            elif command == 'step':
                response = self.handle_step(data)
            else:
                response = {'status': 'error', 'message': f'Unknown command: {command}'}
            
            self.send_response(response)
            
        except json.JSONDecodeError as e:
            print(f"[Server] Invalid JSON: {message}")
            print(f"[Server] Error: {e}")
        except Exception as e:
            print(f"[Server] Process error: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_init(self, data):
        """初始化模擬環境"""
        print("[Server] Handling init command...")
        
        grid_width = data.get('grid_width', 50)
        grid_height = data.get('grid_height', 50)
        agent_count = data.get('agent_count', 10)
        exit_x = data.get('exit_x', grid_width // 2)
        exit_y = data.get('exit_y', 0)
        
        # 創建網格地圖 (height x width)
        self.grid_map = np.zeros((grid_height, grid_width), dtype=np.float32)
        
        # 初始化路徑規劃器
        try:
            self.path_planner = DynamicPathPlanner(
                self.grid_map,
                crowd_weight=0.5,
                replanning_threshold=0.5
            )
            print("[Server] ✓ DynamicPathPlanner initialized")
        except Exception as e:
            print(f"[Server] ⚠ DynamicPathPlanner init failed: {e}")
            # 降級使用基礎版本
            self.path_planner = PathPlanner(self.grid_map, crowd_weight=0.5)
            print("[Server] ✓ Using basic PathPlanner")
        
        # 初始化模擬控制器
        try:
            self.simulation_controller = SimulationController(
                self.grid_map,
                time_step=0.1
            )
            print("[Server] ✓ Simulation controller initialized")
        except Exception as e:
            print(f"[Server] ⚠ Simulation controller init failed: {e}")
            self.simulation_controller = None
        
        # 生成代理人（避開邊界）
        self.agents = []
        margin = 3
        for i in range(agent_count):
            agent = {
                'id': i,
                'position': [
                    float(np.random.uniform(margin, grid_width - margin)),
                    float(np.random.uniform(margin, grid_height - margin))
                ],
                'target': [float(exit_x), float(exit_y)],
                'path': [],
                'active': True
            }
            self.agents.append(agent)
        
        print(f"[Server] ✓ Generated {agent_count} agents")
        
        response = {
            'status': 'initialized',
            'agent_count': agent_count,
            'grid_size': [grid_width, grid_height],
            'exit': [exit_x, exit_y],
            'agents': self.agents
        }
        
        print(f"[Server] Sending init response with {len(self.agents)} agents")
        return response
    
    def handle_update(self, data):
        """更新代理人位置"""
        print("[Server] Handling update command...")
        
        time_step = data.get('time_step', 0.1)
        speed = 1.0  # 每秒移動距離
        
        active_count = 0
        
        # 更新所有代理人的位置（用於擁擠度計算）
        positions = [(int(a['position'][1]), int(a['position'][0])) 
                     for a in self.agents if a['active']]
        self.path_planner.update_crowd_density(positions)
        
        for agent in self.agents:
            if not agent['active']:
                continue
            
            active_count += 1
            
            # 如果沒有路徑，計算新路徑
            if not agent['path']:
                try:
                    # 注意：網格座標是 (row, col) = (y, x)
                    start = (int(agent['position'][1]), int(agent['position'][0]))
                    goal = (int(agent['target'][1]), int(agent['target'][0]))
                    
                    # 確保座標在範圍內
                    start = (
                        max(0, min(self.grid_map.shape[0] - 1, start[0])),
                        max(0, min(self.grid_map.shape[1] - 1, start[1]))
                    )
                    goal = (
                        max(0, min(self.grid_map.shape[0] - 1, goal[0])),
                        max(0, min(self.grid_map.shape[1] - 1, goal[1]))
                    )
                    
                    # 使用路徑規劃器
                    path = self.path_planner.find_path(start, goal)
                    
                    if path:
                        # 轉換回 (x, y) 格式
                        agent['path'] = [[float(col), float(row)] for row, col in path]
                    
                except Exception as e:
                    print(f"[Server] Path planning error for agent {agent['id']}: {e}")
            
            # 沿著路徑移動
            if agent['path']:
                next_pos = agent['path'][0]
                
                # 計算移動方向
                dx = next_pos[0] - agent['position'][0]
                dy = next_pos[1] - agent['position'][1]
                distance = np.sqrt(dx**2 + dy**2)
                
                if distance < 0.5:  # 到達路徑點
                    agent['path'].pop(0)
                else:
                    # 朝目標移動
                    move_distance = speed * time_step
                    agent['position'][0] += (dx / distance) * move_distance
                    agent['position'][1] += (dy / distance) * move_distance
            
            # 檢查是否到達目標
            target_dist = np.sqrt(
                (agent['position'][0] - agent['target'][0])**2 +
                (agent['position'][1] - agent['target'][1])**2
            )
            
            if target_dist < 1.0:
                agent['active'] = False
                print(f"[Server] Agent {agent['id']} reached exit")
        
        response = {
            'status': 'updated',
            'agents': self.agents,
            'active_count': active_count
        }
        
        print(f"[Server] Updated {active_count} active agents")
        return response
    
    def handle_step(self, data):
        """使用 SimulationController 進行一步模擬"""
        if self.simulation_controller:
            try:
                self.simulation_controller.step()
                return self.handle_update(data)
            except Exception as e:
                print(f"[Server] Step error: {e}")
                return {'status': 'error', 'message': str(e)}
        else:
            return self.handle_update(data)
    
    def handle_get_paths(self, data):
        """返回所有代理人的路徑"""
        paths = []
        for agent in self.agents:
            if agent['active']:
                paths.append({
                    'id': agent['id'],
                    'path': agent['path']
                })
        
        response = {
            'status': 'paths',
            'paths': paths
        }
        
        return response
    
    def send_response(self, response):
        """發送回應給客戶端"""
        try:
            message = json.dumps(response) + '\n'
            self.client_socket.send(message.encode('utf-8'))
            print(f"[Server] Sent response: {response.get('status', 'unknown')}")
        except Exception as e:
            print(f"[Server] Send error: {e}")
    
    def cleanup(self):
        """清理資源"""
        print("[Server] Cleaning up...")
        self.is_running = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("[Server] Server stopped")

def main():
    """主函數"""
    print("=" * 60)
    print("Unity Simulation Server")
    print("=" * 60)
    
    server = UnitySimulationServer(host='127.0.0.1', port=5555)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[Server] Interrupted by user")
        server.cleanup()
    except Exception as e:
        print(f"[Server] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        server.cleanup()

if __name__ == '__main__':
    main()
