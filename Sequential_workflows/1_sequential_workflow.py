from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI()
from typing import TypedDict

class BMIState(TypedDict):
    weight_kg : float
    height : float
    bmi : float
    category : str


def calculate_BMI(state: BMIState):
    height_m = state['height'] / 100
    bmi_1 = state['weight_kg'] / (height_m ** 2)
    state['bmi'] = bmi_1
    if bmi_1 < 15:
        state['category'] = "Underweight"
    elif 15<= bmi_1 <30:
        state['category'] = "fit"
    else:
        state['category'] = "Over weight"
    return state



# define your graph
graph = StateGraph(BMIState)

## add nodes to your graph
graph.add_node('calculate_BMI', calculate_BMI)


## add aedges to your graph
graph.add_edge(START, 'calculate_BMI')
graph.add_edge('calculate_BMI', END)



agent = graph.compile()

result = agent.invoke({"weight_kg": 88, "height": 172})
print (f' the BMI of the person is {result['bmi']} ,they are {result['category']}')