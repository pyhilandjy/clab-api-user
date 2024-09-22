from datetime import datetime, timedelta
import pytz

from app.db.query import (
    SELECT_PLANS,
    SELECT_USER_PLANS_ID,
    INSERT_USER_PLANS,
    SELECT_PLAN,
    SELECT_MISSION,
    INSERT_USER_MISSION_START_DATE,
    SELECT_USER_MISSION,
    SELECT_USER_MISSION_DETAIL,
)
from app.db.worker import execute_insert_update_query, execute_select_query


def select_plans():
    return execute_select_query(query=SELECT_PLANS)


def select_plans_user(user_id):
    plans_id = execute_select_query(
        query=SELECT_USER_PLANS_ID,
        params={
            "user_id": user_id,
        },
    )
    return execute_select_query(
        query=SELECT_PLAN,
        params={
            "plans_id": plans_id[0].plans_id,
        },
    )


def select_user_missions(user_id):
    return execute_select_query(
        query=SELECT_USER_MISSION,
        params={
            "user_id": user_id,
        },
    )


def select_user_missions_detail(user_id, user_missions_id):
    return execute_select_query(
        query=SELECT_USER_MISSION_DETAIL,
        params={"user_id": user_id, "user_missions_id": user_missions_id},
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


def mission_start_date(start_at, day):
    # 주말을 제외하고 day만큼 더하기
    mission_start_at = start_at
    days_added = 0

    while days_added < day:
        mission_start_at += timedelta(days=1)
        if mission_start_at.weekday() < 5:
            days_added += 1

    # 시간을 9:00으로 설정
    mission_start_at_with_time = datetime.combine(
        mission_start_at, datetime.min.time()
    ).replace(hour=9, minute=0)

    return mission_start_at_with_time


def update_user_plan_mission(user_id, plans_id):
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={
            "plans_id": plans_id,
        },
    )
    day = plan[0].day
    plan_start_at, plan_end_at = plan_date(day)

    execute_insert_update_query(
        query=INSERT_USER_PLANS,
        params={
            "plans_id": plans_id,
            "user_id": user_id,
            "start_at": plan_start_at,
            "end_at": plan_end_at,
        },
    )

    mission = execute_select_query(
        query=SELECT_MISSION,
        params={
            "plans_id": plans_id,
        },
    )

    for i in mission:
        mission_day = i.day - 1
        mission_start_at = mission_start_date(plan_start_at, mission_day)

        execute_insert_update_query(
            query=SELECT_USER_MISSION,
            params={
                "mission_id": i.id,
                "user_id": user_id,
                "mission_start_at": mission_start_at,
                "start_at": mission_start_at,
            },
        )
