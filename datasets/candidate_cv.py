import dotenv

dotenv.load_dotenv()

from pathlib import Path

from langsmith import Client as LS_Client
from langsmith.schemas import ExampleCreate

from .utils import add_new_examples, create_or_get_dataset

CLIENT = LS_Client()
DATASET_NAME = "candidate_cv"
N_EXAMPLES = 1  # set to None to use all examples


def create_cv_examples():
    examples = []
    for cv_path in Path("./notebooks/data/cv").glob("*.txt"):
        with open(cv_path, "r") as f:
            cv_text = f.read()
        examples.append(
            ExampleCreate(
                inputs={"cv_text": cv_text},
                metadata={
                    "source": "cv",
                    "id": cv_path.stem,  # metadata's id - different to example's id
                },
            )
        )

    return examples


def main():
    examples = create_cv_examples()[:N_EXAMPLES]
    ds = create_or_get_dataset(DATASET_NAME, CLIENT)
    add_new_examples(ds.name, examples, CLIENT)


if __name__ == "__main__":
    main()

# uv run python -m datasets.candidate_cv
