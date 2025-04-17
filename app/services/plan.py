from datetime import datetime, timedelta
import pytz
from typing import Optional
from app.config import settings
from supabase import create_client
from app.error_utils import raise_http_500, raise_http_404, capture_message

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
    FIND_USER_ID_FROM_USER_PLANS,
    FIND_USER_ID_FROM_USER_REPORTS,
    FIND_USER_ID_FROM_USER_MISSIONS,
)
from app.db.worker import execute_insert_update_query, execute_select_query

supabase = create_client(settings.supabase_url, settings.supabase_service_key)

IMAGE_FIELDS = ["thumbnail_image_id", "description_image_id", "schedule_image_id"]


def get_plan_image_url(image_id: str) -> Optional[str]:
    """
    Fetch the public URL for a given image ID from the 'plan-images' storage.

    Args:
        image_id (str): The ID of the image.

    Returns:
        Optional[str]: The public URL of the image, or None if an error occurs or the ID is invalid.
    """
    try:
        if image_id:
            return supabase.storage.from_("plan-images").get_public_url(image_id)
    except Exception as e:
        capture_message(f"Failed to fetch public URL: {e}", level="warning")
    return None


def select_plans():
    try:
        results = execute_select_query(
            query=SELECT_PLANS,
        )
        if results:
            plans = []
            for result in results:
                plan = dict(result)
                for field in IMAGE_FIELDS[
                    :1
                ]:  # Only use "thumbnail_image_id" for select_plans
                    plan[f"{field}_url"] = get_plan_image_url(plan.get(field))
                    if field in plan:
                        del plan[field]
                plans.append(plan)
            return plans
        return None
    except Exception as e:
        raise_http_500(e, detail="Failed to select plans")


def select_plans_id(plans_id, user_name):
    try:
        datas = execute_select_query(
            query=SELECT_PLAN_MISSION,
            params={
                "plans_id": plans_id,
            },
        )
        if not datas:
            return None  # raise_http_404 대신 None 반환
        data = [dict(data) for data in datas]
        for row in data:
            if "schedule" in row and "{이름}" in row["schedule"]:
                row["schedule"] = row["schedule"].replace("{이름}", f"{user_name}")
        plan = dict(data[0])
        for field in IMAGE_FIELDS:
            plan[f"{field}_url"] = get_plan_image_url(plan.get(field))
            if field in plan:
                del plan[field]
        return plan
    except Exception as e:
        raise_http_500(e, detail="Failed to select plan by ID")


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


def plan_date(day: int):
    try:
        KST = pytz.timezone("Asia/Seoul")
        today = datetime.now(KST).date()

        if today.weekday() != 0:
            days_until_next_monday = (7 - today.weekday()) % 7
            start_at = today + timedelta(days=days_until_next_monday)
        else:
            start_at = today

        end_at = start_at
        days_added = 0

        while days_added < day:
            end_at += timedelta(days=1)
            if end_at.weekday() < 5:
                days_added += 1

        return start_at, end_at
    except Exception as e:
        raise_http_500(e, detail="Failed to calculate plan dates")


def mission_start_date(start_at, day):
    try:
        mission_start_at = start_at
        days_added = 0

        while days_added < day:
            mission_start_at += timedelta(days=1)
            if mission_start_at.weekday() < 5:
                days_added += 1

        mission_start_at_with_time = datetime.combine(
            mission_start_at, datetime.min.time()
        ).replace(hour=9, minute=0)

        return mission_start_at_with_time
    except Exception as e:
        raise_http_500(e, detail="Failed to calculate mission start date")


def calculate_plan_dates(plan):
    """플랜의 시작일과 종료일을 계산"""
    if plan[0].type == "기간형":
        day = plan[0].day
        return plan_date(day)
    return None, None


def insert_user_plan(user_id, plans_id, plan_start_at, plan_end_at, user_children_id):
    try:
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
    except Exception as e:
        raise_http_500(e, detail="Failed to insert user plan")


def insert_user_missions(user_id, plan_start_at, plan, missions, user_plans_id):
    try:
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
    except Exception as e:
        raise_http_500(e, detail="Failed to insert user missions")


def insert_user_reports(user_id, reports, user_plans_id):
    try:
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
    except Exception as e:
        raise_http_500(e, detail="Failed to insert user reports")


def insert_user_plan_mission(user_id, plans_id, user_children_id):
    try:
        plan = execute_select_query(
            query=SELECT_PLAN,
            params={"plans_id": plans_id},
        )

        plan_start_at, plan_end_at = calculate_plan_dates(plan)

        user_plans_id = insert_user_plan(
            user_id, plans_id, plan_start_at, plan_end_at, user_children_id
        )
        user_plans_id = str(user_plans_id)

        missions = execute_select_query(
            query=SELECT_MISSION,
            params={"plans_id": plans_id},
        )

        mission_id_user_mission_id = insert_user_missions(
            user_id, plan_start_at, plan, missions, user_plans_id
        )

        reports = execute_select_query(
            query=SELECT_REPORTS,
            params={"plans_id": plans_id},
        )

        reports_id_user_reports_id = insert_user_reports(
            user_id, reports, user_plans_id
        )
        user_mission_report_mapping = generate_user_mission_report_mapping(
            mission_id_user_mission_id, reports_id_user_reports_id, missions
        )
        update_user_missions_with_reports(user_mission_report_mapping)
        user_plans_id = {"user_plans_id": user_plans_id}
        return user_plans_id
    except Exception as e:
        raise_http_500(e, detail="Failed to insert user plan mission")


def generate_user_mission_report_mapping(
    mission_id_user_mission_id, reports_id_user_reports_id, missions
):
    try:
        user_mission_report_mapping = {}

        reports_grouped = {}
        for mission in missions:
            reports_id = str(mission["reports_id"])
            if reports_id not in reports_grouped:
                reports_grouped[reports_id] = []
            reports_grouped[reports_id].append(mission)

        group_day_mins = {
            reports_id: min(mission["day"] for mission in missions_list)
            for reports_id, missions_list in reports_grouped.items()
        }

        sorted_reports = sorted(group_day_mins.items(), key=lambda x: x[1])
        report_orders = {
            reports_id: index + 1
            for index, (reports_id, _) in enumerate(sorted_reports)
        }

        lowest_day_min_reports_id = sorted_reports[0][0]
        for reports_id, missions_list in reports_grouped.items():
            status = (
                "IN_PROGRESS"
                if reports_id == lowest_day_min_reports_id
                else "NOT_STARTED"
            )
            report_order = report_orders[reports_id]
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
    except Exception as e:
        raise_http_500(e, detail="Failed to generate user mission report mapping")


def update_user_missions_with_reports(mapping):
    try:
        for user_missions_id, data in mapping.items():
            user_reports_id = data["user_reports_id"]
            status = data["status"]
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
                params={
                    "report_order": report_order,
                    "user_reports_id": user_reports_id,
                },
            )
    except Exception as e:
        raise_http_500(e, detail="Failed to update user missions with reports")


def select_missions_reports_list(user_plans_id):
    try:
        list_page_data = execute_select_query(
            query=SELECT_MISSION_REPORT_LIST, params={"user_plans_id": user_plans_id}
        )
        list_page_data = [dict(data) for data in list_page_data]
        user_children_id = list_page_data[0]["user_children_id"]
        children_image_url = execute_select_query(
            SELECT_CHILDREN_IMAGE_PATH, params={"user_children_id": user_children_id}
        )[0]["profile_image_path"]

        completed_missions = [
            data
            for data in list_page_data
            if data["type"] == "mission" and data["status"] == "COMPLETED"
        ]
        total_missions = len(
            [data for data in list_page_data if data["type"] == "mission"]
        )
        progress = (
            round((len(completed_missions) / total_missions) * 100)
            if total_missions > 0
            else 0
        )

        previous_sort_order = 0

        for data in list_page_data:
            if data["type"] == "report":
                remaining_missions = [
                    mission
                    for mission in list_page_data
                    if mission["type"] == "mission"
                    and previous_sort_order
                    < mission["sort_order"]
                    <= data["sort_order"]
                    and mission["status"] != "COMPLETED"
                ]
                data["mission_progress"] = len(remaining_missions)
                previous_sort_order = data["sort_order"]
            elif data["type"] == "mission":
                data["mission_progress"] = None

        page_info = {
            "user_children_id": list_page_data[0]["user_children_id"],
            "children_image_url": children_image_url,
            "plan_name": list_page_data[0]["plan_name"],
            "progress": progress,
            "plan_status": list_page_data[0]["plan_status"],
        }

        list_data = [
            {
                k: v
                for k, v in data.items()
                if k not in ["user_children_id", "plan_name", "plan_status"]
            }
            for data in list_page_data
        ]

        return {"page_info": page_info, "list_data": list_data}
    except Exception as e:
        raise_http_500(e, detail="Failed to select missions reports list")


def select_user_used_plans(user_id):
    try:
        return execute_select_query(
            query=SELECT_USER_USED_PLANS, params={"user_id": user_id}
        )
    except Exception as e:
        raise_http_500(e, detail="Failed to select user used plans")


def patch_user_reports_is_read(user_reports_id):
    try:
        next_report_id = execute_select_query(
            query=FIND_NEXT_REPORTS_ID, params={"user_reports_id": user_reports_id}
        )

        check_is_read = execute_select_query(
            query=CHECK_USER_REPORTS_IS_READ,
            params={"user_reports_id": user_reports_id},
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
    except Exception as e:
        raise_http_500(e, detail="Failed to patch user reports is read")


def user_missions_data(user_missions_id):
    try:
        return execute_select_query(
            query=GET_USER_MISSIONS_DATA,
            params={"user_missions_id": user_missions_id},
        )
    except Exception as e:
        raise_http_500(e, detail="Failed to get user missions data")


def select_plans_demo():
    try:
        plans_id = "1b893728-7d14-4b5c-88ad-895b1d81832b"
        results = execute_select_query(
            query=SELECT_PLANS_DEMO, params={"plans_id": plans_id}
        )
        if results:
            plans = []
            for result in results:
                plan = dict(result)
                for field in IMAGE_FIELDS[
                    :1
                ]:  # Only use "thumbnail_image_id" for select_plans_demo
                    plan[f"{field}_url"] = get_plan_image_url(plan.get(field))
                    if field in plan:
                        del plan[field]
                plans.append(plan)
            return plans
        return None
    except Exception as e:
        raise_http_500(e, detail="Failed to select plans demo")


def find_owner_id_user_plans(user_plans_id):
    try:
        result = execute_select_query(
            query=FIND_USER_ID_FROM_USER_PLANS, params={"user_plans_id": user_plans_id}
        )
        if result:
            return result[0]["user_id"]
        raise_http_404("User ID not found for given user plans ID")
    except Exception as e:
        raise_http_500(e, detail="Failed to find owner ID from user plans")


def find_owner_id_user_reports(user_reports_id):
    try:
        result = execute_select_query(
            query=FIND_USER_ID_FROM_USER_REPORTS,
            params={"user_reports_id": user_reports_id},
        )
        if result:
            return result[0]["user_id"]
        raise_http_404("User ID not found for given user reports ID")
    except Exception as e:
        raise_http_500(e, detail="Failed to find owner ID from user reports")


def find_owner_id_user_missions(user_missions_id):
    try:
        result = execute_select_query(
            query=FIND_USER_ID_FROM_USER_MISSIONS,
            params={"user_missions_id": user_missions_id},
        )
        if result:
            return result[0]["user_id"]
        raise_http_404("User ID not found for given user missions ID")
    except Exception as e:
        raise_http_500(e, detail="Failed to find owner ID from user missions")
