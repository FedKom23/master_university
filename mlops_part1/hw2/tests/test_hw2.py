import os
import socket
import subprocess
import time
import requests
import pytest


def run_cmd(cmd, cwd=None, check=True):
    res = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{res.stderr}")
    return res.stdout.strip()


@pytest.fixture(scope="session")
def test_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
        os.environ["TEST_PORT"] = str(port)
        return port


@pytest.mark.dependency()
def test_dependencies_installed():
    with open(".python-version") as f:
        assert f.read().strip() == "3.12"

    out = run_cmd("/usr/local/bin/uv pip list").lower()
    for dep in ["flask", "psycopg2-binary", "requests", "pandas"]:
        assert dep in out


@pytest.mark.dependency(depends=["test_dependencies_installed"])
def test_dockerfile_build_and_run(test_port):
    with open("Dockerfile", "r") as f:
        first_line = f.readline().strip()
        assert first_line == "FROM ghcr.io/astral-sh/uv:python3.12-bookworm"

    run_cmd("docker build -t hw2:student .")
    cid = run_cmd(f"docker run --rm -d -p {test_port}:9998 hw2:student")
    try:
        time.sleep(3)
        r = requests.get(f"http://127.0.0.1:{test_port}/health")
        assert r.status_code == 200

        whoami = run_cmd(f"docker exec {cid} whoami")
        assert whoami == "appuser"

        pwd = run_cmd(f"docker exec {cid} pwd")
        assert pwd == "/app"

        out = run_cmd(f"docker exec {cid} /usr/local/bin/uv pip list").lower()
        for dep in ["flask", "psycopg2-binary", "requests", "pandas"]:
            assert dep in out
    finally:
        run_cmd(f"docker stop {cid}", check=False)


@pytest.mark.dependency(depends=["test_dockerfile_build_and_run"])
def test_compose_network(test_port):
    try:
        run_cmd("docker compose up -d")
        time.sleep(5)
        r = requests.get(f"http://127.0.0.1:{test_port}/health")
        assert r.status_code == 200

        out = run_cmd("docker compose exec app /usr/local/bin/uv pip list").lower()
        for dep in ["flask", "psycopg2-binary", "requests", "pandas"]:
            assert dep in out

        r = requests.get(f"http://127.0.0.1:{test_port}/db-check")
        assert r.status_code == 200
        try:
            run_cmd("docker compose exec extra ping -c1 db")
        except RuntimeError as err:
            err = str(err)
            assert "Name or service not known" in err or "unreachable" in err or "bad address" in err
    finally:
        run_cmd("docker compose down -v")


@pytest.mark.dependency(depends=["test_dockerfile_build_and_run"])
def test_registry_image():
    project_path = os.getenv("CI_PROJECT_PATH", f"production-ml-spring-2026/homeworks/{os.getcwd().split('/')[-2]}")
    image = f"registry.gitlab.v-efimov.tech/{project_path}/hw2:latest"
    out = run_cmd(f"docker manifest inspect {image}", check=False)
    assert out.strip() != "", f"Образ {image} не найден в registry"
