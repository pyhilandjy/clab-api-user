from app.db.query_reports import (
    SELECT_WORDCLOUD_DATA,
    SELECT_SENTENCE_LENGTH_DATA,
    SELECT_POS_RATIO_DATA,
    SELECT_SPEECH_ACT_DATA,
    SELECT_INSIGHT_DATA,
    SELECT_COVER_DATA,
)
from app.db.worker import execute_insert_update_query, execute_select_query
from app.services.users import fetch_user_names, fetch_user_name


POS_TAG_TO_KOREAN = {
    "NNP": "고유명사",
    "NNG": "명사",
    "NP": "대명사",
    "VV": "동사",
    "VA": "형용사",
    "MAG": "부사",
    "JKS": "전치사",
    "JC": "접속사",
    "IC": "감탄사",
}


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
    results = execute_select_query(
        query=SELECT_WORDCLOUD_DATA, params={"user_reports_id": user_reports_id}
    )
    if results:
        item = results[0]
        combined = {"data": item["data"], "insights": item["insights"]}
        return combined
    else:
        return []


# sentence_length(SENTENCE_LENGTH)


def select_sentence_length_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 바이올린플롯 데이터를 생성하고 저장합니다.
    """
    data = execute_select_query(
        query=SELECT_SENTENCE_LENGTH_DATA, params={"user_reports_id": user_reports_id}
    )
    if data:
        item = data[0]
    combined = {"data": item["data"], "insights": item["insights"]}
    return combined


# tokenize data


def select_pos_ratio_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 품사분류 데이터를 생성하고 저장합니다.
    """
    data = execute_select_query(
        query=SELECT_POS_RATIO_DATA, params={"user_reports_id": user_reports_id}
    )

    if data:
        item = data[0]
        return {"data": item["data"], "insights": item["insights"]}
    else:
        return []


# 문장분류


def select_speech_act_data(user_reports_id):

    data = execute_select_query(
        query=SELECT_SPEECH_ACT_DATA, params={"user_reports_id": user_reports_id}
    )

    if data:
        item = data[0]
        return {"data": item["data"], "insights": item["insights"]}
    else:
        return []


# 인사이트


def select_insight_data(user_reports_id):

    data = execute_select_query(
        query=SELECT_INSIGHT_DATA, params={"user_reports_id": user_reports_id}
    )
    if data:
        return data
    else:
        return []
