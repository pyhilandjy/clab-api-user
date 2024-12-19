from app.db.query_reports import (
    SELECT_WORDCLOUD_DATA,
    SELECT_SENTENCE_LENGTH_DATA,
    SELECT_POS_RATIO_DATA,
    SELECT_SPEECH_ACT_DATA,
    SELECT_INSIGHT_DATA,
    SELECT_COVER_DATA,
    SELECT_WORDCLOUD_IS_USE,
    SELECT_SENTENCE_LENGTH_IS_USE,
    SELECT_POS_RATIO_IS_USE,
    SELECT_SPEECH_ACT_IS_USE,
    SELECT_INSIGHT_IS_USE,
    SELECT_REPORTS_LIST,
)
from app.db.worker import execute_select_query
from app.services.users import fetch_user_name


def select_cover_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 커버 데이터를 검색합니다.
    """

    data = execute_select_query(
        query=SELECT_COVER_DATA, params={"user_reports_id": user_reports_id}
    )
    if data:
        user_id = str(data[0].user_id)
        user_name = fetch_user_name(user_id)
        data = [dict(item) for item in data]
        for item in data:
            item.pop("user_id", None)
            item["user_name"] = user_name

        return data
    else:
        return []


# 워드클라우드


def select_wordcloud_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 워드클라우드 데이터를 검색합니다.
    """
    is_use_result = execute_select_query(
        query=SELECT_WORDCLOUD_IS_USE, params={"user_reports_id": user_reports_id}
    )
    if is_use_result[0].get("wordcloud_data"):
        results = execute_select_query(
            query=SELECT_WORDCLOUD_DATA, params={"user_reports_id": user_reports_id}
        )
        if results:
            item = results[0]
            combined = {"data": item["data"], "insights": item["insights"]}
            return combined
    return []


# sentence_length(SENTENCE_LENGTH)


def select_sentence_length_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 문장 길이 데이터를 검색합니다.
    """
    is_use_result = execute_select_query(
        query=SELECT_SENTENCE_LENGTH_IS_USE, params={"user_reports_id": user_reports_id}
    )
    if is_use_result[0].get("sentence_length_data"):
        data = execute_select_query(
            query=SELECT_SENTENCE_LENGTH_DATA,
            params={"user_reports_id": user_reports_id},
        )
        if data:
            item = data[0]
            combined = {"data": item["data"], "insights": item["insights"]}
            return combined
    return []


# tokenize data


def select_pos_ratio_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 품사 비율 데이터를 검색합니다.
    """
    is_use_result = execute_select_query(
        query=SELECT_POS_RATIO_IS_USE, params={"user_reports_id": user_reports_id}
    )
    if is_use_result[0].get("pos_ratio_data"):
        data = execute_select_query(
            query=SELECT_POS_RATIO_DATA, params={"user_reports_id": user_reports_id}
        )
        if data:
            item = data[0]
            return {"data": item["data"], "insights": item["insights"]}
    return []


# 문장분류


def select_speech_act_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 발화 행위 데이터를 검색합니다.
    """
    is_use_result = execute_select_query(
        query=SELECT_SPEECH_ACT_IS_USE, params={"user_reports_id": user_reports_id}
    )
    if is_use_result[0].get("speech_act_data"):
        data = execute_select_query(
            query=SELECT_SPEECH_ACT_DATA, params={"user_reports_id": user_reports_id}
        )
        if data:
            item = data[0]
            return {"data": item["data"], "insights": item["insights"]}
    return []


# 인사이트


def select_insight_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 인사이트 데이터를 검색합니다.
    """
    is_use_result = execute_select_query(
        query=SELECT_INSIGHT_IS_USE, params={"user_reports_id": user_reports_id}
    )
    if is_use_result[0].get("insights_data"):
        data = execute_select_query(
            query=SELECT_INSIGHT_DATA, params={"user_reports_id": user_reports_id}
        )
        if data:
            return data
    return []


# reports list
def select_list_data(user_plans_id):
    """
    주어진 user_plans_id에 대한 user_reports_id 리스트를 반환합니다.
    """
    return execute_select_query(
        query=SELECT_REPORTS_LIST,
        params={"user_plans_id": user_plans_id},
    )
