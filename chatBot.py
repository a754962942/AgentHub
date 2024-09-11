import io
import json
import os
from typing import Annotated, Literal
from PIL import Image
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import ToolMessage
from langchain_core.tools import  Tool
from langchain_mistralai import ChatMistralAI
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from openai import max_retries
from sympy.physics.units import temperature
from typing_extensions import TypedDict
from langchain_community.utilities import  GoogleSerperAPIWrapper
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="ChatBot"
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")
class State(TypedDict):
    messages:Annotated[list,add_messages]

graph_builder=StateGraph(State)

class BasicToolNode:
    def __init__(self,tools:list):
        self.tools_by_name={tool.name:tool for tool in tools}
    def __call__(self, inputs:dict):
        if messages := inputs.get("messages",[]):
            message = messages[-1]
        else:
            raise ValueError("未找到信息")
        outputs=[]
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id = tool_call["id"],
                )
            )
        return {"messages":outputs}

search=TavilySearchResults()
# print(search.run("iPhone16 pro 相关的信息，包括配置 价格等"))
tools =[search]
llm_with_tools=ChatMistralAI(model="mistral-large-latest",temperature=0,max_retries=2).bind_tools(tools=tools)
def chatbot(state:State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}



def route_tools(state:State)->Literal["tools","__end__"]:
    if isinstance(state,list):
        ai_message = state[-1]
    elif messages := state.get("messages",[]):
        ai_message = messages[-1]
    else:
        raise ValueError(f"输入状态未找到消息:{State}")
    if hasattr(ai_message,"tool_calls") and len(ai_message.tool_calls)>0:
        return "tools"
    else:
        return "__end__"
graph_builder.add_edge(START,"chatBot")
tool_node = BasicToolNode(tools)
graph_builder.add_node("tools",tool_node)

graph_builder.add_conditional_edges(
    "chatBot",
    route_tools,
    {"tools":"tools","__end__":"__end__"}
)
graph_builder.add_node("chatBot",chatbot)
graph_builder.add_edge(START,"chatBot")
graph_builder.add_edge("tools","chatBot")
# graph_builder.add_edge("chatBot",END)
graph=graph_builder.compile()
# try:
#     filename="./ChatBotGraph_WithTools.png"
#     image_data=graph.get_graph().draw_mermaid_png()
#     img= Image.open(io.BytesIO(image_data))
#     img.save(filename)
# except Exception as e:
#     print(e)

while True:
    user_input=input("User:")
    for event in  graph.stream({"messages":[("user",user_input)]}):
       for value in  event.values():
            print("AIMessage:",value["messages"][-1].content)