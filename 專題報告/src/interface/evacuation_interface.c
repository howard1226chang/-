#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "evacuation_interface.h"

// 全局模擬狀態
static SimulationState current_state;

void InitSimulation(int width, int height, int agent_count) {
    current_state.width = width;
    current_state.height = height;
    current_state.agent_count = agent_count;
    current_state.time = 0.0f;
    
    // 分配內存
    current_state.agents = (Agent*)malloc(agent_count * sizeof(Agent));
    current_state.congestion_map = (float*)malloc(width * height * sizeof(float));
    
    // 初始化擁擠度地圖
    memset(current_state.congestion_map, 0, width * height * sizeof(float));
    
    // 初始化代理
    for (int i = 0; i < agent_count; i++) {
        current_state.agents[i].id = i;
        current_state.agents[i].x = 0.0f;
        current_state.agents[i].y = 0.0f;
        current_state.agents[i].evacuated = 0;
    }
}

void UpdateSimulationState(float time, float* agent_positions, int* agent_evacuated, float* congestion_data) {
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

void GetAgentPosition(int agent_id, float* x, float* y, int* evacuated) {
    if (agent_id >= 0 && agent_id < current_state.agent_count) {
        *x = current_state.agents[agent_id].x;
        *y = current_state.agents[agent_id].y;
        *evacuated = current_state.agents[agent_id].evacuated;
    }
}

float GetCongestionAt(int x, int y) {
    if (x >= 0 && x < current_state.width && y >= 0 && y < current_state.height) {
        return current_state.congestion_map[y * current_state.width + x];
    }
    return 0.0f;
}

void CleanupSimulation() {
    free(current_state.agents);
    free(current_state.congestion_map);
    
    // 重置狀態
    current_state.agents = NULL;
    current_state.congestion_map = NULL;
    current_state.agent_count = 0;
    current_state.width = 0;
    current_state.height = 0;
}
