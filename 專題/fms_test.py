from fsm import FSM

# 建立角色狀態機實例
role_fsm = FSM("小孩")

# 狀態轉換模擬
role_fsm.start_evacuation()    # Idle → Evacuate
role_fsm.encounter_obstacle()  # Evacuate → Avoid
role_fsm.avoid_finished()      # Avoid → Evacuate
role_fsm.reach_exit()  # Evacuate → Arrived
role_fsm.show_history()

# 檢查過程輸出
role_fsm.show_history()
