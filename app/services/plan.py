from datetime import datetime, timedelta
import pytz

from app.db.query import SELECT_PLANS, SELECT_PLANS_USER, UPDATE_USER_PLAN, SELECT_PLAN
from app.db.worker import execute_insert_update_query, execute_select_query


def select_plans():
    return execute_select_query(query=SELECT_PLANS)


def select_plans_user(user_id):
    return execute_select_query(
        query=SELECT_PLANS_USER,
        params={
            "user_id": user_id,
        },
    )


def plan_date(day: int):
    KST = pytz.timezone("Asia/Seoul")
    today = datetime.now(KST).date()

    # 오늘이 월요일이 아닌 경우 다음 주 월요일 설정
    if today.weekday() != 0:
        days_until_next_monday = (7 - today.weekday()) % 7
        start_at = today + timedelta(days=days_until_next_monday)
    else:
        start_at = today

    # 주말을 제외하고 day만큼 더하기
    end_at = start_at
    days_added = 0

    while days_added < day:
        end_at += timedelta(days=1)
        if end_at.weekday() < 5:
            days_added += 1

    return start_at, end_at


def update_user_plan(user_id, plan_id):
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={
            "plan_id": plan_id,
        },
    )
    day = plan[day]
    start_at, end_at = plan_date(day)
    execute_insert_update_query(
        query=UPDATE_USER_PLAN,
        params={
            "plan_id": plan_id,
            "user_id": user_id,
            "start_at": start_at,
            "end_at": end_at,
        },
    )
