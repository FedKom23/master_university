import datetime
import os
from collections import defaultdict

import requests

results = defaultdict(list)

HINTS = {
    "test_task1_count_files": "Вспомни разницу между файлами и директориями при работе с `ls`,"
                              "также могут помочь команды `grep` и `wc`.",
    "test_task2_biggest_files": "Используй утилиту `du` для получения размера файлов и sort для порядка.",
    "test_task3_sort_unique": "Воспользуйся доп параметрами команды `sort`.",
    "test_task4_grep_error": "Воспользуйся `grep` для фильтрации, `cut` для форматирования, `sort` для уникальности.",
    "test_task5_empty_files": "Поиск пустых файлов возможен с помощью команды `find` и пары ее параметров.",
}


def pytest_runtest_logreport(report):
    if report.when == "call":
        task_name = report.nodeid.split("::")[1].split("[")[0]
        results[task_name].append(report.outcome)


def pytest_sessionfinish(session, exitstatus):
    score = 0
    total = len(results)
    failed_tasks = []
    passed_tasks = []

    for task, outcomes in results.items():
        if all(o == "passed" for o in outcomes):
            score += 1
            passed_tasks.append(task)
        else:
            failed_tasks.append(task)

    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deadline = os.getenv("HW1_SOFT_DEADLINE", "")
    if deadline and deadline < cur_time:
        score *= 0.5

    indication = "✅" if score == total else ("❌" if score == 0 else "⚠️")
    lines = [f"### Автоматическая проверка: {score}/{total} баллов {indication}\n"]

    if passed_tasks:
        lines.append("**Выполненные задания:**\n")
        for t in sorted(passed_tasks):
            lines.append(f"✅ {t}\n")
        lines.append("")

    if failed_tasks:
        lines.append("**Невыполненные задания:**\n")
        for t in sorted(failed_tasks):
            hint = HINTS.get(t, "")
            lines.append(f"❌ {t} — {hint}\n")
        lines.append("")

    message = "\n".join(lines)

    api_key = os.getenv("GRADER_API_KEY")
    api_url = os.getenv("CI_API_V4_URL")
    project_id = os.getenv("CI_PROJECT_ID")
    mr_iid = os.getenv("CI_MERGE_REQUEST_IID")

    print(message)

    if not all([api_key, api_url, project_id, mr_iid]):
        return

    url = f"{api_url}/projects/{project_id}/merge_requests/{mr_iid}/notes"
    headers = {"PRIVATE-TOKEN": api_key}
    data = {"body": message}

    try:
        requests.post(url, headers=headers, data=data, timeout=10)
    except Exception as e:
        print(f"Ошибка при вызове GitLab API: {e}")
