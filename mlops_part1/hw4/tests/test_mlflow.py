import json
import boto3
import os
import tomllib
from botocore.exceptions import ClientError

CONTROL_KEYS = {
    "34": 31563,
    "71": 4616,
    "173": 3953,
    "221": 2368,
    "204": 103,
    "128": 22,
    "93": 4,
    "23": 1,
    "98": 1,
    "132": 1
}


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["HW4_S3_ENDPOINT_URL"],
        aws_access_key_id=os.environ["HW4_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["HW4_AWS_SECRET_ACCESS_KEY"],
    )


def parse_bucket_and_prefix(s3_path: str) -> tuple[str, str]:
    """ 'bucket/prefix' → (bucket, prefix/) """
    parts = s3_path.split("/", 1)
    bucket = parts[0]
    prefix = ""
    if len(parts) > 1 and parts[1]:
        prefix = parts[1].rstrip("/") + "/"
    return bucket, prefix


def check_run(s3, bucket: str, base_prefix: str, run_path: str, experiment_id: str) -> list[str]:
    """Проверяет один run. Если нет ошибок - run валидный."""
    errors = []

    prefix_root = f"{base_prefix}{run_path}"

    # --- classification_metrics.json ---
    metrics_key = f"{prefix_root}artifacts/classification_metrics.json"
    try:
        obj = s3.get_object(Bucket=bucket, Key=metrics_key)
        metrics = json.loads(obj["Body"].read().decode("utf-8"))
    except ClientError:
        errors.append("metrics.json не найден")
        metrics = {}
    except json.JSONDecodeError:
        errors.append("metrics.json некорректен")
        metrics = {}

    required = ["train_accuracy", "test_accuracy", "train_f1_macro", "test_f1_macro"]
    for key in required:
        if key not in metrics:
            errors.append(f"нет метрики {key}")
        elif not (0 <= metrics[key] <= 1):
            errors.append(f"значение {key} вне диапазона 0–1")

    # --- dataset_label_counts.json ---
    label_key = f"{prefix_root}artifacts/dataset_label_counts.json"
    try:
        obj = s3.get_object(Bucket=bucket, Key=label_key)
        labels = json.loads(obj["Body"].read().decode("utf-8"))
        if not isinstance(labels, dict):
            errors.append("dataset_label_counts.json должен быть словарем {label: count}")
        else:
            if len(labels) != 207:
                errors.append(f"train_label_counts.json должен содержать 207 классов, найдено {len(labels)}")

            for k, min_count in CONTROL_KEYS.items():
                count = labels.get(k)
                if count is None:
                    errors.append(f"Отсутствует ключ {k} в train_label_counts.json")
                elif count < min_count:
                    errors.append(f"Ключ {k} содержит {count} объектов, требуется ≥{min_count}")
    except ClientError:
        errors.append("train_label_counts.json не найден")
    except json.JSONDecodeError:
        errors.append("train_label_counts.json некорректен")

    # --- проверка модели в <experiment_id>/models/.../artifacts/MLmodel ---
    models_prefix = f"{base_prefix}{experiment_id}/models/"
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix=models_prefix)
        model_found = any(obj["Key"].endswith("artifacts/MLmodel") for obj in resp.get("Contents", []))
        if not model_found:
            errors.append("Модель не найдена (отсутствует MLmodel в папке models/...)")
    except ClientError:
        errors.append("Ошибка при проверке модели в S3")

    return errors


def check_mlflow_experiment(s3_path: str, experiment_id: str) -> dict:
    """Проверяет MLflow эксперимент в S3"""
    bucket, base_prefix = parse_bucket_and_prefix(s3_path)
    s3 = get_s3_client()
    result = {"success": False, "message": "", "runs_found": 0, "valid_runs": 0, "run_errors": {}}

    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix=f"{base_prefix}{experiment_id}/", Delimiter="/")
        runs = [
            cp["Prefix"].replace(base_prefix, "", 1)
            for cp in resp.get("CommonPrefixes", [])
            if "model" not in cp["Prefix"]
        ]
        result["runs_found"] = len(runs)

        if len(runs) < 3:
            result["message"] = f"Найдено {len(runs)} runs, нужно ≥3"
            return result

        valid_runs = 0
        run_errors = {}
        for run in runs:
            errors = check_run(s3, bucket, base_prefix, run, experiment_id)
            run_id = run.rstrip("/").split("/")[-1]
            if errors:
                run_errors[run_id] = errors
            else:
                valid_runs += 1

        result["valid_runs"] = valid_runs
        result["run_errors"] = run_errors
        result["success"] = valid_runs >= 3
        result["message"] = f"{valid_runs}/{len(runs)} runs валидны"

        return result

    except ClientError as e:
        result["message"] = f"S3 ошибка: {e}"
        return result


def test_mlflow_exp():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    s3_path = cfg["mlflow"][0]["s3_path"]
    exp_id = cfg["mlflow"][0]["experiment_id"]

    assert s3_path and exp_id, "Не задан s3_path или id эксперимента"

    result = check_mlflow_experiment(s3_path, exp_id)

    if result["run_errors"]:
        for run_id, errs in result["run_errors"].items():
            print(f"Run {run_id} ошибки:")
            for e in errs:
                print(f"  - {e}")

    assert result["success"], f"Эксперимент невалиден: {result['message']}"
    assert result["valid_runs"] >= 3, f"Недостаточно валидных runs: {result['valid_runs']}"
