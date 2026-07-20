from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages 
from dotenv import load_dotenv

import sqlite3

load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database = 'chatbot.db', check_same_thread= False)
# Checkpointer
checkpointer = SqliteSaver(conn = conn)



graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for i in checkpointer.list(None):
        all_threads.add(i.config['configurable']['thread_id'])
    return list(all_threads)


# # # # st.session_state -> dict -> 
# CONFIG = {'configurable': {'thread_id': 'thread-1'}}


# for message_chunk, metadata in chatbot.stream({'messages': [HumanMessage(content='what is the receipe to make pasta')]}, config=CONFIG, stream_mode='messages'):
#     if message_chunk.content:
#         print (message_chunk.content, end = '', flush= True)

# response = chatbot.invoke({'messages': [HumanMessage(content="what is my name")]}, config=CONFIG)
# print (response)
# # print (chatbot.get_state(config= CONFIG).values['messages'])