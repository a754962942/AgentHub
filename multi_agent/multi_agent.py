import functools
import io
import operator
import os
from typing import Annotated, TypedDict, Sequence, Literal
from PIL import Image
from kubernetes.stream import stream

from langchain_core.messages import AIMessage, ToolMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import  tool
from langchain_community.tools import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from  langchain_mistralai import ChatMistralAI
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from tabulate import tabulate
from langgraph.constants import START,END


os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="ChatBot"
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")


#tool 定义
tavily_tool=TavilySearchResults(max_result=3)
repl=PythonREPL()
@tool
def python_repl(
        code:Annotated[str,"The python code is running here."],
):
    """Use this to execute python code. If you want to see the output of a value,
        you should print it out with `print(...)`. This is visible to the user."""
    try:
        result=repl.run(code)
    except Exception as e:
        return f"Failed to run code,Error:{e}"
    return f"Successfully run code,\n ```python\n{code}\n```result:\n{result}"


@tool
def table_tool(data:Annotated[list,"The data is used to generate table"]):
    """Use input data to generate table.If you want to see the output of a value,
        you should print it out with `print(...)`.this is visible to the user."""
    # print("data:",data)

    return tabulate(data,headers='firstrow',tablefmt='grid')
tools = [tavily_tool,python_repl,table_tool]

tool_node=ToolNode(tools)
#test toolNode
# message_with_tool=AIMessage(
#     content="",
#     tool_calls=[
#        {
#             "name": "table_tool",
#             "args": {"data": [ ['Name', 'Age', 'City'], ['Alice', 25, 'New York'], ['Bob', 30, 'London'], ['Charlie', 28, 'Paris']]},
#             "id": "tool_call_id",
#             "type": "tool_call",
#         }
#     ],)

# for value in tool_node.stream({"messages":[message_with_tool]}):
#     for v in value.values():
#         print(v[-1].content)

# 建造工作agent
def create_agent(llm,tools,system_message:str):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

    # 将提示模板与语言模型和工具绑定
    return prompt | llm.bind_tools(tools)

# 建造节点
def agent_node(state,agent,name):
    result = agent.invoke(state)

    if isinstance(result,ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type","name"}),name=name)
    return {
        "messages":[result],
        "sender":name,
    }
# 准备llm
research_llm=ChatMistralAI(model="mistral-large-latest",temperature=0,max_retries=2)
table_llm= ChatMistralAI(model="mistral-large-latest",temperature=0,max_retries=2)
# 准备agent
research_agent=create_agent(research_llm,[tavily_tool],system_message='Before using the search engine,carefully think through and clarify the query.'
                                                              "Then,conduct a single search that addresses all aspects of the query in one go."
                                                              "You should Collect information and convert it into json format,Process the acquired data.Do not reply more information besides process data  ")
table_agent=create_agent(table_llm,[table_tool],"create clear and user-friendly table based on the provided data.If data format isn't u need,please conversion it."
                         "Before use the tool, you must makesure data format is good for generate table tool."
                         "such as data = [['Name', 'Age', 'City'],['Alice', 25, 'New York']]"
                         "data:A list containing the tabular data. Each sublist represents a row, and the data is arranged in column order.")
# 生成node
research_node=functools.partial(agent_node,agent=research_agent,name="research_agent")
table_node=functools.partial(agent_node,agent=table_agent,name="table_agent")

# 通信结构
class AgentState(TypedDict):
    messages:Annotated[Sequence[BaseMessage],operator.add]
    sender:str

# 新建workflow添加节点
workflow = StateGraph(AgentState)

workflow.add_node("Researcher",research_node)
workflow.add_node("Table_Generator",table_node)
workflow.add_node("call_tool",tool_node)

# 定义router
def router(state)->Literal["call_tool","__end__","continue"]:
    print(f"routeState:{state}")
    messages = state["messages"]
    last_message= messages[-1]

    if last_message.tool_calls:
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        return "__end__"
    return "continue"
# 连接边
workflow.add_conditional_edges(
    "Researcher",
    router,
    {
        "continue":"Table_Generator",
        "__end__":END,
        "call_tool":"call_tool",
    }
)
workflow.add_conditional_edges(
    "Table_Generator",
    router,
{
        "continue":"Researcher",
        "__end__":END,
        "call_tool":"call_tool",
    }
)
workflow.add_conditional_edges(
    "call_tool",
    lambda x:x["sender"],
    {
"research_agent":"Researcher",
"table_agent":"Table_Generator",
    },
)
workflow.add_edge(START,"Researcher")
# compile
app = workflow.compile()

# draw image
# try:
#     filename="../image/multi_agent.png"
#     image_data=app.get_graph().draw_mermaid_png()
#     img = Image.open(io.BytesIO(image_data))
#     img.save(filename)
# except Exception as e:
#     print(f"Error generating graph: {e}")


# test stream
# conversation_history=[]
# while True:
#     user_input = input("User:")
#     conversation_history.append(("user",user_input))
#     for event in app.stream({"messages":conversation_history}):
#         for value in event:
#             print(f"value:{value}")
#             # print("AIMessage:", value["messages"][-1].content)
#             # conversation_history.append(("ai", value["messages"][-1].content))

events =app.stream(
    {
"messages": [
            HumanMessage(
                content="Obtain the GDP of  china  from 2013 to 2023,and then plot a table with data.end the task after generating the table"
            )
        ],
    },
    {"recursion_limit":20},
    stream_mode="values"
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()