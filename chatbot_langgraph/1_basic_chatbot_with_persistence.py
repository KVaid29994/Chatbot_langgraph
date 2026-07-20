from langgraph.graph import StateGraph, END , START , message
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],message.add_messages]

def chat_node(state: ChatState):
    ## take user query
    message = state['messages']
    ## send tp llm
    response = llm.invoke(message)

    ### store to state
    return {'messages' : [response]}


checkpointer = MemorySaver()
graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

initial_state = {'messages': [HumanMessage(content = 'what is the capital of india')]}

agent = graph.compile(checkpointer=checkpointer)
# print (agent.invoke(initial_state)['messages'][-1].content)


## concept of persistence in langgraph

thread_id= '1'

while True:
    input_user = input('User: ')
    if input_user.strip().lower() in ['exit', 'bye']:
        break
    else:
        config = {
            'configurable' : {'thread_id':thread_id}
        }
        repsonse = agent.invoke({'messages':[HumanMessage(content= input_user)]}, config=config)['messages'][-1].content
        print ("AI :" ,repsonse)

print (agent.get_state(config=config))