"""Task 2 module."""
import re
from typing import List, Union
from io import TextIOWrapper


def file_generator(
        file_or_name: Union[str, TextIOWrapper],
        words_for_search: List[str],
        stop_words: List[str],
):
    stop_words = [s.lower() for s in stop_words]
    words_for_search = [w.lower() for w in words_for_search]

    if isinstance(file_or_name, str):
        with open(file_or_name, "r", encoding="utf-8") as file:
            yield from _process_file(file, words_for_search, stop_words)
    else:
        yield from _process_file(file_or_name, words_for_search, stop_words)


def _process_file(file, words_for_search, stop_words):
    for line in file:
        text = line.lower().strip()
        words = re.findall(r'\b\w+\b', text)
        for stop_word in stop_words:
            if stop_word in words:
                break
        else:
            for word in words_for_search:
                if word in words:
                    yield line
                    break
