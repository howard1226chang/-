# Unity 與 Python 疏散模擬系統串接指南

## 系統架構

```
Python 伺服器 (專題報告/)          Unity 客戶端 (test/)
┌─────────────────────┐          ┌─────────────────────┐
│ unity_server.py     │          │ PythonClient.cs     │
│                     │          │                     │
│ ┌─────────────────┐ │  TCP     │ ┌─────────────────┐ │
│ │ PathPlanner     │ │  JSON    │ │ TCP Client      │ │
│ │ (A* + Crowd)    │ ├─────────>│ │ (Socket)        │ │
│ └─────────────────┘ │  5555    │ └─────────────────┘ │
│                     │          │                     │
│ ┌─────────────────┐ │          │ ┌─────────────────┐ │
│ │ Agents          │ │          │ │ Agent GameObj   │ │
│ │ Simulation      │ │          │ │ Visualization   │ │
│ └─────────────────┘ │          │ └─────────────────┘ │
└─────────────────────┘          └─────────────────────┘
```

## 執行步驟

### 步驟 1: 啟動 Python 伺服器

1. 開啟終端機，切換到專題報告目錄：
   ```bash
   cd 專題報告
   ```

2. 啟動伺服器：
   ```bash
   python unity_server.py
   ```

3. 你應該會看到：
   ```
   伺服器啟動於 127.0.0.1:5555
   等待 Unity 連接...
   ```

### 步驟 2: 設定 Unity 場景

1. 在 Unity 中開啟 `test` 專案

2. 創建新場景或使用現有場景

3. 在 Hierarchy 中創建空的 GameObject，命名為 "SimulationManager"

4. 附加 `PythonClient` 腳本到該 GameObject

5. 在 Inspector 中設定 PythonClient 參數：
   - **Server IP**: `127.0.0.1`
   - **Server Port**: `5555`
   - **Map Width**: `20`
   - **Map Height**: `20`

6. 指派 Prefabs（需要先創建這些 Prefab）：
   - **Agent Prefab**: 紅色球體或膠囊體
   - **Floor Prefab**: 灰色平面
   - **Wall Prefab**: 深灰色立方體
   - **Exit Prefab**: 綠色平面

### 步驟 3: 創建 Prefabs（如果還沒有）

#### Agent Prefab
1. 創建 3D Object > Sphere
2. 縮放至 (0.5, 0.5, 0.5)
3. 設定材質顏色為紅色
4. 拖曳到 Assets/Prefabs/ 創建 Prefab
5. 刪除場景中的實例

#### Floor Prefab
1. 創建 3D Object > Cube
2. 縮放至 (1, 0.1, 1)
3. 設定材質顏色為灰白色
4. 拖曳到 Assets/Prefabs/ 創建 Prefab
5. 刪除場景中的實例

#### Wall Prefab
1. 創建 3D Object > Cube
2. 縮放至 (1, 2, 1)
3. 設定材質顏色為深灰色
4. 拖曳到 Assets/Prefabs/ 創建 Prefab
5. 刪除場景中的實例

#### Exit Prefab
1. 創建 3D Object > Cube
2. 縮放至 (1, 0.2, 1)
3. 設定材質顏色為綠色
4. 拖曳到 Assets/Prefabs/ 創建 Prefab
5. 刪除場景中的實例

### 步驟 4: 執行模擬

1. 確保 Python 伺服器正在運行

2. 在 Unity 中點擊 Play

3. Unity 會自動連接到 Python 伺服器

4. Python 終端會顯示：
   ```
   Unity 已連接: ('127.0.0.1', xxxxx)
   初始化 10 個代理
   代理 X 已疏散
   ...
   所有代理已疏散！總時間: XX.XX 秒
   ```

5. Unity 場景中會顯示：
   - 地圖環境（地板、牆壁、出口）
   - 代理的移動動畫
   - 疏散時代理變為綠色

## 調整參數

### Python 端 (unity_server.py)

修改這些參數來調整模擬：

```python
# 第 21-23 行
self.map_width = 20        # 地圖寬度
self.map_height = 20       # 地圖高度
self.agent_count = 10      # 代理數量

# 第 27 行
crowd_weight=0.5           # 擁擠度權重 (0-1)

# 第 35 行
self.time_step = 0.1       # 模擬時間步長（秒）

# 第 86 行
'speed': 0.5 + np.random.random() * 0.5  # 代理速度 (0.5-1.0)
```

### Unity 端 (PythonClient.cs)

在 Inspector 中調整：
- **Server IP**: 伺服器 IP（本地為 127.0.0.1）
- **Server Port**: 伺服器端口（預設 5555）
- **Map Width/Height**: 必須與 Python 端一致

## 問題排除

### Python 伺服器無法啟動

**錯誤**: `Address already in use`

**解決**:
```bash
# Windows
netstat -ano | findstr :5555
taskkill /PID <PID> /F

# 或更改端口
# unity_server.py 第 13 行改為: port=5556
# PythonClient.cs Inspector 中改為: 5556
```

### Unity 無法連接

**症狀**: Unity Console 顯示 "無法連接到 Python 伺服器"

**檢查**:
1. Python 伺服器是否正在運行
2. 防火牆是否阻擋端口 5555
3. IP 和端口設定是否正確

### 代理不移動

**可能原因**:
1. 沒有找到有效路徑（檢查地圖設置）
2. 起始位置在牆內（unity_server.py:66-70 會避開）
3. Python 伺服器錯誤（查看 Python 終端輸出）

### Prefab 未指派

**症狀**: Unity Console 警告 "Agent Prefab 未設置"

**解決**: 在 Inspector 中拖曳對應的 Prefab 到欄位

## 架構說明

### 資料流程

1. **Python 計算** (每 0.1 秒):
   - 更新代理位置
   - 計算擁擠度
   - 動態路徑規劃

2. **發送 JSON**:
   ```json
   {
     "time": 1.5,
     "agents": [
       {"id": 0, "x": 5.2, "y": 3.7, "evacuated": false},
       {"id": 1, "x": 6.8, "y": 4.1, "evacuated": false}
     ],
     "all_evacuated": false
   }
   ```

3. **Unity 接收並渲染**:
   - 創建/更新 GameObject
   - 平滑移動動畫
   - 更新顏色狀態

### 座標系統

- **Python**: (row, col) 格式，原點在左上
- **Unity**: (x, y, z) 格式，y 軸朝上
- **轉換**: Python 的 (row, col) → Unity 的 (x=col, z=row)

## 進階功能

### 添加動態障礙物

在 `unity_server.py` 的 `simulation_loop()` 中加入：

```python
# 在特定時間添加障礙物
if 5.0 < self.current_time < 10.0:
    self.path_planner.add_dynamic_obstacle((10, 5))
```

### 修改地圖佈局

編輯 `create_map()` 方法 (第 38-59 行) 來自訂地圖。

### 調整擁擠度影響

修改 `crowd_weight` 參數 (第 27 行):
- `0.0`: 不考慮擁擠度（純最短路徑）
- `0.5`: 平衡路徑長度和擁擠度
- `1.0`: 高度避開擁擠區域

## 檔案對應關係

| 功能 | Python | Unity |
|------|--------|-------|
| 路徑規劃 | `src/pathfinding/dynamic_path_planner.py` | - |
| A* 演算法 | `src/pathfinding/path_planner.py` | - |
| 模擬控制 | `unity_server.py` | - |
| 網路通訊 | `unity_server.py` (Server) | `PythonClient.cs` (Client) |
| 視覺化 | - | `PythonClient.cs` |
| 環境創建 | `create_map()` | `CreateEnvironment()` |

## 延伸應用

1. **儲存模擬資料**: 在 Python 端記錄所有代理路徑到 CSV
2. **多場景測試**: 創建不同的地圖配置
3. **性能分析**: 比較不同 `crowd_weight` 的疏散效率
4. **VR 整合**: 將 Unity 場景轉換為 VR 體驗
5. **多出口測試**: 修改 `exit_positions` 測試不同出口配置

## 參考資料

- Python 疏散模擬: `專題報告/src/`
- Unity 腳本: `test/Assets/Scripts/`
- 專案說明: `CLAUDE.md`
