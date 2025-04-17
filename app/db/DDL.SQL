
-- ========================================
-- Clab Supabase Project Schema
-- ========================================

-- act_types
CREATE TABLE public.act_types (
    id bigint NOT NULL,
    act_type character varying NOT NULL
);

-- audio_files
CREATE TABLE public.audio_files (
    place text,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status character varying DEFAULT 'READY'::character varying,
    user_missions_id uuid,
    situation text,
    is_edited boolean NOT NULL DEFAULT false,
    is_used boolean NOT NULL DEFAULT true,
    edited_at timestamp with time zone,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    file_name character varying(255) NOT NULL,
    record_time integer,
    file_path character varying(255) NOT NULL,
    user_id uuid NOT NULL
);

-- category
CREATE TABLE public.category (
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    name character varying NOT NULL,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    parents_id uuid
);

-- missions
CREATE TABLE public.missions (
    message text,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    plans_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    day integer NOT NULL,
    status character varying(255) NOT NULL DEFAULT 'INACTIVE'::character varying,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary text,
    reports_id uuid
);

-- plans
CREATE TABLE public.plans (
    thumbnail_image_name text,
    summary text,
    description_image_name text,
    schedule_image_name text,
    schedule text,
    category_id uuid,
    tags ARRAY,
    type character varying,
    day smallint NOT NULL DEFAULT '0'::smallint,
    end_age_month integer,
    start_age_month integer,
    price integer DEFAULT 0,
    description text,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status character varying(255) DEFAULT 'INACTIVE'::character varying,
    plan_name character varying(255) NOT NULL,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    thumbnail_image_id text,
    description_image_id text,
    schedule_image_id text
);

-- prompts
CREATE TABLE public.prompts (
    user_prompt text,
    purpose text,
    system_prompt text,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    id uuid NOT NULL DEFAULT gen_random_uuid()
);

-- report_files
CREATE TABLE public.report_files (
    user_id uuid NOT NULL,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    file_path character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- reports
CREATE TABLE public.reports (
    sentence_length boolean NOT NULL DEFAULT false,
    plans_id uuid NOT NULL,
    wordcloud boolean NOT NULL DEFAULT false,
    pos_ratio boolean NOT NULL DEFAULT false,
    insight boolean NOT NULL DEFAULT false,
    speech_act boolean NOT NULL DEFAULT false,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    title character varying,
    created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- speech_acts
CREATE TABLE public.speech_acts (
    mood text,
    act_name character varying(255) NOT NULL,
    id integer NOT NULL DEFAULT nextval('speech_acts_id_seq'::regclass)
);

-- stt_data
CREATE TABLE public.stt_data (
    is_turn boolean,
    text_edited character varying(255),
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    talk_more_id bigint DEFAULT '1'::bigint,
    act_types_id integer,
    is_qualitative boolean NOT NULL DEFAULT false,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    audio_files_id uuid NOT NULL,
    act_id integer NOT NULL DEFAULT 1,
    text_order integer NOT NULL,
    start_time integer NOT NULL,
    end_time integer NOT NULL,
    text character varying(255) NOT NULL,
    confidence double precision NOT NULL,
    speaker character varying(255) NOT NULL
);

-- ... (truncated for brevity - full tables continue below)

-- survey_options
CREATE TABLE public.survey_options (
    id bigint NOT NULL,
    question_id bigint NOT NULL,
    option_text text NOT NULL,
    order_num smallint NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- survey_questions
CREATE TABLE public.survey_questions (
    question text NOT NULL,
    updated_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    is_active boolean DEFAULT true,
    survey_type USER-DEFINED NOT NULL,
    max_select smallint DEFAULT '1'::smallint,
    order_num smallint NOT NULL,
    id bigint NOT NULL
);

-- survey_responses
CREATE TABLE public.survey_responses (
    question_id bigint NOT NULL,
    selected_options jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    user_id uuid NOT NULL,
    id bigint NOT NULL
);

-- talk_more
CREATE TABLE public.talk_more (
    id integer NOT NULL DEFAULT nextval('talk_more_id_seq'::regclass),
    talk_more character varying(255) NOT NULL
);

-- user_children
CREATE TABLE public.user_children (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    gender character varying(10) NOT NULL,
    birth_date date NOT NULL,
    profile_image_path text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    last_name character varying(255) NOT NULL,
    first_name character varying(255) NOT NULL,
    user_id uuid NOT NULL
);

-- user_insight
CREATE TABLE public.user_insight (
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    example text,
    insight text,
    title text,
    text ARRAY,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    reports_order smallint,
    user_reports_id uuid NOT NULL
);

-- user_missions
CREATE TABLE public.user_missions (
    user_reports_id uuid,
    status text NOT NULL DEFAULT 'NOT_STARTED'::text,
    created_at timestamp with time zone NOT NULL DEFAULT (now() AT TIME ZONE 'asia/seoul'::text),
    missions_id uuid NOT NULL,
    user_id uuid NOT NULL,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_plans_id uuid,
    start_at timestamp with time zone DEFAULT now()
);

-- user_plans
CREATE TABLE public.user_plans (
    status character varying(255) DEFAULT 'IN_PROGRESS'::character varying,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    plans_id uuid NOT NULL,
    start_at date,
    end_at date,
    created_at timestamp with time zone NOT NULL DEFAULT (now() AT TIME ZONE 'Asia/Seoul'::text),
    user_children_id uuid
);

-- user_pos_ratio
CREATE TABLE public.user_pos_ratio (
    data jsonb,
    user_reports_id uuid NOT NULL,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    insights text,
    created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- user_reports
CREATE TABLE public.user_reports (
    inspection text NOT NULL DEFAULT 'IN_PROGRESS'::text,
    report_order integer,
    user_plans_id uuid,
    is_read boolean NOT NULL DEFAULT false,
    inspected_at timestamp with time zone,
    inspector character varying,
    status character varying NOT NULL DEFAULT 'NOT_STARTED'::character varying,
    send_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    reports_id uuid NOT NULL,
    user_id character varying NOT NULL DEFAULT ''::character varying,
    id uuid NOT NULL DEFAULT gen_random_uuid()
);

-- user_sentence_length
CREATE TABLE public.user_sentence_length (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    insights text,
    data jsonb,
    user_reports_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- user_speech_act
CREATE TABLE public.user_speech_act (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    insights text,
    data jsonb NOT NULL,
    user_reports_id uuid NOT NULL DEFAULT gen_random_uuid(),
    created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- user_wordcloud
CREATE TABLE public.user_wordcloud (
    insights text,
    data jsonb NOT NULL,
    user_reports_id uuid NOT NULL,
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    created_at timestamp with time zone NOT NULL DEFAULT now()
);
