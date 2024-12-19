# from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile

# from app.services.audio_mvp import (
#     create_audio_metadata,
#     create_file_name,
#     create_file_path,
#     insert_audio_metadata,
#     upload_to_s3,
# )
# from app.services.users import get_current_user

# router = APIRouter()


# @router.post("", tags=["Audio"])
# async def create_upload_file(
#     current_user: dict = Depends(get_current_user),
#     audio: UploadFile = File(...),
# ):
#     try:
#         user_id = current_user.get("sub")
#         file_path = create_file_path(user_id)
#         user_name = current_user.get("user_metadata")["full_name"]
#         file_name = create_file_name(user_name)
#         metadata = create_audio_metadata(user_id, file_name, file_path[2:])
#         insert_audio_metadata(metadata)
#         await upload_to_s3(audio, file_path[2:])

#         return {"message": "success"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # 상황 태그 database 추가, api 추가
# @router.post("/situation/", tags=["Audio"])
# async def create_audio_situation(situation: str):
#     pass
