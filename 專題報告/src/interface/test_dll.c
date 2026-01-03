// test_dll.c
#include <stdio.h>
#include <windows.h>
#include "evacuation_interface.h"

// 如果沒有頭文件，則需要手動聲明函數
#ifndef EVACUATION_INTERFACE_H
extern void InitSimulation(int width, int height, int agent_count);
extern void UpdateSimulationState(float time, float* agent_positions, int* agent_evacuated, float* congestion_data);
extern void GetAgentPosition(int agent_id, float* x, float* y, int* evacuated);
extern float GetCongestionAt(int x, int y);
extern void CleanupSimulation();
#endif

int main() {
    // 設置控制台為 UTF-8 編碼
    SetConsoleOutputCP(65001);

    printf("測試避難模擬 DLL...\n");
    
    // 初始化模擬
    InitSimulation(10, 10, 3);
    printf("模擬初始化完成，地圖大小: 10x10，代理數量: 3\n");
    
    // 創建測試數據
    float agent_positions[6] = {1.0, 1.0, 2.0, 2.0, 3.0, 3.0};
    int agent_evacuated[3] = {0, 0, 0};
    float congestion_data[100] = {0};  // 10x10 地圖
    
    // 設置一些擁擠度數據
    congestion_data[55] = 5.0;  // 位置 (5,5)
    
    // 更新模擬狀態
    UpdateSimulationState(1.0, agent_positions, agent_evacuated, congestion_data);
    printf("模擬狀態已更新\n");
    
    // 測試獲取代理位置
    float x, y;
    int evacuated;
    GetAgentPosition(0, &x, &y, &evacuated);
    printf("代理 0 位置: (%.1f, %.1f), 疏散狀態: %d\n", x, y, evacuated);
    
    // 測試獲取擁擠度
    float congestion = GetCongestionAt(5, 5);
    printf("位置 (5,5) 的擁擠度: %.1f\n", congestion);
    
    // 清理資源
    CleanupSimulation();
    printf("資源已清理\n");
    
    printf("測試完成!\n");
    return 0;
}
