from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)
llm_generate = ChatOpenAI()

class EvaluationSchema(BaseModel):
    approved: Literal["yes", "no"]
    feedback: str


evaluator = llm.with_structured_output(EvaluationSchema)


class ContentState(TypedDict, total=False):
    topic: str
    post: str
    approved: Literal["yes", "no"]
    improvement_feedback: str
    iteration: int
    max_iteration: int


def generate_post(state: ContentState):

    prompt = f"""
You are an expert social media creator.

Topic:
{state['topic']}

Write an engaging post containing:

1. Hook
2. Main content
3. Key takeaway
4. Call to action

Style:
- Concise
- Attention-grabbing
- Suitable for Instagram or LinkedIn
"""

    response = llm_generate.invoke(prompt)

    return {
        "post": response.content
    }


def evaluate_post(state: ContentState):

    prompt = f"""
Evaluate this social media post.

POST:
{state['post']}

Criteria:
- Hook quality
- Engagement
- Clarity
- Readability
- CTA effectiveness

Current iteration:
{state['iteration']}/{state['max_iteration']}

Return:
approved = yes/no
feedback = actionable suggestions
"""

    result = evaluator.invoke(prompt)

    return {
        "approved": result.approved,
        "improvement_feedback": result.feedback
    }


def optimise_post(state: ContentState):

    prompt = f"""
Improve this social media post.

Topic:
{state['topic']}

Current Post:
{state['post']}

Reviewer Feedback:
{state['improvement_feedback']}

Rewrite the entire post addressing all feedback.

Keep:
- strong hook
- engaging tone
- concise structure
- compelling CTA
"""

    response = llm.invoke(prompt)

    return {
        "post": response.content,
        "iteration": state["iteration"] + 1
    }


def route(state: ContentState):

    if state["approved"] == "yes":
        return END

    if state["iteration"] >= state["max_iteration"]:
        return END

    return "optimise_post"


builder = StateGraph(ContentState)

builder.add_node("generate_post", generate_post)
builder.add_node("evaluate_post", evaluate_post)
builder.add_node("optimise_post", optimise_post)

builder.add_edge(START, "generate_post")
builder.add_edge("generate_post", "evaluate_post")

builder.add_conditional_edges(
    "evaluate_post",
    route
)

builder.add_edge(
    "optimise_post",
    "evaluate_post"
)

agent = builder.compile()

for event in agent.stream(
    {
        "topic": "Indian Railways",
        "iteration": 0,
        "max_iteration": 3
    }
):

    print(event)