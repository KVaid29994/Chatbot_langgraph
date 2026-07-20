from langgraph.graph import StateGraph, END , START , message
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver


from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI()
class JokeState(TypedDict):
    topic : str
    joke: str
    explanation : str


def generate_joke(state: JokeState):

    prompt = f'generate a joke on the topic {state["topic"]}'
    response = llm.invoke(prompt).content

    return {'joke': response}

def generate_explanation(state: JokeState):

    prompt = f'write an explanation for the joke - {state["joke"]}'
    response = llm.invoke(prompt).content

    return {'explanation': response}

graph = StateGraph(JokeState)

graph.add_node('generate_joke', generate_joke)
graph.add_node('generate_explanation', generate_explanation)

graph.add_edge(START, 'generate_joke')
graph.add_edge('generate_joke', 'generate_explanation')
graph.add_edge('generate_explanation', END)

checkpointer = InMemorySaver()

workflow = graph.compile(checkpointer=checkpointer)

config1 = {"configurable": {"thread_id": "1"}}
print (workflow.invoke({'topic':'pizza'}, config=config1))

print (workflow.get_state(config1))

print(list(workflow.get_state_history(config1)))

config2 = {"configurable": {"thread_id": "2"}}
workflow.invoke({'topic':'pasta'}, config=config2)

print(workflow.get_state(config2))
print (workflow.get_state_history(config2))

workflow.update_state({"configurable":{'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f178884-e66a-6c8c-bfff-ad6c3272d873'}}, {'topic':'samosa'})
print (list(workflow.get_state_history(config1)))


workflow.invoke(None, {"configurable": {"thread_id": "1", "checkpoint_id": "1f06cc72-ca16-6359-8001-7eea05e07dd2"}})

print (list(workflow.get_state_history(config1)))
