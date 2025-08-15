class State:
    def __init__(self, name):
        self.name = name

    def execute(self):
        """Run the state logic.
        Return the name of the next state."""
        raise NotImplementedError


class Operator:
    def __init__(self, states, start_state):
        self.states = states
        self.state_name = start_state

    def run(self):
        while True:
            state_obj = self.states[self.state_name]
            next_state = state_obj.execute()
            if next_state != self.state_name:
                print(f"[STATE CHANGE] {self.state_name} → {next_state}")
            self.state_name = next_state

# class State:
#     def __init__(self, name):
#         self.name = name

#     def execute(self):
#         raise NotImplementedError

# class Operator:
#     def __init__(self, states, start_state):
#         self.states = states
#         self.state_name = start_state

#     def run(self):
#         while True:
#             state_obj = self.states[self.state_name]
#             next_state = state_obj.execute()
#             if next_state != self.state_name:
#                 print(f"[STATE CHANGE] {self.state_name} → {next_state}")
#             self.state_name = next_state

