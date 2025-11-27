from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

from prompts.candidate_scores import CANDIDATE_SCORES_PROMPT
from schemas.candidate_scores import CandidateScores
from settings import MODELS


class ContextSchema(TypedDict):
    model_name: str
    prompt: str


class State(TypedDict):
    cv_text: str  # input
    candidate_scores: CandidateScores


# node
async def get_candidate_scores(state: State, runtime: Runtime[ContextSchema]) -> dict:
    """Extract candidate scores using structured output"""
    llm = MODELS[runtime.context["model_name"]]
    prompt = runtime.context["prompt"].format(cv_text=state["cv_text"])
    scores = await llm.with_structured_output(CandidateScores).ainvoke(prompt)
    return {"candidate_scores": scores}


def compile_candidate_scores():
    """Compile the candidate scores graph"""
    graph = StateGraph(state_schema=State, context_schema=ContextSchema)
    graph.add_node("get_candidate_scores", get_candidate_scores)
    graph.add_edge(START, "get_candidate_scores")
    graph.add_edge("get_candidate_scores", END)
    candidate_scores_graph = graph.compile()
    return candidate_scores_graph


async def invoke_candidate_scores(cv_text: str):
    """Invoke the candidate scores graph"""
    candidate_scores_graph = compile_candidate_scores()
    prompt = CANDIDATE_SCORES_PROMPT
    METADATA = {
        "function_name": __name__,
        "model": "gpt-4o",
    }

    res = await candidate_scores_graph.ainvoke(
        {"cv_text": cv_text},
        context={"model_name": METADATA["model"], "prompt": prompt},
    )
    return res["candidate_scores"]
