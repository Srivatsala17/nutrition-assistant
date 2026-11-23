from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from core.llm import get_llm
from core.prompts import build_agent_prompt
from core.tools import make_tools
from db import crud

memory = MemorySaver()  # remembers the conversation


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_agent(user_id: int):
    user = crud.get_user(user_id)
    tools = make_tools(user_id)
    llm = get_llm().bind_tools(tools)
    system = SystemMessage(content=build_agent_prompt(user))

    def call_model(state: AgentState):
        response = llm.invoke([system] + state["messages"])
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)  # tool call -> tools, else end
    graph.add_edge("tools", "agent")                       # after a tool, think again
    return graph.compile(checkpointer=memory)


def chat(agent, user_id: int, text: str) -> str:
    config = {"configurable": {"thread_id": f"user-{user_id}"}, "recursion_limit": 12}
    result = agent.invoke({"messages": [("user", text)]}, config)
    return result["messages"][-1].content