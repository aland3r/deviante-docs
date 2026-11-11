"""Gera o log sintético Torno CNC (XES, start/complete) com 8 atividades, 8 variantes e mudanças de patamar."""
import random, sys
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import quoteattr

SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 7
OUT = sys.argv[1]
rng = random.Random(SEED)
C, P, M, ME, A, D, K, L = ("Carregamento de matéria-prima", "Parada curta", "Máquina em operação", "Medição",
                           "Ajuste de ferramenta", "Descarregamento de produto acabado", "Apontamento de Kanban", "Limpeza")
VARIANTS = [
    (45, [C, M, ME, D]),
    (15, [C, P, M, ME, D]),
    (10, [C, M, ME, D, K]),
    (8, [C, M, D]),
    (8, [C, M, ME, D, L]),
    (6, [C, M, ME, A, M, ME, D]),
    (5, [C, P, M, ME, D, K]),
    (3, [C, P, M, ME, A, M, ME, D]),
]
N = 500
# patamares do tempo de ciclo da máquina (s): 5 trechos = 4 mudanças
LEVELS = [(0, 170), (100, 300), (200, 160), (300, 310), (400, 210)]
BASE = {C: (14, 2), P: (25, 5), ME: (40, 5), A: (90, 10), D: (12, 2), K: (20, 3), L: (60, 8)}

def level(i):
    v = LEVELS[0][1]
    for start, val in LEVELS:
        if i >= start: v = val
    return v

seq_pool = [s for w, s in VARIANTS for _ in range(w)]
t = datetime(2026, 3, 2, 7, 0, 0, tzinfo=timezone(timedelta(hours=-3)))
out = ['<?xml version="1.0" encoding="UTF-8" ?>', '<log xes.version="1.0" xes.features="nested-attributes" openxes.version="1.0RC7">',
       '\t<extension name="Lifecycle" prefix="lifecycle" uri="http://www.xes-standard.org/lifecycle.xesext"/>',
       '\t<extension name="Time" prefix="time" uri="http://www.xes-standard.org/time.xesext"/>',
       '\t<extension name="Concept" prefix="concept" uri="http://www.xes-standard.org/concept.xesext"/>',
       '\t<string key="concept:name" value="Torno CNC"/>']
for i in range(N):
    seq = rng.choice(seq_pool)
    out.append('\t<trace>')
    out.append(f'\t\t<string key="concept:name" value="OP-{i + 1:04d}"/>')
    for act in seq:
        if act == M:
            dur = max(60, round(rng.gauss(level(i), 10)))
        else:
            mu, sd = BASE[act]
            dur = max(1, round(rng.gauss(mu, sd)))
        for lc, ts in (("start", t), ("complete", t + timedelta(seconds=dur))):
            out.append('\t\t<event>')
            out.append(f'\t\t\t<string key="concept:name" value={quoteattr(act)}/>')
            out.append(f'\t\t\t<string key="lifecycle:transition" value="{lc}"/>')
            out.append(f'\t\t\t<date key="time:timestamp" value="{ts.isoformat(timespec="milliseconds")}"/>')
            out.append('\t\t</event>')
        t += timedelta(seconds=dur)
    out.append('\t</trace>')
    t += timedelta(seconds=rng.randint(20, 90))
out.append('</log>')
open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
