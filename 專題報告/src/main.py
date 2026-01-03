import numpy as np
from pathfinding.path_planner import PathPlanner
from pathfinding.dynamic_path_planner import DynamicPathPlanner
from simulation.simulation_controller import SimulationController
import matplotlib.pyplot as plt

def create_test_map(width=20, height=20):
    """創建測試地圖"""
    grid_map = np.zeros((height, width), dtype=int)
    
    # 添加一些障礙物
    for i in range(5, 15):
        grid_map[i, 10] = 1  # 垂直牆
    grid_map[10, 10] = 0  # 牆中的門
    
    return grid_map

def main():
    # 創建地圖
    grid_map = create_test_map()
    
    # 初始化模擬控制器
    sim = SimulationController(grid_map)
    
    # 添加代理
    sim.add_agent(0, (2, 2), (17, 17))
    sim.add_agent(1, (3, 3), (16, 16))
    sim.add_agent(2, (4, 4), (15, 15))
    
    # 添加一些事件
    sim.add_event(5.0, "add_obstacle", (10, 10))
    sim.add_event(10.0, "remove_obstacle", (10, 10))
    
    # 運行模擬
    stats = sim.run_simulation(max_time=30.0)
    
    # 輸出結果
    print("模擬完成!")
    print(f"疏散時間: {stats['evacuation_time']:.2f} 秒")
    print(f"路徑變更次數: {stats['path_changes']}")
    print(f"擁擠點數量: {len(stats['congestion_points'])}")
    
    # 繪製最終擁擠度地圖
    plt.figure(figsize=(8, 6))
    plt.imshow(sim.path_planner.crowd_density, cmap='hot')
    plt.colorbar(label='擁擠度')
    plt.title('最終擁擠度地圖')
    plt.show()

if __name__ == "__main__":
    main()
