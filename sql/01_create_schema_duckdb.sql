-- Creates analytical tables from the synthetic CSV files.
-- Engine: DuckDB

CREATE OR REPLACE TABLE dim_prompts AS
SELECT
    prompt_id,
    prompt_version,
    use_case,
    task_type,
    expected_format,
    CAST(created_at AS DATE) AS created_at
FROM read_csv_auto('data/sample_prompts.csv');

CREATE OR REPLACE TABLE fact_responses AS
SELECT
    response_id,
    prompt_id,
    CAST(response_date AS DATE) AS response_date,
    model_name,
    input_language,
    output_language,
    CAST(response_length_chars AS INTEGER) AS response_length_chars,
    CAST(latency_seconds AS DOUBLE) AS latency_seconds
FROM read_csv_auto('data/sample_responses.csv');

CREATE OR REPLACE TABLE fact_evaluations AS
SELECT
    evaluation_id,
    response_id,
    reviewer_id,
    CAST(review_date AS DATE) AS review_date,
    CAST(accuracy_score AS INTEGER) AS accuracy_score,
    CAST(completeness_score AS INTEGER) AS completeness_score,
    CAST(clarity_score AS INTEGER) AS clarity_score,
    CAST(tone_score AS INTEGER) AS tone_score,
    CAST(actionability_score AS INTEGER) AS actionability_score,
    issue_type,
    severity,
    final_status,
    CAST(review_time_minutes AS INTEGER) AS review_time_minutes,
    ROUND(
        (
            CAST(accuracy_score AS DOUBLE)
            + CAST(completeness_score AS DOUBLE)
            + CAST(clarity_score AS DOUBLE)
            + CAST(tone_score AS DOUBLE)
            + CAST(actionability_score AS DOUBLE)
        ) / 5,
        2
    ) AS quality_score
FROM read_csv_auto('data/sample_evaluations.csv');

CREATE OR REPLACE VIEW vw_ai_quality_enriched AS
SELECT
    responses.response_id,
    responses.response_date,
    responses.model_name,
    responses.input_language,
    responses.output_language,
    responses.response_length_chars,
    responses.latency_seconds,
    prompts.prompt_id,
    prompts.prompt_version,
    prompts.use_case,
    prompts.task_type,
    prompts.expected_format,
    evaluations.evaluation_id,
    evaluations.reviewer_id,
    evaluations.review_date,
    evaluations.accuracy_score,
    evaluations.completeness_score,
    evaluations.clarity_score,
    evaluations.tone_score,
    evaluations.actionability_score,
    evaluations.quality_score,
    evaluations.issue_type,
    evaluations.severity,
    evaluations.final_status,
    evaluations.review_time_minutes
FROM fact_responses AS responses
LEFT JOIN dim_prompts AS prompts
    ON responses.prompt_id = prompts.prompt_id
LEFT JOIN fact_evaluations AS evaluations
    ON responses.response_id = evaluations.response_id;
