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
        version_boost = {"v1": -0.3, "v2": 0.2, "v3": 0.4}[prompt["prompt_version"]]
        base = max(1, min(5, random.gauss(3.8 + version_boost, 0.75)))
        scores = [max(1, min(5, round(random.gauss(base, 0.55)))) for _ in range(5)]
        quality = sum(scores) / 5

        if quality >= 4.0:
            issue = "None"
            severity = "Low"
            status = "Approved"
        elif quality >= 3.0:
            issue = random.choice([i for i in ISSUES if i != "None"])
            severity = "Medium"
            status = "Needs Rework"
        else:
            issue = random.choice(["Incomplete", "Wrong Category", "Missing Context"])
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
