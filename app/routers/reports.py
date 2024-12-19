from typing import List, Dict
from fastapi import APIRouter

from pydantic import BaseModel

from app.services.reports import (
    select_wordcloud_data,
    select_sentence_length_data,
    select_insight_data,
    select_cover_data,
    select_pos_ratio_data,
    select_speech_act_data,
)

router = APIRouter()


@router.get("/cover/data", tags=["User_Report"])
def get_cover_data(user_reports_id):
    return select_cover_data(user_reports_id)


@router.get("/wordcloud/data", tags=["User_Report"])
def get_wordcloud_data(user_reports_id):
    return select_wordcloud_data(user_reports_id)


@router.get("/sentence_length/data", tags=["User_Report"])
def get_sentence_length_data(user_reports_id):
    return select_sentence_length_data(user_reports_id)


@router.get("/pos_ratio/data", tags=["User_Report"])
def get_pos_ratio_data(user_reports_id):
    return select_pos_ratio_data(user_reports_id)


@router.get("/speech_act/data", tags=["User_Report"])
def get_speech_act_data(user_reports_id):
    return select_speech_act_data(user_reports_id)


@router.get("/insight/data", tags=["User_Report"])
def get_insight_data(user_reports_id):
    return select_insight_data(user_reports_id)
