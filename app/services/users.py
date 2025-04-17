from typing import Dict, List
from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
import jwt
from supabase import Client, create_client

from app.config import settings
from app.error_utils import raise_http_500, raise_http_400, raise_http_404, safe_execute
from sentry_sdk import capture_message

api_key_header = APIKeyHeader(name="authorization", auto_error=False)

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)

JWT_AUDIENCE = "authenticated"


def get_user_info_from_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_key,
            algorithms=["HS256"],
            audience=JWT_AUDIENCE,
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise_http_400("Token has expired.")
    except jwt.InvalidTokenError as e:
        raise_http_400("Invalid token.")
    except Exception as e:
        raise_http_500(e, detail="Failed to decode token.")


async def get_current_user(authorization: str = Security(api_key_header)):
    try:
        token = authorization.split(" ")[1]
        payload = get_user_info_from_token(token)
        return payload
    except IndexError:
        raise_http_400("Authorization header is malformed.")
    except Exception as e:
        raise_http_500(e, detail="Failed to get current user.")


async def get_current_user_for_admin(authorization: str = Security(api_key_header)):
    if not authorization:
        return None
    try:
        token = authorization.split(" ")[1]
        payload = get_user_info_from_token(token)
        return payload
    except IndexError:
        raise_http_400("Authorization header is malformed.")
    except Exception as e:
        raise_http_500(e, detail="Failed to get current user.")


async def fetch_user_names(user_ids: List[str]) -> Dict[str, str]:
    """
    Supabase를 통해 user_id에 해당하는 사용자 이름(user_name)을 비동기로 가져옵니다.
    """
    user_data = {}

    for user_id in user_ids:
        try:
            response = safe_execute(
                supabase.auth.admin.get_user_by_id,
                user_id,
                exception_detail=f"Failed to fetch user by ID: {user_id}",
            )
            if not response or not response.user:
                raise_http_404(f"User with ID {user_id} not found.")
            user_name = response.user.user_metadata.get("name") or ""
            user_data[user_id] = user_name
        except Exception as e:
            capture_message(
                f"Failed to fetch user name for ID: {user_id}", level="warning"
            )
            user_data[user_id] = ""

    return user_data


def fetch_user_name(user_id: str) -> Dict[str, str]:
    """
    Supabase를 통해 user_id에 해당하는 사용자 이름(user_name)을 가져옵니다.
    """
    try:
        response = safe_execute(
            supabase.auth.admin.get_user_by_id,
            user_id,
            exception_detail=f"Failed to fetch user by ID: {user_id}",
        )
        if not response or not response.user:
            raise_http_404(f"User with ID {user_id} not found.")
        user_name = response.user.user_metadata.get("name", "")
        return user_name
    except Exception as e:
        raise_http_500(e, detail=f"Error fetching user name for ID: {user_id}")
