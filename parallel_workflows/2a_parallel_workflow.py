from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict, Annotated
import operator
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatOpenAI(model='gpt-4o-mini')

class Evaluation_Schema(BaseModel):
    feedback: str = Field(description="Detailed feedback for essay")
    score: int = Field(description="score out of ten", ge=0, le=10)

structured_model = llm.with_structured_output(Evaluation_Schema)

essay = '''
ROLE OF INDIA IN AI

India is emerging as a global hub in Artificial Intelligence, blending innovation with scale. The country is investing heavily in AI research, fostering startups, and integrating AI into governance, healthcare, and education. With initiatives like Digital India and partnerships with global tech leaders, India aims to leverage AI for inclusive growth. Its vast talent pool and expanding digital infrastructure position it as a key player in shaping the future of AI worldwide.
'''

class UPSCState(TypedDict):
    essay: str
    clarity_of_thought: str
    depth_of_analysis: str
    language_feedback: str
    overall_feedback: str
    indivdual_score: Annotated[list[int], operator.add]
    final_score: float


### ✨ Clarity of Thought
def clarity_of_thought(state: UPSCState) -> UPSCState:
    essay = state['essay']
    prompt1 = f'''1. "Assess whether the essay presents India's role in AI in a clear, logical, and easy-to-follow manner."
    2. "Evaluate if the ideas are well-organized, coherent, and free from ambiguity."
    3. "Judge how effectively the essay communicates its central message without unnecessary repetition or confusion."
    Essay: {essay}'''
    result = structured_model.invoke(prompt1)
    return {"clarity_of_thought": result.feedback, "indivdual_score": [result.score]}


### 📚 Depth of Analysis
def depth_of_analysis(state: UPSCState) -> UPSCState:
    essay = state['essay']
    prompt2 = f'''1. "Examine whether the essay goes beyond surface-level description to provide meaningful insights into India's AI initiatives."
    2. "Evaluate if the essay includes examples, context, or implications that demonstrate deeper understanding of India's AI role."
    3. "Judge how thoroughly the essay explores India's strengths, challenges, and global positioning in AI."
    Essay: {essay}'''
    result = structured_model.invoke(prompt2)
    return {"depth_of_analysis": result.feedback, "indivdual_score": [result.score]}


### 🖋️ Language Feedback
def language_feedback(state: UPSCState) -> UPSCState:
    essay = state['essay']
    prompt3 = f'''1. "Assess the quality of grammar, vocabulary, and sentence structure used in the essay."
    2. "Evaluate whether the language is formal, precise, and appropriate for an academic context like UPSC."
    3. "Judge how effectively the essay uses concise phrasing and avoids redundancy while maintaining readability."
    Essay: {essay}'''
    result = structured_model.invoke(prompt3)
    return {"language_feedback": result.feedback, "indivdual_score": [result.score]}


### 🧮 Final Aggregation
def final_evaluation(state: UPSCState) -> UPSCState:
    scores = state['indivdual_score']
    final_score = sum(scores) / len(scores)

    overall_feedback = f'''Clarity of Thought: {state['clarity_of_thought']}

Depth of Analysis: {state['depth_of_analysis']}

Language Feedback: {state['language_feedback']}'''

    return {"overall_feedback": overall_feedback, "final_score": final_score}


graph = StateGraph(UPSCState)

graph.add_node("clarity_of_thought", clarity_of_thought)
graph.add_node("depth_of_analysis", depth_of_analysis)
graph.add_node("language_feedback", language_feedback)
graph.add_node("final_evaluation", final_evaluation)

# Fan out from START to all three parallel evaluators
graph.add_edge(START, "clarity_of_thought")
graph.add_edge(START, "depth_of_analysis")
graph.add_edge(START, "language_feedback")

# Fan in to final_evaluation
graph.add_edge("clarity_of_thought", "final_evaluation")
graph.add_edge("depth_of_analysis", "final_evaluation")
graph.add_edge("language_feedback", "final_evaluation")

graph.add_edge("final_evaluation", END)

agent = graph.compile()

result = agent.invoke({'essay': essay})
print(result)