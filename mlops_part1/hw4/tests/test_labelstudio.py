import xml.etree.ElementTree as ET
import pytest
import boto3
import json
import os
import tomllib


@pytest.fixture
def xml_root():
    file_path = "labeling_interface.xml"
    tree = ET.parse(file_path)
    return tree.getroot()


def test_labeling_interface(xml_root):
    errors = []

    # Название
    field = xml_root.find(".//Text[@name='product_name']")
    if field is None:
        errors.append("Не найдено поле Название (product_name)")

    # Описание
    field = xml_root.find(".//Text[@name='product_description']")
    if field is None:
        errors.append("Не найдено поле Описание (product_description)")

    # Бренд
    field = xml_root.find(".//Text[@name='vendor']")
    if field is None:
        errors.append("Не найдено поле Бренд (vendor)")

    # Цена
    field = xml_root.find(".//Number[@name='price']")
    if field is None:
        errors.append("Не найдено числовое поле Цена (price)")
    else:
        if field.attrib.get('required') != 'true':
            errors.append("Поле Цена должно быть обязательным (required=\"true\")")
        if field.attrib.get('min') != '0':
            errors.append("Поле Цена должно иметь min=\"0\"")
        if field.attrib.get('step') != '0.01':
            errors.append("Поле Цена должно иметь step=\"0.01\"")

    # Изображение
    field = xml_root.find(".//Image[@name='product_image']")
    if field is None:
        errors.append("Не найдено поле Изображение (product_image)")
    else:
        if field.attrib.get('maxWidth') != '400px':
            errors.append("Изображение должно иметь maxWidth=\"400px\"")

    assert not errors, "Ошибки в XML:\n" + "\n".join(errors)


def parse_bucket_and_prefix(s3_path: str) -> tuple[str, str]:
    """ 'bucket/prefix' → (bucket, prefix/) """
    parts = s3_path.split("/", 1)
    bucket = parts[0]
    prefix = ""
    if len(parts) > 1 and parts[1]:
        prefix = parts[1].rstrip("/") + "/"
    return bucket, prefix


def test_s3_labelstudio():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    s3_path = cfg["label_studio"][0]["s3_path"]

    assert s3_path, "Не задан путь s3_path для labelstudio"

    bucket_name, prefix = parse_bucket_and_prefix(s3_path)

    s3_client = boto3.client(
        "s3",
        endpoint_url=os.environ["HW4_S3_ENDPOINT_URL"],
        aws_access_key_id=os.environ["HW4_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["HW4_AWS_SECRET_ACCESS_KEY"],
    )

    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if "Contents" not in response:
        pytest.fail(f"Бакет {bucket_name} с префиксом {prefix} пустой или не найден.")

    files = [obj["Key"] for obj in response["Contents"]]
    print(f"Все найденные файлы: {files}")

    json_files = []
    for key in files:
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        try:
            content = obj["Body"].read().decode("utf-8")
            json.loads(content)
            json_files.append(key)
        except Exception:
            continue

    assert len(json_files) >= 5, f"Найдено только {len(json_files)} JSON-файлов с разметкой, нужно ≥ 5"
