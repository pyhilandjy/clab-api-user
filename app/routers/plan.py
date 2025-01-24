from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.plan import (
    select_plans,
    select_plans_id,
    update_user_plan_mission,
    select_missions_reports_list,
    select_user_used_plans,
    patch_user_reports_is_read,
    patch_user_reports_is_read,
)
from app.services.users import get_current_user, fetch_user_name

router = APIRouter()


@router.get("/plans", tags=["Plan"])
async def get_plans():
    """
    plan 데이터를 가져오는 엔드포인트
    """
    plan = select_plans()
    if not plan:
        raise HTTPException(status_code=404, detail="Files not found")
    return plan


@router.get("/plans/{plans_id}", tags=["Plan"])
async def get_plan(plans_id: str, current_user=Depends(get_current_user)):
    """
    request Param으로 planId를 넘겨받아, response로 상세정보(플랜 설명, 추천월령, 기간정보, 미션목록(미션 설명포함))를 조회하는 api
    """
    user_id = current_user.get("sub")
    user_name = fetch_user_name(user_id)
    plan_detail = select_plans_id(plans_id, user_name)
    return plan_detail


class PlanPostRequest(BaseModel):
    plan_id: str
    user_children_id: str


@router.post("/plans", tags=["Plan"])
async def post_user_plan(
    payload: PlanPostRequest, current_user=Depends(get_current_user)
):
    """user_plans, user_missions, user_reports insert"""
    try:
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        payload = payload.model_dump()
        plan_id = payload.get("plan_id")
        user_children_id = payload.get("user_children_id")
        user_plans_id = update_user_plan_mission(user_id, plan_id, user_children_id)
        return user_plans_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contents/list/{user_plans_id}", tags=["Plan"])
async def get_missions_reports_list(user_plans_id: str):
    """missions, reports 의 id, type, record_time, summary, status, sort_order 반환하는 함수."""
    return select_missions_reports_list(user_plans_id)


@router.get("/user/plans", tags=["Plan"])
async def get_user_used_plans(current_user=Depends(get_current_user)):
    user_id = current_user.get("sub")
    return select_user_used_plans(user_id)


@router.patch("/reports/is-read/{user_reports_id}", tags=["Plan"])
async def patch_is_read(user_reports_id):
    """유저가 report를 읽었을 경우 user_reports의 is_read값 변경, 다음 Missions status IN_PROGRESS"""
    patch_user_reports_is_read(user_reports_id)
