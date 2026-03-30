import pytest
from parser import parse_product
import json
import os

ATTRS = ["title", "vendor", "description", "price"]
PORT = 8123


@pytest.mark.parametrize("i", range(1, 6))
def test_product(i, request):
    """Проверяем продукт i (product1..product5)"""
    url = f"http://localhost:{PORT}/domain_headphones/product{i}.html"

    attr_results = {attr: False for attr in ATTRS}

    try:
        parsed = parse_product(url)
    except Exception:
        parsed = {attr: None for attr in ATTRS}

    answers_path = os.path.join(os.path.dirname(__file__), "../answers.json")
    with open(answers_path, "r", encoding="utf-8") as f:
        answers = json.load(f)

    expected = answers.get(f"product{i}", {})

    wrong_attrs = []

    for attr in ATTRS:
        value = parsed.get(attr)
        correct = value == expected.get(attr)
        attr_results[attr] = correct
        if not correct:
            wrong_attrs.append(attr)

    request.node.user_properties.append(("attr_results", attr_results))

    if wrong_attrs:
        pytest.fail(f"{url}: неверные атрибуты: {', '.join(wrong_attrs)}")
