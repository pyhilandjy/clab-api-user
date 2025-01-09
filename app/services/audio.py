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
    user_id: str, file_name: str, file_path: str, record_time: int
):
    """오디오 파일 메타데이터 생성"""
    return {
        "user_id": user_id,
        "file_name": file_name,
        "file_path": file_path,
        "record_time": record_time,
    }


def insert_audio_metadata(metadata: dict):
    """오디오 파일 메타데이터 db적재"""
    return execute_insert_update_query(
        query=INSERT_AUDIO_META_DATA,
        params=metadata,
        return_id=True,
    )


async def upload_to_s3(audio: UploadFile, file_path):
    """m4a 파일을 S3에 저장"""
    try:
        audio_content = await audio.read()
        audio_stream = BytesIO(audio_content)

        # S3에 업로드
        s3.upload_fileobj(audio_stream, settings.bucket_name, file_path)
    except NoCredentialsError:
        return {"error": "Credentials not available"}
    except ClientError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
    else:
        logger.info(f"File uploaded to S3: {file_path}")
        return {"message": "File uploaded successfully"}


def get_record_time(audio):
    """M4A 파일의 재생 시간을 가져옴"""
    try:
        audio_data = audio.file.read()
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
        duration_seconds = len(audio_segment) / 1000.0
        return round(duration_seconds)
    except Exception as e:
        logger.error(f"Error getting record time: {e}")
        raise Exception("Failed to get record time")


def get_total_record_time(user_missions_id: str):
    total_record_time = execute_select_query(
        query=SELECT_AUDIO_RECORD_TIME, params={"user_missions_id": user_missions_id}
    )
    return total_record_time[0].total_record_time


# 마지막 미션이 완료가 된 시점에서는 user_reports.status도 COMPLETED로 수정해야함 완료
# 테스트를 해봐야하는데.. 하기가 힘드네
def update_user_missions_status(total_record_time, record_time, user_missions_id):
    updated_time = total_record_time + record_time

    if updated_time >= 180:
        status = "COMPLETED"
    elif 0 < updated_time < 180:
        status = "IN_PROGRESS"
    else:
        return

    execute_insert_update_query(
        query=UPDATE_USER_MISSION_STATUS,
        params={"id": user_missions_id, "status": status},
    )

    if status == "COMPLETED":
        user_reports_id = execute_select_query(
            query=GET_USER_REPORTS_ID_BY_USER_MISSIONS_ID,
            params={"user_missions_id": user_missions_id},
        ).get("user_reports_id")

        if user_reports_id:
            all_missions_status = execute_select_query(
                query=CHECK_ALL_USER_MISSIONS_STATUS,
                params={"user_reports_id": user_reports_id},
            )
            if all(status["status"] == "COMPLETED" for status in all_missions_status):
                execute_insert_update_query(
                    query=UPDATE_USER_REPORT_STATUS,
                    params={"id": user_reports_id, "status": "ONPROGRESS"},
                )
