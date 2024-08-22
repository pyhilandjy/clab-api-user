from datetime import date

from fastapi import APIRouter, Header, Depends
from pydantic import BaseModel

from app.services.report import (
    get_report,
    get_report_file_path,
    get_report_metadata,
)
from app.services.users import get_current_user

router = APIRouter()


class ReportModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.get("/reports", tags=["Report"])
async def select_report_metadata(current_user=Depends(get_current_user)):
    user_id = current_user.get("sub")
    report_metadata = get_report_metadata(user_id)
    return report_metadata


@router.get("/reports/{report}", tags=["Report"])
async def select_report_pdf(report: str):
    file_path = get_report_file_path(report)
    return get_report(file_path)
