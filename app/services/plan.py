from datetime import datetime, timedelta
import pytz
from app.config import settings
from supabase import create_client

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
    SELECT_MISSION_REPORT_LIST,
    SELECT_USER_USED_PLANS,
    UPDATE_USER_REPORTS_IS_READ,
    USER_REPORTS_ORDER,
    FIND_NEXT_REPORTS_ID,
    UPDATE_NEXT_MISSIONS_STATUS,
    CHECK_USER_REPORTS_IS_READ,
    SELECT_CHILDREN_IMAGE_PATH,
    GET_USER_MISSIONS_DATA,
    FIND_USER_PLANS_ID,
    UPDATE_USER_PLANS_STATUS,
    SELECT_PLANS_DEMO,
)
from app.db.worker import execute_insert_update_query, execute_select_query

supabase = create_client(settings.supabase_url, settings.supabase_service_key)


def select_plans():
    results = execute_select_query(
        query=SELECT_PLANS,
    )
    if results:
        plans = []
        image_fields = ["thumbnail_image_id"]

        for result in results:
            plan = dict(result)
            for field in image_fields:
                try:
                    if plan.get(field):
                        plan[f"{field}_url"] = supabase.storage.from_(
                            "plan-images"
                        ).get_public_url(plan[field])
                    else:
                        plan[f"{field}_url"] = None
                except Exception:
                    plan[f"{field}_url"] = None
                if field in plan:
                    del plan[field]
            plans.append(plan)
        return plans
    return None


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
    if data:
        plan = dict(data[0])
        image_fields = [
            "description_image_id",
            "schedule_image_id",
            "thumbnail_image_id",
        ]

        for field in image_fields:
            try:
                if plan.get(field):
                    plan[f"{field}_url"] = supabase.storage.from_(
                        "plan-images"
                    ).get_public_url(plan[field])
                else:
                    plan[f"{field}_url"] = None
            except Exception as e:
                plan[f"{field}_url"] = None
            if field in plan:
                del plan[field]
        return plan
    return None
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
    missions = [{"title": data["title"], "summary": data["summary"]} for data in data]

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


def insert_user_plan_mission(user_id, plans_id, user_children_id):
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
    user_plans_id = {"user_plans_id": user_plans_id}
    return user_plans_id


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

    # 각 그룹의 day 최소값 계산
    group_day_mins = {
        reports_id: min(mission["day"] for mission in missions_list)
        for reports_id, missions_list in reports_grouped.items()
    }

    # day 최소값 기준으로 정렬하여 순위(order) 부여
    sorted_reports = sorted(group_day_mins.items(), key=lambda x: x[1])
    report_orders = {
        reports_id: index + 1 for index, (reports_id, _) in enumerate(sorted_reports)
    }

    # 상태 설정 및 order 추가
    lowest_day_min_reports_id = sorted_reports[0][
        0
    ]  # 가장 낮은 day 최소값의 reports_id
    for reports_id, missions_list in reports_grouped.items():
        status = (
            "IN_PROGRESS" if reports_id == lowest_day_min_reports_id else "NOT_STARTED"
        )
        report_order = report_orders[reports_id]  # order 값 가져오기
        for mission in missions_list:
            missions_id = str(mission["id"])
            user_missions_id = mission_id_user_mission_id.get(missions_id)
            user_reports_id = reports_id_user_reports_id.get(reports_id)

            if user_missions_id and user_reports_id:
                user_mission_report_mapping[user_missions_id] = {
                    "user_reports_id": user_reports_id,
                    "status": status,
                    "report_order": report_order,
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
        report_order = data["report_order"]
        execute_insert_update_query(
            query=UPDATE_REPORTS_ID_STATUS,
            params={
                "user_missions_id": user_missions_id,
                "user_reports_id": user_reports_id,
                "status": status,
            },
        )
        execute_insert_update_query(
            query=USER_REPORTS_ORDER,
            params={"report_order": report_order, "user_reports_id": user_reports_id},
        )


def select_missions_reports_list(user_plans_id):
    """
    user_plans 테이블로 missions, reports 의 id, type, record_time, summary, status, sort_order 반환하는 함수.
    """
    list_page_data = execute_select_query(
        query=SELECT_MISSION_REPORT_LIST, params={"user_plans_id": user_plans_id}
    )
    list_page_data = [dict(data) for data in list_page_data]
    user_children_id = list_page_data[0]["user_children_id"]
    children_image_url = execute_select_query(
        SELECT_CHILDREN_IMAGE_PATH, params={"user_children_id": user_children_id}
    )[0]["profile_image_path"]

    # progress 계산
    completed_missions = [
        data
        for data in list_page_data
        if data["type"] == "mission" and data["status"] == "COMPLETED"
    ]
    total_missions = len([data for data in list_page_data if data["type"] == "mission"])
    progress = (
        round((len(completed_missions) / total_missions) * 100)
        if total_missions > 0
        else 0
    )

    # 이전 report의 최대 sort_order 추적
    previous_sort_order = 0

    # 각 데이터에 mission_progress 추가
    for data in list_page_data:
        if data["type"] == "report":
            # 이전 report의 sort_order 이후부터 현재 report의 sort_order까지 확인
            remaining_missions = [
                mission
                for mission in list_page_data
                if mission["type"] == "mission"
                and previous_sort_order < mission["sort_order"] <= data["sort_order"]
                and mission["status"] != "COMPLETED"
            ]
            data["mission_progress"] = len(remaining_missions)
            # 현재 report의 sort_order를 이전 값으로 업데이트
            previous_sort_order = data["sort_order"]
        elif data["type"] == "mission":
            # mission에는 기본값 추가
            data["mission_progress"] = None

    # page_info 생성
    page_info = {
        "user_children_id": list_page_data[0]["user_children_id"],
        "children_image_url": children_image_url,
        "plan_name": list_page_data[0]["plan_name"],
        "progress": progress,
        "plan_status": list_page_data[0]["plan_status"],  # plan_status 추가
    }

    # list_data 생성
    list_data = [
        {
            k: v
            for k, v in data.items()
            if k not in ["user_children_id", "plan_name", "plan_status"]
        }
        for data in list_page_data
    ]

    return {"page_info": page_info, "list_data": list_data}


def select_user_used_plans(user_id):
    return execute_select_query(
        query=SELECT_USER_USED_PLANS, params={"user_id": user_id}
    )


def patch_user_reports_is_read(user_reports_id):
    next_report_id = execute_select_query(
        query=FIND_NEXT_REPORTS_ID, params={"user_reports_id": user_reports_id}
    )

    check_is_read = execute_select_query(
        query=CHECK_USER_REPORTS_IS_READ, params={"user_reports_id": user_reports_id}
    )
    is_read = check_is_read[0]["is_read"]
    if next_report_id and not is_read:
        next_id = next_report_id[0]["next_user_reports_id"]

        execute_insert_update_query(
            query=UPDATE_USER_REPORTS_IS_READ,
            params={"user_reports_id": user_reports_id},
        )
        status = "IN_PROGRESS"
        execute_insert_update_query(
            query=UPDATE_NEXT_MISSIONS_STATUS,
            params={"user_reports_id": next_id, "status": status},
        )
    elif not next_report_id and not is_read:
        execute_insert_update_query(
            query=UPDATE_USER_REPORTS_IS_READ,
            params={"user_reports_id": user_reports_id},
        )
        user_plans_id = execute_select_query(
            query=FIND_USER_PLANS_ID, params={"user_reports_id": user_reports_id}
        )[0]["user_plans_id"]
        user_plans_id = str(user_plans_id)
        status = "COMPLETED"
        execute_insert_update_query(
            query=UPDATE_USER_PLANS_STATUS,
            params={"user_plans_id": user_plans_id, "status": status},
        )


def user_missions_data(user_missions_id):
    # 쿼리 수정 필요
    return execute_select_query(
        query=GET_USER_MISSIONS_DATA,
        params={"user_missions_id": user_missions_id},
    )


def select_plans_demo():
    plans_id = "1b893728-7d14-4b5c-88ad-895b1d81832b"
    results = execute_select_query(
        query=SELECT_PLANS_DEMO, params={"plans_id": plans_id}
    )
    if results:
        plans = []
        image_fields = ["thumbnail_image_id"]

        for result in results:
            plan = dict(result)
            for field in image_fields:
                try:
                    if plan.get(field):
                        plan[f"{field}_url"] = supabase.storage.from_(
                            "plan-images"
                        ).get_public_url(plan[field])
                    else:
                        plan[f"{field}_url"] = None
                except Exception:
                    plan[f"{field}_url"] = None
                if field in plan:
                    del plan[field]
            plans.append(plan)
        return plans
    return None
