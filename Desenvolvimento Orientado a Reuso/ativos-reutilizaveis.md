# Ativos reutilizáveis do Deviante

O Deviante é uma linha de produto: um núcleo comum entregue a várias empresas clientes (Alfa, Beta, Gama e Delta), cada uma numa variante escolhida por configuração. Esta página lista os ativos desse núcleo. Eles estão classificados pelos quatro tipos de artefato de domínio de Pohl et al. (2005): requisitos, arquitetura, componentes e testes. Cada ativo diz onde está, o que é comum a todos os clientes e qual é o seu ponto de variação.

## Ativos

São seis ativos. Juntos, cobrem os quatro tipos de artefato de domínio: requisito, arquitetura, componente e teste.

| # | Ativo | Tipo | Onde está | Comum a todo cliente | Ponto de variação |
|---|---|---|---|---|---|
| 1 | Modelo de variabilidade e requisitos marcados como comuns, opcionais ou exclusivos (tabela abaixo) | Requisito | `defesa/variabilidade.md` §0; `deviante-api/src/main/resources/application.yaml` (`productLine`); `architecture/arc42.md` §1.2 | Features e RFs de processo, log, grafo e análise de drift | Plano (módulo de manutenção) e funções exclusivas (CSV) de cada empresa |
| 2 | Arquitetura de referência e modelo de dados multiempresa | Arquitetura | `architecture/arc42.md` (C4, ADR 01–10); tabela `deviante.businesses` + `business_id` obrigatório em processo, análise, atividade, máquina, monitoramento e agenda | Core, mining, web e o esquema do banco | Dados de cada empresa |
| 3 | Núcleo da linha de produto no Core: `ProductLine`, `ClientVariant`, `FeatureGate`, `CompanyScope` e `AppConfig` | Componente | `deviante-api/src/main/kotlin/variability/ProductLine.kt`, `Routing.kt`, `AppConfig.kt` | Mecanismo de variantes, filtro por empresa, 401 e 403 | Variante lida da configuração, sem recompilar; empresa e papel do usuário |
| 4 | Motor de análise: `AnalysisEngine`, `IpddAdwinAdapter` → `DriftDetector` e `Pm4pyGraphAdapter` → `GraphMiner` | Componente | `deviante-api/mining/app/` | IPDD/ADWIN da pesquisa e pm4py, usados sem alteração | δ, tratamento (bruto ou tratado), atividades analisadas e o log de cada processo |
| 5 | Componentes de interface: `FormModal` e campos, base do Observer (`Subject`), pontos de variação (`hasFeature`, `FeatureRoute`, `canDelete`, `canManageCatalog`, `CatalogRoute`) e tokens de design | Componente | `deviante-web/src/components/ui/FormModal.jsx`, `src/lib/subject.js`, `src/lib/features.js`, `src/lib/permissions.js`, `src/components/auth/`, `src/index.css` | Esqueleto dos formulários, assinar e notificar, menu e rotas, tokens semânticos | Campos de cada CRUD, telas que observam, plano e papel do usuário, tema escuro ou claro |
| 6 | Testes automatizados e bases de teste | Teste | `deviante-api/src/test/kotlin` (7 classes), `deviante-api/mining/tests` (6 módulos), `Datasets/Alfa` (4 logs XES) | Padrões, linha de produto e exclusão | Resultado esperado por base: 0, 4, 7 e 9 desvios |

## Requisitos comuns, opcionais e exclusivos

| Tipo | Requisitos | Quem recebe |
|---|---|---|
| Comum | RF-01, RF-02, RF-03, RF-05, RF-06, RF-08, RF-09, RF-10, RF-14, RF-15 | Todo cliente |
| Comum, só para o administrador | Catálogo de atividades e tela de Operações (RF-07) | Papel administrador de qualquer cliente |
| Opcional (plano Manutenção) | RF-11, RF-12, RF-13, RF-16, RF-17, RF-18 | Alfa e Gama |
| Exclusivo (por cliente) | Exportar a agenda de manutenção em CSV | Alfa |

## Variantes e os ativos que cada uma usa

| Empresa | Plano | Exclusivas | O que muda na tela | Ativos que resolvem a variação |
|---|---|---|---|---|
| Alfa | Manutenção | CSV | Menu completo e "Exportar CSV" em Agendamentos | 1, 3, 5 |
| Beta | Essencial | nenhuma | Sem Equipamentos e Agendamentos no menu; a rota volta ao painel | 1, 3, 5 |
| Gama | Manutenção | nenhuma | Agendamentos sem "Exportar CSV" | 1, 3, 5 |
| Delta | Essencial | nenhuma | Igual à Beta | 1, 3, 5 |

Em todas as empresas o papel também varia a tela. Só administrador e gestor excluem registros, e só o administrador mantém o catálogo de atividades (ativos 3 e 5). Os dados de cada empresa ficam separados pelo ativo 2 e filtrados pelo ativo 3.

## Telas e os ativos que elas reutilizam

| Tela | Ativos | Variação |
|---|---|---|
| Login (Modo Protótipo, setas de empresa) | 3 | Empresa escolhida |
| Projetos (painel de processos) | 2, 3, 5 | Administrador vê todas as empresas |
| Canvas do processo e upload de log | 2, 3, 4, 5 | Gestor mapeia só para atividades do catálogo |
| Análise de drift | 3, 4, 5, 6 | δ e tratamento |
| Atividades e Operações | 2, 3, 5 | Só administrador |
| Equipamentos | 1, 2, 3, 5 | Só plano Manutenção |
| Agendamentos | 1, 2, 3, 5 | Só plano Manutenção; CSV só na Alfa |
