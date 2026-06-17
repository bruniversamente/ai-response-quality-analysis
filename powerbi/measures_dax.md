# Suggested DAX measures

These measures can be used after loading the analytical tables into Power BI.

## Core metrics

```DAX
Reviewed Responses =
DISTINCTCOUNT(fact_evaluations[response_id])
```

```DAX
Average Quality Score =
AVERAGE(fact_evaluations[quality_score])
```

```DAX
Approved Responses =
CALCULATE(
    DISTINCTCOUNT(fact_evaluations[response_id]),
    fact_evaluations[final_status] = "Approved"
)
```

```DAX
Approval Rate =
DIVIDE([Approved Responses], [Reviewed Responses])
```

```DAX
Needs Rework Responses =
CALCULATE(
    DISTINCTCOUNT(fact_evaluations[response_id]),
    fact_evaluations[final_status] = "Needs Rework"
)
```

```DAX
Rework Rate =
DIVIDE([Needs Rework Responses], [Reviewed Responses])
```

```DAX
Rejected Responses =
CALCULATE(
    DISTINCTCOUNT(fact_evaluations[response_id]),
    fact_evaluations[final_status] = "Rejected"
)
```

```DAX
High Severity Issues =
CALCULATE(
    DISTINCTCOUNT(fact_evaluations[response_id]),
    fact_evaluations[severity] = "High"
)
```

```DAX
Critical Issue Rate =
DIVIDE([High Severity Issues], [Reviewed Responses])
```

```DAX
Average Review Time =
AVERAGE(fact_evaluations[review_time_minutes])
```

## Dimension scores

```DAX
Average Accuracy =
AVERAGE(fact_evaluations[accuracy_score])
```

```DAX
Average Completeness =
AVERAGE(fact_evaluations[completeness_score])
```

```DAX
Average Clarity =
AVERAGE(fact_evaluations[clarity_score])
```

```DAX
Average Tone Fit =
AVERAGE(fact_evaluations[tone_score])
```

```DAX
Average Actionability =
AVERAGE(fact_evaluations[actionability_score])
```

## Notes

For final dashboard use, connect `fact_responses` to `dim_prompts` by `prompt_id` and `fact_responses` to `fact_evaluations` by `response_id`.
