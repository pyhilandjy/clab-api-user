from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile

from app.services.audio import (
    create_audio_metadata,
    create_file_name,
    create_file_path,
    insert_audio_metadata,
    upload_to_s3,
)
from app.services.users import get_user_info_from_token

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = get_user_info_from_token(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/", tags=["Audio"])
async def create_upload_file(
    current_user: dict = Depends(get_current_user),
    audio: UploadFile = File(...),
):
    try:
        user_id = current_user.get("sub")
        file_path = create_file_path(user_id)
        user_name = current_user.get("user_metadata")["full_name"]
        file_name = create_file_name(user_name)
        metadata = create_audio_metadata(user_id, file_name, file_path[2:])
        insert_audio_metadata(metadata)
        await upload_to_s3(audio, file_path[2:])

        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))