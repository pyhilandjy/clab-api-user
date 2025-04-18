from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.plan import (
    select_plans,
    select_plans_id,
    insert_user_plan_mission,
    select_missions_reports_list,
    select_user_used_plans,
    patch_user_reports_is_read,
    user_missions_data,
    select_plans_demo,
    find_owner_id_user_plans,
    find_owner_id_user_reports,
    find_owner_id_user_missions,
)
from app.services.users import (
    get_current_user,
    fetch_user_name,
    get_current_user_for_admin,
)

router = APIRouter()


@router.get("/plans", tags=["Plan"])
async def get_plans():
    """
    plan이 INPROGRESS인 데이터를 가져오는 엔드포인트
    """
    return select_plans()


@router.get("/plans/demo", tags=["Plan"])
async def get_plans_demo():
    """
    데모 플랜 데이터를 가져오는 엔드포인트
    """
    return select_plans_demo()


@router.get("/plans/{plans_id}", tags=["Plan"])
async def get_plan(plans_id: str, current_user=Depends(get_current_user)):
    """
    request Param으로 planId를 넘겨받아, response로 상세정보(플랜 설명, 추천월령, 기간정보, 미션목록(미션 설명포함))를 조회하는 api
    """
    user_id = current_user.get("sub")
    user_name = fetch_user_name(user_id)
    return select_plans_id(plans_id, user_name)


class PlanPostRequest(BaseModel):
    plan_id: str
    user_children_id: str


@router.post("/plans", tags=["Plan"])
async def post_user_plan(
    payload: PlanPostRequest, current_user=Depends(get_current_user)
):
    """user_plans, user_missions, user_reports insert"""
    user_id = current_user.get("sub")
    payload = payload.model_dump()
    plan_id = payload.get("plan_id")
    user_children_id = payload.get("user_children_id")
    return insert_user_plan_mission(user_id, plan_id, user_children_id)


@router.get("/contents/list/{user_plans_id}", tags=["Plan"])
async def get_missions_reports_list(
    user_plans_id: str, current_user=Depends(get_current_user)
):
    """missions, reports 의 id, type, record_time, summary, status, sort_order 반환하는 함수."""
    user_id = current_user.get("sub")
    owner_id = find_owner_id_user_plans(user_plans_id)
    if user_id == str(owner_id):
        return select_missions_reports_list(user_plans_id)


@router.get("/user/plans", tags=["Plan"])
async def get_user_used_plans(current_user=Depends(get_current_user)):
    user_id = current_user.get("sub")
    return select_user_used_plans(user_id)


@router.patch("/reports/is-read/{user_reports_id}", tags=["Plan"])
async def patch_is_read(
    user_reports_id, current_user=Depends(get_current_user_for_admin)
):
    """유저가 report를 읽었을 경우 user_reports의 is_read값 변경, 다음 Missions status IN_PROGRESS"""
    if not current_user:
        return {"skipped": True}
    current_user_id = current_user.get("sub")
    owner_id = find_owner_id_user_reports(user_reports_id)
    if current_user_id == str(owner_id):
        patch_user_reports_is_read(user_reports_id)


@router.get("/missions/{user_missions_id}", tags=["Plan"])
async def get_audio_file(
    user_missions_id: str, current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    user_name = current_user.get("user_metadata")["full_name"]
    owner_id = find_owner_id_user_missions(user_missions_id)
    if user_id != str(owner_id):
        return user_missions_data(user_missions_id)
