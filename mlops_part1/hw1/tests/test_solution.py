import subprocess
import os
import shutil
from pathlib import Path

import pytest

from hw1.solution import (
    cmd_task1_count_files,
    cmd_task2_biggest_files,
    cmd_task3_sort_unique,
    cmd_task4_grep_error,
    cmd_task5_empty_files
)


def run_cmd(cmd, cwd):
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return result.stdout.strip()


@pytest.fixture
def workdir():
    path = Path.cwd() / "hw1" / "workspace"
    path.mkdir()
    yield path
    shutil.rmtree(path)


@pytest.mark.parametrize("files,dirs,expected", [
    (["a.txt", "b.txt", "c.sh"], ["dir1", "dir2"], "3"),
    (["x.py"], [], "1"),
    ([], ["onlydir"], "0"),
])
def test_task1_count_files(workdir, files, dirs, expected):
    for f in files:
        (workdir / f).write_text("dummy")
    for d in dirs:
        (workdir / d).mkdir()

    output = run_cmd(cmd_task1_count_files, workdir)
    assert output == expected


@pytest.mark.parametrize("sizes,expected_top", [
    ({"a": 100, "b": 200, "c": 50}, {"b", "a", "c"}),
    ({"f": 50000, "e": 1000, "d": 20000}, {"f", "d", "e"}),
    ({"aa": 100, "ab": 200, "ac": 300, "ad": 400, "ae": 500, "af": 600}, {"af", "ae", "ad", "ac", "ab"}),
])
def test_task2_biggest_files(workdir, sizes, expected_top):
    for name, size in sizes.items():
        with open(workdir / name, "wb") as f:
            f.write(os.urandom(size))

    output = run_cmd(cmd_task2_biggest_files, workdir)
    files = {os.path.basename(p) for p in output.splitlines()}
    assert files == expected_top


@pytest.mark.parametrize("lines,expected", [
    (["b", "a", "a", "c", "b"], ["a", "b", "c"]),
    (["z", "z", "z"], ["z"]),
    ([], []),
])
def test_task3_sort_unique(workdir, lines, expected):
    (workdir / "input.txt").write_text("\n".join(lines))
    run_cmd(cmd_task3_sort_unique, workdir)
    result = (workdir / "clean.txt").read_text().splitlines() if (workdir / "clean.txt").exists() else []
    assert result == expected


@pytest.mark.parametrize("logs,expected", [
    ({"a.log": "INFO ok\nERROR fail\nERROR fail"}, ["ERROR fail"]),
    ({"b.log": "ERROR crash\nINFO start", "c.log": "ERROR disk"}, ["ERROR crash", "ERROR disk"]),
    ({"x.log": "INFO good\nWARN meh"}, []),
])
def test_task4_grep_error(workdir, logs, expected):
    for fname, text in logs.items():
        (workdir / fname).write_text(text)

    output = run_cmd(cmd_task4_grep_error, workdir)
    result = output.splitlines() if output else []
    assert result == expected


@pytest.mark.parametrize("files,expected", [
    ({"a.txt": "", "b.txt": "hello", "c.sh": ""}, {"a.txt", "c.sh"}),
    ({"x": ""}, {"x"}),
    ({"notempty": "1"}, set()),
])
def test_task5_empty_files(workdir, files, expected):
    for fname, text in files.items():
        (workdir / fname).write_text(text)

    output = run_cmd(cmd_task5_empty_files, workdir)
    result = {os.path.basename(f) for f in output.splitlines()} if output else set()
    assert result == expected
