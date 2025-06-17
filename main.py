from dotenv import load_dotenv
import os 
load_dotenv()  # take environment variables from .env

from azure.identity import DefaultAzureCredential
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores.azuresearch import AzureSearch
# MemorySaver class from LangGraph is used to manage message history.
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage


# === Configuration variables ===
AZURE_INFERENCE_ENDPOINT = os.getenv("AZURE_INFERENCE_ENDPOINT")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# === Use DefaultAzureCredential for authentication ===
credential = DefaultAzureCredential()

prompt = ChatPromptTemplate.from_template(
    "Answer the question based only on the context below.\n\n" \
    "Context:\n{context}\n\nQuestion: {question}"
)

class ChatState(dict): 
    pass

# === Initialize Chat Model ===
chat_model = AzureChatOpenAI(
    deployment_name="gpt-35-turbo",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    model_version="0125"
)

# === Initialize Embeddings ===
embedding_model = AzureOpenAIEmbeddings(
    deployment="text-embedding-ada-002",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
)

# === Initialize Vector Store ===
vectorstore = AzureSearch(
    azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
    azure_search_key=AZURE_SEARCH_KEY,
    index_name=AZURE_SEARCH_INDEX_NAME,
    embedding_function=embedding_model.embed_query
)
retriever = vectorstore.as_retriever(search_type="similarity", k=5)


qa_chain = (
    RunnableParallel(
        context = retriever,
        question = RunnablePassthrough()
    )
    | prompt
    | chat_model
    | StrOutputParser()
)

# node function
def chat_node(state: ChatState):
    """
    A simple chat node that takes a question and returns an answer.
    """
    if "messages" not in state or not state["messages"]:
        return state  # No messages to process
    user_message = state["messages"][-1].content
    docs = retriever.invoke(user_message)
    context = "\n".join([doc.page_content for doc in docs])
    # prompt_text = prompt.format(context=context, question=user_message)
    # response = chat_model.invoke(prompt_text)
    # prompt_text = prompt.format(context=context, question=user_message)
    # response = chat_model.invoke([HumanMessage(content=prompt_text)])
    # Add AI response to messages

    chat_history = state["messages"][:-1]  # all previous messages
    # Add the new prompt as the latest user message
    prompt_message = HumanMessage(content=prompt.format(context=context, question=user_message))
    # Compose the full message list
    messages = chat_history + [prompt_message]
    response = chat_model.invoke(messages)
    state["messages"].append(AIMessage(content=response))


    return state

# state graph setup
graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.set_entry_point("chat")
graph.add_edge("chat", END)

# === Initialize MemorySaver Instead of ConversationBufferMemory ===
memory = MemorySaver()

app = graph.compile(checkpointer=memory)

# === Wrap with Message History using the MemorySaver instance ===
# chat_with_memory = RunnableWithMessageHistory(
#     qa_chain,
#     lambda thread_id memory,  # Now returns your GraphMemory instance
#     input_messages_key="query"
# )

# === Run the Chat ===
# if __name__ == "__main__":
#     print("💬 Azure AI Foundry Chat with LangGraph Memory (type 'exit' to quit)")
#     thread_id = "user-session-1"
#     state = ChatState(messages=[])
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             break
#         state["messages"].append(HumanMessage(content=user_input))
#         state = app.invoke(state, config={"configurable": {"thread_id": thread_id}})
#         if state is None or "messages" not in state or not state["messages"]:
#             print("Assistant: [No response]")
#         else:
#             print("Assistant:", state["messages"][-1].content)
#         #print("Assistant:", state["messages"][-1].content)

if __name__ == "__main__":
    print("💬 Azure AI Foundry Chat with LangGraph Memory (type 'exit' to quit)")
    thread_id = "user-session-1"
    state = ChatState(messages=[])
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        if state is None:
            print("Assistant: [Fatal error, state is None]")
            break
        state["messages"].append(HumanMessage(content=user_input))
        try:
            state = app.invoke(state, config={"configurable": {"thread_id": thread_id}})
        except Exception as e:
            print(f"Assistant: [Exception occurred: {e}]")
            break
        if state is None or "messages" not in state or not state["messages"]:
            print("Assistant: [No response]")
        else:
            print("Assistant:", state["messages"][-1].content)
     