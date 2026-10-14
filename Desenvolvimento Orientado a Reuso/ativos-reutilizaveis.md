# Ativos reutilizáveis do Deviante

O Deviante é uma linha de produto: um núcleo comum entregue a várias empresas clientes (Alfa, Beta, Gama e Delta), cada uma numa variante escolhida por configuração. Esta página lista os ativos desse núcleo. Eles estão agrupados pelos quatro tipos de artefato de domínio de Pohl et al. (2005): requisitos, arquitetura, componentes e testes. Cada ativo diz onde está, o que é comum a todos os clientes e qual é o seu ponto de variação.

## Ativos

| # | Ativo | Tipo | Onde está | Comum a todo cliente | Ponto de variação |
|---|---|---|---|---|---|
| 1 | Requisitos marcados como comuns, opcionais ou exclusivos (tabela abaixo) | Requisito | esta página; `architecture/arc42.md` §1.2 | RFs de processo, log, grafo e análise de drift | RFs do módulo de manutenção (por plano) e exportação CSV (por cliente) |
| 2 | Modelo de variabilidade: features, planos e clientes | Requisito | `defesa/variabilidade.md` §0; `deviante-api/src/main/resources/application.yaml` (`productLine`) | Lista de features | Plano e funções exclusivas de cada empresa |
| 3 | Arquitetura de referência: arc42, C4 e ADR 01–10 | Arquitetura | `architecture/arc42.md` | Core, mining e web | Nenhum; é o ponto de partida de toda instância |
| 4 | Modelo de dados multiempresa | Arquitetura | tabela `deviante.businesses` + `business_id` obrigatório em processo, análise, atividade, máquina, monitoramento e agenda | Esquema | Dados de cada empresa |
| 5 | Linha de produto: `Feature`, `Plan`, `ClientVariant`, `ProductLine` e o plugin `FeatureGate` | Componente | `deviante-api/src/main/kotlin/variability/ProductLine.kt` | Mecanismo de variantes | Variante lida da configuração, sem recompilar |
| 6 | `AppConfig` (Singleton) | Componente | `deviante-api/src/main/kotlin/AppConfig.kt` | Leitura única da configuração | Valores de cada ambiente |
| 7 | `CompanyScope` e autenticação Supabase | Componente | `deviante-api/src/main/kotlin/Routing.kt` | Filtro por empresa, respostas 401 e 403 | Empresa e papel do usuário |
| 8 | Motor de drift: `AnalysisEngine` + `IpddAdwinAdapter` → `DriftDetector` | Componente | `deviante-api/mining/app/analysis_engine.py`, `drift_detector.py` | IPDD/ADWIN da pesquisa, usado sem alteração | δ, tratamento (bruto ou tratado) e atividades analisadas |
| 9 | Descoberta de processo: `Pm4pyGraphAdapter` → `GraphMiner` | Componente | `deviante-api/mining/app/graph_miner.py` | pm4py | Log de cada processo |
| 10 | Base do Observer e seus sujeitos | Componente | `deviante-web/src/lib/subject.js`, `driftSubject.js`, `maintenanceSubject.js` | Assinar e notificar | Telas que observam |
| 11 | Pontos de variação da tela: `hasFeature`, `FeatureRoute`, `canDelete`, `canManageCatalog`, `CatalogRoute` | Componente | `deviante-web/src/lib/features.js`, `lib/permissions.js`, `components/auth/` | Menu e rotas | Plano da empresa e papel do usuário |
| 12 | Formulário compartilhado: `FormModal`, `Field`, `TextInput`, `Select`, `TextArea` | Componente | `deviante-web/src/components/ui/FormModal.jsx` | Esqueleto do modal | Campos e ação de cada CRUD |
| 13 | Tokens de design: cores, superfícies e temas | Componente | `deviante-web/src/index.css` | Tokens semânticos (`--surface-*`, `--graph-*`) | Tema escuro ou claro |
| 14 | Testes automatizados e bases de teste | Teste | `deviante-api/src/test/kotlin` (7 classes), `deviante-api/mining/tests` (6 módulos), `Datasets/Alfa` (4 logs XES) | Padrões, linha de produto e exclusão | Resultado esperado por base: 0, 4, 7 e 9 desvios |

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
| Alfa | Manutenção | CSV | Menu completo e "Exportar CSV" em Agendamentos | 2, 5, 11 |
| Beta | Essencial | nenhuma | Sem Equipamentos e Agendamentos no menu; a rota volta ao painel | 2, 5, 11 |
| Gama | Manutenção | nenhuma | Agendamentos sem "Exportar CSV" | 2, 5, 11 |
| Delta | Essencial | nenhuma | Igual à Beta | 2, 5, 11 |

Em todas as empresas o papel também varia a tela. Só administrador e gestor excluem registros, e só o administrador mantém o catálogo de atividades (ativos 7 e 11). Os dados de cada empresa ficam separados pelo ativo 4 e filtrados pelo ativo 7.

## Telas e os ativos que elas reutilizam

| Tela | Ativos comuns | Variação |
|---|---|---|
| Login (Modo Protótipo, setas de empresa) | 7 | Empresa escolhida |
| Projetos (painel de processos) | 4, 7, 13 | Administrador vê todas as empresas |
| Canvas do processo e upload de log | 4, 7, 9, 13 | Gestor mapeia só para atividades do catálogo |
| Análise de drift | 6, 8, 10, 13, 14 | δ e tratamento |
| Atividades e Operações | 4, 7, 11, 12 | Só administrador |
| Equipamentos | 4, 7, 11, 12 | Só plano Manutenção |
| Agendamentos | 4, 7, 10, 11, 12 | Só plano Manutenção; CSV só na Alfa |
