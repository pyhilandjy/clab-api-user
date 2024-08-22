from sqlalchemy import text

INSERT_AUDIO_META_DATA = text(
    """
    INSERT INTO audio_files (user_id, file_name, file_path, created_at) VALUES 
    (
        :user_id,
        :file_name,
        :file_path,
        current_timestamp
    )
    """
)

SELECT_REPORT_METADATA = text(
    """
    SELECT id, title, created_at
    FROM report_files
    WHERE user_id = :user_id;
    """
)

SELECT_REPORT_FILE_PATH = text(
    """
    SELECT file_path
    FROM report_files
    where id = :id
    """
)


SELECT_PLANS = text(
    """
    SELECT * FROM plans
    WHERE status = 'active'
    ORDER BY created_at DESC
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
    """
)

SELECT_USER_MISSION = text(
    """
    SELECT * FROM missions
    WHERE plans_id = :plans_id
    """
)
