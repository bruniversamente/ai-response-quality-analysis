# Data

This folder contains synthetic data for an AI response quality analysis project. No real customer data, private messages or sensitive content is used.

## Files

- `sample_prompts.csv`: prompt versions, use cases and expected output format.
- `sample_responses.csv`: synthetic AI response records with model and latency metadata.
- `sample_evaluations.csv`: human review scores and issue classification.

## Notes

The sample CSV files are intentionally small so they can be reviewed directly on GitHub. The script `scripts/generate_ai_quality_data.py` generates a larger dataset under `data/generated/`.
