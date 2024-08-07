import io
import boto3
from fastapi import Response

from app.config import settings
from app.db.query import (
    SELECT_REPORT_FILE_PATH,
    SELECT_REPORT_METADATA,
)
from app.db.worker import execute_select_query

session = boto3.Session(
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

bucket_name = settings.bucket_name

s3 = session.client("s3")


def get_report_metadata(user_id):
    report_metadata = execute_select_query(
        query=SELECT_REPORT_METADATA, params={"user_id": user_id}
    )
    return report_metadata


def get_report_file_path(report: str) -> str:
    result = execute_select_query(query=SELECT_REPORT_FILE_PATH, params={"id": report})
    if isinstance(result, list) and len(result) > 0 and "file_path" in result[0]:
        return result[0]["file_path"]
    else:
        print("e")


def get_report(file_path: str):
    try:
        # S3에서 PDF 파일 불러오기
        pdf_file = s3.get_object(Bucket=bucket_name, Key=file_path)
        pdf_content = pdf_file["Body"].read()
        file_name = file_path.split("/")[-1]

        # PDF 내용을 BytesIO 객체에 쓰기
        buffer = io.BytesIO(pdf_content)

        headers = {"Content-Disposition": f"inline; filename={file_name}"}

        # BytesIO 객체의 시작 위치를 0으로 되돌립니다.
        buffer.seek(0)

        # PDF 파일을 Response로 반환
        return Response(
            content=buffer.read(), headers=headers, media_type="application/pdf"
        )
    except Exception as e:
        raise e
