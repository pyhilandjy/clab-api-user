from fastapi import APIRouter, HTTPException, Depends

from app.services.reports import (
    select_wordcloud_data,
    select_sentence_length_data,
    select_insight_data,
    select_cover_data,
    select_pos_ratio_data,
    select_speech_act_data,
    select_list_data,
)

from app.services.users import get_current_user

router = APIRouter()


@router.get("/cover/data/{user_reports_id}", tags=["User_Report"])
def get_cover_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 커버 데이터를 반환합니다.
    """
    return select_cover_data(user_reports_id)


@router.get("/wordcloud/data/{user_reports_id}", tags=["User_Report"])
def get_wordcloud_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 워드클라우드 데이터를 반환합니다.
    """
    return select_wordcloud_data(user_reports_id)


@router.get("/sentence_length/data/{user_reports_id}", tags=["User_Report"])
def get_sentence_length_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 문장 길이 데이터를 반환합니다.
    """
    return select_sentence_length_data(user_reports_id)


@router.get("/pos_ratio/data/{user_reports_id}", tags=["User_Report"])
def get_pos_ratio_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 품사 비율 데이터를 반환합니다.
    """
    return select_pos_ratio_data(user_reports_id)


@router.get("/speech_act/data/{user_reports_id}", tags=["User_Report"])
def get_speech_act_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 발화 행위 데이터를 반환합니다.
    """
    return select_speech_act_data(user_reports_id)


@router.get("/insight/data/{user_reports_id}", tags=["User_Report"])
def get_insight_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 인사이트 데이터를 반환합니다.
    """
    return select_insight_data(user_reports_id)


@router.get("/reports/list/{user_plans_id}", tags=["User_Report"])
def get_user_reports_list(user_plans_id: str):
    try:
        # user_id = current_user.get("sub")
        # if not user_id:
        #     raise HTTPException(status_code=400, detail="Invalid user ID")
        list_data = select_list_data(user_plans_id)
        return list_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
