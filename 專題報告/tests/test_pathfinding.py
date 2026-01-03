import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pathfinding.path_planner import PathPlanner
from pathfinding.dynamic_path_planner import DynamicPathPlanner

def test_basic_pathfinding():
    # 創建一個簡單的測試地圖
    grid_map = np.zeros((20, 20), dtype=int)
    
    # 添加一些障礙物
    for i in range(5, 15):
        grid_map[i, 10] = 1  # 垂直牆
    grid_map[10, 10] = 0  # 牆中的門
    
    # 初始化路徑規劃器
    planner = PathPlanner(grid_map)
    
    # 測試幾組起點和終點
    test_cases = [
        ((5, 5), (15, 15)),  # 需要穿過門
        ((1, 1), (18, 18)),  # 對角線路徑
        ((5, 15), (15, 5))   # 從另一側穿過
    ]
    
    plt.figure(figsize=(15, 5))
    for i, (start, goal) in enumerate(test_cases):
        path = planner.find_path(start, goal)
        
        # 繪製地圖和路徑
        plt.subplot(1, 3, i+1)
        plt.imshow(grid_map, cmap='binary')
        
        if path:
            path_x = [p[0] for p in path]
            path_y = [p[1] for p in path]
            plt.plot(path_y, path_x, 'r-', linewidth=2)
            plt.plot(start[1], start[0], 'go', markersize=10)
            plt.plot(goal[1], goal[0], 'bo', markersize=10)
            plt.title(f"測試 {i+1}: 路徑長度 = {len(path)}")
        else:
            plt.title(f"測試 {i+1}: 未找到路徑")
    
    plt.tight_layout()
    plt.show()
    
    return all(planner.find_path(start, goal) is not None for start, goal in test_cases)

def test_crowd_density_influence():
    # 創建測試地圖
    grid_map = np.zeros((20, 20), dtype=int)
    
    # 初始化路徑規劃器，設置不同的擁擠度權重
    planner_no_crowd = PathPlanner(grid_map, crowd_weight=0)
    planner_medium_crowd = PathPlanner(grid_map, crowd_weight=1.0)
    planner_high_crowd = PathPlanner(grid_map, crowd_weight=3.0)
    
    # 設置起點和終點
    start = (2, 2)
    goal = (17, 17)
    
    # 在中間區域添加人群
    crowd_positions = []
    for i in range(8, 12):
        for j in range(8, 12):
            crowd_positions.append((i, j))
    
    # 更新三個規劃器的擁擠度地圖
    planner_no_crowd.update_crowd_density(crowd_positions)
    planner_medium_crowd.update_crowd_density(crowd_positions)
    planner_high_crowd.update_crowd_density(crowd_positions)
    
    # 計算三個不同路徑
    path_no_crowd = planner_no_crowd.find_path(start, goal)
    path_medium_crowd = planner_medium_crowd.find_path(start, goal)
    path_high_crowd = planner_high_crowd.find_path(start, goal)
    
    # 繪製結果
    plt.figure(figsize=(15, 5))
    
    # 繪製擁擠度地圖
    crowd_density = planner_medium_crowd.crowd_density
    
    for i, (path, title) in enumerate([
        (path_no_crowd, "無擁擠度影響"),
        (path_medium_crowd, "中等擁擠度影響"),
        (path_high_crowd, "高擁擠度影響")
    ]):
        plt.subplot(1, 3, i+1)
        plt.imshow(crowd_density, cmap='hot', alpha=0.6)
        plt.colorbar(label='擁擠度')
        
        if path:
            path_x = [p[0] for p in path]
            path_y = [p[1] for p in path]
            plt.plot(path_y, path_x, 'b-', linewidth=2)
            plt.plot(start[1], start[0], 'go', markersize=10)
            plt.plot(goal[1], goal[0], 'ro', markersize=10)
            plt.title(f"{title}\n路徑長度: {len(path)}")
        
    plt.tight_layout()
    plt.show()
    
    # 驗證高擁擠度權重的路徑應該繞開擁擠區域
    if path_high_crowd and path_no_crowd:
        # 計算路徑與擁擠中心的最小距離
        crowd_center = (10, 10)
        min_dist_no_crowd = min(abs(p[0] - crowd_center[0]) + abs(p[1] - crowd_center[1]) for p in path_no_crowd)
        min_dist_high_crowd = min(abs(p[0] - crowd_center[0]) + abs(p[1] - crowd_center[1]) for p in path_high_crowd)
        
        # 高擁擠度權重的路徑應該與擁擠中心保持更遠的距離
        return min_dist_high_crowd > min_dist_no_crowd
    return False

def test_dynamic_obstacle_handling():
    # 創建測試地圖
    grid_map = np.zeros((20, 20), dtype=int)
    
    # 初始化動態路徑規劃器
    planner = DynamicPathPlanner(grid_map)
    
    # 設置起點和終點
    start = (2, 2)
    goal = (17, 17)
    
    # 計算初始路徑
    initial_path = planner.find_path(start, goal)
    
    # 添加動態障礙物阻擋路徑
    # 找到路徑中間的點
    if initial_path:
        middle_point = initial_path[len(initial_path) // 2]
        planner.add_dynamic_obstacle(middle_point)
    
    # 重新規劃路徑
    replanned_path = planner.update_and_replan(start, goal, initial_path)
    
    # 繪製結果
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.imshow(grid_map, cmap='binary')
    if initial_path:
        path_x = [p[0] for p in initial_path]
        path_y = [p[1] for p in initial_path]
        plt.plot(path_y, path_x, 'b-', linewidth=2)
        plt.plot(start[1], start[0], 'go', markersize=10)
        plt.plot(goal[1], goal[0], 'ro', markersize=10)
        if initial_path:
            middle_point = initial_path[len(initial_path) // 2]
            plt.plot(middle_point[1], middle_point[0], 'kx', markersize=12)
    plt.title("初始路徑")
    
    plt.subplot(1, 2, 2)
    plt.imshow(grid_map, cmap='binary')
    if replanned_path:
        path_x = [p[0] for p in replanned_path]
        path_y = [p[1] for p in replanned_path]
        plt.plot(path_y, path_x, 'g-', linewidth=2)
        plt.plot(start[1], start[0], 'go', markersize=10)
        plt.plot(goal[1], goal[0], 'ro', markersize=10)
        if initial_path:
            middle_point = initial_path[len(initial_path) // 2]
            plt.plot(middle_point[1], middle_point[0], 'kx', markersize=12, label='動態障礙物')
            plt.legend()
    plt.title("重規劃路徑")
    
    plt.tight_layout()
    plt.show()
    
    # 驗證重規劃的路徑應該避開動態障礙物
    if initial_path and replanned_path:
        obstacle_point = initial_path[len(initial_path) // 2]
        return obstacle_point not in replanned_path
    return False

if __name__ == "__main__":
    print("測試基本路徑規劃...")
    test_basic_pathfinding()
    
    print("\n測試擁擠度影響...")
    test_crowd_density_influence()
    
    print("\n測試動態障礙處理...")
    test_dynamic_obstacle_handling()