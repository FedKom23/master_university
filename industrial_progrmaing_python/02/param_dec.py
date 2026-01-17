from functools import wraps
from typing import List, Optional


def retry_deco(num_retyr: Optional[int] = None,
               list_ex: Optional[List[Exception]] = None):
    def inner_deco1(fn):
        @wraps(fn)
        def inner_deco2(*args, **kwargs):
            retr = num_retyr if num_retyr is not None else 1
            for attempt in range(1, retr + 1):
                try:
                    result = fn(*args, **kwargs)
                    print(f"run {fn.__name__} with args = {args}, "
                          f"kwargs = {kwargs}, attempt = {attempt}, "
                          f"result = {result}")
                    return result
                except Exception as ex:  # pylint: disable=broad-except
                    if list_ex and type(ex) in list_ex:
                        print(f"run {fn.__name__} with args = {args}, "
                              f"kwargs = {kwargs}, attempt = {attempt}, "
                              f"exception = {type(ex).__name__}")
                        return None
                    print(f"run {fn.__name__} with args = {args}, "
                          f"kwargs = {kwargs}, attempt = {attempt}, "
                          f"exception = {type(ex).__name__}")
            return None
        return inner_deco2
    return inner_deco1


@retry_deco(3)
def add(a, b):
    return a + b


add(4, 2)
# run "add" with positional args = (4, 2), attempt = 1, result = 6

add(4, b=3)
# run "add" with positional args = (4,), keyword kwargs = {"b": 3},
# attempt = 1, result = 7


@retry_deco(3)
def check_str(value=None):
    if value is None:
        raise ValueError()

    return isinstance(value, str)


check_str(value="123")
# run "check_str" with keyword kwargs = {"value": "123"},
# attempt = 1, result = True

check_str(value=1)
# run "check_str" with keyword kwargs = {"value": 1},
# attempt = 1, result = False

check_str(value=None)
# run "check_str" with keyword kwargs = {"value": None},
# attempt = 1, exception = ValueError
# run "check_str" with keyword kwargs = {"value": None},
# attempt = 2, exception = ValueError
# run "check_str" with keyword kwargs = {"value": None},
# attempt = 3, exception = ValueError


@retry_deco(2, [ValueError])
def check_int(value=None):
    if value is None:
        raise ValueError()

    return isinstance(value, int)


check_int(value=1)
# run "check_int" with keyword kwargs = {"value": 1},
# attempt = 1, result = True

check_int(value=None)
# run "check_int" with keyword kwargs = {"value": None},
# attempt = 1, exception = ValueError # нет перезапуска
