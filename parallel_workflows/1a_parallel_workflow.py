# simple parallel workflow

## input --> runs, balls, six and 4, calculate strike rate , runs in boundary %

from langgraph.graph import StateGraph, START,END
from langchain_openai import ChatOpenAI
from typing import TypedDict

class RunState(TypedDict):
    runs :int
    fours : int
    six : int
    balls : int
    strikerate : float
    run_bound_percent : float
    summary : str

def strike_rate(state: RunState):
    runs = state['runs']
    balls = state['balls']
    strikerate = (runs/balls)*100
    return {"strikerate": round(strikerate,2)}

def run_bound(state: RunState):
    runs = state['runs']
    boundary_runs = state['fours']*4 + state['six']*6
    run_bound_percent = (boundary_runs / runs) * 100
    return { "run_bound_percent": round(run_bound_percent,2)}


def summary_card(state: RunState):

    summary = (
        f"Runs: {state['runs']}, "
        f"SR: {state['strikerate']:.2f}, "
        f"Boundary %: {state['run_bound_percent']:.2f}"
    )

    return {"summary": summary}


graph = StateGraph(RunState)

graph.add_node("strike_rate",strike_rate)
graph.add_node("run_bound",run_bound)
graph.add_node("summary",summary_card)

graph.add_edge(START, "strike_rate")
graph.add_edge(START, "run_bound")
graph.add_edge("run_bound", "summary")
graph.add_edge("strike_rate", "summary")
graph.add_edge("summary", END)

agent = graph.compile()

dict1 = { "runs" : 120,
    "fours" : 5,
    "six" : 6,
    "balls" : 44}
result = agent.invoke(dict1)
print(result)