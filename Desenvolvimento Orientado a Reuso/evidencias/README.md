# Evidências de variabilidade e reuso

Prints do sistema em produção (`deviante.alander.io`), tirados em 16/10/2026 com as contas do "Modo Protótipo". As janelas amarelas à esquerda são as colas de variabilidade da própria interface: cada uma diz o ponto de variação daquela tela e em que arquivo ele está.

## 1. Variabilidade por empresa (plano e função exclusiva)

O produto é o mesmo; cada empresa recebe uma variante definida no `application.yaml` (plano + funções exclusivas).

| | |
|---|---|
| ![Login com a escolha da empresa](01-login-empresas.png) | **Escolha da empresa no login.** As setas trocam a empresa cliente (Alfa, plano Manutenção + CSV exclusivo, 1/4); os quatro papéis entram em qualquer uma. |
| ![Alfa, Gestor](02-alfa-gestor-menu.png) | **Alfa, plano Manutenção.** O menu tem Equipamentos e Agendamentos (módulo opcional). O painel mostra só os processos e análises da Alfa. |
| ![Alfa, Agendamentos com CSV](03-alfa-agendamentos-csv.png) | **Função exclusiva.** Na Alfa, Agendamentos tem "Exportar CSV". |
| ![Gama, Agendamentos sem CSV](04-gama-agendamentos-sem-csv.png) | **Mesmo plano, outra variante.** A Gama também tem o módulo de manutenção, mas não contratou o CSV: o botão não existe. |
| ![Beta, plano Essencial](05-beta-sem-modulo.png) | **Plano Essencial.** Na Beta o menu só tem Projetos: sem Equipamentos e Agendamentos. Os dados também são outros (o torno real). |
| ![Administrador](06-admin-todas-empresas.png) | **Administrador.** Vê os processos de todas as empresas, com o selo da empresa dona em cada card (Beta, Delta…), e ainda Operações e Atividades no menu. |

## 2. Variabilidade por papel (Alfa)

A empresa define o que o produto tem; o papel define o que cada usuário vê e faz.

| | |
|---|---|
| ![Gestor oculta um processo](07-gestor-visibilidade.png) | **Gestor: visibilidade.** Em cada processo, "Visibilidade" permite ocultá-lo para o Operador ou para o Técnico. Aqui o processo "ST_20 · sem desvio (artigo)" é ocultado para o Operador. |
| ![Operador, painel](08-operador-menu.png) | **Operador.** Menu só com Projetos, sem "Novo processo". O processo ocultado pelo gestor (ST_20) não aparece: são 3 processos, contra 4 do gestor. |
| ![Operador, Editar no grafo](09-operador-editar-grafo.png) | **Operador no grafo.** Ao passar o mouse na atividade "Short_Downtime", aparece "Editar". O operador não renomeia, não carrega log e não exclui. |
| ![Detalhe do trace](10-operador-detalhe-trace.png) | **Detalhe do trace.** O modal escolhe o caso (trace 497) e grava o detalhe naquela atividade; a lista mostra as notas já salvas (casos 497 e 498). |
| ![Técnico, tela inicial](11-tecnico-inicio.png) | **Técnico.** A tela inicial é Agendamentos e o menu só tem Agendamentos. Não há "Nova manutenção". |
| ![Técnico, modal da manutenção](12-tecnico-status.png) | **Técnico na manutenção.** O modal só tem Situação e Observações: sem editar título, máquina ou datas, e sem excluir. O link "Ver análise de origem" aparece quando a manutenção tem um processo de origem; esta foi criada antes do campo existir. |
| ![Técnico registra o andamento](13-tecnico-analise.png) | **Técnico registra o andamento.** Situação "Em andamento" e a observação "Ferramenta trocada; aguardando teste de operação". |

## 3. Reuso

| | |
|---|---|
| ![FormModal no equipamento](14-formmodal-equipamento.png) | **Componente reutilizado (`@deviante/ui`).** O modal "Cadastrar equipamento" é o `FormModal` do pacote, com os campos `Field`, `TextInput` e `Select`. |
| ![FormModal na agenda](15-formmodal-agenda.png) | **O mesmo componente em outro CRUD.** "Nova manutenção" usa o mesmo `FormModal`; só os campos mudam. |
| ![Observer: contador do menu](16-observer-contador.png) | **Observer.** Depois de salvar uma manutenção, o contador ao lado de "Agendamentos" passa de 1 (print 03) para 2 sem recarregar a página: o formulário publica no `maintenanceSubject` e o contador do menu é um dos assinantes. |
| ![Análise de drift](17-analise-drift.png) | **Adapter e Singleton na análise.** A análise do DR_20 detecta 4 desvios com IPDD + ADWIN (δ 0,002, série crua), o mesmo resultado do artigo. O código da pesquisa roda sem alteração por trás do `IpddAdwinAdapter`, chamado pelo `AnalysisEngine` (Singleton). |

## Onde está cada ponto no código

- Empresa e plano: `deviante-api/src/main/kotlin/variability/ProductLine.kt`, `application.yaml` (`productLine`), `deviante-web/src/lib/features.js`. Detalhes em [`defesa/variabilidade.md`](../defesa/variabilidade.md) §1–§4.
- Papel: `deviante-api/src/main/kotlin/model/ManagerRecord.kt`, `deviante-web/src/lib/permissions.js`. Detalhes em [`defesa/variabilidade.md`](../defesa/variabilidade.md) §5.
- Padrões: [`defesa/padroes-de-projeto.md`](../defesa/padroes-de-projeto.md). Ativos: [`ativos-reutilizaveis.md`](../ativos-reutilizaveis.md).
