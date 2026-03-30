import datetime
import requests
import os
from collections import defaultdict

results = defaultdict(list)

HINTS = {
    "test_dependencies_installed": "Зафиксируй все зависимости через uv, добавь соответствующие файлы в git",
    "test_dockerfile_build_and_run": "В Dockerfile настрой WORKDIR, USER и запуск через uv",
    "test_compose_network": "Настрой отдельные сети: app и db должны быть связаны, extra — нет",
    "test_registry_image": "Собери образ и запушь его в GitLab Registry",
}

SCORES = {
    "test_dependencies_installed": 1.0,
    "test_dockerfile_build_and_run": 1.5,
    "test_compose_network": 1.5,
    "test_registry_image": 1.0,
}


def pytest_runtest_logreport(report):
    if report.when == "call":
        task_name = report.nodeid.split("::")[1].split("[")[0]
        results[task_name].append(report.outcome)


def pytest_sessionfinish(session, exitstatus):
    score = 0.0
    total = 5.0
    failed, passed = [], []
    for task, outcomes in results.items():
        if all(o == "passed" for o in outcomes):
            score += SCORES.get(task)
            passed.append(task)
        else:
            failed.append(task)

    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deadline = os.getenv("HW2_SOFT_DEADLINE", "")
    if deadline and deadline < cur_time:
        score *= 0.5

    indication = "✅" if score == total else ("❌" if score == 0.0 else "⚠️")
    lines = [f"### Автоматическая проверка: {score}/{total} баллов {indication}\n"]
    if passed:
        lines.append("**Выполненные задания:**\n")
        for t in sorted(passed):
            lines.append(f"✅ {t}\n")
    if failed:
        lines.append("**Невыполненные задания:**\n")
        for t in sorted(failed):
            lines.append(f"❌ {t} — {HINTS.get(t)}\n")
    message = "\n".join(lines)
    print(message)

    api_key = os.getenv("GRADER_API_KEY")
    api_url = os.getenv("CI_API_V4_URL")
    project_id = os.getenv("CI_PROJECT_ID")
    mr_iid = os.getenv("CI_MERGE_REQUEST_IID")

    if not all([api_key, api_url, project_id, mr_iid]):
        return

    url = f"{api_url}/projects/{project_id}/merge_requests/{mr_iid}/notes"
    headers = {"PRIVATE-TOKEN": api_key}
    data = {"body": message}
    try:
        requests.post(url, headers=headers, data=data, timeout=10)
    except Exception as e:
        print(f"Ошибка при вызове GitLab API: {e}")
