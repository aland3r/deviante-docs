# Parte I: modelo de características (FeatureIDE)

![Modelo de características do Driftor](modelo-de-caracteristicas.png)

O modelo tem 32 características e 10 restrições. Ele descreve as variações do Driftor entre as empresas clientes (Alfa, Beta, Gama e Delta) e entre papéis de usuário (administrador, gestor, operador e técnico).

A imagem acima é a versão em alta resolução, gerada do mesmo modelo. A imagem exportada do FeatureIDE (Eclipse) está em [`modelo-eclipse.png`](modelo-eclipse.png).

## Arquivos

| Arquivo | O que é |
|---|---|
| `model.xml` | Modelo para abrir no FeatureIDE (Eclipse) |
| `configs/*.xml` | Uma configuração por empresa cliente: Alfa, Beta, Gama, Delta |
| `modelo-eclipse.png` | Diagrama exportado do FeatureIDE |
| `modelo-de-caracteristicas.png` / `.svg` | Diagrama em alta resolução |
| `gerar.py` | Fonte única: gera `model.xml` e as configurações e valida o modelo por SAT |
| `renderizar.py` | Gera o diagrama em alta resolução a partir do mesmo modelo |

**Abrir no Eclipse:** File → New → Other… → FeatureIDE → FeatureIDE Project. Substitua o `model.xml` do projeto por este e copie `configs/` para a pasta `configs` do projeto.

**Validação:** `python gerar.py` confere que o modelo é satisfazível, que não há características mortas nem falso-opcionais, que nenhuma restrição é redundante e que as 4 configurações são válidas. O modelo admite 14.342 produtos.

## Estrutura

- **Login**: como se entra (Autenticacao: login demo ou Google) e com qual papel (Papeis).
- **Workspace**: os dois espaços de trabalho onde o usuário cria algo para analisar: Processo (log de eventos, mapeamento de atividades, grafo e filtros) e Monitoramento (máquinas acompanhadas).
- **Equipamento**: cadastro de máquinas e de seus componentes, independente do monitoramento.
- **Analise**: o que o Driftor calcula: desvio de processo (drift) e vida útil restante (RUL).
- **Agendamento**: intervenções agendadas nas máquinas: inspeção e manutenção.

Uma característica filha é parte da mãe e só existe com ela. Quem usa cada função não é hierarquia: aparece nas restrições com Papeis.

## Tipos de característica e justificativas

| Tipo | Características | Justificativa |
|---|---|---|
| **Abstrata** | Driftor, Login, Autenticacao, Papeis, Workspace, LogEventos, Filtros, Equipamento, Analise | Só organizam a árvore e não têm um trecho de código próprio. Equipamento, por exemplo, agrupa Máquina e Componente, que são as telas de fato. |
| **Concreta** | LoginDemo, LoginGoogle, os quatro papéis, Monitoramento, Processo, XES, CSV, MapeamentoAtividades, GrafoProcesso, NotasAtividade, os três filtros, Maquina, Componente, Desvio, RUL, Agendamento, Inspecao, Manutencao | Cada uma corresponde a uma tela, rota ou função do sistema. Agendamento é concreta porque a agenda é uma tela própria, além dos tipos de intervenção. |
| **Obrigatória** | Login, Autenticacao, Papeis, Workspace, Analise; LogEventos, MapeamentoAtividades e GrafoProcesso dentro de Processo; Maquina dentro de Equipamento | Todo produto tem entrada, papéis, ao menos um workspace e ao menos uma análise. Um processo sempre vem de um log, precisa do mapeamento para gerar as atividades e sempre mostra o grafo. Não há cadastro de equipamento sem máquina. |
| **Opcional** | Equipamento, Agendamento, Componente, NotasAtividade, Filtros | Variam de cliente para cliente. Empresas só com processos (Beta, Delta) não têm equipamentos nem agenda. Componente é uma variação prevista: ainda não está implementado. |
| **Grupo Or** (ao menos um) | Papeis; Workspace (Monitoramento, Processo); LogEventos (XES, CSV); Filtros; Analise (Desvio, RUL); Agendamento (Inspecao, Manutencao) | Um produto pode combinar livremente papéis, workspaces, formatos de log, filtros, análises e tipos de intervenção, mas precisa de ao menos um de cada grupo que tiver. |
| **Grupo Alternative** (exatamente um) | Autenticacao (LoginDemo, LoginGoogle) | Cada empresa cliente entra por um único método. As quatro empresas atuais usam o login demo; o login Google fica para clientes em produção. |

## Restrições

As 10 restrições usam os quatro operadores pedidos: Implies (⇒) em todas, And (∧) em R08, Or (∨) em R06 e R10 e Not (¬) em R04.

| # | Restrição | Justificativa |
|---|---|---|
| R01 | `Tecnico ⇒ Agendamento` | O técnico só trabalha na agenda; sem Agendamento ele não tem tela. |
| R02 | `Desvio ⇒ Processo` | O drift é detectado no log de eventos de um processo. |
| R03 | `RUL ⇒ Monitoramento` | O RUL usa as leituras de sensores das máquinas monitoradas. |
| R04 | `¬Maquina ⇒ ¬Agendamento` | Todo agendamento é de uma máquina: sem cadastro de máquinas não há agenda. |
| R05 | `Monitoramento ⇒ Maquina` | O monitoramento acompanha máquinas já cadastradas. |
| R06 | `Inspecao ⇒ (Operador ∨ Tecnico)` | A inspeção é feita pelo operador ou pelo técnico. |
| R07 | `RUL ⇒ Manutencao` | A previsão de vida útil só faz sentido se a falha prevista puder virar manutenção agendada. |
| R08 | `(LoginDemo ∧ Agendamento) ⇒ Tecnico` | No demo, empresa com agenda oferece também o técnico. |
| R09 | `NotasAtividade ⇒ Operador` | Só o operador anota detalhes de uma atividade do processo. |
| R10 | `Processo ⇒ (Administrador ∨ Gestor)` | Alguém precisa criar processos: o administrador ou o gestor. |

## Configurações por empresa

| Empresa | LoginGoogle | LoginDemo | XES | CSV | Maquina | Monitoramento | RUL | Manutencao | Tecnico |
|---|---|---|---|---|---|---|---|---|---|
| Alfa |  | ✓ | ✓ |  | ✓ | ✓ |  | ✓ | ✓ |
| Beta |  | ✓ |  | ✓ |  |  |  |  |  |
| Gama |  | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |
| Delta |  | ✓ | ✓ |  |  |  |  |  |  |

Todas as empresas têm Processo com mapeamento, grafo, notas de atividade, os três filtros, a análise de desvio e os papéis Administrador, Gestor e Operador. Inspeção e Componente estão no modelo, mas ainda não estão implementados, então nenhuma configuração atual os seleciona: são variações previstas.

R08 registra uma correção que o modelo apontou. Antes, Beta e Delta aceitavam login de técnico, mas o técnico só trabalha na agenda, que essas empresas não têm. Pela R01, essas configurações seriam inválidas. Agora o cartão de técnico só aparece nas empresas com agenda.
