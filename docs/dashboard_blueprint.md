# Dashboard blueprint

This document describes the proposed Power BI dashboard for the project.

## Page 1 - Quality overview

Goal: provide a quick view of AI response quality.

### Main cards

- Responses reviewed
- Average quality score
- Approval rate
- Rework rate
- Critical issue rate
- Average review time

### Charts

1. Quality score by use case
2. Approval rate by prompt version
3. Issue type distribution
4. Review time by use case
5. Quality score by model
6. Status distribution

## Page 2 - Prompt version comparison

Goal: compare quality before and after prompt changes.

### Charts

- Average score by prompt version
- Approval rate by prompt version
- Rework rate by prompt version
- Issue distribution by prompt version
- Table with use case, version, score and status

## Page 3 - Review operations

Goal: monitor workload and review efficiency.

### Charts

- Reviews by reviewer
- Average review time by reviewer
- Review volume by date
- High severity issues by use case
- Responses needing rework

## Page 4 - Improvement backlog

Goal: support prioritization of prompt and process improvements.

### Views

- Use cases with low actionability score
- Use cases with high rework rate
- Most frequent issue types
- Prompt versions with quality drop

## Design notes

The first version should be simple, transparent and focused on governance. The dashboard should make quality gaps visible without hiding review assumptions.
