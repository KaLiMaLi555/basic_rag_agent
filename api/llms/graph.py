from typing import Any, Dict, List, Optional

from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph

from .agent import Agent, AgentState
from .sarwam_api import get_speech

REPORT_TEMPLATE = """
**INTRODUCTION**
------------
{introduction}\n\n

**RESEARCH STEPS**
--------------
{research_steps}\n\n

**REPORT**
------
{main_body}\n\n

**CONCLUSION**
----------
{conclusion}\n\n

**SOURCES**
-------
{sources}
"""


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
            if tool_obj.name not in ("final_answer", "miscellaneous_chat"):
                graph.add_edge(tool_obj.name, "oracle")
        graph.add_edge("final_answer", END)
        graph.add_edge("miscellaneous_chat", END)
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


def build_report(
    results: dict, text_to_speech: bool = False, sarwam_api_key: str = ""
):
    last_tool = results["intermediate_steps"][-1].tool
    if last_tool == "miscellaneous_chat":
        results = results["intermediate_steps"][-1].tool_input
        speech = None
        if text_to_speech:
            speech = get_speech(results["answer"], sarwam_api_key)
        return (results["answer"], speech)

    output = results["intermediate_steps"][-1].tool_input
    research_steps = output["research_steps"]
    if isinstance(research_steps, list):
        research_steps = "\n".join([f"- {r}" for r in research_steps])
    sources = output["sources"]
    for steps in results["intermediate_steps"]:
        if steps.tool == "fetch_sound_ncert":
            sources.append("Ncert sound chapter")
            break
    if isinstance(sources, list):
        sources = "\n".join([f"- {s}" for s in sources])
    report = REPORT_TEMPLATE.format(
        introduction=output["introduction"],
        research_steps=research_steps,
        main_body=output["main_body"],
        conclusion=output["conclusion"],
        sources=sources,
    )
    speech = None
    if text_to_speech:
        speech = get_speech(output["conclusion"], sarwam_api_key)
    return (report, speech)
