import operator
from typing import Annotated, Any, Dict, List, TypedDict

from langchain.tools import BaseTool
from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

SYSTEM_PROMPT = """You are the oracle, the great AI assistant and decision maker.
Your objective is to process the user's query by deciding the best tool to use from the list provided.

Tool Usage Management:
- Avoid calling any tool with the same input more than twice.
- Ensure that no tool is used more than twice.
- Do not use the tool with tool_usage greater than or equal to 2.

Query Processing:
- Assess the user’s query.
- Choose the most appropriate tool from the provided list.
- Execute and log the actions taken.

Final Execution:
- After completing the necessary tool interactions, run final_answer to present the user with the final results."""


class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
    tool_usage: Annotated[dict[str, int], operator.add]


class Agent:
    def __init__(self, tools: List[BaseTool]):
        self.tools: List[BaseTool] = tools
        self.tool_str_to_func: Dict[str, BaseTool] = {
            tool.name: tool for tool in tools
        }
        self.agent_chain = self.get_agent_chain()

    def get_agent_chain(self) -> Runnable:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
        )
        llm_with_tools = llm.bind_tools(self.tools, tool_choice="any")
        agent_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                (
                    "assistant",
                    "scratchpad: {scratchpad}\ntool_usage: {tool_usage}",
                ),
            ]
        )
        agent_chain: Runnable = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "scratchpad": lambda x: self.create_scratchpad(
                    intermediate_steps=x["intermediate_steps"]
                ),
                "tool_usage": lambda x: x["tool_usage"],
            }
            | agent_prompt
            | llm_with_tools
        )
        return agent_chain

    @staticmethod
    def create_scratchpad(intermediate_steps: list[AgentAction]):
        research_steps = []
        for _, action in enumerate(intermediate_steps):
            if action.log != "TBD":
                # this was the ToolExecution
                research_steps.append(
                    f"Tool: {action.tool}, input: {action.tool_input}\n"
                    f"Output: {action.log}"
                )
        return "\n---\n".join(research_steps)

    def run_tool(self, state: Dict[str, Any]):
        # use this as helper function so we repeat less code
        tool_name = state["intermediate_steps"][-1].tool
        tool_args = state["intermediate_steps"][-1].tool_input
        tool_usage = state["tool_usage"]
        if tool_name != "final_answer":
            print(f"{tool_name}.invoke(input={tool_args})")
        else:
            print(f"{tool_name}.invoke(input=OUTPUT)")
        if tool_usage.get(tool_name, 0) >= 2:
            action_out = AgentAction(
                tool=tool_name,
                tool_input=tool_args,
                log=f"{tool_name} cannot be used anymore, try some other tools",
            )
            print(f"Tool Usage {tool_name} Exceeded, try some other tools")
            return {"intermediate_steps": [action_out]}
        tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        # run tool
        tool_output = self.tool_str_to_func[tool_name].invoke(input=tool_args)
        action_out = AgentAction(
            tool=tool_name,
            tool_input=tool_args,
            log=str(tool_output),
        )
        return {"intermediate_steps": [action_out]}

    def run_agent(self, state: Dict[str, Any]):
        result = self.agent_chain.invoke(state)
        tool_name = result.tool_calls[0]["name"]
        tool_args = result.tool_calls[0]["args"]
        action_out = AgentAction(
            tool=tool_name, tool_input=tool_args, log="TBD"
        )
        return {"intermediate_steps": [action_out]}
