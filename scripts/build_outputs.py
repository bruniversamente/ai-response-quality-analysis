"""Build reviewed outputs and a static dashboard for the AI Quality case.

Usage:
    python scripts/build_outputs.py

The script regenerates synthetic AI quality data, builds a DuckDB model,
exports reviewed CSV extracts, writes executive findings, and creates a
portable HTML dashboard for the portfólio.
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from generate_ai_quality_data import main as generate_ai_quality_data

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "generated"
OUTPUT_DIR = ROOT / "outputs"
DASHBOARD_DIR = ROOT / "dashboard"
DB_PATH = ROOT / "ai_quality.duckdb"


def sql_path(path: Path) -> str:
    return path.resolve().as_posix()


def pct(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def num(value: float | int | None, decimals: int = 0) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):,.{decimals}f}"


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    DASHBOARD_DIR.mkdir(exist_ok=True)


def create_model(con: duckdb.DuckDBPyConnection) -> None:
    prompts_csv = DATA_DIR / "prompts.csv"
    responses_csv = DATA_DIR / "responses.csv"
    evaluations_csv = DATA_DIR / "evaluations.csv"

    con.execute(
        f"""
        CREATE OR REPLACE TABLE dim_prompts AS
        SELECT
            prompt_id,
            prompt_version,
            use_case,
            task_type,
            expected_format,
            TRY_CAST(created_at AS DATE) AS created_at
        FROM read_csv_auto('{sql_path(prompts_csv)}', all_varchar = true);

        CREATE OR REPLACE TABLE fact_responses AS
        SELECT
            response_id,
            prompt_id,
            TRY_CAST(response_date AS DATE) AS response_date,
            model_name,
            input_language,
            output_language,
            TRY_CAST(response_length_chars AS INTEGER) AS response_length_chars,
            TRY_CAST(latency_seconds AS DOUBLE) AS latency_seconds
        FROM read_csv_auto('{sql_path(responses_csv)}', all_varchar = true);

        CREATE OR REPLACE TABLE fact_evaluations AS
        SELECT
            evaluation_id,
            response_id,
            reviewer_id,
            TRY_CAST(review_date AS DATE) AS review_date,
            TRY_CAST(accuracy_score AS INTEGER) AS accuracy_score,
            TRY_CAST(completeness_score AS INTEGER) AS completeness_score,
            TRY_CAST(clarity_score AS INTEGER) AS clarity_score,
            TRY_CAST(tone_score AS INTEGER) AS tone_score,
            TRY_CAST(actionability_score AS INTEGER) AS actionability_score,
            issue_type,
            severity,
            final_status,
            TRY_CAST(review_time_minutes AS INTEGER) AS review_time_minutes,
            ROUND(
                (
                    TRY_CAST(accuracy_score AS DOUBLE)
                    + TRY_CAST(completeness_score AS DOUBLE)
                    + TRY_CAST(clarity_score AS DOUBLE)
                    + TRY_CAST(tone_score AS DOUBLE)
                    + TRY_CAST(actionability_score AS DOUBLE)
                ) / 5,
                2
            ) AS quality_score
        FROM read_csv_auto('{sql_path(evaluations_csv)}', all_varchar = true);

        CREATE OR REPLACE VIEW vw_ai_quality_enriched AS
        SELECT
            responses.response_id,
            responses.response_date,
            STRFTIME(responses.response_date, '%Y-%m') AS response_month,
            responses.model_name,
            responses.input_language,
            responses.output_language,
            responses.response_length_chars,
            responses.latency_seconds,
            prompts.prompt_id,
            prompts.prompt_version,
            prompts.use_case,
            prompts.task_type,
            prompts.expected_format,
            evaluations.evaluation_id,
            evaluations.reviewer_id,
            evaluations.review_date,
            evaluations.accuracy_score,
            evaluations.completeness_score,
            evaluations.clarity_score,
            evaluations.tone_score,
            evaluations.actionability_score,
            evaluations.quality_score,
            evaluations.issue_type,
            evaluations.severity,
            evaluations.final_status,
            evaluations.review_time_minutes,
            CASE
                WHEN evaluations.final_status = 'Approved'
                  AND evaluations.quality_score >= 4.0
                  AND evaluations.severity <> 'High'
                THEN TRUE
                ELSE FALSE
            END AS is_release_ready
        FROM fact_responses AS responses
        LEFT JOIN dim_prompts AS prompts
            ON responses.prompt_id = prompts.prompt_id
        LEFT JOIN fact_evaluations AS evaluations
            ON responses.response_id = evaluations.response_id;
        """
    )


def query_outputs(con: duckdb.DuckDBPyConnection) -> dict[str, object]:
    outputs: dict[str, object] = {}

    outputs["kpi_summary"] = con.execute(
        """
        SELECT
            COUNT(response_id) AS reviewed_responses,
            ROUND(AVG(quality_score), 2) AS avg_quality_score,
            ROUND(COUNT(CASE WHEN is_release_ready THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS release_ready_rate,
            ROUND(COUNT(CASE WHEN final_status = 'Needs Rework' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS rework_rate,
            ROUND(COUNT(CASE WHEN severity = 'High' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS critical_issue_rate,
            ROUND(AVG(review_time_minutes), 2) AS avg_review_time_minutes,
            ROUND(AVG(latency_seconds), 2) AS avg_latency_seconds
        FROM vw_ai_quality_enriched
        WHERE evaluation_id IS NOT NULL;
        """
    ).fetchdf()

    outputs["prompt_version_performance"] = con.execute(
        """
        SELECT
            prompt_version,
            COUNT(response_id) AS reviewed_responses,
            ROUND(AVG(quality_score), 2) AS avg_quality_score,
            ROUND(COUNT(CASE WHEN is_release_ready THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS release_ready_rate,
            ROUND(COUNT(CASE WHEN final_status = 'Needs Rework' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS rework_rate,
            ROUND(COUNT(CASE WHEN severity = 'High' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS critical_issue_rate,
            ROUND(AVG(review_time_minutes), 2) AS avg_review_time_minutes
        FROM vw_ai_quality_enriched
        WHERE evaluation_id IS NOT NULL
        GROUP BY prompt_version
        ORDER BY prompt_version;
        """
    ).fetchdf()

    outputs["quality_by_use_case"] = con.execute(
        """
        SELECT
            use_case,
            task_type,
            COUNT(response_id) AS reviewed_responses,
            ROUND(AVG(quality_score), 2) AS avg_quality_score,
            ROUND(AVG(accuracy_score), 2) AS avg_accuracy,
            ROUND(AVG(completeness_score), 2) AS avg_completeness,
            ROUND(AVG(clarity_score), 2) AS avg_clarity,
            ROUND(AVG(tone_score), 2) AS avg_tone,
            ROUND(AVG(actionability_score), 2) AS avg_actionability,
            ROUND(COUNT(CASE WHEN is_release_ready THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS release_ready_rate,
            ROUND(AVG(review_time_minutes), 2) AS avg_review_time_minutes
        FROM vw_ai_quality_enriched
        WHERE evaluation_id IS NOT NULL
        GROUP BY use_case, task_type
        ORDER BY avg_quality_score ASC;
        """
    ).fetchdf()

    outputs["dimension_scores"] = con.execute(
        """
        SELECT 'Accuracy' AS dimension, ROUND(AVG(accuracy_score), 2) AS avg_score FROM vw_ai_quality_enriched WHERE evaluation_id IS NOT NULL
        UNION ALL SELECT 'Completeness', ROUND(AVG(completeness_score), 2) FROM vw_ai_quality_enriched WHERE evaluation_id IS NOT NULL
        UNION ALL SELECT 'Clarity', ROUND(AVG(clarity_score), 2) FROM vw_ai_quality_enriched WHERE evaluation_id IS NOT NULL
        UNION ALL SELECT 'Tone fit', ROUND(AVG(tone_score), 2) FROM vw_ai_quality_enriched WHERE evaluation_id IS NOT NULL
        UNION ALL SELECT 'Actionability', ROUND(AVG(actionability_score), 2) FROM vw_ai_quality_enriched WHERE evaluation_id IS NOT NULL
        ORDER BY avg_score ASC;
        """
    ).fetchdf()

    outputs["issue_distribution"] = con.execute(
        """
        SELECT
            issue_type,
            severity,
            COUNT(*) AS occurrences,
            ROUND(COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS share_of_reviews
        FROM vw_ai_quality_enriched
        WHERE evaluation_id IS NOT NULL
          AND issue_type <> 'None'
        GROUP BY issue_type, severity
        ORDER BY occurrences DESC, severity;
        """
    ).fetchdf()

    outputs["monthly_quality_trend"] = con.execute(
        """
        SELECT
            response_month,
            COUNT(response_id) AS reviewed_responses,
            ROUND(AVG(quality_score), 2) AS avg_quality_score,
            ROUND(COUNT(CASE WHEN is_release_ready THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS release_ready_rate,
            ROUND(COUNT(CASE WHEN severity = 'High' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS critical_issue_rate
        FROM vw_ai_quality_enriched
        WHERE evaluation_id IS NOT NULL
        GROUP BY response_month
        ORDER BY response_month;
        """
    ).fetchdf()

    outputs["reviewer_calibration"] = con.execute(
        """
        SELECT
            reviewer_id,
            COUNT(response_id) AS reviewed_responses,
            ROUND(AVG(quality_score), 2) AS avg_quality_score,
            ROUND(STDDEV_SAMP(quality_score), 2) AS score_stddev,
            ROUND(AVG(review_time_minutes), 2) AS avg_review_time_minutes,
            ROUND(COUNT(CASE WHEN final_status = 'Needs Rework' THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS rework_rate
        FROM vw_ai_quality_enriched
        WHERE evaluation_id IS NOT NULL
        GROUP BY reviewer_id
        ORDER BY reviewed_responses DESC;
        """
    ).fetchdf()

    outputs["improvement_backlog"] = con.execute(
        """
        SELECT
            use_case,
            prompt_version,
            COUNT(response_id) AS reviewed_responses,
            ROUND(AVG(quality_score), 2) AS avg_quality_score,
            ROUND(AVG(actionability_score), 2) AS avg_actionability,
            ROUND(COUNT(CASE WHEN is_release_ready THEN 1 END) / NULLIF(COUNT(response_id), 0), 4) AS release_ready_rate,
            COUNT(CASE WHEN final_status <> 'Approved' THEN 1 END) AS not_approved_cases,
            ROUND(AVG(review_time_minutes), 2) AS avg_review_time_minutes
        FROM vw_ai_quality_enriched
        WHERE evaluation_id IS NOT NULL
        GROUP BY use_case, prompt_version
        HAVING AVG(quality_score) < 4.0
            OR AVG(actionability_score) < 4.0
            OR COUNT(CASE WHEN final_status <> 'Approved' THEN 1 END) >= 3
        ORDER BY release_ready_rate ASC, avg_quality_score ASC, not_approved_cases DESC
        LIMIT 10;
        """
    ).fetchdf()

    outputs["data_quality_summary"] = con.execute(
        """
        SELECT 'response_without_evaluation' AS rule_name, 'Critical' AS severity, COUNT(*) AS failed_records
        FROM fact_responses AS responses
        LEFT JOIN fact_evaluations AS evaluations
            ON responses.response_id = evaluations.response_id
        WHERE evaluations.response_id IS NULL
        UNION ALL
        SELECT 'evaluation_without_response', 'Critical', COUNT(*)
        FROM fact_evaluations AS evaluations
        LEFT JOIN fact_responses AS responses
            ON evaluations.response_id = responses.response_id
        WHERE responses.response_id IS NULL
        UNION ALL
        SELECT 'score_outside_expected_range', 'Critical', COUNT(*)
        FROM fact_evaluations
        WHERE accuracy_score NOT BETWEEN 1 AND 5
           OR completeness_score NOT BETWEEN 1 AND 5
           OR clarity_score NOT BETWEEN 1 AND 5
           OR tone_score NOT BETWEEN 1 AND 5
           OR actionability_score NOT BETWEEN 1 AND 5
        UNION ALL
        SELECT 'approved_with_high_severity', 'Critical', COUNT(*)
        FROM fact_evaluations
        WHERE final_status = 'Approved'
          AND severity = 'High'
        UNION ALL
        SELECT 'duplicate_response_evaluation', 'Critical', COUNT(*)
        FROM (
            SELECT response_id
            FROM fact_evaluations
            GROUP BY response_id
            HAVING COUNT(*) > 1
        )
        UNION ALL
        SELECT 'approved_but_below_threshold', 'Warning', COUNT(*)
        FROM fact_evaluations
        WHERE final_status = 'Approved'
          AND quality_score < 4.0;
        """
    ).fetchdf()

    return outputs


def write_outputs(outputs: dict[str, object]) -> None:
    for name, frame in outputs.items():
        frame.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)

    dashboard_data = {
        name: json.loads(frame.to_json(orient="records"))
        for name, frame in outputs.items()
    }
    (OUTPUT_DIR / "dashboard_data.json").write_text(
        json.dumps(dashboard_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_findings(dashboard_data)
    write_dashboard(dashboard_data)


def write_findings(data: dict[str, list[dict[str, object]]]) -> None:
    kpis = data["kpi_summary"][0]
    versions = data["prompt_version_performance"]
    use_cases = data["quality_by_use_case"]
    issues = data["issue_distribution"]
    dimensions = data["dimension_scores"]
    dq_rows = data["data_quality_summary"]

    best_version = max(versions, key=lambda row: row.get("release_ready_rate") or 0)
    worst_use_case = min(use_cases, key=lambda row: row.get("avg_quality_score") or 99)
    top_issue = issues[0] if issues else {"issue_type": "None", "occurrences": 0}
    weakest_dimension = dimensions[0]
    critical_failures = sum(
        int(row["failed_records"])
        for row in dq_rows
        if row["severity"] == "Critical"
    )

    body_pt = f"""# Achados executivos - AI Response Quality

## Resumo de decisão

O principal sinal do case não é apenas a nota média. A leitura mais útil é combinar qualidade, retrabalho, severidade e prontidão para uso. No build atual, {pct(kpis["release_ready_rate"])} das respostas estão prontas para uso sem retrabalho relevante, com score médio de {num(kpis["avg_quality_score"], 2)} em uma escala de 1 a 5.

## O que os dados mostram

- Respostas revisadas: {num(kpis["reviewed_responses"])}
- Score médio de qualidade: {num(kpis["avg_quality_score"], 2)}
- Respostas prontas para uso: {pct(kpis["release_ready_rate"])}
- Taxa de retrabalho: {pct(kpis["rework_rate"])}
- Taxa de problema crítico: {pct(kpis["critical_issue_rate"])}
- Tempo médio de revisão: {num(kpis["avg_review_time_minutes"], 1)} minutos
- Melhor versão de prompt: {best_version["prompt_version"]} ({pct(best_version["release_ready_rate"])} prontas para uso)
- Caso de uso mais frágil: {worst_use_case["use_case"]} (score {num(worst_use_case["avg_quality_score"], 2)})
- Principal tipo de problema: {top_issue["issue_type"]} ({num(top_issue["occurrences"])} ocorrências)
- Dimensão mais fraca da rubrica: {weakest_dimension["dimension"]} (score {num(weakest_dimension["avg_score"], 2)})
- Falhas críticas de qualidade de dados: {critical_failures}

## Recomendações

1. Usar a versão {best_version["prompt_version"]} como referência operacional antes de escalar novos prompts.
2. Priorizar melhorias no caso de uso **{worst_use_case["use_case"]}**, porque ele combina menor qualidade média e maior risco de retrabalho.
3. Atacar primeiro a dimensão **{weakest_dimension["dimension"]}**, pois ela aparece como o menor score médio da rubrica.
4. Separar backlog por tipo de problema, não apenas por prompt. Isso evita corrigir sintomas isolados.
5. Manter checagens de qualidade dos dados e calibração de revisores antes de comparar versões de prompt.

## Evidências geradas

- `outputs/kpi_summary.csv`
- `outputs/prompt_version_performance.csv`
- `outputs/quality_by_use_case.csv`
- `outputs/dimension_scores.csv`
- `outputs/issue_distribution.csv`
- `outputs/monthly_quality_trend.csv`
- `outputs/reviewer_calibration.csv`
- `outputs/improvement_backlog.csv`
- `outputs/data_quality_summary.csv`
- `dashboard/ai_response_quality_dashboard.html`
"""

    body_en = f"""# Executive findings - AI Response Quality

## Decision summary

The most important signal is not the average score alone. The useful read combines quality, rework, severity and readiness for use. In the current build, {pct(kpis["release_ready_rate"])} of responses are release-ready without meaningful rework, with an average quality score of {num(kpis["avg_quality_score"], 2)} on a 1-to-5 scale.

## What the data shows

- Reviewed responses: {num(kpis["reviewed_responses"])}
- Average quality score: {num(kpis["avg_quality_score"], 2)}
- Release-ready responses: {pct(kpis["release_ready_rate"])}
- Rework rate: {pct(kpis["rework_rate"])}
- Critical issue rate: {pct(kpis["critical_issue_rate"])}
- Average review time: {num(kpis["avg_review_time_minutes"], 1)} minutes
- Best prompt version: {best_version["prompt_version"]} ({pct(best_version["release_ready_rate"])} release-ready)
- Weakest use case: {worst_use_case["use_case"]} (score {num(worst_use_case["avg_quality_score"], 2)})
- Main issue type: {top_issue["issue_type"]} ({num(top_issue["occurrences"])} occurrences)
- Weakest rubric dimension: {weakest_dimension["dimension"]} (score {num(weakest_dimension["avg_score"], 2)})
- Critical data quality failures: {critical_failures}

## Recommendations

1. Use version {best_version["prompt_version"]} as the operational reference before scaling new prompts.
2. Prioritize improvements in **{worst_use_case["use_case"]}**, because it combines lower average quality and higher rework risk.
3. Address **{weakest_dimension["dimension"]}** first, because it has the lowest average rubric score.
4. Separate the backlog by issue type, not only by prompt. This avoids fixing isolated symptoms.
5. Keep data quality checks and reviewer calibration in place before comparing prompt versions.

## Generated evidence

- `outputs/kpi_summary.csv`
- `outputs/prompt_version_performance.csv`
- `outputs/quality_by_use_case.csv`
- `outputs/dimension_scores.csv`
- `outputs/issue_distribution.csv`
- `outputs/monthly_quality_trend.csv`
- `outputs/reviewer_calibration.csv`
- `outputs/improvement_backlog.csv`
- `outputs/data_quality_summary.csv`
- `dashboard/ai_response_quality_dashboard.html`
"""

    (OUTPUT_DIR / "executive_findings.md").write_text(body_en, encoding="utf-8")
    (OUTPUT_DIR / "executive_findings.pt-BR.md").write_text(body_pt, encoding="utf-8")


def write_dashboard(data: dict[str, list[dict[str, object]]]) -> None:
    dashboard_json = json.dumps(data, ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Response Quality Dashboard</title>
  <style>
    :root {{
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #617089;
      --line: #d9e0eb;
      --blue: #2563eb;
      --cyan: #0891b2;
      --green: #16a34a;
      --amber: #d97706;
      --red: #dc2626;
      --shadow: 0 18px 45px rgba(23, 32, 51, 0.09);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 28px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
      gap: 18px;
      margin-bottom: 18px;
    }}
    .panel, .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    .hero-copy, .hero-side {{ padding: 24px; }}
    .eyebrow {{
      color: var(--cyan);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 8px 0 10px;
      font-size: clamp(28px, 4vw, 46px);
      line-height: 1.04;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0;
      font-size: 18px;
      letter-spacing: 0;
    }}
    p {{ margin: 0; color: var(--muted); font-size: 16px; }}
    .decision {{
      border-left: 4px solid var(--blue);
      padding-left: 14px;
    }}
    .decision strong {{ display: block; margin-bottom: 6px; font-size: 16px; }}
    .note {{ color: var(--muted); font-size: 13px; }}
    .grid {{ display: grid; gap: 16px; }}
    .kpi-grid {{
      grid-template-columns: repeat(4, minmax(0, 1fr));
      margin-bottom: 16px;
    }}
    .card {{ padding: 18px; min-height: 126px; }}
    .card small {{ display: block; color: var(--muted); font-weight: 800; margin-bottom: 10px; }}
    .card strong {{ display: block; font-size: 30px; line-height: 1; }}
    .card span {{ display: block; margin-top: 10px; color: var(--muted); }}
    .two-col {{ grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); margin-bottom: 16px; }}
    .panel {{ padding: 20px; min-width: 0; }}
    .panel-header {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 14px;
    }}
    .bars {{ display: grid; gap: 11px; }}
    .bar-row {{
      display: grid;
      grid-template-columns: 160px minmax(130px, 1fr) 82px;
      gap: 12px;
      align-items: center;
    }}
    .bar-label {{ font-weight: 800; }}
    .track {{
      height: 22px;
      border: 1px solid #e4e9f2;
      border-radius: 5px;
      background: #edf2f8;
      overflow: hidden;
    }}
    .fill {{ height: 100%; border-radius: 5px; background: linear-gradient(90deg, var(--blue), var(--cyan)); }}
    .bar-value {{ text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 10px 8px;
      border-bottom: 1px solid #e8edf5;
      text-align: left;
      white-space: nowrap;
    }}
    th {{
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
    }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .trend {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
      gap: 8px;
      align-items: end;
      min-height: 220px;
    }}
    .trend-col {{
      display: grid;
      gap: 8px;
      align-items: end;
      min-height: 200px;
    }}
    .trend-bar {{
      width: 100%;
      min-height: 8px;
      border-radius: 5px 5px 2px 2px;
      background: linear-gradient(180deg, var(--green), var(--cyan));
    }}
    .trend-col span {{ color: var(--muted); font-size: 12px; text-align: center; }}
    .sources {{ margin-top: 16px; color: var(--muted); font-size: 12px; }}
    @media (max-width: 920px) {{
      main {{ padding: 16px; }}
      .hero, .two-col, .kpi-grid {{ grid-template-columns: 1fr; }}
      .bar-row {{ grid-template-columns: 1fr; gap: 6px; }}
      .bar-value {{ text-align: left; }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="hero-copy panel">
        <div class="eyebrow">AI Operations Case | Quality Evaluation</div>
        <h1>Qualidade de respostas de IA</h1>
        <p>Dashboard reprodutível para acompanhar score de qualidade, prontidão para uso, retrabalho, problemas críticos e evolução por versão de prompt.</p>
      </div>
      <aside class="hero-side panel">
        <div class="decision">
          <strong>Leitura executiva</strong>
          <span id="decisionText">Carregando síntese...</span>
        </div>
        <p class="note" style="margin-top:14px">Fonte: dados sintéticos gerados por Python, avaliados por rubrica de cinco dimensões e modelados em DuckDB.</p>
      </aside>
    </section>

    <section class="grid kpi-grid" id="kpis"></section>

    <section class="grid two-col">
      <div class="panel">
        <div class="panel-header">
          <h2>Versões de prompt</h2>
          <span class="note">Prontas para uso</span>
        </div>
        <div class="bars" id="promptBars"></div>
      </div>
      <div class="panel">
        <div class="panel-header">
          <h2>Dimensões da rubrica</h2>
          <span class="note">Score médio, escala 1-5</span>
        </div>
        <div class="bars" id="dimensionBars"></div>
      </div>
    </section>

    <section class="grid two-col">
      <div class="panel">
        <div class="panel-header">
          <h2>Qualidade por caso de uso</h2>
          <span class="note">Menores scores primeiro</span>
        </div>
        <table id="useCaseTable"></table>
      </div>
      <div class="panel">
        <div class="panel-header">
          <h2>Principais problemas</h2>
          <span class="note">Exclui respostas sem problema</span>
        </div>
        <table id="issueTable"></table>
      </div>
    </section>

    <section class="grid two-col">
      <div class="panel">
        <div class="panel-header">
          <h2>Tendência mensal</h2>
          <span class="note">Score médio por mês</span>
        </div>
        <div class="trend" id="trend"></div>
      </div>
      <div class="panel">
        <div class="panel-header">
          <h2>Backlog de melhoria</h2>
          <span class="note">Prioridade por risco e retrabalho</span>
        </div>
        <table id="backlogTable"></table>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Calibração dos revisores</h2>
        <span class="note">Volume, média, dispersão e tempo de revisão</span>
      </div>
      <table id="reviewerTable"></table>
    </section>

    <section class="sources">
      <strong>Metodologia:</strong> respostas são avaliadas em accuracy, completeness, clarity, tone fit e actionability. Uma resposta pronta para uso precisa estar aprovada, ter score >= 4,0 e não ter severidade alta. O dashboard foi gerado por `scripts/build_outputs.py`; os extratos revisados ficam em `outputs/`.
    </section>
  </main>

  <script id="dashboardData" type="application/json">{dashboard_json}</script>
  <script>
    const data = JSON.parse(document.getElementById("dashboardData").textContent);
    const fmt = new Intl.NumberFormat("pt-BR");
    const pct = (v) => `${{(Number(v || 0) * 100).toFixed(1).replace(".", ",")}}%`;
    const score = (v) => Number(v || 0).toFixed(2).replace(".", ",");
    const num = (v) => fmt.format(Number(v || 0));
    const kpi = data.kpi_summary[0];

    const bestVersion = [...data.prompt_version_performance].sort((a, b) => Number(b.release_ready_rate || 0) - Number(a.release_ready_rate || 0))[0];
    const worstCase = [...data.quality_by_use_case].sort((a, b) => Number(a.avg_quality_score || 0) - Number(b.avg_quality_score || 0))[0];
    document.getElementById("decisionText").textContent =
      `A versão ${{bestVersion.prompt_version}} tem a melhor prontidão para uso (${{pct(bestVersion.release_ready_rate)}}). O ponto mais frágil está em "${{worstCase.use_case}}", com score médio ${{score(worstCase.avg_quality_score)}}.`;

    const kpis = [
      ["Respostas", num(kpi.reviewed_responses), "Amostra revisada"],
      ["Score médio", score(kpi.avg_quality_score), "Escala de 1 a 5"],
      ["Prontas para uso", pct(kpi.release_ready_rate), "Aprovadas, score >= 4, sem severidade alta"],
      ["Retrabalho", pct(kpi.rework_rate), "Respostas que precisam ajuste"]
    ];
    document.getElementById("kpis").innerHTML = kpis.map(([label, value, sub]) => `
      <article class="card"><small>${{label}}</small><strong>${{value}}</strong><span>${{sub}}</span></article>
    `).join("");

    function bars(el, rows, labelKey, valueKey, formatter, maxValue = null, color = "linear-gradient(90deg, var(--blue), var(--cyan))") {{
      const max = maxValue ?? Math.max(...rows.map((row) => Number(row[valueKey] || 0)));
      document.getElementById(el).innerHTML = rows.map((row) => {{
        const value = Number(row[valueKey] || 0);
        const width = Math.max(2, value / max * 100);
        return `<div class="bar-row">
          <div class="bar-label">${{row[labelKey]}}</div>
          <div class="track"><div class="fill" style="width:${{width}}%; background:${{color}}"></div></div>
          <div class="bar-value">${{formatter(value)}}</div>
        </div>`;
      }}).join("");
    }}

    bars("promptBars", data.prompt_version_performance, "prompt_version", "release_ready_rate", pct, 1, "linear-gradient(90deg, var(--green), var(--cyan))");
    bars("dimensionBars", data.dimension_scores, "dimension", "avg_score", score, 5);

    function table(el, headers, rows) {{
      document.getElementById(el).innerHTML = `
        <thead><tr>${{headers.map((h) => `<th class="${{h.num ? "num" : ""}}">${{h.label}}</th>`).join("")}}</tr></thead>
        <tbody>${{rows.map((row) => `<tr>${{headers.map((h) => `<td class="${{h.num ? "num" : ""}}">${{h.format ? h.format(row[h.key]) : row[h.key]}}</td>`).join("")}}</tr>`).join("")}}</tbody>
      `;
    }}

    table("useCaseTable", [
      {{ key: "use_case", label: "Caso de uso" }},
      {{ key: "reviewed_responses", label: "N", num: true, format: num }},
      {{ key: "avg_quality_score", label: "Score", num: true, format: score }},
      {{ key: "release_ready_rate", label: "Prontas", num: true, format: pct }},
      {{ key: "avg_review_time_minutes", label: "Min", num: true, format: (v) => Number(v || 0).toFixed(1).replace(".", ",") }}
    ], data.quality_by_use_case);

    table("issueTable", [
      {{ key: "issue_type", label: "Problema" }},
      {{ key: "severity", label: "Sev." }},
      {{ key: "occurrences", label: "Ocorr.", num: true, format: num }},
      {{ key: "share_of_reviews", label: "Share", num: true, format: pct }}
    ], data.issue_distribution.slice(0, 8));

    table("backlogTable", [
      {{ key: "use_case", label: "Caso" }},
      {{ key: "prompt_version", label: "Versão" }},
      {{ key: "avg_quality_score", label: "Score", num: true, format: score }},
      {{ key: "release_ready_rate", label: "Prontas", num: true, format: pct }},
      {{ key: "not_approved_cases", label: "Não aprov.", num: true, format: num }}
    ], data.improvement_backlog.slice(0, 8));

    table("reviewerTable", [
      {{ key: "reviewer_id", label: "Revisor" }},
      {{ key: "reviewed_responses", label: "N", num: true, format: num }},
      {{ key: "avg_quality_score", label: "Score médio", num: true, format: score }},
      {{ key: "score_stddev", label: "Desvio", num: true, format: score }},
      {{ key: "avg_review_time_minutes", label: "Min/revisão", num: true, format: (v) => Number(v || 0).toFixed(1).replace(".", ",") }},
      {{ key: "rework_rate", label: "Retrabalho", num: true, format: pct }}
    ], data.reviewer_calibration);

    const trendRows = data.monthly_quality_trend;
    document.getElementById("trend").innerHTML = trendRows.map((row) => {{
      const height = Math.max(8, Number(row.avg_quality_score || 0) / 5 * 190);
      return `<div class="trend-col">
        <div class="trend-bar" style="height:${{height}}px"></div>
        <span>${{row.response_month}}<br><strong>${{score(row.avg_quality_score)}}</strong></span>
      </div>`;
    }}).join("");
  </script>
</body>
</html>
"""
    pt_html = html
    replacements = [
        ('<html lang="pt-BR">', '<html lang="en">'),
        ("Qualidade de respostas de IA", "AI Response Quality"),
        (
            "Dashboard reprodutível para acompanhar score de qualidade, prontidão para uso, retrabalho, problemas críticos e evolução por versão de prompt.",
            "Reproducible dashboard to monitor quality score, release readiness, rework, critical issues and evolution by prompt version.",
        ),
        ("Leitura executiva", "Executive read"),
        ("Carregando síntese...", "Loading summary..."),
        (
            "Fonte: dados sintéticos gerados por Python, avaliados por rubrica de cinco dimensões e modelados em DuckDB.",
            "Source: synthetic data generated with Python, evaluated through a five-dimension rubric and modeled in DuckDB.",
        ),
        ("Versões de prompt", "Prompt versions"),
        ("Prontas para uso", "Release-ready"),
        ("Dimensões da rubrica", "Rubric dimensions"),
        ("Score médio, escala 1-5", "Average score, 1-5 scale"),
        ("Qualidade por caso de uso", "Quality by use case"),
        ("Menores scores primeiro", "Lowest scores first"),
        ("Principais problemas", "Main issues"),
        ("Exclui respostas sem problema", "Excludes responses with no issue"),
        ("Tendência mensal", "Monthly trend"),
        ("Score médio por mês", "Average score by month"),
        ("Backlog de melhoria", "Improvement backlog"),
        ("Prioridade por risco e retrabalho", "Priority by risk and rework"),
        ("Calibração dos revisores", "Reviewer calibration"),
        ("Volume, média, dispersão e tempo de revisão", "Volume, average, dispersion and review time"),
        (
            "<strong>Metodologia:</strong> respostas são avaliadas em accuracy, completeness, clarity, tone fit e actionability. Uma resposta pronta para uso precisa estar aprovada, ter score >= 4,0 e não ter severidade alta. O dashboard foi gerado por `scripts/build_outputs.py`; os extratos revisados ficam em `outputs/`.",
            "<strong>Methodology:</strong> responses are evaluated on accuracy, completeness, clarity, tone fit and actionability. A release-ready response must be approved, have score >= 4.0 and have no high severity. The dashboard is generated by `scripts/build_outputs.py`; reviewed extracts are available in `outputs/`.",
        ),
        ('new Intl.NumberFormat("pt-BR")', 'new Intl.NumberFormat("en-US")'),
        ('toFixed(1).replace(".", ",")', "toFixed(1)"),
        ('toFixed(2).replace(".", ",")', "toFixed(2)"),
        (
            "A versão ${{bestVersion.prompt_version}} tem a melhor prontidão para uso (${{pct(bestVersion.release_ready_rate)}}). O ponto mais frágil está em \"${{worstCase.use_case}}\", com score médio ${{score(worstCase.avg_quality_score)}}.",
            "Version ${{bestVersion.prompt_version}} has the strongest readiness (${{pct(bestVersion.release_ready_rate)}}). The weakest point is \"${{worstCase.use_case}}\", with average score ${{score(worstCase.avg_quality_score)}}.",
        ),
        (
            'A versão ${bestVersion.prompt_version} tem a melhor prontidão para uso (${pct(bestVersion.release_ready_rate)}). O ponto mais frágil está em "${worstCase.use_case}", com score médio ${score(worstCase.avg_quality_score)}.',
            'Version ${bestVersion.prompt_version} has the strongest readiness (${pct(bestVersion.release_ready_rate)}). The weakest point is "${worstCase.use_case}", with average score ${score(worstCase.avg_quality_score)}.',
        ),
        ('["Respostas", num(kpi.reviewed_responses), "Amostra revisada"]', '["Responses", num(kpi.reviewed_responses), "Reviewed sample"]'),
        ('["Score médio", score(kpi.avg_quality_score), "Escala de 1 a 5"]', '["Average score", score(kpi.avg_quality_score), "1 to 5 scale"]'),
        ('["Prontas para uso", pct(kpi.release_ready_rate), "Aprovadas, score >= 4, sem severidade alta"]', '["Release-ready", pct(kpi.release_ready_rate), "Approved, score >= 4, no high severity"]'),
        ('["Retrabalho", pct(kpi.rework_rate), "Respostas que precisam ajuste"]', '["Rework", pct(kpi.rework_rate), "Responses needing adjustment"]'),
        ("Caso de uso", "Use case"),
        ("Prontas", "Ready"),
        ("Problema", "Issue"),
        ("Ocorr.", "Occurr."),
        ("Caso", "Use case"),
        ("Versão", "Version"),
        ("Não aprov.", "Not appr."),
        ("Revisor", "Reviewer"),
        ("Score médio", "Average score"),
        ("Desvio", "Std dev"),
        ("Min/revisão", "Min/review"),
        ("Retrabalho", "Rework"),
    ]
    en_html = pt_html
    for source, target in replacements:
        en_html = en_html.replace(source, target)

    (DASHBOARD_DIR / "ai_response_quality_dashboard_pt-BR.html").write_text(pt_html, encoding="utf-8")
    (DASHBOARD_DIR / "ai_response_quality_dashboard_en.html").write_text(en_html, encoding="utf-8")
    (DASHBOARD_DIR / "ai_response_quality_dashboard.html").write_text(en_html, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    generate_ai_quality_data()
    con = duckdb.connect(str(DB_PATH))
    try:
        create_model(con)
        outputs = query_outputs(con)
        write_outputs(outputs)
    finally:
        con.close()

    print(f"Outputs written to {OUTPUT_DIR}")
    print(f"Dashboard written to {DASHBOARD_DIR / 'ai_response_quality_dashboard.html'}")


if __name__ == "__main__":
    main()
