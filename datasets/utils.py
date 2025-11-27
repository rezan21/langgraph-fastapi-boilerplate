from logger import get_logger

logger = get_logger(__name__)


def create_or_get_dataset(dataset_name, client):
    try:
        return client.create_dataset(dataset_name=dataset_name)
    except Exception as warning:
        logger.warning(warning)
        return client.read_dataset(dataset_name=dataset_name)


def add_new_examples(dataset_name, new_examples, client):
    assert new_examples and new_examples[0].metadata["id"], (
        "must be a non-empty list of examples with metadata's id field available"
    )
    logger.debug(f"{len(new_examples)=} (original)")

    # get existing examples metadata ids
    existing_ids = set(ex.metadata.get("id") for ex in client.list_examples(dataset_name=dataset_name))
    logger.debug(f"{len(existing_ids)=}")

    # filter out examples that already exist based on metadata's id
    new_examples = list(
        filter(None, [ex if ex.metadata.get("id") not in existing_ids else None for ex in new_examples])
    )
    logger.debug(f"{len(new_examples)=} (new only)")

    # create examples if there are any new ones
    if new_examples:
        res = client.create_examples(dataset_name=dataset_name, examples=new_examples)
        return res
    logger.warning("no new examples were added")
