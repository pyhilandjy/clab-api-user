from fastapi import APIRouter, Depends, File, Header, HTTPException
from app.services.plan import select_plans, update_user_plan
from app.services.users import get_current_user

router = APIRouter()


@router.get("/plans/", tags=["Plan"])
async def get_plans():
    """
    plan 데이터를 가져오는 엔드포인트
    """
    file_ids = select_plans()
    if not file_ids:
        raise HTTPException(status_code=404, detail="Files not found")
    return file_ids


@router.post("/plans/user/{plan_id}", tags=["Audio"])
async def post_user_plan(plan_id: str, current_user=Depends(get_current_user)):
    try:
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        update_user_plan(user_id, plan_id)
        return {"message": "User plan updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
