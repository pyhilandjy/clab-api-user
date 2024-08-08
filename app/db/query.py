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
    ORDER BY created_at DESC
    """
)

SELECT_PLAN = text(
    """
    SELECT * FROM plans
    WHERE id = :plan_id
    """
)

SELECT_PLANS_USER = text(
    """
    SELECT * FROM user_plan
    WHERE user_id = :user_id
    """
)

INSERT_USER_PLAN = text(
    """
    INSERT INTO user_plan (plan_id, user_id, start_at, end_at)
    VALUES (:plan_id, :user_id, :start_at, :end_at)
    """
)
