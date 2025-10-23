from langgraph.llm import LLMRouterNode
from agent.tools import ALL_TOOLS

class RouterNode(LLMRouterNode):
    """LLM вирішує, який інструмент викликати далі."""
    model = "gpt-4o"
    tools = ALL_TOOLS

    def prompt(self, state):
        return f"""
        You are an AI orchestrator converting a Rails project to Django.

        Current state:
        {state.__dict__}

        Choose the next best tool call.
        Tools: {', '.join([t.name for t in self.tools])}.
        Return reasoning and the function call.
        """
