import asyncio
import io
import os
from typing import TypedDict, Annotated

from PIL import Image
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import add_messages, StateGraph

os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="ChatBot"
code_writer_prompt=ChatPromptTemplate.from_messages(
        [
            (
                # "system",
                # "You are a professional fairy tale writer, please help me write a short essay around InputMessage"
                # "I will evaluate the results you generate and suggest changes based on my suggestions.Then, You should Modify the story based on my suggestions"
                # "must Reply to me in Chinese"
                "system",
                "You are a top development engineer proficient in the field of programming, "
                "familiar with programming related fields including system architecture design,"
                " system development coding, system operation and maintenance, and system testing."
                " You are very proficient in all processes related to the software. Please help me design or code according to my needs"
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
teacher_prompt=ChatPromptTemplate.from_messages(
    [
        (
            # "system"
            # "You are a professional writing instructor, please rate my story and give guidance and advice."
            # " Provide detailed recommendations, including requests for length, depth, style, etc."
            # "must Reply to me in Chinese"
            "system",
           "You are a software engineer with over twenty years of experience leading large teams in software design and software development. "
           "Please give me guidance on my design or coding, "
           "and you can advise me on multiple dimensions. "
           "I need to refer to your advice"
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
writer_llm=code_writer_prompt|ChatOllama(
    model="llama3.1:8b-instruct-q8_0",
    max_tokens=9000,
    temperature=1.3
)
teacher_llm=teacher_prompt|ChatOllama(
    model="llama3.1:8b-instruct-q8_0",
    max_tokens=9000,
    temperature=0.1
)
topic = HumanMessage(
    content="帮助我编写一个react框架，支持ios及android的软件，要求实现简单的登录，并对常用的组件进行封装。如 aioxs"
)
# article=""
# for chunk in writer_llm.stream({"messages":[topic]}):
#     print(chunk.content,end="")
#     article+=chunk.content
#
# reflection=""
# for chunk in teacher_llm.stream({"messages":[HumanMessage(content=article)]}):
#     print(chunk.content,end="")
#     reflection+=chunk.content

class State(TypedDict):
    messages: Annotated[list,add_messages]

async def generation_node(state:State)->State:
    return {"messages":[await writer_llm.ainvoke(state['messages'])]}

async def reflection_node(state:State)->State:
    cls_map = {"ai":HumanMessage,"human":AIMessage}

    translated=[state['messages'][0]]+[cls_map[msg.type](content=msg.content) for msg in state["messages"][1:]]
    res = await  teacher_llm.ainvoke(translated)
    return {"messages":[HumanMessage(content=res.content)]}
MAX_ROUND=8
def should_continue(state:State):
    if len(state["messages"])>MAX_ROUND:
        return END
    return "reflect"



builder=StateGraph(State)
builder.add_node("writer",generation_node)
builder.add_node("reflect",reflection_node)
builder.add_edge(START,"writer")
builder.add_conditional_edges("writer",should_continue,{
    "reflect":"reflect",
    END:"__end__"
})
builder.add_edge("reflect","writer")
memory=MemorySaver()
graph=builder.compile(memory)
# try:
#     filename= "image/reflection_agent.png"
#     image_data=graph.get_graph().draw_mermaid_png()
#     img= Image.open(io.BytesIO(image_data))
#     img.save(filename)
# except Exception as e:
#     print(e)

inputs = {
    "messages":[
        HumanMessage(content="帮助我编写一个react框架，支持ios及android的软件，要求实现简单的登录，并对常用的组件进行封装。如 aioxs")
    ],
}
config={"configurable":{"thread_id":"1"}}
async def main():
    async for event in graph.astream(inputs,config):
        for value in event.values():
            print(value["messages"].content)


if __name__=="__main__":
    asyncio.run(main())