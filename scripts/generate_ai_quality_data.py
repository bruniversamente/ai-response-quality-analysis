"""Generate synthetic AI response quality data."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

USE_CASES = [
    ("Ticket Summary", "Summarization", "Bullets"),
    ("Message Classification", "Classification", "Category Label"),
    ("Report Drafting", "Drafting", "Structured Text"),
    ("Data Explanation", "Analysis Support", "Short Explanation"),
]
MODELS = ["model-a", "model-b"]
REVIEWERS = ["REV01", "REV02", "REV03", "REV04"]
ISSUES = ["None", "Incomplete", "Too Generic", "Missing Context", "Wrong Category", "Format Issue", "Low Actionability"]
USE_CASE_ADJUSTMENTS = {
    "Ticket Summary": {
        "base": -0.20,
        "dimension_penalty": {"completeness": -0.35, "actionability": -0.20},
        "issues": ["Incomplete", "Missing Context", "Too Generic"],
    },
    "Message Classification": {
        "base": -0.05,
        "dimension_penalty": {"accuracy": -0.20, "clarity": -0.10},
        "issues": ["Wrong Category", "Missing Context", "Format Issue"],
    },
    "Report Drafting": {
        "base": 0.05,
        "dimension_penalty": {"tone": -0.10, "actionability": -0.25},
        "issues": ["Low Actionability", "Too Generic", "Format Issue"],
    },
    "Data Explanation": {
        "base": -0.10,
        "dimension_penalty": {"accuracy": -0.15, "completeness": -0.15},
        "issues": ["Missing Context", "Incomplete", "Low Actionability"],
    },
}


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    prompts = []
    responses = []
    evaluations = []
    start = date(2026, 1, 1)

    prompt_index = 1
    for version in ["v1", "v2", "v3"]:
        for use_case, task_type, expected_format in USE_CASES:
            prompts.append({
                "prompt_id": f"P{prompt_index:04d}",
                "prompt_version": version,
                "use_case": use_case,
                "task_type": task_type,
                "expected_format": expected_format,
                "created_at": (start + timedelta(days=prompt_index * 3)).isoformat(),
            })
            prompt_index += 1

    for idx in range(1, 501):
        prompt = random.choice(prompts)
        response_id = f"R{idx:05d}"
        response_date = start + timedelta(days=random.randint(40, 150))
        model_name = random.choice(MODELS)
        version_boost = {"v1": -0.45, "v2": 0.12, "v3": 0.42}[prompt["prompt_version"]]
        use_case_rules = USE_CASE_ADJUSTMENTS[prompt["use_case"]]
        base = max(1, min(5, random.gauss(3.85 + version_boost + use_case_rules["base"], 0.70)))
        raw_scores = {
            "accuracy": random.gauss(base + use_case_rules["dimension_penalty"].get("accuracy", 0), 0.55),
            "completeness": random.gauss(base + use_case_rules["dimension_penalty"].get("completeness", 0), 0.55),
            "clarity": random.gauss(base + use_case_rules["dimension_penalty"].get("clarity", 0), 0.55),
            "tone": random.gauss(base + use_case_rules["dimension_penalty"].get("tone", 0), 0.55),
            "actionability": random.gauss(base + use_case_rules["dimension_penalty"].get("actionability", 0), 0.55),
        }
        scores = [max(1, min(5, round(raw_scores[key]))) for key in ["accuracy", "completeness", "clarity", "tone", "actionability"]]
        quality = sum(scores) / 5

        if quality >= 4.0:
            issue = "None"
            severity = "Low"
            status = "Approved"
        elif quality >= 3.0:
            issue = random.choice(use_case_rules["issues"])
            severity = "Medium"
            status = "Needs Rework"
        else:
            issue = random.choice(use_case_rules["issues"])
            severity = "High"
            status = "Rejected"

        responses.append({
            "response_id": response_id,
            "prompt_id": prompt["prompt_id"],
            "response_date": response_date.isoformat(),
            "model_name": model_name,
            "input_language": "pt",
            "output_language": "pt",
            "response_length_chars": random.randint(80, 1200),
            "latency_seconds": round(random.uniform(1.2, 5.5), 2),
        })
        evaluations.append({
            "evaluation_id": f"E{idx:05d}",
            "response_id": response_id,
            "reviewer_id": random.choice(REVIEWERS),
            "review_date": (response_date + timedelta(days=random.randint(0, 2))).isoformat(),
            "accuracy_score": scores[0],
            "completeness_score": scores[1],
            "clarity_score": scores[2],
            "tone_score": scores[3],
            "actionability_score": scores[4],
            "issue_type": issue,
            "severity": severity,
            "final_status": status,
            "review_time_minutes": random.randint(3, 18),
        })

    write_csv(OUT / "prompts.csv", prompts)
    write_csv(OUT / "responses.csv", responses)
    write_csv(OUT / "evaluations.csv", evaluations)
    print(f"Prompts: {len(prompts)} | Responses: {len(responses)} | Evaluations: {len(evaluations)}")


if __name__ == "__main__":
    main()
