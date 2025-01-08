from fastapi import APIRouter, Depends, HTTPException
from app.services.plan import select_plans, select_plans_id, update_user_plan_mission
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


@router.post("/plans/{plan_id}", tags=["Plan"])
async def post_user_plan(
    plan_id: str, user_children_id: str, current_user=Depends(get_current_user)
):
    """user_plans, user_missions, user_reports insert"""
    try:
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        update_user_plan_mission(user_id, plan_id, user_children_id)
        return {"message": "User plan updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/user/plans", tags=["Plan"])
# async def post_user_plan(current_user=Depends(get_current_user)):
#     try:
#         user_id = current_user.get("sub")
#         if not user_id:
#             raise HTTPException(status_code=400, detail="Invalid user ID")
#         user_plan = select_plans_user(user_id)
#         return user_plan
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/user/missions", tags=["Plan"])
# async def post_user_plan(current_user=Depends(get_current_user)):
#     try:
#         user_id = current_user.get("sub")
#         if not user_id:
#             raise HTTPException(status_code=400, detail="Invalid user ID")
#         user_mission = select_user_missions(user_id)
#         return user_mission
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/user/missions/{user_missions_id}", tags=["Plan"])
# async def post_user_plan(user_missions_id: str, current_user=Depends(get_current_user)):
#     try:
#         user_id = current_user.get("sub")
#         if not user_id:
#             raise HTTPException(status_code=400, detail="Invalid user ID")
#         user_mission = select_user_missions_detail(user_id, user_missions_id)
#         return user_mission
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
