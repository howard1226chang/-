import numpy as np
import matplotlib.pyplot as plt

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
