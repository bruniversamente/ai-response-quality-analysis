# Regras de negócio

## Escopo

O projeto simula uma operação de avaliação de respostas geradas por IA para uso interno. As respostas apoiam resumos, classificações, rascunhos e explicações de dados.

## Unidade de avaliação

Cada linha em `responses.csv` representa uma resposta gerada por IA. Cada resposta deve ter exatamente uma avaliação em `evaluations.csv`.

## Score de qualidade

O score final é a média de cinco dimensões:

```text
quality_score = (accuracy + completeness + clarity + tone + actionability) / 5
```

## Resposta pronta para uso

Uma resposta é considerada pronta para uso quando:

```text
final_status = Approved
quality_score >= 4.0
severity <> High
```

Essa regra é mais rigorosa que olhar apenas o status final, porque impede que uma resposta aprovada com score baixo ou severidade alta entre como pronta.

## Taxa de prontidão para uso

```text
release_ready_rate = release_ready_responses / reviewed_responses
```

## Taxa de retrabalho

```text
rework_rate = responses_needing_rework / reviewed_responses
```

## Taxa de problema crítico

```text
critical_issue_rate = high_severity_issues / reviewed_responses
```

## Comparação de versões de prompt

Versões de prompt devem ser comparadas por:

- score médio de qualidade;
- taxa de prontidão para uso;
- taxa de retrabalho;
- taxa de problema crítico;
- tempo médio de revisão;
- distribuição de tipos de problema.

## Calibração de revisores

Revisores devem ser monitorados por volume, score médio, dispersão de score, tempo médio de revisão e taxa de retrabalho. Grandes diferenças entre revisores podem indicar critério inconsistente.

## Filtros e cuidados

- Apenas respostas com avaliação devem entrar nos KPIs de qualidade.
- Respostas sem avaliação devem ser sinalizadas.
- Scores devem estar entre 1 e 5.
- Respostas aprovadas com severidade alta devem ser revisadas novamente.
- Respostas aprovadas com score abaixo de 4,0 devem ser tratadas como alerta.
