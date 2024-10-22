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
    SELECT_REPORTS,
    INSERT_REPORTS,
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


def calculate_plan_dates(plan):
    """플랜의 시작일과 종료일을 계산"""
    if plan[0].type == "기간형":
        day = plan[0].day
        return plan_date(day)
    return None, None


def insert_user_plan(user_id, plans_id, plan_start_at, plan_end_at):
    """user_plans 테이블에 플랜 정보를 삽입"""
    execute_insert_update_query(
        query=INSERT_USER_PLANS,
        params={
            "plans_id": plans_id,
            "user_id": user_id,
            "start_at": plan_start_at,
            "end_at": plan_end_at,
        },
    )


def insert_user_missions(user_id, plan_start_at, plan, missions):
    """미션 데이터를 user_missions 테이블에 삽입하고 mission_id와 user_mission_id를 매핑"""
    mission_to_user_mission = {}
    for mission in missions:
        mission_start_at = (
            mission_start_date(plan_start_at, mission.day - 1)
            if plan[0].type == "기간형"
            else None
        )
        user_mission_id = execute_insert_update_query(
            query=INSERT_USER_MISSION_START_DATE,
            params={
                "missions_id": mission.id,
                "user_id": user_id,
                "start_at": mission_start_at,
            },
            return_id=True,
        )
        mission_to_user_mission[str(mission.id)] = str(user_mission_id)
    return mission_to_user_mission


def insert_user_reports(user_id, plan_start_at, plan, reports, mission_to_user_mission):
    """리포트 데이터를 user_reports 테이블에 삽입"""
    date = 0
    for report in reports:
        matched_user_missions = [
            mission_to_user_mission[str(mission_id)]
            for mission_id in report.missions_id
            if str(mission_id) in mission_to_user_mission
        ]

        matched_user_missions_str = "{" + ",".join(matched_user_missions) + "}"
        date += len(report.missions_id)
        # TODO: send_at 발행일자의 명확한 정의가 필요 주말은 제외하는지, 휴일은 제외하는지

        send_at = (
            datetime.combine(
                plan_start_at + timedelta(days=len(report.missions_id) + date),
                datetime.min.time(),
            ).replace(hour=9, minute=0, second=0)
            if plan[0].type == "기간형"
            else None
        )

        execute_insert_update_query(
            query=INSERT_REPORTS,
            params={
                "reports_id": report.id,
                "user_id": user_id,
                "user_missions_id": matched_user_missions_str,
                "send_at": send_at,
            },
        )


def update_user_plan_mission(user_id, plans_id):
    # 플랜 데이터
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={"plans_id": plans_id},
    )

    # 플랜 시작 및 종료일 계산
    plan_start_at, plan_end_at = calculate_plan_dates(plan)

    # user_plans 적재
    insert_user_plan(user_id, plans_id, plan_start_at, plan_end_at)

    # 미션 데이터
    missions = execute_select_query(
        query=SELECT_MISSION,
        params={"plans_id": plans_id},
    )

    # user_missions 적재
    mission_to_user_mission = insert_user_missions(
        user_id, plan_start_at, plan, missions
    )

    # 리포트 데이터
    reports = execute_select_query(
        query=SELECT_REPORTS,
        params={"plans_id": plans_id},
    )

    # user_reports 적재
    insert_user_reports(user_id, plan_start_at, plan, reports, mission_to_user_mission)
