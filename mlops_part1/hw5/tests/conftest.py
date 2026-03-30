import os
import threading
import requests
import re
from collections import defaultdict
from http.server import HTTPServer, SimpleHTTPRequestHandler
import pytest
import datetime

PORT = 8123
ATTR_SCORE = 0.25
ATTRS_PER_PRODUCT = 4
TOTAL_MAX_SCORE = 5.0
ATTRS = ["title", "vendor", "description", "price"]

results = defaultdict(dict)


@pytest.fixture(scope="session", autouse=True)
def http_server():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(root)

    server = HTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"HTTP server started at http://localhost:{PORT}")
    yield
    server.shutdown()
    thread.join()
    print("HTTP server stopped")


def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    node = report.nodeid.split("::", 1)[1]
    m = re.search(r"\[(\d+)\]", node)
    if m:
        idx = int(m.group(1))
        test_name = f"product{idx}"
    else:
        test_name = node.split("[")[0]

    detected = {attr: "FAIL" for attr in ATTRS}

    if hasattr(report, "user_properties"):
        for prop, value in report.user_properties:
            if prop == "attr_results":
                detected.update({attr: str(value.get(attr, "FAIL")) for attr in ATTRS})
                break

    log_str = ", ".join(f"{attr}='{detected[attr]}'" for attr in ATTRS)
    print(f"[DEBUG] {test_name}: {log_str}")

    results[test_name] = {
        attr: value == "True" if value in ["True", "False"] else False
        for attr, value in detected.items()
    }


def pytest_sessionfinish(session, exitstatus):
    total_score = 0.0
    lines = []

    for product, attrs in sorted(results.items()):
        correct_count = sum(1 for v in attrs.values() if v)
        score = correct_count * ATTR_SCORE
        total_score += score

        cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        deadline = os.getenv("HW5_SOFT_DEADLINE", "")
        if deadline and deadline < cur_time:
            score *= 0.5

        if correct_count == ATTRS_PER_PRODUCT:
            indication = "✅"
        elif correct_count > 0:
            indication = "⚠️"
        else:
            indication = "❌"

        lines.append(f"{product}: {correct_count}/{ATTRS_PER_PRODUCT} атрибутов верны {indication}")
        maxlen = max(len(a) for a in attrs)
        for attr, ok in attrs.items():
            mark = "✅" if ok else "❌"
            lines.append(f"├─ {attr.ljust(maxlen)} : {mark}")
        lines.append("└────────────────────────────")

    indication = "✅" if total_score == TOTAL_MAX_SCORE else ("❌" if total_score == 0.0 else "⚠️")
    result_message = f"### Автоматическая проверка: {total_score:.2f}/{TOTAL_MAX_SCORE:.2f} баллов {indication}\n"
    message = result_message + "```\n" + "\n".join(lines) + "\n```"

    print(message)

    api_key = os.getenv("GRADER_API_KEY")
    api_url = os.getenv("CI_API_V4_URL")
    project_id = os.getenv("CI_PROJECT_ID")
    mr_iid = os.getenv("CI_MERGE_REQUEST_IID")

    if all([api_key, api_url, project_id, mr_iid]):
        url = f"{api_url}/projects/{project_id}/merge_requests/{mr_iid}/notes"
        headers = {"PRIVATE-TOKEN": api_key}
        data = {"body": message}
        try:
            requests.post(url, headers=headers, data=data, timeout=10)
        except Exception as e:
            print(f"Ошибка при вызове GitLab API: {e}")
