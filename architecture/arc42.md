# Arquitetura do Deviante — arc42

_Deviante é suporte à decisão em manutenção industrial. O núcleo analítico é o
framework **IPDD** (Interactive Process Drift Detection), de **Denise M. V. Sato**
(Sato et al., 2025), com a implementação IPDD/ADWIN de **Luiz F. Picolo**._

**Grupo:** Alander Menezes Arantes de Ávila, Bernardo Creplive Vieira, Emanuelle Skolut Jose, Murilo Regnier Stange.

---

## 1. Introdução e Metas

O Deviante é um sistema de suporte a decisões em manutenção industrial capaz de detectar desvios temporais a partir de registros do chão de fábrica. O sistema identifica quando o tempo de execução de uma atividade da máquina muda de comportamento e transforma esse sinal de anomalia em recomendação de manutenção proativa, antes da falha do equipamento.

A presente documentação apresenta um conjunto de decisões de design que afetam a estrutura e o comportamento do sistema. Essas decisões incluem a escolha de padrões arquiteturais, a definição de componentes e suas interações, e a consideração de requisitos funcionais e não funcionais. A arquitetura proposta serve como um guia para o desenvolvimento, influenciando diretamente a qualidade do software e a eficiência do processo de desenvolvimento.

### 1.1 Visão Geral de Requisitos

O Deviante apoia o gestor de manutenção numa atividade de negócio: perceber, a partir dos registros do chão de fábrica, que uma máquina começou a demorar mais do que o normal e agir antes da falha. As tabelas abaixo resumem os requisitos; a versão completa, com origem, tipo, status e evidência, fica no banco **Requirements** do Notion (IPDD: SEVEN DIMENSIONS). Os requisitos vêm de duas fontes: o negócio (PIBITI e produto) e a disciplina de Arquitetura e Soluções Cloud.

**Requisitos funcionais de negócio**

| ID | Requisito | Atendido por |
|---|---|---|
| RF-01 | Login via conta Google (OAuth) | Microfrontend + Supabase Auth |
| RF-02 | Criar processos, análises e monitoramentos a partir do dashboard | Core API (processos, monitoramentos), MS2 (análises) |
| RF-03 | Editar e excluir processos, análises e monitoramentos | Core API, MS2 |
| RF-04 | Upload de log de eventos em CSV ou XES | MS1 · Ingestão |
| RF-05 | Gerar e exibir o DFG (Directly-Follows Graph) do log | MS1 (pm4py) |
| RF-06 | Mapear atividades do log em uma ou mais operações do processo | Core API |
| RF-07 | Editar e remover o mapeamento de operações | Core API |
| RF-08 | Configurar o filtro de traces antes da 1ª execução da análise | MS2 |
| RF-09 | Executar a análise de desvio (drift) sobre um processo ou máquina | MS2 + Azure Function |
| RF-10 | Ajustar a sensibilidade do IPDD/ADWIN e reexecutar sem novo upload | MS2 + Azure Function |
| RF-11 | Criar ação proativa (manutenção ou inspeção) a partir de uma recomendação | Core API |
| RF-12 | Editar e excluir ações proativas | Core API |
| RF-13 | Exibir diagnóstico e prognóstico de saúde de uma máquina monitorada | Core API (classe de prognóstico em Kotlin, etapa futura) |
| RF-14 | Exibir os equipamentos no detalhe do processo | Core API |
| RF-15 | Agrupar um ou mais equipamentos sob um monitoramento | Core API |

**Requisitos funcionais de negócio da Entrega 1 (v1, fluxo principal)**

| ID | Requisito | Atendido por |
|---|---|---|
| RF1 | Autenticar o gestor (convite, Google/JWT) e compartilhar processos entre usuários | Supabase Auth + Core API |
| RF2 | Manter processos de manufatura (criar, listar, editar; excluir só pelo dono) | Core API |
| RF3 | Manter um catálogo global de atividades normalizadas | Core API |
| RF4 | Importar event log (CSV/XES), fazer o parse e persistir operações, traces e tempos | MS1 · Ingestão |
| RF5 | Mapear cada rótulo bruto (operation) para uma atividade normalizada | Core API |
| RF6 | Gerar o grafo do processo observado a partir do log mapeado | MS1 (pm4py) |
| RF7 | Executar a análise de drift (IPDD/ADWIN) e persistir o resultado | MS2 + Azure Function |
| RF8 | Investigar o desvio e registrar a decisão de manutenção proativa | Core API |
| RF9 | Monitorar a saúde de equipamentos por parâmetros de máquina | Core API |

**Requisitos funcionais de arquitetura (Cloud)**

| ID | Requisito | Atendido por |
|---|---|---|
| RF01 | CRUD completo no Microserviço 1 | MS1 · Ingestão (event logs) |
| RF02 | CRUD completo no Microserviço 2 | MS2 · Análises (análises de drift) |
| RF03 | Proxy das requisições de CRUD no BFF | BFF |
| RF04 | `GET /aggregated-data` consome MS1, MS2 e a Function num único response | BFF |
| RF05 | Function faz cálculo ou enriquecimento de dados | Azure Function (IPDD/ADWIN) |

**Requisitos não funcionais de negócio**

| ID | Requisito | Atendido por |
|---|---|---|
| RNF-01 | Back-end em Kotlin | Core API (Ktor) |
| RNF-02 | Supabase com PostgreSQL em nuvem | Banco do Core |
| RNF-03 | Interface em React + Vite | Microfrontend |
| RNF-04 | Figma como fonte única de tokens e componentes de UI | Microfrontend |
| RNF-05 | Microsserviços Python em FastAPI, consumidos via REST | MS1, MS2 |
| RNF-06 | Microsserviços Python como Azure Functions (serverless) | Parcial: o IPDD/ADWIN é Function; MS1 e MS2 rodam no [Fly.io](http://Fly.io) (ADR 04) |
| RNF-07 | Ingestão multiformato (CSV, XES, JSON) só por configuração | MS1 (parser por formato) |
| RNF-08 | Isolamento de dados entre clientes com RLS | Banco do Core (RLS no Supabase) |
| RNF-09 | Git e CI/CD com build, testes e deploy a cada alteração | GitHub Actions em cada repositório |
| RNF-10 | Autenticação Supabase Auth com Google; JWT com tenant e papel | Supabase Auth, API Gateway, Core API |

**Requisitos não funcionais de arquitetura (Cloud)**

| ID | Requisito | Atendido por |
|---|---|---|
| RNF01 | SPA estruturada como microfrontend que consome só o BFF | Microfrontend |
| RNF02 | BFF em Node.js (Express ou NestJS) | BFF (NestJS) |
| RNF03 | Microservices com Database per Service | Core, MS1 e MS2, cada um com seu banco |
| RNF04 | Microserviço 1 com MongoDB Atlas (Free Tier) | MS1 |
| RNF05 | Microserviço 2 com Azure SQL (Free, 1 DTU) | MS2 |
| RNF06 | Azure Function exposta via HTTP | Azure Function (HTTP Trigger) |
| RNF07 | API Gateway na AWS | API Gateway |
| RNF08 | Arquitetura Orientada a Eventos | Azure Service Bus (`EventLogParsed`, `DriftDetected`) |
| RNF09 | Clean Architecture (Domain, Application, Infrastructure, API) | Todos os serviços (§5.2) |
| RNF10 | Vertical Slice (uma pasta por feature) | Todos os serviços (§5.2) |
| RNF11 | Testes unitários e de arquitetura | §8.5 |
| RNF12 | Swagger no BFF, microserviços e eventos | OpenAPI do NestJS e do FastAPI |
| RNF13 | Imagens do BFF e dos microserviços no Docker Hub | §7 |
| RNF14 | Aplicação em URLs da nuvem, não [localhost](http://localhost) | §7 |

### 1.2 Metas de Qualidade

As cinco metas abaixo são as qualidades que mais pesam para os stakeholders, em ordem de prioridade, com o nome da característica da ISO/IEC 25010:2023 a que cada uma corresponde. Cada meta tem um cenário verificável; a seção 4 mostra como a arquitetura atende cada uma e a seção 10 detalha os cenários.

| Prioridade | Meta | ISO/IEC 25010 | Cenário |
|---|---|---|---|
| 1 | Correção analítica | Adequação funcional (correção) | Para os logs sintéticos `DR_*` o drift detectado cai a até 5 traces do ponto injetado (ground truth de `adwin_dataset.py`). |
| 2 | Modificabilidade | Manutenibilidade (modificabilidade) | Um novo formato de log (ex.: JSON) entra com uma nova subclasse de parser, sem alterar MS2, BFF ou Core. |
| 3 | Isolamento | Confiabilidade (tolerância a falhas) | Uma falha no MS2 ou na Function não derruba o CRUD de processos e equipamentos; o BFF devolve o agregado parcial. |
| 4 | Segurança | Segurança (confidencialidade, autenticidade) | Nenhum serviço é acessível sem JWT válido emitido pelo Supabase Auth; dados de um gestor não aparecem para outro. |
| 5 | Implantabilidade | Flexibilidade (instalabilidade) | Cada serviço é uma imagem Docker publicada no Docker Hub e implantada de forma independente. |

### 1.3 Stakeholders

Pessoas e papéis que precisam conhecer, aprovar ou usar esta arquitetura. Os três primeiros são os usuários do sistema; os demais avaliam, orientam ou constroem o projeto.

| Papel / Nome | Contato | Expectativa |
|---|---|---|
| Operador | Usuário do sistema | Informar as atividades da cadeia produtiva e registrar os dados sem retrabalho. |
| Gestor de manutenção | Usuário do sistema | Monitorar os dados, gerar análises a partir do processo registrado e acionar a manutenção a tempo. |
| Técnico de manutenção | Usuário do sistema | Saber o que fazer, registrar a manutenção realizada e reabilitar a máquina no sistema. |
| Analista / mentor | Grupo de pesquisa IPDD (PUCPR) | Validar as análises e ajustar a sensibilidade do IPDD/ADWIN. |
| Denise M. V. Sato, autora do framework IPDD | [denise.vecino@pucpr.br](mailto:denise.vecino@pucpr.br) | Ver o método aplicado com fidelidade ao trabalho original. |
| Luiz F. Picolo, autor da implementação IPDD/ADWIN | [luiz.picolo@pucpr.edu.br](mailto:luiz.picolo@pucpr.edu.br) | Ver o detector reaproveitado sem alteração e com resultados reproduzíveis. |
| Eduardo de Freitas Loures, orientador PIBITI | [eduardo.loures@pucpr.br](mailto:eduardo.loures@pucpr.br) | Orientar a pesquisa e validar a aplicação na manutenção industrial. |
| Manoel Valerio da Silveira Neto, professor de Arquitetura e Soluções Cloud | [manoel.valerio@pucpr.br](mailto:manoel.valerio@pucpr.br) | Avaliar estilos arquiteturais e implantação em nuvem. |
| Tiago Adelino Navarro, professor de Desenvolvimento Orientado a Reuso | [tiago.adelino@pucpr.edu.br](mailto:tiago.adelino@pucpr.edu.br) | Avaliar padrões de projeto, variabilidade e reuso. |
| Grupo de desenvolvimento: Alander Menezes Arantes de Ávila, Bernardo Creplive Vieira, Emanuelle Skolut Jose, Murilo Regnier Stange | [github.com/aland3r](http://github.com/aland3r) | Uma arquitetura que caiba no prazo e no free tier. |

---

## 2. Restrições da Arquitetura

O Deviante atende a três frentes, cada uma com suas restrições e demandas.

A primeira é a Iniciação Tecnológica (PIBITI), vigente de agosto de 2025 a julho de 2026 e apresentada no SEMIC em outubro de 2026, com orientação do Prof. Eduardo de Freitas Loures. O produto continua uma pesquisa da PUCPR que envolve graduandos, mestrandos e doutorandos. Por isso parte da estratégia já chega consolidada e validada pelo grupo de pesquisa: o PM4Py para minerar o processo e o IPDD/ADWIN para detectar os desvios de desempenho.

As outras duas são disciplinas do 6º período de Engenharia de Software da PUCPR. **Arquitetura e Soluções Cloud** (Prof. Manoel Valerio da Silveira Neto) define o estilo e a infraestrutura: microfrontend, BFF em Node.js, dois microsserviços com bancos próprios (MongoDB Atlas e Azure SQL), uma Azure Function, API Gateway na AWS e comunicação por eventos, com Clean Architecture, Vertical Slice, testes unitários e de arquitetura, imagens no Docker Hub, repositórios públicos e documentação arc42 com C4. **Desenvolvimento Orientado a Reuso** (Prof. Tiago Adelino Navarro) pede que o projeto seja modelado com padrões de projeto, deixe explícitos os pontos de variabilidade e reaproveite componentes existentes em vez de reescrevê-los.

As restrições abaixo seguem o template arc42 em três grupos: técnicas, organizacionais e convenções. Cada uma traz o motivo que a impõe.

### 2.1 Restrições técnicas

| ID | Restrição | Motivo |
|---|---|---|
| RT1 | Interface como microfrontend em React que consome só o BFF | Exigência de Cloud (RNF01). React + Vite é decisão do grupo (RNF-03). |
| RT2 | BFF em Node.js (NestJS), com o endpoint `GET /aggregated-data` | Exigência de Cloud (RNF02, RF03, RF04). |
| RT3 | Microsserviço 1 com MongoDB Atlas (Free Tier) | Exigência de Cloud (RNF04). |
| RT4 | Microsserviço 2 com Azure SQL (Free, 1 DTU) | Exigência de Cloud (RNF05). 1 DTU limita consultas pesadas. |
| RT5 | Azure Function com HTTP Trigger ou Message Trigger | Exigência de Cloud (RNF06, RF05). |
| RT6 | API Gateway na AWS como porta de entrada | Exigência de Cloud (RNF07). |
| RT7 | Comunicação assíncrona por eventos entre serviços | Exigência de Cloud (RNF08). |
| RT8 | Back-end de domínio em Kotlin; microsserviços analíticos em Python com FastAPI | Decisão do grupo (RNF-01, RNF-05). PM4Py e o código IPDD/ADWIN só existem em Python. |
| RT9 | Supabase para autenticação (Google) e Postgres com RLS | Decisão do grupo (RNF-02, RNF-08, RNF-10). |
| RT10 | Código IPDD/ADWIN de L. F. Picolo reaproveitado sem reescrita | Fidelidade científica: o método publicado (Sato et al., 2025) precisa dar os mesmos resultados. |
| RT11 | Só serviços gratuitos (free tiers) | Projeto acadêmico sem orçamento. Limites de memória, conexões e DTU condicionam o desenho. |

### 2.2 Restrições organizacionais

| ID | Restrição | Motivo |
|---|---|---|
| RO1 | Equipe de quatro alunos: Alander, Bernardo, Emanuelle e Murilo | Grupo do projeto integrador (PjBL) do 6º período. |
| RO2 | Prazos: documentação de Cloud em 15/10/2026; Reuso e apresentação do PIBITI em 16/10/2026; arquitetura completa de Cloud em 12/11/2026 | Calendário das disciplinas e do PIBITI (banco Entregas do Notion). |
| RO3 | Método analítico definido pela pesquisa e validado pelo orientador | O PIBITI continua o trabalho do grupo de pesquisa IPDD da PUCPR. |
| RO4 | Um repositório público no GitHub por serviço, cada um com README (arquitetura, tecnologias, como rodar, nomes dos alunos) | Exigência de Cloud. |
| RO5 | Imagem Docker do BFF e de cada microsserviço publicada no Docker Hub | Exigência de Cloud (RNF13). |
| RO6 | CI com build, testes e deploy a cada alteração; testes unitários e de arquitetura | RNF-09 e exigência de Cloud (RNF11). |
| RO7 | Demonstração em URLs da nuvem, não [localhost](http://localhost), em vídeo no YouTube com todos os integrantes falando | Exigência de Cloud (RNF14). |

### 2.3 Convenções

| ID | Convenção | Motivo |
|---|---|---|
| C1 | Documentação de arquitetura no template arc42 (12 seções), com diagramas C4 nos níveis de contexto, contêineres e componentes | Exigência de Cloud. |
| C2 | O Notion é a fonte da documentação; `architecture/arc42.md` e o site são gerados a partir dele | O grupo edita num lugar só e o site acompanha (ADR 07). |
| C3 | Diagramas em Mermaid, versionados como texto | Renderizam no site e no Notion sem ferramenta extra. |
| C4 | Clean Architecture (`domain`, `application`, `infrastructure`, `api`) com uma pasta por feature (Vertical Slice) | Exigência de Cloud (RNF09, RNF10). |
| C5 | APIs e eventos documentados em Swagger/OpenAPI | Exigência de Cloud (RNF12). |
| C6 | Figma como fonte única de tokens e componentes de interface | Decisão do grupo (RNF-04). |
| C7 | Documentação em português; código, nomes de classes e eventos em inglês | Público da documentação é a banca da PUCPR; código segue o padrão das bibliotecas. |

---

## 3. Contexto e Escopo

O Deviante é tratado aqui como uma caixa-preta. Dentro do escopo estão o registro do processo, a importação do event log, a análise de desvios e o registro das manutenções. Fora do escopo ficam o sistema de origem da fábrica (MES/ERP), que só exporta o log, e o provedor de identidade (Google). Os três usuários acessam o sistema pelo navegador.

### 3.1 Contexto de negócio

**C4 — Nível 1 · System Context**

```mermaid
%%{init: {"c4": {"width": 300}}}%%
C4Context
    title C4 Nivel 1 - Contexto do Sistema: Deviante

    System(e1, " ", " ")
    Person(operador, "Operador", "Informa as atividades da cadeia produtiva e registra os dados.")
    System(e2, " ", " ")
    Person(gestor, "Gestor", "Monitora os dados, gera analises e aciona a manutenção.")
    System(deviante, "Deviante", "Sistema de Suporte a Decisão na gestão de manutenção industrial.")
    System(e3, " ", " ")
    System(e4, " ", " ")
    Person(tecnico, "Técnico", "Realiza a manutenção, registrando o que foi feito para reabilitar a máquina.")
    System(e5, " ", " ")

    Rel(operador, deviante, "Registra atividades e dados")
    Rel(gestor, deviante, "Analisa e aciona manutenção")
    Rel(tecnico, deviante, "Registra manutenção e reabilita maquina")

    UpdateRelStyle(gestor, deviante, $offsetX="-100", $offsetY="-75")

    UpdateElementStyle(e1, $bgColor="transparent", $borderColor="transparent", $fontColor="transparent")
    UpdateElementStyle(e2, $bgColor="transparent", $borderColor="transparent", $fontColor="transparent")
    UpdateElementStyle(e3, $bgColor="transparent", $borderColor="transparent", $fontColor="transparent")
    UpdateElementStyle(e4, $bgColor="transparent", $borderColor="transparent", $fontColor="transparent")
    UpdateElementStyle(e5, $bgColor="transparent", $borderColor="transparent", $fontColor="transparent")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

| Parceiro | Entrada | Saída |
|---|---|---|
| Operador | Atividades da cadeia produtiva, event log, leituras | Processo registrado |
| Gestor de manutenção | Mapeamentos, parâmetros de análise, acionamento da manutenção | Grafo, drifts, recomendações |
| Técnico de manutenção | Manutenção realizada, reabilitação da máquina | Manutenções agendadas |
| Sistema de origem (MES/ERP) | — | Event log XES/CSV (exportado pelo gestor) |
| Google | — | Identidade (OAuth 2.0) |

### 3.2 Contexto técnico

Todo o tráfego externo entra por um único canal, o API Gateway da AWS, e segue para o BFF. Os canais internos entre os serviços aparecem na seção 5 (C4 nível 2) e na seção 7.

| Parceiro | Canal técnico | Entrada/saída de negócio que passa por ele |
|---|---|---|
| Operador, gestor e técnico (navegador) | HTTPS/JSON até o API Gateway e o BFF, com JWT no header `Authorization` | Atividades, mapeamentos, parâmetros de análise e manutenções entram; grafo, drifts e recomendações saem |
| Sistema de origem (MES/ERP) | Arquivo XES ou CSV enviado por upload (multipart via HTTPS) | Event log do processo |
| Google | OAuth 2.0 / OpenID Connect, intermediado pelo Supabase Auth | Identidade do usuário (JWT) |

---

## 4. Estratégia da Solução

O Deviante gira em torno de um fluxo curto: o operador registra o processo, o event log da máquina é importado, o IPDD/ADWIN procura mudanças no tempo das atividades e o gestor decide a manutenção que o técnico executa. As decisões abaixo saem desse fluxo, das metas de qualidade (seção 1.2) e das restrições (seção 2).

**Decomposição.** O sistema é dividido por responsabilidade, cada parte com seu banco (Database per Service). A interface é um microfrontend em React que conversa só com o BFF em NestJS, e o BFF fica atrás do API Gateway da AWS. O domínio (processos, atividades, máquinas, monitoramentos e manutenções) fica na Core API em Kotlin/Ktor sobre o Supabase. A ingestão do log e o grafo do processo ficam no MS1 (FastAPI + PM4Py, MongoDB Atlas) e as análises de desvio no MS2 (FastAPI, Azure SQL).

**Núcleo analítico.** O IPDD/ADWIN roda numa Azure Function sem estado, chamada sob demanda. O código original de L. F. Picolo é envolvido por um Adapter em vez de reescrito, o que preserva os resultados do método publicado.

**Integração.** Os serviços trocam eventos no Azure Service Bus (`EventLogParsed`, `DriftDetected`). Assim ingestão, análise e domínio evoluem e falham separados, e o BFF consegue devolver um agregado parcial quando um deles está fora.

**Estrutura interna e reuso.** Todo serviço segue Clean Architecture com uma pasta por feature (Vertical Slice). Os padrões Singleton, Adapter e Observer, um de cada família GoF, resolvem pontos concretos do fluxo (seção 8.3).

**Tecnologia e operação.** Só serviços gratuitos: Vercel para a interface, Fly.io para a Core API, o MS1 e o MS2 (ADR 04), Azure para a Function, o Service Bus e o Azure SQL. Cada serviço vira uma imagem no Docker Hub e é publicado pelo GitHub Actions.

**Organização.** A documentação é escrita no Notion e publicada no site a partir do repositório (ADR 07), para que o grupo edite num lugar só.

A tabela liga cada meta de qualidade à abordagem que a atende.

| Meta de qualidade | Cenário | Abordagem de solução |
|---|---|---|
| Correção analítica | Para os logs sintéticos `DR_*`, o drift detectado cai a até 5 traces do ponto injetado. | Reaproveitar o IPDD/ADWIN original por um Adapter (`IpddAdwinAdapter`), sem reescrita, e validar contra o ground truth de `adwin_dataset.py` (seções 8.3 e 10). |
| Modificabilidade | Um novo formato de log (ex.: JSON) entra sem alterar MS2, BFF ou Core. | Um parser por formato isolado no MS1; eventos separam o MS1 de quem consome o log; Clean Architecture e Vertical Slice limitam o impacto da mudança (seções 5 e 8). |
| Isolamento | Uma falha no MS2 ou na Function não derruba o CRUD de processos e equipamentos; o BFF devolve o agregado parcial. | Database per Service, Function sem estado, eventos idempotentes no Service Bus e BFF com timeout por serviço (seções 5, 6 e 8). |
| Segurança | Nenhum serviço responde sem JWT válido do Supabase Auth; dados de um gestor não aparecem para outro. | Login Google pelo Supabase Auth, JWT validado no API Gateway e nos serviços, RLS no Postgres por tenant (seção 8). |
| Implantabilidade | Cada serviço é uma imagem Docker no Docker Hub, implantada de forma independente. | Um repositório, uma imagem e um pipeline do GitHub Actions por serviço (seção 7). |

---

## 5. Visão de Blocos de Construção

### 5.1 Nível 1 — Containers

**C4 — Nível 2 · Container**

```mermaid
flowchart TB
    operador(["<b>Operador</b><br/>[Pessoa]"])
    gestor(["<b>Gestor de Manutenção</b><br/>[Pessoa]"])
    tecnico(["<b>Técnico de Manutenção</b><br/>[Pessoa]"])
    auth["<b>Autenticação Supabase</b><br/>[Sistema externo]<br/>Google OAuth / JWT"]

    subgraph dv["Deviante [Sistema]"]
        web["<b>Microfrontend</b><br/>[React + Vite · Vercel]"]
        gw["<b>API Gateway</b><br/>[AWS]"]
        bff["<b>BFF</b><br/>[Node.js + NestJS]"]
        core["<b>Core API</b><br/>[Kotlin + Ktor]<br/>processos e manutenção"]
        ms1["<b>MS1 · Ingestão</b><br/>[FastAPI + pm4py]<br/>upload e grafo"]
        ms2["<b>MS2 · Análises</b><br/>[FastAPI]<br/>CRUD de análises"]
        fn["<b>IPDD/ADWIN</b><br/>[Azure Function]"]
        bus{{"<b>Service Bus</b><br/>[Azure · eventos]"}}
        dbCore[("<b>Postgres</b><br/>[Supabase]")]
        dbMs1[("<b>MongoDB</b><br/>[Atlas]")]
        dbMs2[("<b>Azure SQL</b>")]
    end

    operador & gestor & tecnico -->|HTTPS| web
    web -.->|login| auth
    web -->|REST| gw --> bff
    bff --> core & ms1 & ms2
    bff -->|agregado| fn
    ms2 -->|calcula drift| fn
    core --> dbCore
    ms1 --> dbMs1
    ms2 --> dbMs2
    ms1 -.->|EventLogParsed| bus
    bus -.-> ms2
    ms2 -.->|DriftDetected| bus
    bus -.-> core

    classDef person fill:#08427B,stroke:#073B6F,color:#fff
    classDef container fill:#438DD5,stroke:#3C7FC0,color:#fff
    classDef external fill:#999999,stroke:#8A8A8A,color:#fff
    class operador,gestor,tecnico person
    class web,gw,bff,core,ms1,ms2,fn,bus,dbCore,dbMs1,dbMs2 container
    class auth external
    style dv fill:none,stroke:#666,stroke-dasharray:5 5
```

| Container | Responsabilidade | Tecnologia | Banco |
|-----------|------------------|------------|-------|
| Microfrontend | SPA do produto e do site público | React + Vite, Vercel | — |
| API Gateway | Entrada única, roteamento, JWT, rate limit | AWS API Gateway (HTTP API) | — |
| BFF | Proxy dos CRUDs; `GET /aggregated-data` junta Core, MS1, MS2 e Function num único JSON | Node.js + NestJS, Fly.io | — |
| Core API | Processos, atividades, mapeamentos, equipamentos, monitoramento, recomendações e agendas | Kotlin + Ktor, Fly.io | Supabase Postgres |
| MS1 · Ingestão | Upload CSV/XES, parse, operações, traces e grafo (DFG) com pm4py; CRUD de event logs | Python + FastAPI + pm4py, Fly.io | MongoDB Atlas |
| MS2 · Análises | CRUD das análises de drift; monta a série de tempos e chama a Function | Python + FastAPI, Fly.io | Azure SQL |
| Azure Function | IPDD/ADWIN: recebe a série, devolve os pontos de drift; sem estado | Python, HTTP Trigger | — |
| Service Bus | Transporte de eventos entre serviços | Azure Service Bus | — |

### 5.2 Nível 2 — Componentes do Core API

Cada serviço segue a mesma organização; o Core é o exemplo detalhado. Os
componentes de domínio espelham os objetos do ORCA (§8.1).

**C4 — Nível 3 · Component**

```mermaid
flowchart TB
    bff["<b>BFF</b><br/>[Container: NestJS]"]
    auth["<b>Autenticação Supabase</b><br/>[Sistema externo]<br/>JWKS"]
    bus{{"<b>Service Bus</b><br/>[Container: Azure]"}}
    db[("<b>Postgres</b><br/>[Container: Supabase]")]

    subgraph core["Core API · Kotlin/Ktor [Container]"]
        api["<b>api</b><br/>[Component: rotas Ktor]<br/>endpoints e validação de JWT"]
        app["<b>application</b><br/>[Component: slices]<br/>processes · activities · equipment<br/>monitoring · maintenance"]
        domain["<b>domain</b><br/>[Component: Kotlin puro]<br/>entidades e regras"]
        infra["<b>infrastructure</b><br/>[Component: Exposed]<br/>repositórios e eventos"]
    end

    bff -->|REST| api
    api -.->|valida JWT| auth
    api --> app --> domain
    infra -.->|implementa portas| app
    infra -->|JDBC| db
    bus -.->|DriftDetected| infra

    classDef container fill:#438DD5,stroke:#3C7FC0,color:#fff
    classDef component fill:#85BBF0,stroke:#78A8D8,color:#000
    classDef external fill:#999999,stroke:#8A8A8A,color:#fff
    class bff,bus,db container
    class api,app,domain,infra component
    class auth external
    style core fill:none,stroke:#666,stroke-dasharray:5 5
```

| Slice (`application/`) | Features |
|------------------------|----------|
| `processes` | CreateProcess, UpdateProcess, DeleteProcess, ListProcesses |
| `activities` | ManageActivityCatalog, MapOperation, UnmapOperation |
| `equipment` | CreateEquipment, UpdateEquipment, DeleteEquipment, ManageParameters |
| `monitoring` | CreateMonitoring, LinkEquipment, RecordReading |
| `maintenance` | RecommendMaintenance, ScheduleMaintenance, CompleteMaintenance |

### 5.3 Nível 3 — Classes de domínio

**C4 — Nível 4 · UML de Classes** (Core API). Atributos, métodos e associações de todas as classes, de todos os serviços, ficam na database Classes da [página no Notion](https://app.notion.com/p/3ec5fc7249408016b3d1fcf7e9da3725).

```mermaid
classDiagram
    direction LR

    class Manager {
      +UUID id
      +UUID userId
      +String email
      +String fullName
      +Role role
      +canEdit(process) Boolean
      +isOwner() Boolean
    }
    class Process {
      +UUID id
      +UUID managerId
      +String name
      +String companyName
      +String sector
      +rename(name)
      +addActivity(activity)
      +linkEquipment(equipment)
      +canBeDeletedBy(manager) Boolean
    }
    class Activity {
      +UUID id
      +String name
      +String description
      +matches(rawLabel) Boolean
    }
    class OperationMapping {
      +UUID id
      +UUID processId
      +String operationRef
      +String rawLabel
      +MappingStatus status
      +mapTo(activity)
      +unmap()
      +autoMap(catalog)
    }
    class Equipment {
      +UUID id
      +String name
      +String tag
      +String kind
      +EquipmentStatus status
      +changeStatus(status)
      +addParameter(parameter)
    }
    class Monitoring {
      +UUID id
      +String name
      +String sourceType
      +MonitoringStatus status
      +addEquipment(equipment)
      +removeEquipment(equipment)
      +activate()
      +pause()
    }
    class MonitoringParameter {
      +UUID id
      +String name
      +String unit
      +record(reading)
      +history(range) List
    }
    class Reading {
      +UUID id
      +Instant observedAt
      +Double value
      +String quality
      +isValid() Boolean
    }
    class MaintenanceRecommendation {
      +UUID id
      +String analysisRef
      +String action
      +Priority priority
      +RecommendationStatus status
      +accept()
      +reject()
      +toSchedule() MaintenanceSchedule
    }
    class MaintenanceSchedule {
      +UUID id
      +String title
      +Instant scheduledStart
      +Instant scheduledEnd
      +ScheduleStatus status
      +reschedule(start, end)
      +complete()
      +cancel()
    }

    Manager "1" --> "*" Process : possui
    Process "*" --> "*" Activity : usa
    Process "1" --> "*" OperationMapping : mapeia
    OperationMapping "*" --> "0..1" Activity : destino
    Process "*" --> "*" Equipment : envolve
    Monitoring "*" --> "*" Equipment : acompanha
    Monitoring "1" --> "*" MonitoringParameter : mede
    MonitoringParameter "1" --> "*" Reading : registra
    Equipment "1" --> "*" MaintenanceRecommendation : recebe
    MaintenanceRecommendation "1" --> "0..1" MaintenanceSchedule : vira
```

Classes dos outros serviços: MS1 — `EventLog`, `Trace`, `Event`, `ProcessGraph`,
`EventLogParser` (+ `CsvParser`, `XesParser`, `JsonParser`); MS2 —
`DriftAnalysis`, `DriftPoint`; Function — `IpddAdwinDetector`.

### 5.4 UML de Componentes

**C4 — Nível 4 · UML de Componentes** (interfaces fornecidas e requeridas)

```mermaid
flowchart LR
    subgraph BFF["«component» BFF"]
        bffAgg(["IAggregatedData"])
    end
    subgraph CORE["«component» Core API"]
        coreRest(["IDomainCrud"])
        coreEvt(["IDriftDetectedHandler"])
    end
    subgraph MS1["«component» MS1 Ingestão"]
        ms1Rest(["IEventLogs"])
    end
    subgraph MS2["«component» MS2 Análises"]
        ms2Rest(["IAnalyses"])
        ms2Evt(["IEventLogParsedHandler"])
    end
    subgraph FN["«component» Azure Function"]
        fnHttp(["IDriftCalculation"])
    end
    BFF -.->|requer| coreRest
    BFF -.->|requer| ms1Rest
    BFF -.->|requer| ms2Rest
    BFF -.->|requer| fnHttp
    MS2 -.->|requer| fnHttp
    MS1 -.->|publica para| ms2Evt
    MS2 -.->|publica para| coreEvt
```

## 6. Visão de Runtime

### 6.1 Upload do event log e análise de drift

**C4 — Nível 4 · UML de Sequência**

```mermaid
sequenceDiagram
    actor G as Gestor
    participant W as Microfrontend
    participant GW as API Gateway
    participant B as BFF
    participant M1 as MS1 Ingestão
    participant Q as Service Bus
    participant M2 as MS2 Análises
    participant F as Azure Function
    participant C as Core API
    G->>W: envia event log CSV/XES
    W->>GW: POST /event-logs (JWT)
    GW->>B: POST /event-logs
    B->>M1: POST /event-logs
    M1-->>B: 202 parse em andamento
    M1->>M1: parse + DFG (pm4py)
    M1->>Q: EventLogParsed
    Q->>M2: EventLogParsed
    M2->>F: POST /ipdd-adwin (série, delta)
    F-->>M2: pontos de drift
    M2->>Q: DriftDetected
    Q->>C: DriftDetected
    C->>C: cria MaintenanceRecommendation
```

### 6.2 Abrir o processo (`GET /aggregated-data`)

```mermaid
sequenceDiagram
    actor G as Gestor
    participant W as Microfrontend
    participant B as BFF
    participant C as Core API
    participant M1 as MS1 Ingestão
    participant M2 as MS2 Análises
    participant F as Azure Function
    G->>W: abre o processo
    W->>B: GET /aggregated-data?processId=...
    par em paralelo
        B->>C: processo, equipamentos, recomendações
        B->>M1: grafo e traces
        B->>M2: análises e drifts
        B->>F: prévia com a sensibilidade escolhida
    end
    B-->>W: JSON único
    Note over B: se um serviço falhar, o campo vem nulo<br/>e o restante é devolvido
```

## 7. Visão de Implantação

```mermaid
flowchart TB
    browser([Navegador])
    subgraph vercel["Vercel"]
        fe["Microfrontend"]
    end
    subgraph aws["AWS"]
        gw["API Gateway"]
    end
    subgraph fly["Fly.io (imagens do Docker Hub)"]
        bff["BFF"]
        core["Core API"]
        ms1["MS1 Ingestão"]
        ms2["MS2 Análises"]
    end
    subgraph azure["Microsoft Azure"]
        fn["Function IPDD/ADWIN"]
        sql[("Azure SQL")]
        bus{{"Service Bus"}}
    end
    subgraph saas["SaaS"]
        supa[("Supabase Postgres + Auth")]
        mongo[("MongoDB Atlas")]
    end
    browser -->|HTTPS| fe
    fe -->|HTTPS| gw --> bff
    bff --> core & ms1 & ms2
    bff --> fn
    ms2 --> fn
    core --> supa
    ms1 --> mongo
    ms2 --> sql
    ms1 & ms2 & core <--> bus
```

| Nó | Implantação |
|----|-------------|
| Microfrontend | Vercel, deploy a cada push na `main` |
| BFF, Core, MS1, MS2 | Imagem no Docker Hub, deploy no Fly.io via GitHub Actions |
| Azure Function | Plano Consumption, deploy via GitHub Actions |
| Bancos | Supabase, MongoDB Atlas M0, Azure SQL Free |

## 8. Conceitos Transversais

### 8.1 Modelo de domínio e dados

**Objetos de negócio (OOUX / ORCA).** Os seis objetos do ORCA são o
vocabulário comum entre interface, código e dados. Cada objeto vira uma classe
de domínio (§5.3), uma tela no Microfrontend e uma tabela ou coleção; cada CTA
vira um caso de uso.

| Objeto ORCA | Classe / dado | Serviço dono | CTAs | Requisitos |
|-------------|---------------|--------------|------|------------|
| Process | `Process` | Core API | criar, editar, excluir, ver detalhe | RF-02, RF-03, RF-14 |
| Activity | `Activity` (+ `OperationMapping` dos rótulos do log) | Core API | mapear, editar e remover mapeamento | RF-06, RF-07 |
| Analysis | `Analysis` (+ cálculo na Function) | MS2 · Análises | criar, filtrar traces, executar, ajustar sensibilidade | RF-02, RF-03, RF-08, RF-09, RF-10 |
| Monitoring | `Monitoring`, `MonitoringParameter`, `Reading` | Core API | criar, editar, excluir, agrupar máquinas | RF-02, RF-03, RF-15 |
| Machine | `Equipment` | Core API | ver diagnóstico e prognóstico | RF-13, RF-14 |
| Maintenance | `MaintenanceRecommendation` → `MaintenanceSchedule` | Core API | criar ação proativa, editar, excluir | RF-11, RF-12 |

O gestor (`Manager`) é o ator, não um objeto ORCA. O event log, os traces e o
grafo (MS1) são dados de suporte de Process e Activity.

Cada serviço é dono dos seus dados; entre bancos só trafegam ids (`*_ref`). Detalhe por tabela (banco, campos, chaves e a classe que persiste cada uma) na database Entidades da [página no Notion](https://app.notion.com/p/3ec5fc7249408016bae5f7b940dd50d7).

**Diagrama de Entidades e Relacionamentos — Core (Supabase Postgres)**

```mermaid
erDiagram
    MANAGERS ||--o{ PROCESSES : possui
    MANAGERS ||--o{ EQUIPMENT : cadastra
    MANAGERS ||--o{ MONITORINGS : cria
    PROCESSES ||--o{ PROCESS_ACTIVITIES : usa
    ACTIVITIES ||--o{ PROCESS_ACTIVITIES : compoe
    PROCESSES ||--o{ OPERATION_MAPPINGS : mapeia
    ACTIVITIES ||--o{ OPERATION_MAPPINGS : destino
    PROCESSES ||--o{ PROCESS_EQUIPMENT : envolve
    EQUIPMENT ||--o{ PROCESS_EQUIPMENT : participa
    MONITORINGS ||--o{ MONITORING_EQUIPMENT : acompanha
    EQUIPMENT ||--o{ MONITORING_EQUIPMENT : monitorado
    MONITORINGS ||--o{ MONITORING_PARAMETERS : mede
    MONITORING_PARAMETERS ||--o{ MONITORING_READINGS : registra
    EQUIPMENT ||--o{ MAINTENANCE_RECOMMENDATIONS : recebe
    MAINTENANCE_RECOMMENDATIONS ||--o| MAINTENANCE_SCHEDULES : vira
    MANAGERS {
        uuid id PK
        uuid user_id
        string email
        string role
    }
    PROCESSES {
        uuid id PK
        uuid manager_id FK
        string name
        string company_name
        string sector
    }
    ACTIVITIES {
        uuid id PK
        string name
    }
    OPERATION_MAPPINGS {
        uuid id PK
        uuid process_id FK
        uuid activity_id FK
        string operation_ref
        string raw_label
        string status
    }
    EQUIPMENT {
        uuid id PK
        uuid manager_id FK
        string name
        string tag
        string status
    }
    MONITORINGS {
        uuid id PK
        uuid manager_id FK
        string name
        string status
    }
    MONITORING_PARAMETERS {
        uuid id PK
        uuid monitoring_id FK
        uuid equipment_id FK
        string name
        string unit
    }
    MONITORING_READINGS {
        uuid id PK
        uuid parameter_id FK
        timestamp observed_at
        float value
    }
    MAINTENANCE_RECOMMENDATIONS {
        uuid id PK
        uuid equipment_id FK
        string analysis_ref
        string priority
        string status
    }
    MAINTENANCE_SCHEDULES {
        uuid id PK
        uuid recommendation_id FK
        string title
        timestamp scheduled_start
        string status
    }
```

**MS2 (Azure SQL)**

```mermaid
erDiagram
    DRIFT_ANALYSES ||--o{ DRIFT_POINTS : encontra
    DRIFT_ANALYSES {
        uuid id PK
        string process_ref
        string event_log_ref
        string activity
        float delta
        int trace_count
        int drift_count
        string status
    }
    DRIFT_POINTS {
        uuid id PK
        uuid analysis_id FK
        int trace_index
        float mean_before
        float mean_after
    }
    EQUIPMENT_ANALYSIS_RUNS {
        uuid id PK
        string equipment_ref
        string parameter_ref
        float delta
        int observation_count
        float rul_value
        float failure_probability
    }
```

**MS1 (MongoDB Atlas)** — coleções `event_logs`, `traces` (eventos embutidos),
`operations` e `process_graphs` (nós e arestas do DFG com frequências).

### 8.2 Segurança

O login é feito no Supabase Auth com Google. O JWT é validado no API Gateway e
de novo no Core (JWKS); o BFF repassa o token. Os serviços só aceitam chamadas
vindas do BFF ou do Service Bus.

### 8.3 Padrões de reuso

Um padrão de cada família, todos sobre o que a v1 faz de fato (upload, grafo, análise de drift, investigação). Manutenção preditiva (RUL, probabilidade de falha) fica fora da v1.

| Padrão | Família | Exemplos | Onde |
|--------|---------|----------|------|
| Singleton | Criacional | `AnalysisEngine` (instância única do wrapper do detector, reaproveitada entre chamadas), `AppConfig` (registro único de configuração e parâmetros padrão da análise) | Function, Core |
| Adapter | Estrutural | `IpddAdwinAdapter` → `DriftDetector` (código IPDD/ADWIN de L. F. Picolo), `Pm4pyGraphAdapter` → `GraphMiner` (pm4py) | Function, MS1 |
| Observer | Comportamental | `DriftSubject` notifica `InvestigationPanel`, `MonitoringContext` e `AnalysisHud` quando o ADWIN detecta um drift ou a análise conclui | Microfrontend |

```mermaid
classDiagram
    direction LR
    class AnalysisEngine {
      <<singleton>>
      -instance$ AnalysisEngine
      +getInstance()$ AnalysisEngine
      +run(series, delta) List~DriftPoint~
    }
    class DriftDetector {
      <<interface>>
      +detect(series, delta) List~DriftPoint~
    }
    class IpddAdwinAdapter {
      +detect(series, delta) List~DriftPoint~
    }
    class ipdd_adwin {
      <<código de L. F. Picolo>>
    }
    class DriftSubject {
      -observers List~DriftObserver~
      +subscribe(o)
      +notify(event)
    }
    class DriftObserver {
      <<interface>>
      +update(event)
    }
    class InvestigationPanel
    class MonitoringContext
    class AnalysisHud
    AnalysisEngine --> DriftDetector : usa
    DriftDetector <|.. IpddAdwinAdapter
    IpddAdwinAdapter --> ipdd_adwin : adapta
    DriftSubject --> DriftObserver : notifica
    DriftObserver <|.. InvestigationPanel
    DriftObserver <|.. MonitoringContext
    DriftObserver <|.. AnalysisHud
```

O Adapter é o padrão que preserva a pesquisa: o código do Picolo é envolvido, não copiado nem alterado ("wrap, não fork"). O Singleton evita recarregar o detector a cada chamada, e o Observer desacopla a detecção das telas que reagem a ela.

### 8.4 Tratamento de erros e resiliência

Erros saem como JSON `{ "error": "..." }` com status HTTP adequado. O BFF usa
timeout por serviço e devolve agregado parcial. Eventos são idempotentes
(chave = id do event log ou da análise).

### 8.5 Testes de arquitetura

| Serviço | Ferramenta | Regras |
|---------|-----------|--------|
| Core (Kotlin) | Konsist | `domain` não importa `infrastructure`, `api` nem Ktor; classes de uma slice não importam outra slice |
| BFF (Node) | dependency-cruiser | módulos de feature não se importam entre si; nenhum driver de banco no BFF |
| MS1, MS2 (Python) | import-linter | contrato de camadas `api → application → domain`, `infrastructure → domain` |

## 9. Decisões de Arquitetura

| ADR | Decisão | Motivo | Consequência |
|-----|---------|--------|--------------|
| 01 | IPDD/ADWIN roda como Azure Function e o MS2 só gerencia as análises | Reaproveitar o código de L. F. Picolo sem estado; o enunciado conta MS2 (CRUD + Azure SQL) e Function separadamente | Uma chamada HTTP a mais por análise |
| 02 | MS1 = ingestão + grafo com pm4py, em MongoDB | Log e traces têm forma de documento | Consultas relacionais sobre traces ficam no MS2/Core |
| 03 | Core API em Kotlin continua como serviço de domínio no Supabase | Reaproveita o `deviante-api` e o Auth já em produção | Três bancos para operar |
| 04 | BFF, Core, MS1 e MS2 hospedados no Fly.io | Deploy já funcionando, free tier | Tráfego entre nuvens (Fly, Azure, AWS) |
| 05 | Eventos via Azure Service Bus | Desacoplar ingestão, análise e domínio (EDA) | Consistência eventual |
| 06 | Prognóstico de manutenção (RUL) fica para depois, como classe Kotlin no Core | Foco no drift para esta entrega | Campos de RUL ficam vazios por enquanto |
| 07 | O arc42 é escrito no Notion; `architecture/arc42.md` é gerado a partir dele, com diagramas em Mermaid | O grupo edita num lugar só, e o site e o PDF continuam vindo de um arquivo versionado | Mudanças feitas direto no `.md` são sobrescritas na próxima sincronização |

## 10. Requisitos de Qualidade

| ID | Atributo | Cenário | Medida |
|----|----------|---------|--------|
| Q1 | Correção | Rodar a análise em `DR_01.xes` … `DR_30.xes` | Drift a até 5 traces do ground truth em ≥ 90% dos logs |
| Q2 | Desempenho | `GET /aggregated-data` com os quatro serviços no ar | Resposta em até 2 s |
| Q3 | Disponibilidade parcial | MS2 fora do ar | CRUD de processos segue funcionando; agregado vem sem análises |
| Q4 | Modificabilidade | Novo formato de log | Uma classe nova no MS1, zero mudança nos demais |
| Q5 | Segurança | Chamada sem JWT | 401 no API Gateway |

## 11. Riscos e Dívida Técnica

| Prioridade | Risco / dívida | Mitigação |
|-----------|----------------|-----------|
| 1 | Hoje MS1 e MS2 são um só serviço (`mining/`) sobre Postgres | Separar em dois deploys e migrar dados para Mongo e Azure SQL |
| 2 | Limites do free tier (Azure SQL 1 DTU, Atlas M0, cold start da Function) | Séries pequenas, cache no BFF, aquecer a Function antes da demo |
| 3 | Latência entre três nuvens | Chamadas em paralelo no BFF |
| 4 | Código atual organizado por tipo, não por feature | Reorganizar em slices junto com os testes de arquitetura |
| 5 | Testes de arquitetura ainda não existem | Konsist, dependency-cruiser e import-linter (§8.5) |

## 12. Glossário

| Termo | Definição |
|-------|-----------|
| Event log | Registro de eventos de um processo: caso (trace), atividade e tempos de início e fim. |
| Trace | Sequência de eventos de um mesmo caso. |
| Sojourn time | Tempo que um caso passa numa atividade (fim − início). |
| Drift | Mudança estatisticamente relevante no comportamento de uma série, aqui o sojourn time. |
| IPDD | Interactive Process Drift Detection, framework de D. Sato. |
| ADWIN | Adaptive Windowing: algoritmo que detecta mudança na média de uma série. |
| DFG | Directly-Follows Graph: grafo de quais atividades seguem quais. |
| RUL | Remaining Useful Life: vida útil restante estimada de um equipamento. |
| BFF | Backend for Frontend: API feita sob medida para a interface. |
| Process (Processo) | Objeto ORCA: processo de manufatura monitorado. Ver §8.1. |
| Activity (Atividade) | Objeto ORCA: etapa normalizada do processo; os rótulos do event log são mapeados para ela. |
| Analysis (Análise) | Objeto ORCA: execução do IPDD/ADWIN com parâmetros e pontos de drift. |
| Monitoring (Monitoramento) | Objeto ORCA: agrupamento de máquinas acompanhadas por parâmetros e leituras. |
| Machine (Máquina) | Objeto ORCA: equipamento do chão de fábrica; no código, `Equipment`. |
| Maintenance (Manutenção) | Objeto ORCA: ação proativa (manutenção ou inspeção) recomendada e agendada antes da falha. |
| OOUX / ORCA | Object-Oriented UX; ORCA = Objects, Relationships, CTAs, Attributes. |
