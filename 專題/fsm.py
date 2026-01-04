from enum import Enum
import time

class State(Enum):
    IDLE = "Idle"
    WAIT = "Wait"
    EVACUATE = "Evacuate"
    AVOID = "Avoid"
    ARRIVED = "Arrived"


class FSM:
    def __init__(self, agent):
        self.agent = agent
        self.name = agent.name
        self.state = State.IDLE
        self.history = []
        self.log = []
        self.start_reaction_time = time.time()
        self.last_move_time = time.time()

    def change_state(self, new_state: State):
        print(f"{self.name}: {self.state.value} → {new_state.value}")
        self.history.append((self.state.value, new_state.value))
        self.state = new_state

    def update(self, event=None, crowd_density=0.0):
        current_time = time.time()

        # --- 狀態邏輯 ---
        if self.state == State.IDLE:
            if event == "alarm":
                elapsed = current_time - self.start_reaction_time
                if elapsed >= self.agent.reaction_time:
                    self.change_state(State.EVACUATE)
                else:
                    self.change_state(State.WAIT)

        elif self.state == State.WAIT:
            elapsed = current_time - self.start_reaction_time
            if elapsed >= self.agent.reaction_time:
                self.change_state(State.EVACUATE)

        elif self.state == State.EVACUATE:
            if crowd_density > self.agent.tolerance:
                self.change_state(State.WAIT)
            elif event == "obstacle":
                self.change_state(State.AVOID)
            elif event == "arrived":
                self.change_state(State.ARRIVED)
            else:
                # 模擬移動間隔
                if current_time - self.last_move_time >= self.agent.move_delay:
                    self.agent.move_toward_exit()
                    self.last_move_time = current_time

        elif self.state == State.AVOID:
            if event == "clear":
                self.change_state(State.EVACUATE)

        elif self.state == State.ARRIVED:
            pass  # 結束狀態

    def show_history(self):
        print(f"\n{self.name} 狀態轉換紀錄：")
        for old, new in self.history:
            print(f"  {old} → {new}")