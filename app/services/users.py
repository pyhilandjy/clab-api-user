from typing import Dict, List
from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
import jwt
from supabase import Client, create_client

from app.config import settings

api_key_header = APIKeyHeader(name="authorization", auto_error=False)

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)

JWT_AUDIENCE = "authenticated"


def get_user_info_from_token(token: str) -> str:

    payload = jwt.decode(
        token,
        settings.supabase_jwt_key,
        algorithms=["HS256"],
        audience=JWT_AUDIENCE,
    )
    return payload


async def get_current_user(authorization: str = Security(api_key_header)):
    try:
        token = authorization.split(" ")[1]
        payload = get_user_info_from_token(token)
        return payload
    except Exception as e:
        raise e


async def fetch_user_names(user_ids: List[str]) -> Dict[str, str]:
    """
    Supabase를 통해 user_id에 해당하는 사용자 이름(user_name)을 비동기로 가져옵니다.
    """
    user_data = {}

    for user_id in user_ids:
        try:
            response = supabase.auth.admin.get_user_by_id(user_id)
            user_name = response.user.user_metadata.get("name", "")
            user_data[user_id] = user_name
        except Exception as e:
            user_data[user_id] = ""

    return user_data


def fetch_user_name(user_id: str) -> Dict[str, str]:
    """
    Supabase를 통해 user_id에 해당하는 사용자 이름(user_name)을 비동기로 가져옵니다.
    """
    response = supabase.auth.admin.get_user_by_id(user_id)
    user_name = response.user.user_metadata.get("name", "")

    return user_name
