# LangGraph-FastAPI-Boilerplate

A production-ready boilerplate for building AI agents and workflows using LangGraph.

This template provides a structured foundation for developing LLM-powered applications with:

- **Graph-based Workflows** — Define complex AI pipelines using LangGraph's StateGraph pattern with typed state and runtime context
- **Structured Outputs** — Pydantic schemas for reliable, typed LLM responses
- **Prompt Management** — Organized prompt templates separated from workflow logic
- **Dataset Management** — Utilities for creating and managing LangSmith datasets with deduplication
- **Evaluation Pipelines** — LLM-as-judge evaluations using openevals with results tracked in LangSmith
- **Observability** — Built-in LangSmith tracing for debugging and monitoring
- **Multiple Interfaces** — Serve workflows via FastAPI endpoints or develop interactively in notebooks

## Project Structure

**Core Workflow Components**

| Directory | Purpose |
|-----------|---------|
| `graphs/` | LangGraph workflow definitions using StateGraph pattern |
| `schemas/` | Pydantic models for structured LLM outputs |
| `prompts/` | LLM prompt templates (includes `evals/` for evaluation prompts) |

**LangSmith Integration**

| Directory | Purpose |
|-----------|---------|
| `datasets/` | Dataset creation and management utilities |
| `evals/` | Evaluation pipelines using openevals LLM-as-judge |

**Usage Options**

| Directory | Purpose |
|-----------|---------|
| `app/` | FastAPI application with routers for API serving |
| `notebooks/` | Interactive development and prototyping (includes sample data) |

**Configuration**

| File | Purpose |
|------|---------|
| `settings.py` | Environment variables and model definitions |
| `logger.py` | Logging configuration |

## Prerequisites

- Python 3.11
- [uv](https://github.com/astral-sh/uv) package manager

## Environment Variables

Create a `.env` file with:

```bash
# Required
OPENAI_API_KEY=your-openai-key
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=your-project-name

# Optional (for vector storage)
CHROMA_HOST=api.trychroma.com
CHROMA_TENANT=your-tenant
CHROMA_DATABASE=your-database
CHROMA_TOKEN=your-token

# Optional
LOG_LEVEL=INFO  # DEBUG, WARNING, ERROR
```

## Running the Application

### Local Development

```bash
uv sync
fastapi dev
```

### Docker

```bash
uv sync && docker compose up --watch --build
```

API docs available at: `http://localhost:8000/docs`

## Building Workflows

Workflows are defined in `graphs/` using LangGraph's `StateGraph`. Example pattern from `graphs/candidate_scores.py`:

### 1. Define State and Context Schemas

```python
from langgraph.graph import StateGraph
from typing_extensions import TypedDict

class ContextSchema(TypedDict):
    model_name: str
    prompt: str

class State(TypedDict):
    cv_text: str  # input
    candidate_scores: CandidateScores  # output (Pydantic model)
```

### 2. Create Node Functions

```python
async def get_candidate_scores(state: State, runtime: Runtime[ContextSchema]) -> dict:
    llm = MODELS[runtime.context["model_name"]]
    prompt = runtime.context["prompt"].format(cv_text=state["cv_text"])
    scores = await llm.with_structured_output(CandidateScores).ainvoke(prompt)
    return {"candidate_scores": scores}
```

### 3. Compile the Graph

```python
def compile_candidate_scores():
    graph = StateGraph(state_schema=State, context_schema=ContextSchema)
    graph.add_node("get_candidate_scores", get_candidate_scores)
    graph.add_edge(START, "get_candidate_scores")
    graph.add_edge("get_candidate_scores", END)
    return graph.compile()
```

### 4. Invoke with Runtime Context

```python
result = await graph.ainvoke(
    {"cv_text": cv_text},
    context={"model_name": "gpt-4o", "prompt": PROMPT_TEMPLATE}
)
```

## Creating Datasets

Datasets are managed via LangSmith and stored remotely for use in evaluations. The `datasets/` directory contains scripts for populating datasets from local files.

### How It Works

1. **Source Data** — Place raw data files (e.g., `.txt` files) in `notebooks/data/`
2. **Example Creation** — Each file is converted to a LangSmith `ExampleCreate` with inputs and metadata
3. **Deduplication** — Examples include a metadata `id` field; the utility skips examples that already exist in the dataset
4. **Upload** — New examples are created in LangSmith via the API

### Running Dataset Scripts

```bash
uv run python -m datasets.candidate_cv
```

### Adding New Datasets

Create a new module in `datasets/` following the pattern in `datasets/candidate_cv.py`:

```python
from langsmith.schemas import ExampleCreate
from datasets.utils import create_or_get_dataset, add_new_examples

examples = [
    ExampleCreate(
        inputs={"your_input_field": data},
        metadata={"id": unique_id},  # Required for deduplication
    )
]

ds = create_or_get_dataset("your_dataset_name", CLIENT)
add_new_examples(ds.name, examples, CLIENT)
```

## Running Evaluations

Evaluations run your graph against a LangSmith dataset and score outputs using LLM-as-judge. Results are tracked as experiments in LangSmith for comparison across runs.

### How It Works

1. **Target Function** — Wraps your compiled graph to accept dataset inputs and return outputs
2. **Evaluator** — An LLM-as-judge (via openevals) scores each output against criteria defined in `prompts/evals/`
3. **Experiment** — LangSmith records all inputs, outputs, and scores with metadata for analysis

### Running Evaluation Scripts

```bash
uv run python -m evals.candidate_scores
```

### Adding New Evaluations

Create a new module in `evals/` following the pattern in `evals/candidate_scores.py`:

```python
from langsmith.evaluation import aevaluate
from openevals.llm import create_llm_as_judge

async def target(inputs: dict) -> dict:
    graph = compile_your_graph()
    result = await graph.ainvoke(inputs, context={...})
    return {"result": result}

evaluator = create_llm_as_judge(
    prompt=YOUR_EVAL_PROMPT,
    feedback_key="correctness",
    model="openai:o3-mini",
)

await aevaluate(
    target,
    data=dataset,
    evaluators=[evaluator],
    experiment_prefix="your-experiment",
    metadata={"model": "gpt-4o"},
)
```

## Available Models

Configured in `settings.py`:

| Model | Temperature |
|-------|-------------|
| gpt-3.5-turbo | default |
| gpt-4o-mini | default |
| gpt-4o | 0.0 |
| o3-mini | default |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/docs` | GET | OpenAPI documentation |
| `/healthcheck` | GET | Health check |
| `/candidates/candidate-scores` | POST | Score a CV for education/experience |
| `/vectors/collections` | GET | List ChromaDB collections |

