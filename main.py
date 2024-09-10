import bs4
from langchain_chroma import Chroma
from langchain_community.chat_models import  ChatOllama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import  HuggingFaceHubEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
b4_strainer=bs4.SoupStrainer(class_=("post-title","post-content"))

loader=WebBaseLoader(web_paths=("https://lilianweng.github.io/posts/2024-02-05-human-data-quality/",),
              bs_kwargs={"parse_only":b4_strainer})
post_content=loader.load()
# print(len(post_content[0].page_content))
splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=100,add_start_index=True)
all_chunks=splitter.split_documents(post_content)
# print(all_chunks[1].page_content)

vector_store=Chroma.from_documents(documents=all_chunks,embedding=HuggingFaceHubEmbeddings())
retriever=vector_store.as_retriever(search_type="similarity",search_kwargs={"k":6})

# print(retrieved_docs)
llm = ChatOllama(model="gemma2")
prompt=hub.pull("rlm/rag-prompt")
prompt_v1=hub.pull("rlm/rag-document-relevance")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

res=rag_chain.invoke("Everyone wants to do the model work")
print(res)
