# Data dictionary

## `sample_prompts.csv`

| Field | Description |
|---|---|
| `prompt_id` | Unique prompt identifier. |
| `prompt_version` | Prompt version used to generate the response. |
| `use_case` | Business use case supported by the prompt. |
| `task_type` | Type of task: summarization, classification, drafting or analysis support. |
| `expected_format` | Expected answer format. |
| `created_at` | Prompt creation date. |

## `sample_responses.csv`

| Field | Description |
|---|---|
| `response_id` | Unique response identifier. |
| `prompt_id` | Prompt used to generate the response. |
| `response_date` | Date when the response was generated. |
| `model_name` | Synthetic model label. |
| `input_language` | Input language. |
| `output_language` | Output language. |
| `response_length_chars` | Response length in characters. |
| `latency_seconds` | Response generation latency in seconds. |

## `sample_evaluations.csv`

| Field | Description |
|---|---|
| `evaluation_id` | Unique evaluation identifier. |
| `response_id` | Response being evaluated. |
| `reviewer_id` | Synthetic reviewer identifier. |
| `review_date` | Date of human review. |
| `accuracy_score` | Accuracy score from 1 to 5. |
| `completeness_score` | Completeness score from 1 to 5. |
| `clarity_score` | Clarity score from 1 to 5. |
| `tone_score` | Tone fit score from 1 to 5. |
| `actionability_score` | Actionability score from 1 to 5. |
| `issue_type` | Main issue identified. |
| `severity` | Issue severity. |
| `final_status` | Review outcome. |
| `review_time_minutes` | Human review time. |
