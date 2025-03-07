from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile

from app.services.audio import (
    create_audio_metadata,
    create_file_name,
    create_file_path,
    insert_audio_metadata,
    upload_to_s3,
    get_record_time,
    get_total_record_time,
    update_user_missions_status,
    update_user_missions_status_for_demo,
)
from app.services.users import get_current_user

router = APIRouter()


# audio_files의
@router.post("/audio", tags=["Audio"])
async def create_upload_file(
    user_missions_id: str,
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    try:
        total_record_time = get_total_record_time(user_missions_id)
        user_id = current_user.get("sub")
        file_path = create_file_path(user_id)
        user_name = current_user.get("user_metadata")["full_name"]
        file_name = create_file_name(user_name)
        record_time = get_record_time(audio)
        # 3분 이상시 status = COMPLETED
        update_user_missions_status(total_record_time, record_time, user_missions_id)
        metadata = create_audio_metadata(
            user_id, file_name, file_path[2:], record_time, user_missions_id
        )
        id = insert_audio_metadata(metadata)
        await upload_to_s3(audio, file_path[2:])
        return id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audio/demo", tags=["Audio"])
async def create_upload_file(
    user_missions_id: str,
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """demo 버전 오디오 파일 업로드 3분->15분 제한"""
    try:
        total_record_time = get_total_record_time(user_missions_id)
        user_id = current_user.get("sub")
        file_path = create_file_path(user_id)
        user_name = current_user.get("user_metadata")["full_name"]
        file_name = create_file_name(user_name)
        record_time = get_record_time(audio)
        # 15분 이상시 status = COMPLETED
        update_user_missions_status_for_demo(
            total_record_time, record_time, user_missions_id
        )
        metadata = create_audio_metadata(
            user_id, file_name, file_path[2:], record_time, user_missions_id
        )
        id = insert_audio_metadata(metadata)
        await upload_to_s3(audio, file_path[2:])
        return id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
