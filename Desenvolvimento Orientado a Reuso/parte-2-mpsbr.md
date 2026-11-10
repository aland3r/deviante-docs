# Parte II: Avaliação MPS.BR (Guia Geral MPS de Software, 2016)

Legenda: **Verde** = resultado atendido; **Amarelo** = atendido em parte; **Vermelho** = não atendido.

## 1. Gerência de Reutilização (GRU)

Propósito do processo (nível E, Parcialmente Definido): gerenciar o ciclo de vida dos ativos reutilizáveis.

O Driftor tem seis ativos reutilizáveis catalogados: modelo de variabilidade e requisitos, arquitetura de referência e modelo de dados multiempresa, núcleo da linha de produto no Core, motor de análise, componentes de interface (pacote versionado, versão 1.0.0) e testes automatizados com bases de teste.

| Resultado | Situação | Evidência no Driftor | Adequação proposta |
|---|---|---|---|
| **GRU 1.** Estratégia de gerenciamento de ativos documentada, com definição de ativo reutilizável e critérios de aceitação, certificação, classificação, descontinuidade e avaliação | Amarelo | O documento de ativos reutilizáveis define o que é ativo e classifica os seis ativos pelos quatro tipos de artefato de domínio (requisito, arquitetura, componente e teste). Não há critérios de aceitação, certificação, descontinuidade nem avaliação. | Completar o documento com uma seção de estratégia: um ativo só é aceito se tiver dono, documentação de uso, ponto de variação explícito e teste automatizado; é certificado quando passa nos testes e na revisão de código; é descontinuado quando nenhuma variante o usa por dois ciclos de entrega; e é avaliado a cada entrega pela quantidade de telas e variantes que o reutilizam. |
| **GRU 2.** Mecanismo de armazenamento e recuperação de ativos implantado | Verde | Os ativos ficam nos repositórios GitHub do projeto (Core, web e documentação). Os componentes de interface são um pacote versionado (versão 1.0.0) consumido pelo front. O catálogo indica onde está cada ativo. | Manter. Como melhoria, publicar o pacote de interface num registro (GitHub Packages) para que outros projetos o instalem pela versão. |
| **GRU 3.** Dados de utilização dos ativos registrados | Vermelho | Não há registro de quem usa cada ativo. A tabela "Telas e os ativos que elas reutilizam" mostra o uso planejado, mas não é atualizada a cada mudança. | Registrar o uso no próprio catálogo: para cada ativo, as telas, variantes e versões que o usam, atualizadas a cada entrega. Uma verificação automática no CI pode listar os imports do pacote de interface e do núcleo da linha de produto e gerar essa tabela. |
| **GRU 4.** Ativos mantidos periodicamente segundo os critérios definidos, com modificações controladas ao longo do ciclo de vida | Amarelo | Toda modificação é controlada pelo Git (histórico, autoria e commits por mudança), e o pacote de interface tem versão. Não há manutenção periódica planejada nem critérios para ela. | Definir uma revisão dos ativos a cada entrega, com base nos critérios do GRU 1, e versionar cada ativo com versionamento semântico e um registro de mudanças (CHANGELOG). |
| **GRU 5.** Usuários dos ativos notificados sobre problemas, modificações, novas versões e descontinuidade | Vermelho | Não há notificação. Quem usa um ativo só descobre uma mudança lendo o histórico do repositório. | Publicar cada nova versão como release no GitHub, com notas de mudança, e avisar no canal do grupo. Problemas e descontinuidades viram issues marcadas com o nome do ativo, que notificam quem acompanha o repositório. |

## 2. Desenvolvimento para Reutilização (DRU)

Propósito do processo (nível C, Definido): identificar oportunidades de reutilização sistemática de ativos na organização e, se possível, estabelecer um programa de reutilização para desenvolver ativos a partir de engenharia de domínios de aplicação.

O enunciado pede a classificação dos resultados DRU 1 a 9 e a adequação dos resultados DRU 6 a 9.

### 2.1 Classificação dos resultados DRU 1 a 5

| Resultado | Situação | Evidência no Driftor |
|---|---|---|
| **DRU 1.** Domínios de aplicação identificados, com o potencial de reutilização | Amarelo | O domínio está claro na arquitetura (mineração de processos e manutenção industrial), e o produto é tratado como linha de produto para várias empresas. O potencial de reutilização de cada domínio não foi analisado nem registrado. |
| **DRU 2.** Capacidade de reutilização sistemática avaliada, com ações corretivas | Vermelho | Não houve avaliação formal da capacidade de reutilização do grupo. Esta avaliação MPS.BR é a primeira. |
| **DRU 3.** Programa de reutilização planejado, com propósitos, escopo, metas e objetivos | Vermelho | A reutilização foi feita por entregas da disciplina, sem um programa com metas próprias. |
| **DRU 4.** Programa de reutilização implantado, monitorado e avaliado | Vermelho | Sem programa definido, não há implantação nem monitoramento. |
| **DRU 5.** Propostas de reutilização avaliadas para garantir que o resultado seja apropriado à aplicação alvo | Amarelo | As decisões de arquitetura avaliaram a reutilização dos algoritmos IPDD/ADWIN da pesquisa e da biblioteca pm4py, integrados por adaptadores sem alteração. Não há um critério padrão para avaliar novas propostas. |

### 2.2 Classificação e adequação dos resultados DRU 6 a 9

| Resultado | Situação | Evidência no Driftor | Adequação proposta |
|---|---|---|---|
| **DRU 6.** Formas de representação para modelos de domínio e arquiteturas de domínio selecionadas | Verde | O modelo de domínio é representado por um diagrama de características na notação FODA estendida (FeatureIDE), e a arquitetura segue o arc42 com diagramas C4 e UML. | Registrar essa escolha como uma decisão de arquitetura (ADR), com o motivo de cada notação, para que novos ativos e domínios usem as mesmas representações. |
| **DRU 7.** Modelo de domínio desenvolvido, com limites e relações com outros domínios, capturando características comuns, variantes, opcionais e obrigatórias | Amarelo | O modelo de características da Parte I captura as funções comuns, variantes, opcionais e obrigatórias, com 10 restrições e uma configuração por empresa. Os limites do domínio e as relações com domínios vizinhos (pesquisa em mineração de processos, sensores industriais) não estão descritos. | Acrescentar ao modelo um texto de escopo do domínio (o que fica dentro e fora) e um diagrama de contexto com os domínios relacionados. Revisar o modelo a cada nova função e manter o arquivo do FeatureIDE versionado junto com o código. |
| **DRU 8.** Arquitetura de domínio descrevendo uma família de aplicações, desenvolvida e mantida por todo o ciclo de vida | Amarelo | A arquitetura (arc42) já tem os pontos de variação no código: núcleo da linha de produto, configuração por empresa e controle por papel. Porém o documento descreve um produto, e não a família de aplicações, e não é atualizado a cada mudança. | Incluir no arc42 uma visão de linha de produto que liga cada característica do modelo ao componente que a implementa e ao mecanismo de variação usado (configuração, rota protegida, papel). Atualizar essa visão em toda entrega, como parte da definição de pronto. |
| **DRU 9.** Ativos do domínio especificados, adquiridos ou desenvolvidos, e mantidos por todo o ciclo de vida | Amarelo | Os seis ativos estão especificados no catálogo de ativos reutilizáveis. Alguns foram desenvolvidos (núcleo da linha de produto, componentes de interface) e outros adquiridos (IPDD/ADWIN, pm4py). A manutenção depende do histórico do Git, sem plano. | Para cada ativo, registrar uma ficha com especificação, origem (desenvolvido ou adquirido), responsável, versão e testes. Ligar a manutenção dos ativos aos critérios e às revisões propostas no GRU 1 e no GRU 4. |
