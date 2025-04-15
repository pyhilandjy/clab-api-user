from sqlalchemy import text

INSERT_AUDIO_META_DATA = text(
    """
    INSERT INTO audio_files (user_id, file_name, file_path, record_time, user_missions_id) VALUES
    (
        :user_id,
        :file_name,
        :file_path,
        :record_time,
        :user_missions_id
    ) RETURNING id
    """
)

SELECT_AUDIO_RECORD_TIME = text(
    """
    SELECT COALESCE(SUM(record_time), 0) AS total_record_time
    FROM audio_files
    WHERE user_missions_id = :user_missions_id;
    """
)

UPDATE_USER_MISSION_STATUS = text(
    """
    UPDATE user_missions
    SET status = :status
    WHERE id = :id;
    """
)

SELECT_PLANS = text(
    """
    SELECT 
        p.id, 
        p.plan_name,
        p.summary,
        (SELECT COUNT(*) FROM missions m WHERE m.plans_id = p.id) AS missions_count,
        (SELECT COUNT(*) FROM reports r WHERE r.plans_id = p.id) AS reports_count,
        p.thumbnail_image_id
    FROM plans p
    WHERE p.status = 'ACTIVE'
    ORDER BY p.created_at DESC;
    """
)

SELECT_PLANS_DEMO = text(
    """
    SELECT 
        p.id, 
        p.plan_name,
        p.summary,
        (SELECT COUNT(*) FROM missions m WHERE m.plans_id = p.id) AS missions_count,
        (SELECT COUNT(*) FROM reports r WHERE r.plans_id = p.id) AS reports_count,
        p.thumbnail_image_id
    FROM plans p
    WHERE p.id = :plans_id
    ORDER BY p.created_at DESC;
    """
)
# request Param으로 planId를 넘겨받아, response로 상세정보(플랜 설명, 추천월령, 기간정보, 미션목록(미션 설명포함))를 조회하는 api
SELECT_PLAN_MISSION = text(
    """
SELECT 
    p.description, 
    p.start_age_month, 
    p.end_age_month, 
    p.schedule, 
    p.thumbnail_image_id, 
    p.description_image_id, 
    p.schedule_image_id, 
    p.plan_name,
    COALESCE(r.report_count, 0) AS report_count,
    COALESCE(m_count.mission_count, 0) AS mission_count
FROM 
    plans p
LEFT JOIN 
    missions m 
ON 
    m.plans_id = p.id
LEFT JOIN (
    SELECT 
        plans_id, 
        COUNT(*) AS report_count
    FROM 
        reports
    GROUP BY 
        plans_id
) r 
ON 
    r.plans_id = p.id
LEFT JOIN (
    SELECT 
        plans_id, 
        COUNT(*) AS mission_count
    FROM 
        missions
    GROUP BY 
        plans_id
) m_count
ON 
    m_count.plans_id = p.id
WHERE 
    p.id = :plans_id;
    """
)

SELECT_PLAN = text(
    """
    SELECT * FROM plans
    WHERE id = :plans_id
    """
)

SELECT_USER_PLANS_ID = text(
    """
    SELECT plans_id FROM user_plans
    WHERE user_id = :user_id
    """
)


INSERT_USER_PLANS = text(
    """
    INSERT INTO user_plans (plans_id, user_id, start_at, end_at, user_children_id)
    VALUES (:plans_id, :user_id, :start_at, :end_at, :user_children_id)
    RETURNING id;
    """
)

SELECT_MISSION = text(
    """
    SELECT * FROM missions
    WHERE plans_id = :plans_id
    """
)

INSERT_USER_MISSION_START_DATE = text(
    """
    INSERT INTO user_missions (missions_id, user_id, start_at, user_plans_id)
    VALUES (:missions_id, :user_id, :start_at, :user_plans_id)
    RETURNING id;
    """
)

# SELECT_USER_MISSION = text(
#     """
#     select
#     user_missions.id,
#     user_missions.start_at,
#     user_missions.created_at,
#     missions.day,
#     missions.title,
#     coalesce(sum(af.record_time), 0) as play_seconds,
#     count(af.record_time) as counts
#     from
#     user_missions
#     join missions on user_missions.missions_id = missions.id
#     left join audio_files af on user_missions.id = af.user_missions_id
#     where
#     user_missions.user_id = :user_id
#     and user_missions.status = 'IN_PROGRESS'
#     group by
#     user_missions.id,
#     missions.day,
#     missions.title
#     order by
#     day asc;
#     """
# )

# SELECT_USER_MISSION_DETAIL = text(
#     """
#     select
#     um.id,
#     um.start_at,
#     um.created_at,
#     m.day,
#     m.title,
#     m.message,
#     m.summary
#     from
#     user_missions um
#     join missions m on um.missions_id = m.id
#     where
#     um.user_id = :user_id
#     and um.status = 'IN_PROGRESS'
#     and um.id = :user_missions_id
#     group by
#     um.id,
#     m.day,
#     m.title,
#     m.message,
#     m.summary
#     order by
#     day asc;
#     """
# )

SELECT_REPORTS = text(
    """
    SELECT * FROM reports
    WHERE plans_id = :plans_id
    """
)

INSERT_REPORTS = text(
    """
    INSERT INTO user_reports (reports_id, user_id, user_plans_id)
    VALUES (:reports_id, :user_id, :user_plans_id)
    RETURNING id;
    """
)

UPDATE_REPORTS_ID_STATUS = text(
    """
    UPDATE user_missions
    SET user_reports_id = :user_reports_id,
        status = :status
    WHERE id = :user_missions_id;
    """
)

USER_REPORTS_ORDER = text(
    """
    UPDATE user_reports
    SET report_order = :report_order
    WHERE id = :user_reports_id
    """
)


SELECT_MISSION_REPORT_LIST = text(
    """
    WITH user_related_plans AS (
        SELECT
            up.id AS user_plans_id,
            up.user_id,
            up.plans_id,
            up.user_children_id AS user_children_id,
            plans.plan_name,
            up.status AS plan_status
        FROM 
            user_plans up
        JOIN 
            plans ON up.plans_id = plans.id
        WHERE 
            up.id = :user_plans_id
    ),
    user_mission_data AS (
        SELECT DISTINCT
            um.id AS user_missions_id,
            um.status AS user_mission_status,
            um.user_plans_id,
            urp.user_children_id,
            urp.plan_name,
            missions.id AS mission_id,
            missions.title AS mission_title,
            missions.summary AS mission_summary,
            missions.day AS mission_order,
            missions.reports_id
        FROM 
            user_missions um
        JOIN 
            missions ON um.missions_id = missions.id
        JOIN 
            user_related_plans urp ON um.user_plans_id = urp.user_plans_id
    ),
    user_report_data AS (
        SELECT DISTINCT
            ur.id AS user_reports_id,
            ur.status AS user_report_status,
            ur.is_read,
            ur.reports_id,
            ur.user_plans_id,
            urp.user_children_id,
            urp.plan_name,
            reports.title AS report_title
        FROM 
            user_reports ur
        JOIN 
            reports ON ur.reports_id = reports.id
        JOIN 
            user_related_plans urp ON ur.user_plans_id = urp.user_plans_id
    ),
    audio_time_sum AS (
        SELECT 
            audio_files.user_missions_id,
            COALESCE(SUM(audio_files.record_time), 0) AS total_record_time
        FROM 
            audio_files
        GROUP BY 
            audio_files.user_missions_id
    ),
    combined_data AS (
        SELECT
            umd.user_missions_id AS id,
            umd.mission_title AS title,
            umd.mission_summary AS summary,
            umd.user_mission_status AS status,
            'mission' AS type,
            umd.mission_order AS sort_order,
            COALESCE(ats.total_record_time, 0) AS record_time,
            NULL AS is_read,
            umd.user_children_id,
            umd.plan_name
        FROM 
            user_mission_data umd
        LEFT JOIN 
            audio_time_sum ats ON umd.user_missions_id = ats.user_missions_id
        UNION ALL
        SELECT
            urd.user_reports_id AS id,
            urd.report_title AS title,
            NULL AS summary,
            urd.user_report_status AS status,
            'report' AS type,
            (SELECT MAX(day) 
            FROM missions 
            WHERE missions.reports_id = urd.reports_id) AS sort_order,
            NULL AS record_time,
            urd.is_read,
            urd.user_children_id,
            urd.plan_name
        FROM 
            user_report_data urd
    )
    SELECT DISTINCT
        id,
        title,
        type,
        summary,
        status,
        sort_order,
        record_time,
        is_read,
        user_children_id,
        plan_name,
        (SELECT plan_status FROM user_related_plans LIMIT 1) AS plan_status
    FROM 
        combined_data
    ORDER BY 
        sort_order, type ASC;
    """
)


SELECT_CHILDREN_IMAGE_PATH = text(
    """
    SELECT profile_image_path
    FROM user_children
    WHERE id = :user_children_id;
    """
)

GET_USER_REPORTS_ID_BY_USER_MISSIONS_ID = text(
    """
    SELECT user_reports_id
    FROM user_missions
    WHERE id = :user_missions_id;
    """
)

GET_USER_MISSIONS_DATA = text(
    """
    SELECT 
        p.plan_name, 
        m.title, 
        uc.profile_image_path,
        COALESCE(SUM(af.record_time), 0) AS record_time,
        um.status AS user_mission_status
    FROM 
        user_missions um
    JOIN 
        missions m ON um.missions_id = m.id
    LEFT JOIN
        audio_files af ON um.id = af.user_missions_id
    JOIN 
        user_plans up ON um.user_plans_id = up.id
    JOIN 
        plans p ON up.plans_id = p.id
    JOIN 
        user_children uc ON up.user_children_id = uc.id
    WHERE 
        um.id = :user_missions_id
    GROUP BY 
        p.plan_name, m.title, uc.profile_image_path, um.status;
    """
)

CHECK_ALL_USER_MISSIONS_STATUS = text(
    """
    SELECT status
    FROM user_missions
    WHERE user_reports_id = :user_reports_id;
    """
)

UPDATE_USER_REPORT_STATUS = text(
    """
    UPDATE user_reports
    SET status = :status
    WHERE id = :id;

    """
)

SELECT_USER_USED_PLANS = text(
    """
    SELECT up.id AS user_plans_id, up.plans_id, p.plan_name
    FROM user_plans up
    JOIN plans p ON up.plans_id = p.id
    WHERE up.user_id = :user_id;
    """
)


UPDATE_USER_REPORTS_IS_READ = text(
    """
    UPDATE user_reports
    SET is_read = True
    WHERE id = :user_reports_id;
    """
)

UPDATE_USER_PLANS_STATUS = text(
    """
    UPDATE user_plans
    SET status = :status
    WHERE id = :user_plans_id;
    """
)

FIND_USER_PLANS_ID = text(
    """
    SELECT user_plans_id FROM user_reports
    WHERE id = :user_reports_id
    """
)

FIND_USER_ID_FROM_USER_PLANS = text(
    """
    SELECT user_id FROM user_plans
    WHERE id = :user_plans_id
    """
)

FIND_USER_ID_FROM_USER_REPORTS = text(
    """
    SELECT user_id FROM user_reports
    WHERE id = :user_reports_id
    """
)

FIND_NEXT_REPORTS_ID = text(
    """
    SELECT ur_next.id AS next_user_reports_id
    FROM user_reports ur_current
    JOIN user_reports ur_next 
    ON ur_current.user_plans_id = ur_next.user_plans_id
    AND ur_next.report_order = ur_current.report_order + 1
    WHERE ur_current.id = :user_reports_id;
    """
)

UPDATE_NEXT_MISSIONS_STATUS = text(
    """
    UPDATE user_missions
    SET status = :status
    WHERE user_reports_id = :user_reports_id;
    """
)

CHECK_USER_REPORTS_IS_READ = text(
    """
    SELECT is_read FROM user_reports
    WHERE id = :user_reports_id;
    """
)
