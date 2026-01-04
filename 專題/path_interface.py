def agent_to_path_request(agent, grid, grid_occupancy, goal):
    return {
        "start": (agent.x, agent.y),
        "goal": goal,
        "grid": grid,
        "grid_occupancy": grid_occupancy,
        "avoid": agent.role.get("avoid_terrain", []),
        "can_use_stairs": agent.role.get("can_use_stairs", True),
    }

def apply_path_to_agent(agent, path):
    agent.path = path
    agent.path_index = 0