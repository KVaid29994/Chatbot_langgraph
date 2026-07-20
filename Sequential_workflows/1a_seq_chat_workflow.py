from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from typing import TypedDict

from dotenv import load_dotenv
load_dotenv()
llm = ChatOpenAI(model="gpt-5-nano")

class ChatState(TypedDict):
    question : str
    answer : str

def chat_nodes(state: ChatState) -> ChatState:
    
    answer = llm.invoke(state['question'])
    answer_final = answer.content
     
    state['answer'] = answer_final
    return state

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_nodes)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node", END)

agent = graph.compile()

question = "What is capital of India"
result =agent.invoke({"question": question})

print (result['answer'])
