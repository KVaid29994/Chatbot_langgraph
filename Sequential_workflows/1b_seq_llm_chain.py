from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from typing import TypedDict


from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI()
class BlogState(TypedDict):
    topic : str
    outline : str
    blog : str

def generate_outline(state: BlogState):
    topic = state['topic']
    prompt = f"for the following {topic} generate an outline to write a funny blog"
    outline_details = llm.invoke(prompt).content
    state['outline'] = outline_details

    return state

def generate_blog(state: BlogState):
    outline_details = state['outline']
    prompt = f"genertae a 40 words blog based on the detials below {outline_details}"
    blog = llm.invoke(prompt).content
    state['blog'] = blog
    return state

graph = StateGraph(BlogState)
graph.add_node("generate_outline", generate_outline)
graph.add_node("generate_blog", generate_blog)

graph.add_edge(START,"generate_outline")
graph.add_edge("generate_outline", "generate_blog")
graph.add_edge("generate_blog", END)

agent = graph.compile()

topic = "Apple pie"
result = agent.invoke({"topic": topic})

print (result)