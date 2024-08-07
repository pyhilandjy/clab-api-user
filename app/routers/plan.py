from fastapi import APIRouter, HTTPException

from app.services.plan import select_plans, select_mission

router = APIRouter()
