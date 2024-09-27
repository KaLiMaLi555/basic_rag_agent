from typing import Any, Dict, List, Optional

from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import END, StateGraph

from .agent import Agent, AgentState


class LLMGraph:
    def __init__(self, tools: List[BaseTool]):
        self.tools = tools
        self.agent = Agent(self.tools)
        self.graph = self.build_graph()

    def build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("oracle", self.agent.run_agent)
        for tool_obj in self.tools:
            graph.add_node(tool_obj.name, self.agent.run_tool)
        graph.set_entry_point("oracle")
        graph.add_conditional_edges(
            source="oracle",
            path=self.router,
        )
        for tool_obj in self.tools:
            if tool_obj.name != "final_answer":
                graph.add_edge(tool_obj.name, "oracle")
        graph.add_edge("final_answer", END)
        compiled_graph = graph.compile()
        return compiled_graph

    @staticmethod
    def router(state: Dict[str, Any]):
        # return the tool name to use
        if isinstance(state["intermediate_steps"], list):
            return state["intermediate_steps"][-1].tool
        # if we output bad format go to final answer
        print("Router invalid format")
        return "final_answer"

    def invoke(self, query: str, chat_history: Optional[List[Any]] = None):
        if chat_history is None:
            chat_history = []
        for i in range(len(chat_history)):
            message = chat_history[i]
            author = message.author
            if author == "User":
                chat_history[i] = HumanMessage(content=message.content)
            elif author == "AI":
                chat_history[i] = AIMessage(content=message.content)
        result = self.graph.invoke(
            {"input": query, "chat_history": chat_history}
        )
        return result


def build_report(results: dict):
    output = results["intermediate_steps"][-1].tool_input
    research_steps = output["research_steps"]
    if type(research_steps) is list:
        research_steps = "\n".join([f"- {r}" for r in research_steps])
    sources = output["sources"]
    if type(sources) is list:
        sources = "\n".join([f"- {s}" for s in sources])
    return f"""
**INTRODUCTION**
------------
{output["introduction"]}\n\n

**RESEARCH STEPS**
--------------
{research_steps}\n\n

**REPORT**
------
{output["main_body"]}\n\n

**CONCLUSION**
----------
{output["conclusion"]}\n\n

**SOURCES**
-------
{sources}
"""
