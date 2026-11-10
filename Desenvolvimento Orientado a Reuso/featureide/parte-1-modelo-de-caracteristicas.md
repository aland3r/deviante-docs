# Parte I: Modelo de características do Driftor

## 1. Apresentação

O Driftor é uma plataforma de mineração de processos e manutenção industrial. Ela detecta desvios de processo (concept drift) em logs de eventos e prevê a vida útil restante (RUL) das máquinas. O produto atende várias empresas clientes (Driftor, Alfa, Beta, Gama e Delta), e cada uma usa um conjunto diferente de funções. Dentro de cada empresa, quatro papéis de usuário (administrador, gestor, operador e técnico) veem e fazem coisas diferentes.

O modelo de características abaixo descreve essa variabilidade. Ele foi elaborado no FeatureIDE (Eclipse), em um diagrama de características na notação FODA estendida. O modelo tem 32 características e 10 restrições.

[Figura 1: Modelo de características do Driftor, exportado do FeatureIDE]

## 2. Estrutura do modelo

A raiz, Driftor, tem cinco ramos:

- **Login**: como se entra no sistema (Autenticação, por login demo ou Google) e com qual papel (Papéis).
- **Workspace**: os dois espaços de trabalho onde o usuário cria algo para analisar. O Processo traz o log de eventos, o mapeamento de atividades, o grafo e os filtros. O Monitoramento acompanha as máquinas.
- **Equipamento**: cadastro de máquinas e dos seus componentes, independente do monitoramento.
- **Análise**: o que o sistema calcula, ou seja, desvio de processo e vida útil restante (RUL).
- **Agendamento**: intervenções agendadas nas máquinas, que podem ser inspeção ou manutenção.

Critério adotado: uma característica filha é parte da mãe e só existe com ela. O papel que usa cada função não é representado na hierarquia. Ele aparece nas restrições, ligando a função ao ramo Papéis.

## 3. Tipos de característica e justificativas

### 3.1 Abstract (abstrata)

**Características:** Driftor, Login, Autenticação, Papéis, Workspace, LogEventos, Filtros, Equipamento, Análise.

**Justificativa:** essas características só organizam a árvore e não correspondem a um trecho de código próprio. Equipamento, por exemplo, apenas agrupa Máquina e Componente, que são as telas de fato. LogEventos agrupa os formatos aceitos, e Filtros agrupa os três tipos de filtro.

### 3.2 Concrete (concreta)

**Características:** LoginDemo, LoginGoogle, Administrador, Operador, Gestor, Técnico, Monitoramento, Processo, XES, CSV, MapeamentoAtividades, GrafoProcesso, NotasAtividade, FiltrarTraces, FiltrarVariantes, FiltrarAtividades, Máquina, Componente, Desvio, RUL, Agendamento, Inspeção, Manutenção.

**Justificativa:** cada uma corresponde a uma tela, rota ou função implementada no sistema. Agendamento é concreta, e não abstrata, porque a agenda é uma tela própria, além dos tipos de intervenção que ela contém.

### 3.3 Mandatory (obrigatória)

**Características:** Login, Autenticação, Papéis, Workspace e Análise (sob a raiz); LogEventos, MapeamentoAtividades e GrafoProcesso (sob Processo); Máquina (sob Equipamento).

**Justificativa:** todo produto tem uma forma de entrada, papéis de usuário, ao menos um workspace e ao menos um tipo de análise. Um processo sempre vem de um log de eventos, sempre precisa do mapeamento das colunas do log para gerar as atividades e sempre exibe o grafo. Não existe cadastro de equipamento sem máquina.

### 3.4 Optional (opcional)

**Características:** Equipamento, Agendamento, Componente, NotasAtividade, Filtros.

**Justificativa:** variam de cliente para cliente. Empresas que só analisam processos (Beta e Delta) não têm equipamentos nem agenda. As notas de atividade e os filtros são recursos complementares do processo. Componente é uma variação prevista, porque o componente só pode ser cadastrado dentro de uma máquina e ainda não está implementado.

### 3.5 Or Group (grupo Or, ao menos um)

**Grupos:** Papéis (Administrador, Operador, Gestor, Técnico); Workspace (Monitoramento, Processo); LogEventos (XES, CSV); Filtros (FiltrarTraces, FiltrarVariantes, FiltrarAtividades); Análise (Desvio, RUL); Agendamento (Inspeção, Manutenção).

**Justificativa:** um produto pode combinar livremente papéis, workspaces, formatos de log, filtros, análises e tipos de intervenção, mas precisa de ao menos uma opção em cada grupo que tiver. Uma empresa pode, por exemplo, aceitar logs em XES e em CSV, ou só em um deles.

### 3.6 Alternative Group (grupo alternativo, exatamente um)

**Grupo:** Autenticação (LoginDemo, LoginGoogle).

**Justificativa:** cada empresa entra por um único método. A empresa Driftor entra só pelo Google, e as empresas do protótipo entram só pelo login demo. Os dois métodos nunca convivem na mesma configuração.

## 4. Restrições (constraints)

As 10 restrições usam os quatro operadores pedidos: Implies (⇒) em todas, And (∧) em R08, Or (∨) em R06 e R10 e Not (¬) em R04.

| # | Restrição | Operadores | Justificativa |
|---|---|---|---|
| R01 | Tecnico ⇒ Agendamento | Implies | O técnico só trabalha na agenda; sem Agendamento ele não tem tela. |
| R02 | Desvio ⇒ Processo | Implies | O desvio (drift) é detectado no log de eventos de um processo. |
| R03 | RUL ⇒ Monitoramento | Implies | O RUL usa as leituras de sensores das máquinas monitoradas. |
| R04 | ¬Maquina ⇒ ¬Agendamento | Implies, Not | Todo agendamento é de uma máquina: sem cadastro de máquinas não há agenda. |
| R05 | Monitoramento ⇒ Maquina | Implies | O monitoramento acompanha máquinas já cadastradas. |
| R06 | Inspecao ⇒ (Operador ∨ Tecnico) | Implies, Or | A inspeção é feita pelo operador ou pelo técnico. |
| R07 | RUL ⇒ Manutencao | Implies | A previsão de vida útil só faz sentido se a falha prevista puder virar uma manutenção agendada. |
| R08 | (LoginDemo ∧ Agendamento) ⇒ Tecnico | Implies, And | No login demo, a empresa com agenda oferece também o perfil de técnico. |
| R09 | NotasAtividade ⇒ Operador | Implies | Só o operador anota detalhes de uma atividade do processo. |
| R10 | Processo ⇒ (Administrador ∨ Gestor) | Implies, Or | Alguém precisa criar processos: o administrador ou o gestor. |

O modelo foi verificado: não há características mortas (que nunca podem ser selecionadas), nem falso-opcionais (opcionais que as restrições tornam obrigatórias), nem restrições redundantes. O modelo admite 14.342 produtos válidos.

## 5. Configurações por empresa

Cada empresa cliente é uma configuração válida do modelo.

| Empresa | Login | Log | Máquina | Monitoramento | RUL | Manutenção | Técnico |
|---|---|---|---|---|---|---|---|
| Driftor | Google | XES e CSV | ✓ | ✓ | ✓ | ✓ | ✓ |
| Alfa | Demo | XES | ✓ | ✓ | | ✓ | ✓ |
| Beta | Demo | CSV | | | | | |
| Gama | Demo | XES | ✓ | ✓ | ✓ | ✓ | ✓ |
| Delta | Demo | XES | | | | | |

Todas as empresas têm Processo com mapeamento, grafo, notas de atividade e os três filtros, a análise de desvio e os papéis Administrador, Gestor e Operador. Inspeção e Componente estão no modelo, mas nenhuma configuração atual os seleciona, porque são variações previstas que ainda não estão implementadas.

A restrição R08 registra uma correção que o próprio modelo apontou. Antes, Beta e Delta ofereciam o login de técnico, mas essas empresas não têm agenda, que é a única tela do técnico. Pela R01, essas configurações seriam inválidas. Depois da correção, o perfil de técnico só aparece no login demo das empresas que têm agenda.
