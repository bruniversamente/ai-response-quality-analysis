-- Prompt version comparison queries.
-- Run after sql/01_create_schema_duckdb.sql.

-- 1. Prompt version performance
SELECT
    prompt_version,
    COUNT(response_id) AS reviewed_responses,
    ROUND(AVG(quality_score), 2) AS avg_quality_score,
    ROUND(COUNT(CASE WHEN final_status = 'Approved' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS approval_rate,
    ROUND(COUNT(CASE WHEN final_status = 'Needs Rework' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS rework_rate,
    ROUND(COUNT(CASE WHEN severity = 'High' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS critical_issue_rate,
    ROUND(AVG(review_time_minutes), 2) AS avg_review_time_minutes
FROM vw_ai_quality_enriched
WHERE evaluation_id IS NOT NULL
GROUP BY prompt_version
ORDER BY prompt_version;

-- 2. Prompt version by use case
SELECT
    use_case,
    prompt_version,
    COUNT(response_id) AS reviewed_responses,
    ROUND(AVG(quality_score), 2) AS avg_quality_score,
    ROUND(AVG(actionability_score), 2) AS avg_actionability,
    ROUND(COUNT(CASE WHEN final_status = 'Approved' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS approval_rate
FROM vw_ai_quality_enriched
WHERE evaluation_id IS NOT NULL
GROUP BY use_case, prompt_version
ORDER BY use_case, prompt_version;

-- 3. Issue type by prompt version
SELECT
    prompt_version,
    issue_type,
    COUNT(*) AS occurrences
FROM vw_ai_quality_enriched
WHERE evaluation_id IS NOT NULL
GROUP BY prompt_version, issue_type
ORDER BY prompt_version, occurrences DESC;

-- 4. Improvement candidates
SELECT
    use_case,
    prompt_version,
    COUNT(response_id) AS reviewed_responses,
    ROUND(AVG(quality_score), 2) AS avg_quality_score,
    ROUND(AVG(actionability_score), 2) AS avg_actionability,
    COUNT(CASE WHEN final_status <> 'Approved' THEN 1 END) AS not_approved_cases,
    ROUND(AVG(review_time_minutes), 2) AS avg_review_time_minutes
FROM vw_ai_quality_enriched
WHERE evaluation_id IS NOT NULL
GROUP BY use_case, prompt_version
HAVING AVG(quality_score) < 4.0
    OR AVG(actionability_score) < 4.0
    OR COUNT(CASE WHEN final_status <> 'Approved' THEN 1 END) > 0
ORDER BY avg_quality_score ASC, not_approved_cases DESC;
