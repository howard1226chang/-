#ifndef EVACUATION_INTERFACE_H
#define EVACUATION_INTERFACE_H

#ifdef __cplusplus
extern "C" {
#endif

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

// 接口函數
void InitSimulation(int width, int height, int agent_count);
void UpdateSimulationState(float time, float* agent_positions, int* agent_evacuated, float* congestion_data);
void GetAgentPosition(int agent_id, float* x, float* y, int* evacuated);
float GetCongestionAt(int x, int y);
void CleanupSimulation();

#ifdef __cplusplus
}
#endif

#endif // EVACUATION_INTERFACE_H
