import logging
from pathlib import Path


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(Path(__file__).name)


def important(func):
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        logger.debug(f"\n\nReturn value from {func.__name__}: {result}\n\n")
        return result

    return wrapper


def normalize_tags(item: dict) -> dict:
    tags = item.get("tags", {})
    for key, value in tags.items():
        if isinstance(value, dict) or isinstance(value, list):
            tags[key] = str(value)

    item["tags"] = tags
    return item
