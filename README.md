# Documentação: Deviante

O **Deviante** é um sistema de suporte à decisão na manutenção industrial. Ele lê o
event log do chão de fábrica, detecta quando o tempo de uma atividade da máquina muda
de comportamento (drift de desempenho, com o IPDD/ADWIN) e transforma esse sinal em
recomendação de manutenção antes da falha.

Este repositório guarda a documentação de arquitetura (arc42 + C4), o discovery de UX
(ORCA) e os scripts que publicam a documentação no site.

## Links principais

| O quê | Onde |
|-------|------|
| Documentação publicada (site) | [deviante.alander.io/documentacao](https://deviante.alander.io/documentacao) |
| Fonte da documentação (Notion) | [Arquitetura: arc42](https://www.notion.so/3f05fc724940819f8655fcd12d1312de), dentro de *IPDD: SEVEN DIMENSIONS* |
| Documento gerado | [`architecture/arc42.md`](architecture/arc42.md) |
| Diagramas C4 avulsos | [`architecture/c4/`](architecture/c4/) |
| Template arc42 (referência oficial) | [docs.arc42.org](https://docs.arc42.org/home/) · [dicas](https://docs.arc42.org/tips/) · [exemplos](https://docs.arc42.org/examples/) |
| Architecture Communication Canvas | [canvas.arc42.org](https://canvas.arc42.org/architecture-communication-canvas) |
| Modelo C4 | [c4model.com](https://c4model.com/) |
| Qualidade de software (metas da §1.2) | [ISO/IEC 25010](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) |

## Como a documentação é feita

1. O grupo escreve no **Notion**: a página *Arquitetura: arc42* tem 12 subpáginas, uma
   por seção do template. O Notion é a fonte de verdade (ADR 07).
2. `scripts/notion_to_md.py` converte as páginas em `architecture/arc42.md`. Imagens e
   avisos internos do Notion não vão para o site.
3. O site lê `architecture/arc42.md` direto da branch `main`; um push publica.
4. O PDF entregue nas disciplinas é gerado a partir do mesmo `.md`.

Os diagramas são **Mermaid** embutidos no `.md`. Cada um fica dentro da seção arc42 que
explica (arc42 recomenda evitar redundância entre as visões):

| C4 | Onde entra no arc42 |
|----|---------------------|
| L1 · System Context | 3. Contexto e Escopo |
| L2 · Container | 5. Blocos de Construção, nível 1 |
| L3 · Component | 5. Blocos de Construção, nível 2 |
| Dynamic / UML Sequence | 6. Runtime |
| Deployment | 7. Implantação |

## Repositórios

| Artefato | GitHub |
|----------|--------|
| Documentação (este) | [deviante-docs](https://github.com/aland3r/deviante-docs) |
| API Core (Kotlin/Ktor) + mining (FastAPI) | [deviante-api](https://github.com/aland3r/deviante-api) |
| Web (React + Vite) | [deviante-web](https://github.com/aland3r/deviante-web) |

## Entregas

| Entrega | Prazo |
|---------|-------|
| Cloud: Entrega 2 (documentação completa) | 15/10/2026 |
| Reuso: projeto completo + prova de autoria | 16/10/2026 |
| PIBITI: apresentação (SEMIC) | 16/10/2026 |
| Cloud: Entrega 3 (arquitetura completa) | 12/11/2026 |

Fonte: banco *Entregas* do Notion.

## Equipe e contatos

**Grupo:** Alander Menezes Arantes de Ávila, Bernardo Creplive Vieira, Emanuelle Skolut
Jose, Murilo Regnier Stange (Engenharia de Software, PUCPR, 6º período).

| Pessoa | Papel | Contato |
|--------|-------|---------|
| Eduardo de Freitas Loures | Orientador PIBITI | eduardo.loures@pucpr.br |
| Manoel Valerio da Silveira Neto | Professor de Arquitetura e Soluções Cloud | manoel.valerio@pucpr.br |
| Tiago Adelino Navarro | Professor de Desenvolvimento Orientado a Reuso | tiago.adelino@pucpr.edu.br |
| Denise M. V. Sato | Autora do framework IPDD | denise.vecino@pucpr.br |
| Luiz F. Picolo | Autor da implementação IPDD/ADWIN | luiz.picolo@pucpr.edu.br |

## Estrutura

```
deviante/docs/
├── PIBITI26_RelatorioFinal_Alander.pdf   # relatório final do PIBITI
├── UX/                     # discovery ORCA + specs de objeto
│   ├── OBJECTS.md
│   ├── RELATIONSHIPS.md
│   ├── CTAs.md
│   ├── ATTRIBUTES.md
│   └── orca/               # 1–5: Object/Relationship/CTA/Attributes Discovery, Object Requirements
├── architecture/           # arc42 (diagramas C4/UML embutidos)
│   ├── arc42.md            # documento arc42 (12 seções + Mermaid inline), gerado do Notion
│   └── c4/                 # diagramas C4 avulsos (.mmd) e render do nível 1
├── scripts/
│   └── notion_to_md.py     # converte as páginas do Notion em arc42.md
└── referencias bibliográficas/   # literatura + repositorios (S1–S6) — local only
```

## Versionamento

A literatura em `referencias bibliográficas/` fica só na máquina local (ver
`.gitignore`). O relatório final do PIBITI está versionado na raiz.

## Obsidian

Abrir **`deviante/docs/`** como vault.

- Objetos / relacionamentos / CTAs / atributos: [[UX/OBJECTS]], [[UX/RELATIONSHIPS]], [[UX/CTAs]], [[UX/ATTRIBUTES]]
- Discovery ORCA (fases 1–5): `UX/orca/`
- Referências bibliográficas + repositórios (S1–S6): `referencias bibliográficas/repositorios/`
- Datasets de pesquisa (Luiz Picolo): ver [§ Datasets de pesquisa](#datasets-de-pesquisa-luiz-picolo) abaixo

## Gestalt (monorepo local)

Esta pasta vive em `c:\gestalt\deviante\docs\` ao lado de `api/` e `web/`.

## Datasets de pesquisa (Luiz Picolo)

*Autoria: L. F. Picolo (datasets + scripts), grupo IPDD/ADWIN · 14/07/2026*

Event logs usados nos experimentos de drift do ADWIN. Empacotados junto com os scripts em `../Adaptive-Detection-of-Performance-Related-Temporal-Drifts-main/`.

**Autor:** Luiz F. Picolo (mestrado — janelamento adaptativo). Regras de ground-truth para os logs sintéticos estão codificadas em `adwin_dataset.py`.

### Resumo

| Coleção | Pasta | Formato | Arquivos | Papel |
|------------|------|--------|-------|------|
| Manufatura sintética | `dataset_manufacturing/` | XES (IEEE 1849) | **121** | Experimentos de drift controlados + baseline estável |
| Torno de chão de fábrica (real) | `real_dataset/` | CSV (`;`) | **1** | Traces reais de um torno em produção (2012) |

Payload XES sintético total: ~**141 MB**.

#### 1. `dataset_manufacturing/` — XES sintético

Gerado com **Fluxicon Disco** (Octane). Processo estilo manufatura, nomes de atividade em inglês (`Raw_Material_Loading`, `Machine_Operating`, …).

Cada log inclui:

- `lifecycle:transition` (`start` / `complete`) — necessário pro sojourn time via PM4Py
- Atributo de trace `Potential_Failure` (logs sintéticos, ausente em `TD.xes`)
- Atividade default monitorada nos scripts: **`Machine_Operating`**

Famílias de nomes (30 arquivos cada + 1 extra):

| Prefixo | Qtd | Drift injetado (ground truth) | Uso |
|--------|-------|-------------------------------|-----|
| **`ST_`** | 30 (`ST_01` … `ST_30`) | **Nenhum** — série estável | Controle negativo / baseline |
| **`DR_`** | 30 (`DR_01` … `DR_30`) | **1 drift** por log no índice de trace `10 + 11×(n−1)` | Ponto de mudança único (ex.: DR_01 → trace 10, DR_02 → 21) |
| **`DR_MS_`** | 30 | **5 drifts** em 0, 100, 200, 300, 400 (+ offset por arquivo) | Múltiplos pontos de mudança |
| **`DR_MS_ST_`** | 30 | **5 drifts** em 20, 60, 100, 140, 180 (offsets escalonados por arquivo) | Múltiplos drifts, padrão escalonado |
| **`TD.xes`** | 1 | Desconhecido (fora de `calculate_real_drifts`) | Log grande; atividades em português (`Atividade`), attrs. `Queda Desempenho`, `Temperatura` — provavelmente export do torno |

Lógica de ground-truth: `../Adaptive-Detection-of-Performance-Related-Temporal-Drifts-main/adwin_dataset.py` → `calculate_real_drifts()`.

Scripts que consomem esses logs:

| Script | Exemplos de arquivo |
|--------|-----------------|
| `main.py` | DR_18, ST_09, DR_MS_13, DR_MS_ST_28 |
| `adwin_streaming.py` | DR_18, DR_MS_13, DR_MS_ST_28 |
| `adwin_dataset.py` | ST_20, DR_20, DR_MS_20, DR_MS_ST_20 (+ métricas de precision/recall) |

PNGs de saída: `resultados_drift/` (criado ao rodar).

#### 2. `real_dataset/` — CSV de chão de fábrica

| Arquivo | Linhas | Tamanho | Período |
|------|------|------|--------|
| **`Prod1Torno.csv`** | ~13 053 eventos | ~0.9 MB | Jan 2012 |

**Separador:** `;` · **Encoding:** UTF-8 (rótulos em português)

Colunas: `Case` (id do trace) · `Atividade` (nome da atividade, ex. `Maquina trabalhando`, `Alimentacao de Maquina`) · `Inicio` (timestamp de início, `DD-MM-YYYY HH:MM:SS`) · `Fim` (timestamp de fim) · `Tempo(s)` (duração em segundos)

**Script:** `adwin_real_dataset.py` — lê o CSV direto (sem PM4Py), monitora a atividade **`Maquina trabalhando`**, grava PNGs em `resultados_drift_real/`.

#### 3. Como isso mapeia pro IPDD

| Necessidade do IPDD | Dataset a usar primeiro |
|---------------|----------------------|
| UC4 upload + parse (XES) | `DR_01.xes` ou `ST_01.xes` (pequeno, comportamento conhecido) |
| UC12 drift (validação sintética) | `DR_*` / `DR_MS_*` com ground truth de `adwin_dataset.py` |
| UC12 drift (realista) | `Prod1Torno.csv` — precisa de path CSV no parser (ainda não conectado) |
| Demo / baseline estável | série `ST_*` |

#### 4. Relacionados

- Scripts: `../Adaptive-Detection-of-Performance-Related-Temporal-Drifts-main/`
- Referência PIBITI: `referencias bibliográficas/repositorios/S3 codigos IPDD ADWIN.md`
