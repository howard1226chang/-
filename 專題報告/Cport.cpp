#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 定義數據結構
typedef struct {
    int id;
    float x;
    float y;
    int evacuated;
} Agent;

typedef struct {
    float time;
    int agent_count;
    Agent* agents;
    int width;
    int height;
    float* congestion_map;
} SimulationState;

// 全局模擬狀態
SimulationState current_state;

// 初始化模擬
void init_simulation(int width, int height, int agent_count) {
    current_state.width = width;
    current_state.height = height;
    current_state.agent_count = agent_count;
    current_state.time = 0.0f;
    
    // 分配內存
    current_state.agents = (Agent*)malloc(agent_count * sizeof(Agent));
    current_state.congestion_map = (float*)malloc(width * height * sizeof(float));
    
    // 初始化擁擠度地圖
    memset(current_state.congestion_map, 0, width * height * sizeof(float));
}

// 更新模擬狀態
void update_simulation_state(float time, float* agent_positions, int* agent_evacuated, float* congestion_data) {
    current_state.time = time;
    
    // 更新代理位置
    for (int i = 0; i < current_state.agent_count; i++) {
        current_state.agents[i].x = agent_positions[i * 2];
        current_state.agents[i].y = agent_positions[i * 2 + 1];
        current_state.agents[i].evacuated = agent_evacuated[i];
    }
    
    // 更新擁擠度地圖
    memcpy(current_state.congestion_map, congestion_data, 
           current_state.width * current_state.height * sizeof(float));
}

// 獲取代理位置
void get_agent_position(int agent_id, float* x, float* y, int* evacuated) {
    if (agent_id >= 0 && agent_id < current_state.agent_count) {
        *x = current_state.agents[agent_id].x;
        *y = current_state.agents[agent_id].y;
        *evacuated = current_state.agents[agent_id].evacuated;
    }
}

// 獲取擁擠度值
float get_congestion_at(int x, int y) {
    if (x >= 0 && x < current_state.width && y >= 0 && y < current_state.height) {
        return current_state.congestion_map[y * current_state.width + x];
    }
    return 0.0f;
}

// 清理資源
void cleanup_simulation() {
    free(current_state.agents);
    free(current_state.congestion_map);
}

// 導出函數（用於Unity的DllImport）
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT void InitSimulation(int width, int height, int agent_count) {
    init_simulation(width, height, agent_count);
}

EXPORT void UpdateSimulationState(float time, float* agent_positions, int* agent_evacuated, float* congestion_data) {
    update_simulation_state(time, agent_positions, agent_evacuated, congestion_data);
}

EXPORT void GetAgentPosition(int agent_id, float* x, float* y, int* evacuated) {
    get_agent_position(agent_id, x, y, evacuated);
}

EXPORT float GetCongestionAt(int x, int y) {
    return get_congestion_at(x, y);
}

EXPORT void CleanupSimulation() {
    cleanup_simulation();
}
