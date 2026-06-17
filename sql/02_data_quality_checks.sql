-- Data quality checks for the AI response quality model.
-- Run after sql/01_create_schema_duckdb.sql.

-- 1. Responses without evaluations
SELECT
    responses.response_id,
    responses.prompt_id,
    responses.response_date
FROM fact_responses AS responses
LEFT JOIN fact_evaluations AS evaluations
    ON responses.response_id = evaluations.response_id
WHERE evaluations.response_id IS NULL;

-- 2. Evaluations without valid response
SELECT
    evaluations.evaluation_id,
    evaluations.response_id
FROM fact_evaluations AS evaluations
LEFT JOIN fact_responses AS responses
    ON evaluations.response_id = responses.response_id
WHERE responses.response_id IS NULL;

-- 3. Scores outside expected range
SELECT
    evaluation_id,
    response_id,
    accuracy_score,
    completeness_score,
    clarity_score,
    tone_score,
    actionability_score
FROM fact_evaluations
WHERE accuracy_score NOT BETWEEN 1 AND 5
   OR completeness_score NOT BETWEEN 1 AND 5
   OR clarity_score NOT BETWEEN 1 AND 5
   OR tone_score NOT BETWEEN 1 AND 5
   OR actionability_score NOT BETWEEN 1 AND 5;

-- 4. Approved responses with high severity issue
SELECT
    evaluation_id,
    response_id,
    issue_type,
    severity,
    final_status
FROM fact_evaluations
WHERE final_status = 'Approved'
  AND severity = 'High';

-- 5. Duplicate response evaluations
SELECT
    response_id,
    COUNT(*) AS evaluations_count
FROM fact_evaluations
GROUP BY response_id
HAVING COUNT(*) > 1;

-- 6. Row count summary
SELECT 'dim_prompts' AS table_name, COUNT(*) AS row_count FROM dim_prompts
UNION ALL
SELECT 'fact_responses', COUNT(*) FROM fact_responses
UNION ALL
SELECT 'fact_evaluations', COUNT(*) FROM fact_evaluations;
