# Blueprint do dashboard

Este documento descreve o dashboard principal do case AI Response Quality.

Artefato entregue:

```text
dashboard/ai_response_quality_dashboard.html
```

## Objetivo

Permitir que recrutadores, líderes de produto, operações e IA entendam rapidamente:

- quantas respostas foram revisadas;
- qual é o nível médio de qualidade;
- qual percentual está pronto para uso;
- qual versão de prompt performa melhor;
- quais casos de uso concentram mais risco;
- quais tipos de problema devem entrar no backlog;
- se revisores estão relativamente calibrados;
- se há problemas de qualidade nos dados da avaliação.

## Estrutura visual

### 1. Leitura executiva

Resumo curto com a melhor versão de prompt e o caso de uso mais frágil.

### 2. Cards principais

- Respostas revisadas
- Score médio
- Taxa de prontidão para uso
- Taxa de retrabalho

### 3. Versões de prompt

Gráfico de barras horizontais com taxa de respostas prontas para uso por versão.

### 4. Dimensões da rubrica

Gráfico de barras com score médio por dimensão: accuracy, completeness, clarity, tone fit e actionability.

### 5. Qualidade por caso de uso

Tabela com score médio, amostra, taxa de prontidão e tempo médio de revisão.

### 6. Principais problemas

Tabela com tipo de problema, severidade, ocorrências e participação nas revisões.

### 7. Tendência mensal

Resumo visual do score médio por mês.

### 8. Backlog de melhoria

Tabela priorizada por risco, retrabalho e baixa taxa de prontidão.

### 9. Calibração de revisores

Tabela com volume, score médio, dispersão, tempo médio e taxa de retrabalho por revisor.

## Princípios de design

- O topo deve responder se a operação está pronta para escalar.
- Métricas devem mostrar denominador e regra de cálculo.
- A comparação de prompt deve usar taxa de prontidão, não apenas nota média.
- O backlog deve ser operacional: caso de uso, versão, score, prontidão e não aprovadas.
- A metodologia deve aparecer no rodapé para explicar a regra de resposta pronta para uso.
