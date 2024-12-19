# import logging
# from datetime import datetime
# from io import BytesIO

# import boto3
# from botocore.exceptions import ClientError, NoCredentialsError
# from fastapi import UploadFile
# from loguru import logger


# from app.config import settings
# from app.db.query import (
#     INSERT_AUDIO_META_DATA,
# )
# from app.db.worker import execute_insert_update_query

# logger = logging.getLogger(__name__)

# session = boto3.Session(
#     aws_access_key_id=settings.aws_access_key_id,
#     aws_secret_access_key=settings.aws_secret_access_key,
# )

# bucket_name = settings.bucket_name

# s3 = session.client("s3")


# def create_file_name(user_name):
#     """파일 이름 생성"""
#     return datetime.now().strftime("%y%m%d%H%M%S") + "_" + user_name


# def create_file_path(user_id):
#     """파일 경로 생성"""
#     return f"./app/audio/{datetime.now().strftime('%y%m%d%H%M%S')}_{user_id}.webm"


# def create_audio_metadata(user_id: str, file_name: str, file_path: str):
#     """오디오 파일 메타데이터 생성"""
#     return {
#         "user_id": user_id,
#         "file_name": file_name,
#         "file_path": file_path,
#     }


# def insert_audio_metadata(metadata: dict):
#     """오디오 파일 메타데이터 db적재"""
#     return execute_insert_update_query(
#         query=INSERT_AUDIO_META_DATA,
#         params=metadata,
#     )


# async def upload_to_s3(audio: UploadFile, file_path):
#     """m4a 파일을 S3에 저장"""
#     try:
#         audio_content = await audio.read()
#         audio_stream = BytesIO(audio_content)

#         # S3에 업로드
#         s3.upload_fileobj(audio_stream, settings.bucket_name, file_path)
#     except NoCredentialsError:
#         return {"error": "Credentials not available"}
#     except ClientError as e:
#         return {"error": str(e)}
#     except Exception as e:
#         return {"error": str(e)}
#     else:
#         logger.info(f"File uploaded to S3: {file_path}")
#         return {"message": "File uploaded successfully"}
