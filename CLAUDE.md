# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the VS Code user configuration directory containing extensions and a project folder (`專題報告`) for an evacuation simulation system with crowd-aware pathfinding.

## Evacuation Simulation Project (專題報告/)

### Running the Simulation

```bash
# Run main simulation
cd 專題報告
python src/main.py

# Run pathfinding tests (visual output with matplotlib)
python tests/test_pathfinding.py
```

### Building the C Interface DLL (for Unity integration)

```bash
cd 專題報告/src/interface
cl /LD evacuation_interface.c /Fe:EvacuationSimulation.dll /link /DEF:EvacuationSimulation.def
```

### Architecture

The simulation system consists of three main components:

1. **Pathfinding Module** (`src/pathfinding/`)
   - `PathPlanner`: A* algorithm with crowd density cost weighting
   - `DynamicPathPlanner`: Extends PathPlanner with dynamic obstacle handling and path replanning based on cost threshold changes

2. **Simulation Module** (`src/simulation/`)
   - `SimulationController`: Event-driven simulation with time-stepped agent movement, congestion tracking, and statistics collection
   - Supports events: `add_obstacle`, `remove_obstacle`, `change_agent_goal`

3. **C Interface** (`src/interface/`)
   - DLL interface for Unity integration
   - Exports functions: `InitSimulation`, `UpdateSimulationState`, `GetAgentPosition`, `GetCongestionAt`, `CleanupSimulation`

### Key Concepts

- Grid maps use 0 for passable cells, 1 for obstacles
- Crowd density is calculated with distance-weighted influence (radius of 3 cells)
- Path replanning triggers when path cost improvement exceeds `replanning_threshold` or when blocked by dynamic obstacles
- Coordinates use (row, column) format matching numpy array indexing

### Dependencies

- Python: numpy, matplotlib
- C: Standard library only (for DLL)
