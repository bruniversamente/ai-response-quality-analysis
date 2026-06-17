# Business rules

## Scope

The project simulates a quality monitoring workflow for AI-generated responses used in internal operations.

## Evaluation unit

Each row in `sample_responses.csv` represents one AI response. Each response should have exactly one evaluation in `sample_evaluations.csv`.

## Quality score

The final quality score is the average of five dimensions:

```text
quality_score = (accuracy + completeness + clarity + tone + actionability) / 5
```

## Approval rate

```text
approval_rate = approved_responses / reviewed_responses
```

## Rework rate

```text
rework_rate = responses_needing_rework / reviewed_responses
```

## Critical issue rate

```text
critical_issue_rate = high_severity_issues / reviewed_responses
```

## Prompt version comparison

Prompt versions should be compared by:

- Average quality score
- Approval rate
- Rework rate
- Review time
- Issue distribution

## Review time

Review time is measured in minutes and represents the effort needed by a human reviewer to validate the response.

## Filters

- Only reviewed responses should be used in quality KPIs.
- Responses without evaluations should be flagged.
- Scores should be between 1 and 5.
- Approved responses with high severity issues should be reviewed again.
