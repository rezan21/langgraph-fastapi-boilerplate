import dotenv
import asyncio

dotenv.load_dotenv()

from langsmith import Client as LS_Client
from langsmith.evaluation import aevaluate
from openevals.llm import create_llm_as_judge

from graphs.candidate_scores import compile_candidate_scores
from prompts.candidate_scores import CANDIDATE_SCORES_PROMPT
from prompts.evals import CORRECTNESS_EVAL_PROMPT

ls_client = LS_Client()
dataset = ls_client.read_dataset(dataset_name="candidate_cv")


async def run_candidate_cv_eval():
    prompt = CANDIDATE_SCORES_PROMPT
    METADATA = {
        "function_name": __name__,
        "model": "gpt-4o",
        "eval-model": "o3-mini",
    }

    async def target(inputs: dict) -> dict:
        candidate_cv_graph = compile_candidate_scores()
        result = await candidate_cv_graph.ainvoke(
            {"cv_text": inputs["cv_text"]}, context={"model_name": METADATA["model"], "prompt": prompt}
        )
        result = result["candidate_scores"].model_dump()
        return {"result": result}

    correctness_evaluator = create_llm_as_judge(
        prompt=CORRECTNESS_EVAL_PROMPT,
        feedback_key="correctness",
        model=f"openai:{METADATA['eval-model']}",
        continuous=True,
        choices=[n / 10 for n in range(0, 11, 1)],
    )

    await aevaluate(
        target,
        data=dataset,
        evaluators=[correctness_evaluator],
        experiment_prefix="dev",
        metadata=METADATA,
    )


if __name__ == "__main__":
    asyncio.run(run_candidate_cv_eval())

# uv run python -m evals.candidate_scores
