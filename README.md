# Documentação: Deviante

Vault Obsidian e documentação do projeto **Deviante** (suporte à decisão em manutenção industrial).

## Abordagem de documentação

A documentação de arquitetura segue o template **[arc42](https://arc42.org)** —
as 12 seções canônicas, de *Introdução e Metas* a *Riscos e Dívida Técnica*.

arc42 é a **estrutura**; **C4** é a camada de **visualização** da arquitetura;
**UML / BPMN** cobrem comportamentos e processos específicos. Não existe uma
seção "C4" separada — cada diagrama vive **dentro da seção arc42 que ele
explica** (arc42 recomenda evitar redundância entre as visões):

| C4 | Onde entra no arc42 |
|----|---------------------|
| L1 · System Context | 3. Contexto e Escopo |
| L2 · Container | 5. Blocos de Construção — Nível 1 |
| L3 · Component | 5. Blocos de Construção — Nível 2 |
| Dynamic / UML Sequence | 6. Runtime |
| Deployment | 7. Implantação |

Todos os diagramas são **Mermaid** embutidos como ` ```mermaid ` no `arc42.md`,
então versionam como texto e renderizam direto no site.

## Repositórios e artefatos

| Artefato | GitHub / link | Pasta local |
|----------|---------------|-------------|
| API (+ mining) | [deviante-api](https://github.com/aland3r/deviante-api) — `[[S1]]` | `../api/` |
| Web | [deviante-web](https://github.com/aland3r/deviante-web) — `[[S2]]` | `../web/` |

**Entrega PIBITI:** relatório final em `PIBITI26_RelatorioFinal_Alander.pdf` (local, não versionado — ver seção *Versionamento* abaixo).

## Estrutura

```
deviante/docs/
├── PIBITI26_RelatorioFinal_Alander.pdf   # relatório final (local only)
├── UX/                     # discovery ORCA + specs de objeto
│   ├── OBJECTS.md
│   ├── RELATIONSHIPS.md
│   ├── CTAs.md
│   ├── ATTRIBUTES.md
│   └── orca/               # 1–5: Object/Relationship/CTA/Attributes Discovery, Object Requirements
├── architecture/           # arc42 (diagramas C4/UML embutidos)
│   └── arc42.md            # documento arc42 (12 seções + Mermaid inline)
└── referencias bibliográficas/   # literatura + repositorios (S1–S6) — local only
```

## Versionamento

Só `.md` vai pro GitHub. PDFs (relatório final e a literatura em
`referencias bibliográficas/`) ficam só na sua máquina — ver `.gitignore`.

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
