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

# SELECT_REPORT_METADATA = text(
#     """
#     SELECT id, title, created_at
#     FROM report_files
#     WHERE user_id = :user_id;
#     """
# )

# SELECT_REPORT_FILE_PATH = text(
#     """
#     SELECT file_path
#     FROM report_files
#     where id = :id
#     """
# )


# SELECT_PLANS = text(
#     """
#     SELECT * FROM plans
#     WHERE status = 'active'
#     ORDER BY created_at DESC
#     """
# )

# SELECT_PLAN = text(
#     """
#     SELECT * FROM plans
#     WHERE id = :plans_id
#     """
# )

# SELECT_USER_PLANS_ID = text(
#     """
#     SELECT plans_id FROM user_plans
#     WHERE user_id = :user_id
#     """
# )


# INSERT_USER_PLANS = text(
#     """
#     INSERT INTO user_plans (plans_id, user_id, start_at, end_at)
#     VALUES (:plans_id, :user_id, :start_at, :end_at)
#     """
# )

# SELECT_MISSION = text(
#     """
#     SELECT * FROM missions
#     WHERE plans_id = :plans_id
#     """
# )

# INSERT_USER_MISSION_START_DATE = text(
#     """
#     INSERT INTO user_missions (missions_id, user_id, start_at)
#     VALUES (:missions_id, :user_id, :start_at)
#     RETURNING id;
#     """
# )

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
#     and user_missions.status = 'active'
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
#     m.summation
#     from
#     user_missions um
#     join missions m on um.missions_id = m.id
#     where
#     um.user_id = :user_id
#     and um.status = 'active'
#     and um.id = :user_missions_id
#     group by
#     um.id,
#     m.day,
#     m.title,
#     m.message,
#     m.summation
#     order by
#     day asc;
#     """
# )

# SELECT_REPORTS = text(
#     """
#     SELECT * FROM reports
#     WHERE plans_id = :plans_id
#     """
# )

# INSERT_REPORTS = text(
#     """
#     INSERT INTO user_reports (reports_id, user_id, user_missions_id, send_at)
#     VALUES (:reports_id, :user_id, :user_missions_id, :send_at)
#     """
# )
