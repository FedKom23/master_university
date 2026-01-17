import json
import time
import random
import string
import custom_json


def generate_large_json_data(num_objects=1000):
    data = {}
    for i in range(num_objects):
        key = f"key_{i}"
        if random.choice([True, False]):
            data[key] = random.randint(-1000, 1000)
        else:
            length = random.randint(10, 20)
            data[key] = ''.join(random.choices(string.ascii_letters, k=length))
    return data


def benchmark_loads(json_str, iterations=100):
    start_time = time.time()
    for _ in range(iterations):
        json.loads(json_str)
    json_time = time.time() - start_time
    start_time = time.time()
    for _ in range(iterations):
        custom_json.loads(json_str)
    custom_time = time.time() - start_time

    return json_time, custom_time


def benchmark_dumps(data, iterations=100):
    start_time = time.time()
    for _ in range(iterations):
        json.dumps(data)
    json_time = time.time() - start_time
    start_time = time.time()
    for _ in range(iterations):
        custom_json.dumps(data)
    custom_time = time.time() - start_time

    return json_time, custom_time


def main():
    print("тесты производительности json")
    print("======================================")

    test_data = generate_large_json_data(2000)
    json_str = json.dumps(test_data)

    print(f"размер тестовых данных: {len(json_str)} символов")
    print(f"количество ключей: {len(test_data)}")
    print()

    print("тест loads (парсинг json строки):")
    json_time, custom_time = benchmark_loads(json_str, 1000)
    print(f"стандартный json.loads: {json_time:.4f} сек")
    print(f"кастомный custom_json.loads: {custom_time:.4f} сек")
    print(f"соотношение: {custom_time/json_time:.2f}")
    print()

    print("тест dumps (сериализация в json):")
    json_time, custom_time = benchmark_dumps(test_data, 1000)
    print(f"стандартный json.dumps: {json_time:.4f} сек")
    print(f"кастомный custom_json.dumps: {custom_time:.4f} сек")
    print(f"соотношение: {custom_time/json_time:.2f}")


if __name__ == "__main__":
    main()
