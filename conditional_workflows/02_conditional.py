from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")


# ==========================
# Structured Output Schema
# ==========================

class SentiSchema(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="Sentiment of the review"
    )

    confidence: float = Field(
        description="Confidence score between 0 and 1"
    )


structured_llm = model.with_structured_output(SentiSchema)


# ==========================
# Graph State
# ==========================

class SentimentState(TypedDict):
    review: str
    sentiment: str
    confidence: float
    label: str
    reply: str
    summary: str


# ==========================
# Nodes
# ==========================

def sentiment_analysis(state: SentimentState):

    prompt = f"""
    Analyze the sentiment of the following review.

    Review:
    {state['review']}

    Determine:
    - sentiment (positive, neutral, negative)
    - confidence score between 0 and 1
    """

    result = structured_llm.invoke(prompt)

    return {
        "sentiment": result.sentiment,
        "confidence": result.confidence
    }


def add_label(state: SentimentState):

    labels = {
        "positive": "😊 Positive",
        "neutral": "😐 Neutral",
        "negative": "😞 Negative"
    }

    return {
        "label": labels[state["sentiment"]]
    }


def check_sentiment(state: SentimentState):

    if state["sentiment"] == "positive":
        return "positive_reply"

    elif state["sentiment"] == "neutral":
        return "neutral_reply"

    else:
        return "negative_reply"


def positive_reply(state: SentimentState):

    prompt = f"""
    Respond to this review warmly.

    Thank the customer.

    Review:
    {state['review']}
    """

    result = model.invoke(prompt)

    return {
        "reply": result.content
    }


def neutral_reply(state: SentimentState):

    prompt = f"""
    Reply politely and professionally.

    Review:
    {state['review']}
    """

    result = model.invoke(prompt)

    return {
        "reply": result.content
    }


def negative_reply(state: SentimentState):

    prompt = f"""
    Reply empathetically.

    Apologize if needed.

    Address the customer's concerns.

    Review:
    {state['review']}
    """

    result = model.invoke(prompt)

    return {
        "reply": result.content
    }


def summary(state: SentimentState):

    text = f"""
Review      : {state['review']}

Sentiment   : {state['label']}

Confidence  : {state['confidence']:.2f}

Reply
------------------------------------------------
{state['reply']}
"""

    return {
        "summary": text
    }


# ==========================
# Graph
# ==========================

graph = StateGraph(SentimentState)

graph.add_node("sentiment_analysis", sentiment_analysis)

graph.add_node("add_label", add_label)

graph.add_node("positive_reply", positive_reply)

graph.add_node("neutral_reply", neutral_reply)

graph.add_node("negative_reply", negative_reply)

graph.add_node("summary", summary)


graph.add_edge(START, "sentiment_analysis")

graph.add_edge("sentiment_analysis", "add_label")


graph.add_conditional_edges(
    "add_label",
    check_sentiment,
    {
        "positive_reply": "positive_reply",
        "neutral_reply": "neutral_reply",
        "negative_reply": "negative_reply"
    }
)

graph.add_edge("positive_reply", "summary")

graph.add_edge("neutral_reply", "summary")

graph.add_edge("negative_reply", "summary")

graph.add_edge("summary", END)


agent = graph.compile()


# ==========================
# Test
# ==========================

result = agent.invoke(
    {
        "review": "The product is awesome and delivery was very fast."
    }
)

print(result)

print("\n")
print(result["summary"])