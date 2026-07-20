from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
import math


class QuadState(TypedDict):
    a: int
    b: int
    c: int

    equation: str
    discriminant: float
    result: str


def show_equation(state: QuadState):
    eq = f"{state['a']}x² + {state['b']}x + {state['c']} = 0"
    return {"equation": eq}


def calculate_disc(state: QuadState):
    d = (state["b"] ** 2) - (4 * state["a"] * state["c"])
    return {"discriminant": d}


def real_roots(state: QuadState):
    a = state["a"]
    b = state["b"]
    d = state["discriminant"]

    x1 = (-b + math.sqrt(d)) / (2 * a)
    x2 = (-b - math.sqrt(d)) / (2 * a)

    return {
        "result": (
            f"Two distinct real roots\n"
            f"x₁ = {x1:.2f}\n"
            f"x₂ = {x2:.2f}"
        )
    }


def repeated_roots(state: QuadState):
    a = state["a"]
    b = state["b"]

    x = -b / (2 * a)

    return {
        "result": (
            f"Two equal real roots\n"
            f"x = {x:.2f}"
        )
    }


def no_real_roots(state: QuadState):
    a = state["a"]
    b = state["b"]
    d = state["discriminant"]

    real = -b / (2 * a)
    imag = math.sqrt(-d) / (2 * a)

    return {
        "result": (
            f"Complex roots\n"
            f"x₁ = {real:.2f} + {imag:.2f}i\n"
            f"x₂ = {real:.2f} - {imag:.2f}i"
        )
    }


def check_conditions(
    state: QuadState,
) -> Literal["real_roots", "repeated_roots", "no_real_roots"]:

    d = state["discriminant"]

    if d > 0:
        return "real_roots"
    elif d == 0:
        return "repeated_roots"   
    else:
        return "no_real_roots"


graph = StateGraph(QuadState)

graph.add_node("show_equation", show_equation)
graph.add_node("calculate_disc", calculate_disc)
graph.add_node("real_roots", real_roots)
graph.add_node("repeated_roots", repeated_roots)
graph.add_node("no_real_roots", no_real_roots)

graph.add_edge(START, "show_equation")
graph.add_edge("show_equation", "calculate_disc")

graph.add_conditional_edges(
    "calculate_disc",
    check_conditions
)

graph.add_edge("real_roots", END)
graph.add_edge("repeated_roots", END)
graph.add_edge("no_real_roots", END)

agent = graph.compile()

result = agent.invoke({
    "a": 2,
    "b": 2,
    "c": 4
})

print(result)