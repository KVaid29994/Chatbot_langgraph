from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv


load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

def chat_node(state : ChatState) -> ChatState:
    messages = state['messages']

    response = llm.invoke(messages)
    return {'messages':[response]}

graph = StateGraph(ChatState)

checkpointer = InMemorySaver()
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

config = {'configurable':{'thread_id':'123'}}
for message_chunk, metadata in chatbot.stream({'messages': [HumanMessage(content="What is the receipe to make pasta")]}, config=config, 
               stream_mode="messages"):
    if message_chunk.content:
        print (message_chunk.content , end = ' ', flush= True)