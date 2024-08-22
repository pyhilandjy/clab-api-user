from fastapi import APIRouter, Depends, HTTPException
from app.services.plan import (
    select_plans,
    update_user_plan_mission,
    select_plans_user,
    select_user_missions,
    select_user_missions_detail,
)
from app.services.users import get_current_user

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


@router.post("/user/plans/{plan_id}", tags=["Plan"])
async def post_user_plan(plan_id: str, current_user=Depends(get_current_user)):
    """user_plans, user_missions insert"""
    try:
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        update_user_plan_mission(user_id, plan_id)
        return {"message": "User plan updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/plans", tags=["Plan"])
async def post_user_plan(current_user=Depends(get_current_user)):
    try:
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        user_plan = select_plans_user(user_id)
        return user_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/missions", tags=["Plan"])
async def post_user_plan(current_user=Depends(get_current_user)):
    try:
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        user_mission = select_user_missions(user_id)
        return user_mission
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/missions/{user_missions_id}", tags=["Plan"])
async def post_user_plan(user_missions_id: str, current_user=Depends(get_current_user)):
    try:
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        user_mission = select_user_missions_detail(user_id, user_missions_id)
        return user_mission
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
