import logging
from datetime import datetime
from io import BytesIO
import io
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import UploadFile
from loguru import logger
from pydub import AudioSegment

from app.config import settings
from app.db.query import (
    INSERT_AUDIO_META_DATA,
    SELECT_AUDIO_RECORD_TIME,
    UPDATE_USER_MISSION_STATUS,
    GET_USER_REPORTS_ID_BY_USER_MISSIONS_ID,
    CHECK_ALL_USER_MISSIONS_STATUS,
    UPDATE_USER_REPORT_STATUS,
)
from app.db.worker import execute_insert_update_query, execute_select_query
from app.error_utils import raise_http_500, safe_execute

logger = logging.getLogger(__name__)

session = boto3.Session(
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

bucket_name = settings.bucket_name

s3 = session.client("s3")


def create_file_name(user_name):
    """파일 이름 생성"""
    return datetime.now().strftime("%y%m%d%H%M%S") + "_" + user_name


def create_file_path(user_id):
    """파일 경로 생성"""
    return f"./app/audio/{datetime.now().strftime('%y%m%d%H%M%S')}_{user_id}.webm"


def create_audio_metadata(
    user_id: str,
    file_name: str,
    file_path: str,
    record_time: int,
    user_missions_id: str,
):
    """오디오 파일 메타데이터 생성"""
    return {
        "user_id": user_id,
        "file_name": file_name,
        "file_path": file_path,
        "record_time": record_time,
        "user_missions_id": user_missions_id,
    }


def insert_audio_metadata(metadata: dict):
    """오디오 파일 메타데이터 db적재"""
    return safe_execute(
        execute_insert_update_query,
        query=INSERT_AUDIO_META_DATA,
        params=metadata,
        return_id=True,
        exception_detail="Failed to insert audio metadata",
    )


async def upload_to_s3(audio: UploadFile, file_path):
    """m4a 파일을 S3에 저장"""
    try:
        audio.file.seek(0)
        audio_content = await audio.read()
        audio_stream = BytesIO(audio_content)

        s3.upload_fileobj(audio_stream, bucket_name, file_path)

    except NoCredentialsError as e:
        raise_http_500(e, detail="AWS credentials not available")

    except ClientError as e:
        raise_http_500(e, detail=f"ClientError during S3 upload: {str(e)}")

    except Exception as e:
        raise_http_500(e, detail="Unexpected error during S3 upload")

    else:
        logger.info(f"S3 업로드 성공: {file_path}")
        return {"message": "File uploaded successfully"}


def get_record_time(audio):
    """M4A 파일의 재생 시간을 가져옴"""
    try:
        audio_data = audio.file.read()
        audio.file.seek(0)
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
        duration_seconds = len(audio_segment) / 1000.0
        return round(duration_seconds)
    except Exception as e:
        raise_http_500(e, detail="Failed to get record time")


def get_total_record_time(user_missions_id: str):
    return (
        safe_execute(
            execute_select_query,
            query=SELECT_AUDIO_RECORD_TIME,
            params={"user_missions_id": user_missions_id},
            exception_detail="Failed to get total record time",
        )[0].total_record_time
        or 0
    )


def update_user_missions_status(total_record_time, record_time, user_missions_id):
    updated_time = total_record_time + record_time

    if updated_time >= 180:
        status = "COMPLETED"
    elif 0 < updated_time < 180:
        status = "IN_PROGRESS"
    else:
        return

    safe_execute(
        execute_insert_update_query,
        query=UPDATE_USER_MISSION_STATUS,
        params={"id": user_missions_id, "status": status},
        exception_detail="Failed to update user mission status",
    )

    if status == "COMPLETED":
        user_reports_id = safe_execute(
            execute_select_query,
            query=GET_USER_REPORTS_ID_BY_USER_MISSIONS_ID,
            params={"user_missions_id": user_missions_id},
            exception_detail="Failed to get user reports ID",
        )
        user_reports_id = str(user_reports_id[0].user_reports_id)

        if user_reports_id:
            all_missions_status = safe_execute(
                execute_select_query,
                query=CHECK_ALL_USER_MISSIONS_STATUS,
                params={"user_reports_id": user_reports_id},
                exception_detail="Failed to check all user missions status",
            )
            if all(status["status"] == "COMPLETED" for status in all_missions_status):
                safe_execute(
                    execute_insert_update_query,
                    query=UPDATE_USER_REPORT_STATUS,
                    params={"id": user_reports_id, "status": "IN_PROGRESS"},
                    exception_detail="Failed to update user report status",
                )


def update_user_missions_status_for_demo(
    total_record_time, record_time, user_missions_id
):
    updated_time = total_record_time + record_time

    if updated_time >= 900:
        status = "COMPLETED"
    elif 0 < updated_time < 900:
        status = "IN_PROGRESS"
    else:
        return

    safe_execute(
        execute_insert_update_query,
        query=UPDATE_USER_MISSION_STATUS,
        params={"id": user_missions_id, "status": status},
        exception_detail="Failed to update user mission status for demo",
    )

    if status == "COMPLETED":
        user_reports_id = safe_execute(
            execute_select_query,
            query=GET_USER_REPORTS_ID_BY_USER_MISSIONS_ID,
            params={"user_missions_id": user_missions_id},
            exception_detail="Failed to get user reports ID for demo",
        )
        user_reports_id = str(user_reports_id[0].user_reports_id)

        if user_reports_id:
            all_missions_status = safe_execute(
                execute_select_query,
                query=CHECK_ALL_USER_MISSIONS_STATUS,
                params={"user_reports_id": user_reports_id},
                exception_detail="Failed to check all user missions status for demo",
            )
            if all(status["status"] == "COMPLETED" for status in all_missions_status):
                safe_execute(
                    execute_insert_update_query,
                    query=UPDATE_USER_REPORT_STATUS,
                    params={"id": user_reports_id, "status": "IN_PROGRESS"},
                    exception_detail="Failed to update user report status for demo",
                )
