import copy

class SandboxManager:
    def __init__(self, graph_handler):
        self.handler = graph_handler
        self.original_graph = None
        self.in_sandbox = False
        self.scenario = None

    def enter_sandbox(self, scenario: str):
        """
        Deep-copies the handler's active graph to construct an isolated thought experiment sandbox.
        """
        self.original_graph = self.handler.graph
        self.handler.graph = copy.deepcopy(self.original_graph)
        self.handler.graph.graph["is_sandbox"] = True
        self.handler.graph.graph["scenario"] = scenario
        self.in_sandbox = True
        self.scenario = scenario

    def exit_sandbox(self):
        """
        Restores the original graph and exits the sandbox.
        """
        if self.in_sandbox:
            self.handler.graph = self.original_graph
            self.original_graph = None
            self.in_sandbox = False
            self.scenario = None
        return True
