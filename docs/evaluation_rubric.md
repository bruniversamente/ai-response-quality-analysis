# Rubrica de avaliação

Esta rubrica define como as respostas de IA são avaliadas no projeto.

Cada resposta recebe nota de 1 a 5 em cinco dimensões. A nota final é a média simples dessas dimensões.

## Escala de pontuação

| Nota | Significado | Interpretação operacional |
|---|---|---|
| 1 | Muito ruim | Exige reescrita completa. |
| 2 | Fraca | Tem vários problemas e utilidade limitada. |
| 3 | Aceitável com revisão | Ajuda parcialmente, mas não deve ser usada sem ajuste. |
| 4 | Boa | Pode ser usada com ajustes pequenos ou revisão leve. |
| 5 | Excelente | Pronta para uso no contexto esperado. |

## Dimensões

### Accuracy

Avalia se a resposta está correta e alinhada ao contexto disponível.

Sinais de baixa nota:

- afirmação incorreta;
- conclusão sem suporte;
- classificação errada;
- dado ou critério inventado.

### Completeness

Avalia se a resposta cobre as partes relevantes da solicitação.

Sinais de baixa nota:

- ignora parte importante do pedido;
- deixa de mencionar restrição relevante;
- resume demais quando o caso exige detalhe;
- não responde a pergunta principal.

### Clarity

Avalia se a resposta é fácil de entender, estruturada e direta.

Sinais de baixa nota:

- texto confuso;
- organização fraca;
- excesso de rodeios;
- mistura de assuntos sem hierarquia.

### Tone fit

Avalia se o tom combina com o caso de uso.

Sinais de baixa nota:

- tom informal demais para contexto executivo;
- tom rígido demais para atendimento;
- falta de empatia quando necessária;
- linguagem desalinhada ao público.

### Actionability

Avalia se a resposta ajuda alguém a tomar uma próxima ação clara.

Sinais de baixa nota:

- recomendação genérica;
- falta de critério de prioridade;
- ausência de próximo passo;
- resposta correta, mas pouco útil para decisão.

## Status final

- `Approved`: resposta pode ser usada sem mudança relevante.
- `Needs Rework`: resposta é aproveitável, mas precisa de ajuste.
- `Rejected`: resposta não deve ser usada.

## Tipos de problema

- `None`
- `Incomplete`
- `Too Generic`
- `Missing Context`
- `Wrong Category`
- `Format Issue`
- `Low Actionability`

## Regra de prontidão para uso

Uma resposta pronta para uso precisa atender aos três critérios:

```text
final_status = Approved
quality_score >= 4.0
severity <> High
```

## Cuidados de avaliação

- Comparar versões de prompt exige a mesma rubrica.
- Revisores precisam estar calibrados para reduzir diferenças de critério.
- Nota média sozinha não basta; severidade, retrabalho e tipo de problema também devem ser analisados.
- Avaliações automatizadas devem ser validadas contra revisão humana antes de uso operacional amplo.
