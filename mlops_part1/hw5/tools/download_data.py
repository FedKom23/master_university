import os
import boto3
from botocore.exceptions import ClientError


def download_from_s3(bucket: str, prefix: str):
    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["HW4_S3_ENDPOINT_URL"],
        aws_access_key_id=os.environ["HW4_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["HW4_AWS_SECRET_ACCESS_KEY"],
    )

    targets = [
        "answers.json",
        "domain_headphones/product3.html",
        "domain_headphones/product4.html",
        "domain_headphones/product5.html",
    ]

    success = 0
    for key in targets:
        s3_key = f"{prefix}/{key}"
        dest = os.path.join(os.getcwd(), key)
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        try:
            s3.head_object(Bucket=bucket, Key=s3_key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print(f"Файл не найден в S3: {s3_key}")
                continue
            else:
                print(f"Ошибка при доступе к S3: {e}")
                continue

        try:
            s3.download_file(bucket, s3_key, dest)
            print(f"Скачан: {dest}")
            success += 1
        except Exception as e:
            print(f"Ошибка при скачивании {key}: {e}")

    print(f"Успешно скачано: {success}/{len(targets)} файлов")


if __name__ == "__main__":
    bucket = os.environ["HW5_S3_BUCKET"]
    prefix = os.environ["HW5_S3_PREFIX"]
    download_from_s3(bucket, prefix)
