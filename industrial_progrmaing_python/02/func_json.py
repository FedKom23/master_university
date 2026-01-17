import json
from typing import Callable, List, Optional


def process_json(
    json_string: str,
    keys_required: Optional[List[str]] = None,
    search_tokens: Optional[List[str]] = None,
    callback_func: Optional[Callable[[str, str], None]] = None,
) -> None:
    json_dict = json.loads(json_string)
    for key, value in json_dict.items():
        if keys_required is None or key not in keys_required:
            continue
        if search_tokens is None or callback_func is None:
            continue

        words = value.split()
        for word in words:
            for token in search_tokens:
                if word.lower() == token.lower():
                    callback_func(key, word)


# например:
JSON_STR = '{"key1": "Word1 word2", "key2": "word2 word3"}'
REQUIRED_KEYS = ["key1", "KEY2"]
TOKENS = ["WORD1", "word2"]

process_json(JSON_STR, REQUIRED_KEYS, TOKENS,
             lambda key, token: f"{key=}, {token=}")

# выведет:
# key="key1", token="WORD1"
# key="key1", token="word2"
