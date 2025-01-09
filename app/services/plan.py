from datetime import datetime, timedelta
import pytz

from app.db.query import (
    SELECT_PLANS,
    SELECT_PLAN,
    INSERT_USER_PLANS,
    SELECT_PLAN_MISSION,
    SELECT_MISSION,
    INSERT_USER_MISSION_START_DATE,
    SELECT_REPORTS,
    INSERT_REPORTS,
    UPDATE_REPORTS_ID_STATUS,
)
from app.db.worker import execute_insert_update_query, execute_select_query


def select_plans():
    return execute_select_query(query=SELECT_PLANS)


def select_plans_id(plans_id, user_name):
    # request Param으로 planId를 넘겨받아, response로 상세정보(플랜 설명, 추천월령, 기간정보, 미션목록(미션 설명포함))를 조회하는 api
    datas = execute_select_query(
        query=SELECT_PLAN_MISSION,
        params={
            "plans_id": plans_id,
        },
    )
    data = [dict(data) for data in datas]
    for row in data:
        if "schedule" in row and "{이름}" in row["schedule"]:
            row["schedule"] = row["schedule"].replace("{이름}", f"{user_name}")

    return format_plan_data(data)


def format_plan_data(data):
    # 첫 번째 row에서 plans 정보를 추출
    plan = {
        "description": data[0]["description"],
        "start_age_month": data[0]["start_age_month"],
        "end_age_month": data[0]["end_age_month"],
        "schedule": data[0]["schedule"],
    }

    # missions 이미지로 대체
    missions = [
        {"title": data["title"], "summation": data["summation"]} for data in data
    ]

    # 결과 반환
    return {"plan": plan, "missions": missions}


# def select_plans_user(user_id):
#     plans_id = execute_select_query(
#         query=SELECT_USER_PLANS_ID,
#         params={
#             "user_id": user_id,
#         },
#     )
#     return execute_select_query(
#         query=SELECT_PLAN,
#         params={
#             "plans_id": plans_id[0].plans_id,
#         },
#     )


# def select_user_missions(user_id):
#     return execute_select_query(
#         query=SELECT_USER_MISSION,
#         params={
#             "user_id": user_id,
#         },
#     )


# def select_user_missions_detail(user_id, user_missions_id):
#     return execute_select_query(
#         query=SELECT_USER_MISSION_DETAIL,
#         params={"user_id": user_id, "user_missions_id": user_missions_id},
#     )


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


def insert_user_plan(user_id, plans_id, plan_start_at, plan_end_at, user_children_id):
    """user_plans 테이블에 플랜 정보를 삽입"""
    return execute_insert_update_query(
        query=INSERT_USER_PLANS,
        params={
            "plans_id": plans_id,
            "user_id": user_id,
            "start_at": plan_start_at,
            "end_at": plan_end_at,
            "user_children_id": user_children_id,
        },
        return_id=True,
    )


def insert_user_missions(user_id, plan_start_at, plan, missions, user_plans_id):
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
                "user_plans_id": user_plans_id,
            },
            return_id=True,
        )
        mission_to_user_mission[str(mission.id)] = str(user_mission_id)
    return mission_to_user_mission


def insert_user_reports(user_id, reports, user_plans_id):
    """리포트 데이터를 user_reports 테이블에 삽입하고 매핑된 딕셔너리 반환"""
    user_reports_id = {}
    for report in reports:
        user_report_id = execute_insert_update_query(
            query=INSERT_REPORTS,
            params={
                "reports_id": str(report.id),
                "user_id": user_id,
                "user_plans_id": user_plans_id,
            },
            return_id=True,
        )

        user_reports_id[str(report.id)] = str(user_report_id)

    return user_reports_id


# def insert_user_reports(user_id, plan_start_at, plan, reports, mission_to_user_mission):
#     """리포트 데이터를 user_reports 테이블에 삽입"""
#     date = 0
#     for report in reports:
#         matched_user_missions = [
#             mission_to_user_mission[str(mission_id)]
#             for mission_id in report.missions_id
#             if str(mission_id) in mission_to_user_mission
#         ]

#         matched_user_missions_str = "{" + ",".join(matched_user_missions) + "}"
#         date += len(report.missions_id)

#         send_at = (
#             datetime.combine(
#                 plan_start_at + timedelta(days=len(report.missions_id) + date),
#                 datetime.min.time(),
#             ).replace(hour=9, minute=0, second=0)
#             if plan[0].type == "기간형"
#             else None
#         )

#         execute_insert_update_query(
#             query=INSERT_REPORTS,
#             params={
#                 "reports_id": report.id,
#                 "user_id": user_id,
#                 "user_missions_id": matched_user_missions_str,
#                 "send_at": send_at,
#             },
#         )


def update_user_plan_mission(user_id, plans_id, user_children_id):
    # 플랜 데이터
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={"plans_id": plans_id},
    )

    # 플랜 시작 및 종료일 계산 달성형일 경우 null
    plan_start_at, plan_end_at = calculate_plan_dates(plan)

    # user_plans 적재
    user_plans_id = insert_user_plan(
        user_id, plans_id, plan_start_at, plan_end_at, user_children_id
    )
    user_plans_id = str(user_plans_id)
    # 미션 데이터
    missions = execute_select_query(
        query=SELECT_MISSION,
        params={"plans_id": plans_id},
    )

    # user_missions 적재 후 missions_id: user_missions_id반환
    mission_id_user_mission_id = insert_user_missions(
        user_id, plan_start_at, plan, missions, user_plans_id
    )

    # 리포트 데이터
    reports = execute_select_query(
        query=SELECT_REPORTS,
        params={"plans_id": plans_id},
    )

    # 적재 후 reports_id : user_reports_id로 반환
    reports_id_user_reports_id = insert_user_reports(user_id, reports, user_plans_id)
    # user_missions_id: user_reports_id 매핑
    user_mission_report_mapping = generate_user_mission_report_mapping(
        mission_id_user_mission_id, reports_id_user_reports_id, missions
    )
    update_user_missions_with_reports(user_mission_report_mapping)


def generate_user_mission_report_mapping(
    mission_id_user_mission_id, reports_id_user_reports_id, missions
):
    user_mission_report_mapping = {}

    # reports_id별로 missions 그룹화
    reports_grouped = {}
    for mission in missions:
        reports_id = str(mission["reports_id"])
        if reports_id not in reports_grouped:
            reports_grouped[reports_id] = []
        reports_grouped[reports_id].append(mission)

    # 각 그룹의 day 합 계산
    group_day_sums = {
        reports_id: sum(mission["day"] for mission in missions_list)
        for reports_id, missions_list in reports_grouped.items()
    }

    # 가장 낮은 day 합을 가진 reports_id 찾기
    lowest_day_sum_reports_id = min(group_day_sums, key=group_day_sums.get)

    # 상태 설정
    for reports_id, missions_list in reports_grouped.items():
        status = (
            "ON_PROGRESS" if reports_id == lowest_day_sum_reports_id else "NOT_STARTED"
        )
        for mission in missions_list:
            missions_id = str(mission["id"])
            user_missions_id = mission_id_user_mission_id.get(missions_id)
            user_reports_id = reports_id_user_reports_id.get(reports_id)

            if user_missions_id and user_reports_id:
                user_mission_report_mapping[user_missions_id] = {
                    "user_reports_id": user_reports_id,
                    "status": status,
                }

    return user_mission_report_mapping


def update_user_missions_with_reports(mapping):
    """
    user_missions 테이블의 user_reports_id와 status 필드를 업데이트하는 함수.

    :param mapping: dict, {user_missions_id: {"user_reports_id": str, "status": str}}
    """
    for user_missions_id, data in mapping.items():
        user_reports_id = data["user_reports_id"]  # user_reports_id 추출
        status = data["status"]  # status 추출

        execute_insert_update_query(
            query=UPDATE_REPORTS_ID_STATUS,
            params={
                "user_missions_id": user_missions_id,
                "user_reports_id": user_reports_id,
                "status": status,
            },
        )
