from sqlalchemy import text

INSERT_AUDIO_META_DATA = text(
    """
    INSERT INTO audio_files (user_id, file_name, file_path, record_time) VALUES
    (
        :user_id,
        :file_name,
        :file_path,
        record_time
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

UPDATE_USER_MISSION_IS_OPEN = text(
    """
    UPDATE user_missions
    SET is_open = false
    WHERE id = :id;
    """
)

SELECT_PLANS = text(
    """
    SELECT 
        p.id, 
        p.plan_name,
        (SELECT COUNT(*) FROM missions m WHERE m.plans_id = p.id) AS missions_count,
        (SELECT COUNT(*) FROM reports r WHERE r.plans_id = p.id) AS reports_count
    FROM plans p
    WHERE p.status = 'active'
    ORDER BY p.created_at DESC;
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
    INSERT INTO user_plans (plans_id, user_id, start_at, end_at)
    VALUES (:plans_id, :user_id, :start_at, :end_at)
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
    INSERT INTO user_missions (missions_id, user_id, start_at)
    VALUES (:missions_id, :user_id, :start_at)
    RETURNING id;
    """
)

SELECT_USER_MISSION = text(
    """
    select
    user_missions.id,
    user_missions.start_at,
    user_missions.created_at,
    missions.day,
    missions.title,
    coalesce(sum(af.record_time), 0) as play_seconds,
    count(af.record_time) as counts
    from
    user_missions
    join missions on user_missions.missions_id = missions.id
    left join audio_files af on user_missions.id = af.user_missions_id
    where
    user_missions.user_id = :user_id
    and user_missions.status = 'active'
    group by
    user_missions.id,
    missions.day,
    missions.title
    order by
    day asc;
    """
)

SELECT_USER_MISSION_DETAIL = text(
    """
    select
    um.id,
    um.start_at,
    um.created_at,
    m.day,
    m.title,
    m.message,
    m.summation
    from
    user_missions um
    join missions m on um.missions_id = m.id
    where
    um.user_id = :user_id
    and um.status = 'active'
    and um.id = :user_missions_id
    group by
    um.id,
    m.day,
    m.title,
    m.message,
    m.summation
    order by
    day asc;
    """
)

SELECT_REPORTS = text(
    """
    SELECT * FROM reports
    WHERE plans_id = :plans_id
    """
)

INSERT_REPORTS = text(
    """
    INSERT INTO user_reports (reports_id, user_id, user_missions_id, send_at)
    VALUES (:reports_id, :user_id, :user_missions_id, :send_at)
    """
)
