
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

go_prompt=ChatPromptTemplate.from_template("帮我生成一份关于{question}golang语言的代码")

python_prompt = ChatPromptTemplate.from_template("帮我生成一份关于{question}python语言的代码")



llm=ChatOllama(model="gemma2")
def output_function(_dict):
    print("go语言代码:",str(_dict["go"]))
    print("python代码:",str(_dict["python"]))
go_chain = go_prompt|llm|StrOutputParser()
py_chain = python_prompt|llm|StrOutputParser()
multi_chain={"go":go_chain,"python":py_chain}|RunnableLambda(output_function)
res=multi_chain.invoke(quetion="如何写入文件?")
print(res)
