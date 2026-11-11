# Torno CNC (log sintético de demonstração)

Log de eventos sintético para mostrar o Driftor: grafo com várias etapas e variantes, e uma série com mudanças de patamar fáceis de ver.

- `torno-cnc.xes`: 500 traces (OP-0001 a OP-0500), eventos start/complete, nomes das atividades em português.
- `gerar_torno_cnc.py`: gera o arquivo (`python gerar_torno_cnc.py torno-cnc.xes 7`). A semente 7 reproduz o arquivo publicado.

## Atividades e variantes

8 atividades: Carregamento de matéria-prima, Parada curta, Máquina em operação, Medição, Ajuste de ferramenta, Descarregamento de produto acabado, Apontamento de Kanban e Limpeza.

| Variante | Sequência | Traces |
| --- | --- | --- |
| 1 | Carregamento → Máquina → Medição → Descarregamento | 227 |
| 2 | Carregamento → Parada curta → Máquina → Medição → Descarregamento | 73 |
| 3 | variante 1 + Apontamento de Kanban | 54 |
| 4 | Carregamento → Máquina → Descarregamento (sem medição) | 42 |
| 5 | variante 1 + Limpeza | 37 |
| 6 | variante 1 com Ajuste de ferramenta e nova usinagem após a medição | 31 |
| 7 | variante 2 + Apontamento de Kanban | 25 |
| 8 | variante 2 com Ajuste de ferramenta | 11 |

## Desvios esperados

O tempo de ciclo da máquina muda de patamar a cada 100 traces (170 s, 300 s, 160 s, 310 s e 210 s). Na série "duração total de cada trace", tratamento bruto, o ADWIN marca 4 desvios, perto dos traces 100, 200, 300 e 400, tanto com δ 0,002 quanto com δ 0,02.
