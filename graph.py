import os
from typing import Annotated

from langchain_core.messages import ToolMessage, HumanMessage
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

from tools import airbnb_search

load_dotenv()
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

class Agent:

    def __init__(self, model, tools):
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("call_airbnb_mcp", self.call_airbnb_mcp)
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {
                True: "call_airbnb_mcp", 
                False: END
            }
        )
        graph.add_edge("call_airbnb_mcp", "llm")
        graph.add_edge(START, "llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_openai(self, state: AgentState):
        messages = state['messages']
        message = self.model.invoke(messages)
        return {'messages': [message]}

    def call_airbnb_mcp(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for tool in tool_calls:
            print(f"Calling: {tool}")
            if not tool['name'] in self.tools:      # check for bad tool name from LLM
                print("\n ....bad tool name....")
                result = "bad tool name, retry"  # instruct LLM to retry if bad
            else:
                result = self.tools[tool['name']].invoke(tool['args'])
            results.append(ToolMessage(tool_call_id=tool['id'], name=tool['name'], content=str(result)))
        print("Back to the model!")
        return {'messages': results}


llm = ChatOpenAI(
    temperature=0.0, 
    model="gpt-4o-mini", 
    api_key=os.getenv("OPENAI_API_KEY")
)

agent = Agent(
    model=llm,
    tools=[airbnb_search]
)

messages = [HumanMessage(content="What the Airbnb lowest prices in Natal, RN ")]
result = agent.graph.invoke({"messages": messages})
print(result['messages'][-1].content)

