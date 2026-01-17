import weakref
import gc
import time
import functools
import cProfile
import tracemalloc
import pstats
import io
gc.disable()


def profile_deco(fn):
    profiler = cProfile.Profile()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        profiler.enable()
        try:
            return fn(*args, **kwargs)
        finally:
            profiler.disable()
            _, peak = tracemalloc.get_traced_memory()
            memory_dict[fn.__name__] += peak
            tracemalloc.stop()

    def print_stat():
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("tottime")
        ps.print_stats()
        print(s.getvalue())
        print("-------Total_Memory_Stats------\n")
        for key, value in memory_dict.items():
            print(f"{key}: {value} bytes\n")
    wrapper.print_stat = print_stat
    return wrapper


class JustDot:  # pylint: disable=too-few-public-methods
    def __init__(self, x):
        self.x = x


class SlotDot:  # pylint: disable=too-few-public-methods
    __slots__ = ['x']

    def __init__(self, x):
        self.x = x


class WeakrefDot:  # pylint: disable=too-few-public-methods
    def __init__(self, x):
        self.x = weakref.ref(x)


@profile_deco
def create_exmpls(n, class_choice, points=None):
    start_time = time.perf_counter()
    for i in range(n):
        if class_choice == WeakrefDot:
            class_choice(points)
        else:
            class_choice(i)
    return time.perf_counter() - start_time


@profile_deco
def read_exmpls(n, ex):
    start_time = time.perf_counter()
    for _ in range(n):
        if isinstance(ex.x, weakref.ref):
            ex.x()
        else:
            _ = ex.x
    return time.perf_counter() - start_time


N = 20_000_000
memory_dict = {
    "create_exmpls": 0,
    "read_exmpls": 0
}
print(f"N = {N}\n")

result = create_exmpls(N, JustDot)
print(
    f"Функция создания {N} эелементов выполнилась за {result:.4f} "
    f"секунд для класса JustDot"
)

result = create_exmpls(N, SlotDot)
print(
    f"Функция создания {N} эелементов выполнилась за {result:.4f} "
    f"секунд для класса SlotDot"
)

point = JustDot(0)
result = create_exmpls(N, WeakrefDot, point)
print(
    f"Функция создания {N} эелементов выполнилась за {result:.4f} "
    f"секунд для класса WeakrefDot"
)

example = JustDot(0)
result = read_exmpls(N, example)
print(
    f"Функция чтения {N} эелементов выполнилась за {result:.4f} "
    f"секунд для класса JustDot"
)

example = SlotDot(0)
result = read_exmpls(N, example)
print(
    f"Функция чтения {N} эелементов выполнилась за {result:.4f} "
    f"секунд для класса SlotDot"
)

example = WeakrefDot(point)
result = read_exmpls(N, example)
print(
    f"Функция чтения {N} эелементов выполнилась за {result:.4f} "
    f"секунд для класса WeakrefDot"
)

create_exmpls.print_stat()
read_exmpls.print_stat()
