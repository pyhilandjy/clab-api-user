from sqlalchemy import text

# 표지
SELECT_COVER_DATA = text(
    """
WITH 
missions_data AS (
    SELECT 
        DISTINCT um.user_id,
        um.user_plans_id,
        um.id AS user_missions_id
    FROM user_missions um
    WHERE um.user_reports_id = :user_reports_id
),

audio_data AS (
    SELECT 
        md.user_id,
        MIN(af.created_at) AS record_start_date,
        MAX(af.created_at) AS record_end_date,
        SUM(af.record_time) AS record_time_sum
    FROM audio_files af
    INNER JOIN missions_data md
        ON af.user_missions_id = md.user_missions_id
    GROUP BY md.user_id
),

children_data AS (
    SELECT 
        DISTINCT uc.first_name,
        up.user_id
    FROM user_children uc
    INNER JOIN user_plans up
        ON uc.id = up.user_childrens_id
    INNER JOIN missions_data md
        ON up.id = md.user_plans_id
),

reports_data AS (
    SELECT 
        DISTINCT r.title AS reports_title,
        ur.id AS user_reports_id
    FROM reports r
    INNER JOIN user_reports ur
        ON r.id = ur.reports_id
    WHERE ur.id = :user_reports_id
)

SELECT DISTINCT
    md.user_id,
    cd.first_name AS user_children_first_name,
    ad.record_start_date,
    ad.record_end_date,
    ad.record_time_sum,
    rd.reports_title
FROM missions_data md
INNER JOIN audio_data ad
    ON md.user_id = ad.user_id
INNER JOIN children_data cd
    ON md.user_id = cd.user_id
INNER JOIN reports_data rd
    ON rd.user_reports_id = :user_reports_id;
    """
)

# Wordcloud

SELECT_WORDCLOUD_DATA = text(
    """
    SELECT DISTINCT data, insights FROM user_wordcloud
    WHERE user_reports_id = :user_reports_id
    """
)


# violinplot
SELECT_SENTENCE_LENGTH_DATA = text(
    """
    SELECT DISTINCT data, insights FROM user_sentence_length
    WHERE user_reports_id = :user_reports_id
    """
)

# 품사 분류
SELECT_POS_RATIO_DATA = text(
    """
    SELECT DISTINCT data, insights FROM user_pos_ratio
    WHERE user_reports_id = :user_reports_id
    """
)

### 문장분류

SELECT_SPEECH_ACT_DATA = text(
    """
    SELECT DISTINCT data, insights FROM user_speech_act
    WHERE user_reports_id = :user_reports_id
    """
)

# 인사이트
SELECT_INSIGHT_DATA = text(
    """
    SELECT * FROM user_insight
    WHERE user_reports_id = :user_reports_id
    ORDER BY reports_order ASC
    """
)

# Reports data
SELECT_WORDCLOUD_IS_USE = text(
    """
    WITH report_ids AS (
        SELECT reports_id
        FROM user_reports
        WHERE id = :user_reports_id
    )
    SELECT 
        r.wordcloud AS wordcloud_data
    FROM report_ids ri
    JOIN reports r ON r.id = ri.reports_id
    """
)

SELECT_SPEECH_ACT_IS_USE = text(
    """
    WITH report_ids AS (
        SELECT reports_id
        FROM user_reports
        WHERE id = :user_reports_id
    )
    SELECT 
        r.speech_act AS speech_act_data
    FROM report_ids ri
    JOIN reports r ON r.id = ri.reports_id
    """
)

SELECT_POS_RATIO_IS_USE = text(
    """
    WITH report_ids AS (
        SELECT reports_id
        FROM user_reports
        WHERE id = :user_reports_id
    )
    SELECT 
        r.pos_ratio AS pos_ratio_data
    FROM report_ids ri
    JOIN reports r ON r.id = ri.reports_id
    """
)

SELECT_SENTENCE_LENGTH_IS_USE = text(
    """
    WITH report_ids AS (
        SELECT reports_id
        FROM user_reports
        WHERE id = :user_reports_id
    )
    SELECT 
        r.sentence_length AS sentence_length_data
    FROM report_ids ri
    JOIN reports r ON r.id = ri.reports_id
    """
)

SELECT_INSIGHT_IS_USE = text(
    """
    WITH report_ids AS (
        SELECT reports_id
        FROM user_reports
        WHERE id = :user_reports_id
    )
    SELECT 
        r.insights AS insights_data
    FROM report_ids ri
    JOIN reports r ON r.id = ri.reports_id
    """
)


SELECT_REPORTS_LIST = text(
    """
WITH valid_reports AS (
    SELECT DISTINCT
        um.user_reports_id
    FROM 
        user_missions um
    WHERE 
        um.user_plans_id = :user_plans_id
),
done_reports AS (
    SELECT DISTINCT
        ur.id AS user_reports_id,
        ur.inspected_at,
        ur.reports_id
    FROM 
        user_reports ur
    INNER JOIN 
        valid_reports vr
    ON 
        ur.id = vr.user_reports_id
    WHERE 
        ur.status = 'DONE'
)
SELECT 
    dr.user_reports_id,
    dr.inspected_at AS created_at,
    r.title AS report_title 
FROM 
    done_reports dr
INNER JOIN 
    reports r
ON 
    dr.reports_id = r.id
ORDER BY 
    r.required_mission_count ASC;
    """
)
