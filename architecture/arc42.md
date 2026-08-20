# Arquitetura do Deviante — arc42

> **Nota:** este é o esqueleto arc42 (12 seções). Os textos abaixo são
> _placeholders substituíveis_ — escreva o conteúdo real direto no Obsidian e
> dê push; o site atualiza sozinho. Os diagramas ficam **embutidos no meio das
> seções** como blocos ` ```mermaid ` (C4 / UML) e renderizam inline.

---

## 1. Introdução e Metas

_Substituir: visão geral do sistema e o que ele resolve._

### 1.1 Visão Geral de Requisitos

_Substituir: resumo dos requisitos funcionais essenciais — as principais
funcionalidades que o Deviante precisa entregar e por quê._

### 1.2 Metas de Qualidade

| Prioridade | Meta de qualidade | Cenário (substituir) |
|-----------|-------------------|----------------------|
| 1 | _(ex.: Precisão de detecção)_ | _…_ |
| 2 | _(ex.: Latência)_ | _…_ |
| 3 | _(ex.: Usabilidade)_ | _…_ |

### 1.3 Stakeholders

| Papel | Contato | Expectativa (substituir) |
|-------|---------|--------------------------|
| _(ex.: Operador)_ | _…_ | _…_ |
| _(ex.: Analista de manutenção)_ | _…_ | _…_ |
| _(ex.: Gestor de manutenção)_ | _…_ | _…_ |

## 2. Restrições da Arquitetura

_Substituir: restrições técnicas, organizacionais e convenções que limitam as
decisões (stack fixa, normas, prazos, etc.)._

## 3. Contexto e Escopo

_Substituir: fronteira do sistema, atores externos e interfaces._

### 3.1 Contexto de negócio

**C4 — Nível 1 · System Context** — sistema, usuários e sistemas externos.

```mermaid
flowchart TB
    operador([Operador / Analista de manutenção])
    deviante["Deviante<br/>Suporte à decisão em manutenção industrial"]
    origem[("Sistema de origem<br/>event log · XES / CSV")]

    operador -->|monitora processos e recebe alertas| deviante
    deviante -->|lê event logs| origem
```

## 4. Estratégia da Solução

_Substituir: decisões-chave de tecnologia e de arquitetura que endereçam as
metas de qualidade — resumo antes do detalhe._

## 5. Visão de Blocos de Construção

_Substituir: decomposição estática do sistema. A Building Block View do arc42 é
hierárquica — mesma lógica de zoom do C4: o Nível 1 decompõe o sistema, o Nível 2
abre um bloco em seus componentes._

### 5.1 Nível 1 — Visão geral do sistema

**C4 — Nível 2 · Container** — frontend, backend/API, banco e serviços.

```mermaid
flowchart TB
    web["Web App<br/>React"]
    api["API<br/>Ktor"]
    mining["Mineração de processos<br/>ADWIN · PM4Py"]
    db[("Supabase<br/>Postgres")]

    web -->|HTTPS / REST| api
    api -->|SQL| db
    api -->|detecção de drift| mining
```

### 5.2 Nível 2 — API

**C4 — Nível 3 · Component** — componentes internos do container da API.

```mermaid
flowchart TB
    subgraph API["API — Ktor"]
        parser["Parser de event log<br/>XES / CSV"]
        detector["Detector de drift<br/>ADWIN"]
        predictor["Preditor de manutenção"]
    end
    parser --> detector --> predictor
```

## 6. Visão de Runtime

_Substituir: cenários dinâmicos importantes (ex.: upload de log → detecção de
drift → alerta). Aqui cabe C4 Dynamic, UML de sequência, atividade ou BPMN — o
placeholder abaixo é uma sequência UML._

```mermaid
sequenceDiagram
    actor U as Operador
    participant W as Web App
    participant A as API
    participant M as Mineração (ADWIN)
    U->>W: envia event log
    W->>A: POST /processes
    A->>M: detectar drift
    M-->>A: pontos de mudança
    A-->>W: resultado
    W-->>U: alerta de manutenção
```

## 7. Visão de Implantação

_Substituir: mapeamento para infraestrutura e os canais entre os nós._

**C4 — Deployment** — onde os containers executam.

```mermaid
flowchart TB
    browser([Browser])
    subgraph cloud["Cloud"]
        fe["Frontend<br/>Vercel"]
        api["API<br/>Fly.io"]
        db[("Supabase<br/>Postgres")]
    end
    browser -->|HTTPS| fe
    fe -->|REST| api
    api -->|SQL| db
```

## 8. Conceitos Transversais

_Substituir: padrões recorrentes — modelo de domínio, segurança/autenticação,
i18n, tratamento de erros, observabilidade._

## 9. Decisões de Arquitetura

_Substituir: registro de decisões (ADRs) relevantes, com contexto e
consequências._

## 10. Requisitos de Qualidade

_Substituir: árvore de qualidade e cenários de qualidade detalhados (refina a
seção 1)._

## 11. Riscos e Dívida Técnica

_Substituir: riscos conhecidos e dívida técnica, ordenados por prioridade._

## 12. Glossário

| Termo | Definição (substituir) |
|-------|------------------------|
| _Drift_ | _…_ |
| _Event log_ | _…_ |
| _Sojourn time_ | _…_ |
