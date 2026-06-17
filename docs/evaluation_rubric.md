# Evaluation rubric

This rubric defines how AI responses are reviewed in the project.

Each response receives a score from 1 to 5 in five dimensions.

## Scoring scale

| Score | Meaning |
|---|---|
| 1 | Very poor. Requires full rewrite. |
| 2 | Weak. Multiple issues and limited usefulness. |
| 3 | Acceptable with revision. Useful but incomplete or unclear. |
| 4 | Good. Minor improvements may be needed. |
| 5 | Excellent. Ready to use. |

## Dimensions

### Accuracy

Evaluates whether the answer is correct and aligned with the available context.

### Completeness

Evaluates whether the answer covers the relevant parts of the request.

### Clarity

Evaluates whether the answer is easy to understand, structured and direct.

### Tone fit

Evaluates whether the answer matches the expected tone for the use case.

### Actionability

Evaluates whether the answer helps the user take a clear next step.

## Final status

- `Approved`: response can be used with no relevant changes.
- `Needs Rework`: response is useful but needs review or adjustment.
- `Rejected`: response should not be used.

## Issue types

- `None`
- `Incomplete`
- `Too Generic`
- `Missing Context`
- `Wrong Category`
- `Format Issue`
- `Low Actionability`

## Quality score

```text
quality_score = average(accuracy, completeness, clarity, tone_fit, actionability)
```

## Approval rule

A response is approved when:

- final status is `Approved`
- no high severity issue exists
- average score is equal to or above 4.0
