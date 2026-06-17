-- Quality metrics for AI response evaluation.
-- Run after sql/01_create_schema_duckdb.sql.

-- 1. Executive quality summary
SELECT
    COUNT(response_id) AS reviewed_responses,
    ROUND(AVG(quality_score), 2) AS avg_quality_score,
    ROUND(COUNT(CASE WHEN final_status = 'Approved' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS approval_rate,
    ROUND(COUNT(CASE WHEN final_status = 'Needs Rework' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS rework_rate,
    ROUND(COUNT(CASE WHEN severity = 'High' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS critical_issue_rate,
    ROUND(AVG(review_time_minutes), 2) AS avg_review_time_minutes
FROM vw_ai_quality_enriched
WHERE evaluation_id IS NOT NULL;

-- 2. Quality by use case
SELECT
    use_case,
    task_type,
    COUNT(response_id) AS reviewed_responses,
    ROUND(AVG(quality_score), 2) AS avg_quality_score,
    ROUND(AVG(accuracy_score), 2) AS avg_accuracy,
    ROUND(AVG(completeness_score), 2) AS avg_completeness,
    ROUND(AVG(clarity_score), 2) AS avg_clarity,
    ROUND(AVG(actionability_score), 2) AS avg_actionability,
    ROUND(COUNT(CASE WHEN final_status = 'Approved' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS approval_rate
FROM vw_ai_quality_enriched
WHERE evaluation_id IS NOT NULL
GROUP BY use_case, task_type
ORDER BY avg_quality_score ASC;

-- 3. Issue distribution
SELECT
    issue_type,
    severity,
    COUNT(*) AS occurrences,
    ROUND(COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS share_of_issues
FROM vw_ai_quality_enriched
WHERE evaluation_id IS NOT NULL
GROUP BY issue_type, severity
ORDER BY occurrences DESC;

-- 4. Review workload by reviewer
SELECT
    reviewer_id,
    COUNT(response_id) AS reviewed_responses,
    ROUND(AVG(quality_score), 2) AS avg_quality_score,
    ROUND(AVG(review_time_minutes), 2) AS avg_review_time_minutes,
    COUNT(CASE WHEN final_status = 'Needs Rework' THEN 1 END) AS rework_cases,
    COUNT(CASE WHEN final_status = 'Rejected' THEN 1 END) AS rejected_cases
FROM vw_ai_quality_enriched
WHERE evaluation_id IS NOT NULL
GROUP BY reviewer_id
ORDER BY reviewed_responses DESC;
