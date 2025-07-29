from typing import Annotated

from langchain_core.messages import ToolMessage, AIMessage
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from dotenv import load_dotenv

load_dotenv()
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

class Agent:

    def __init__(self, model, tools):
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("call_tools", self.call_tools)
        graph.add_conditional_edges(
            "llm",
            self.can_call_tools,
            {
                True: "call_tools", 
                False: END
            }
        )
        graph.add_edge("call_tools", "llm")

        graph.add_edge(START, "llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    
    def can_call_tools(self, state: AgentState):
        """Check if the last message contains a tool call"""
        ia_messages = [item for item in state['messages'] if isinstance(item, AIMessage)]
        result = ia_messages[-1]
        return len(result.tool_calls) > 0

    def call_openai(self, state: AgentState):
        messages = state['messages']
        message = self.model.invoke(messages)
        return {'messages': [message]}

    def call_tools(self, state: AgentState):
        
        ia_messages = [item for item in state['messages'] if isinstance(item, AIMessage)]
        tool_calls = ia_messages[-1].tool_calls

        results = []
        for tool in tool_calls:
            print(f"Calling tool: {tool['name']} with args: {tool['args']}")
            result = self.tools[tool['name']].invoke(tool['args'])
            message = ToolMessage(tool_call_id=tool['id'], name=tool['name'], content=str(result))
            results.append(message)
        print("Back to the model!")
        return {'messages': state["messages"] + results}