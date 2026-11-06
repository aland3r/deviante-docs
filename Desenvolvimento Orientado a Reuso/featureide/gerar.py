"""Fonte única do modelo de características do Deviante.

Gera model.xml (FeatureIDE), um arquivo de configuração por empresa,
valida o modelo com SAT (features mortas, falso-opcionais, restrições
redundantes, configurações válidas) e renderiza o diagrama em SVG.
Uso: python gerar.py   (requer python-sat)
"""
from pathlib import Path
from xml.sax.saxutils import escape
from itertools import count
from pysat.solvers import Minisat22

AQUI = Path(__file__).parent

# (nome, rótulo, tipo do grupo dos filhos, abstrata, obrigatória, filhos)
def F(nome, rotulo, grupo="and", abstrata=False, obrig=False, filhos=()):
    return dict(nome=nome, rotulo=rotulo, grupo=grupo, abstrata=abstrata, obrig=obrig, filhos=list(filhos))

MODELO = F("Deviante", "Deviante", abstrata=True, obrig=True, filhos=[
    F("Autenticacao", "Autenticação", abstrata=True, obrig=True, filhos=[
        F("MetodoLogin", "Método de login", "alt", abstrata=True, obrig=True, filhos=[
            F("LoginGoogle", "Login Google"),
            F("LoginDemo", "Login Demo"),
        ]),
        F("Papeis", "Papéis", "or", abstrata=True, obrig=True, filhos=[
            F("Administrador", "Administrador"),
            F("Gestor", "Gestor", filhos=[F("Visibilidade", "Visibilidade")]),
            F("Operador", "Operador", filhos=[F("NotasTrace", "Notas de trace")]),
            F("Tecnico", "Técnico", filhos=[F("VerAnaliseOrigem", "Ver análise de origem")]),
        ]),
    ]),
    F("Workspace", "Workspace", abstrata=True, obrig=True, filhos=[
        F("Processos", "Processos", obrig=True, filhos=[
            F("UploadLog", "Upload de log", obrig=True),
            F("MapeamentoOperacoes", "Mapeamento de operações", obrig=True),
            F("GrafoProcesso", "Grafo do processo", obrig=True),
            F("FormatoLog", "Formato do log", "or", abstrata=True, obrig=True, filhos=[
                F("XES", "XES"),
                F("CSV", "CSV"),
            ]),
        ]),
        F("AnaliseDrift", "Análise de drift", abstrata=True, obrig=True, filhos=[
            F("DetectorADWIN", "Detector IPDD/ADWIN", obrig=True),
            F("TratamentoSerie", "Tratamento da série", "or", abstrata=True, obrig=True, filhos=[
                F("SerieBruta", "Série bruta"),
                F("SerieTratada", "Série tratada"),
            ]),
            F("HistoricoAnalises", "Histórico de análises"),
        ]),
        F("Monitoramento", "Monitoramento"),
    ]),
    F("CatalogoAtividades", "Catálogo de atividades", obrig=True),
    F("Plano", "Plano", "alt", abstrata=True, obrig=True, filhos=[
        F("PlanoEssencial", "Essencial", abstrata=True),
        F("PlanoManutencao", "Manutenção", abstrata=True),
    ]),
    F("ModuloManutencao", "Módulo de manutenção", abstrata=True, filhos=[
        F("Equipamentos", "Equipamentos", obrig=True),
        F("Agendamentos", "Agendamentos", obrig=True, filhos=[
            F("TipoIntervencao", "Tipo de intervenção", "or", abstrata=True, obrig=True, filhos=[
                F("Manutencao", "Manutenção"),
                F("Inspecao", "Inspeção"),
            ]),
        ]),
        F("PredicaoRF", "Predição RF"),
    ]),
    F("ExportarAgendaCSV", "Exportar agenda CSV"),
])

# Restrições: árvore de ('imp'|'and'|'or'|'not'|'var', ...)
def V(n): return ("var", n)
def IMP(a, b): return ("imp", a, b)
def AND(*a): return ("and",) + a
def OR(*a): return ("or",) + a
def NOT(a): return ("not", a)

RESTRICOES = [
    (IMP(V("PlanoEssencial"), NOT(V("ModuloManutencao"))), "O plano Essencial não inclui o módulo de manutenção."),
    (IMP(V("PlanoManutencao"), V("ModuloManutencao")), "O plano Manutenção sempre traz o módulo."),
    (IMP(V("Tecnico"), V("Agendamentos")), "O técnico só trabalha na agenda; sem Agendamentos ele não tem tela."),
    (IMP(V("PredicaoRF"), V("Monitoramento")), "A predição RF usa as leituras de sensores do monitoramento."),
    (IMP(V("ExportarAgendaCSV"), V("Agendamentos")), "A exportação é da agenda de manutenção."),
    (IMP(V("Visibilidade"), OR(V("Operador"), V("Tecnico"))), "Ocultar objetos só faz sentido se existe operador ou técnico."),
    (IMP(V("VerAnaliseOrigem"), V("HistoricoAnalises")), "O técnico abre a análise salva que originou o agendamento."),
    (IMP(V("Monitoramento"), V("Equipamentos")), "O monitoramento lê sensores das máquinas cadastradas."),
    (IMP(V("LoginDemo"), AND(V("Gestor"), V("Operador"))), "O login demo sempre oferece os cartões de gestor e operador."),
    (IMP(AND(V("LoginDemo"), V("PlanoManutencao")), V("Tecnico")), "No demo, empresa com manutenção oferece também o técnico."),
    (IMP(V("CatalogoAtividades"), OR(V("Administrador"), V("Gestor"))), "O catálogo precisa de quem o mantém (administrador) ou o usa no mapeamento (gestor)."),
    (IMP(V("Inspecao"), V("Tecnico")), "A inspeção é feita em campo pelo técnico, que registra o resultado."),
]

# Configurações (features concretas e de plano escolhidas; o resto é derivado)
EMPRESAS = {
    "Deviante": ["LoginGoogle", "XES", "CSV", "SerieBruta", "SerieTratada", "HistoricoAnalises",
                 "PlanoManutencao", "Equipamentos", "Agendamentos", "Manutencao", "Monitoramento", "PredicaoRF", "ExportarAgendaCSV",
                 "Administrador", "Gestor", "Visibilidade", "Operador", "NotasTrace", "Tecnico", "VerAnaliseOrigem"],
    "Alfa": ["LoginDemo", "XES", "SerieBruta", "SerieTratada", "HistoricoAnalises", "PlanoManutencao", "Equipamentos", "Agendamentos", "Manutencao",
             "Monitoramento", "ExportarAgendaCSV", "Administrador", "Gestor", "Visibilidade", "Operador",
             "NotasTrace", "Tecnico", "VerAnaliseOrigem"],
    "Beta": ["LoginDemo", "CSV", "SerieBruta", "SerieTratada", "HistoricoAnalises", "PlanoEssencial",
             "Administrador", "Gestor", "Visibilidade", "Operador", "NotasTrace"],
    "Gama": ["LoginDemo", "XES", "SerieBruta", "SerieTratada", "HistoricoAnalises", "PlanoManutencao", "Equipamentos", "Agendamentos", "Manutencao",
             "Monitoramento", "PredicaoRF", "Administrador", "Gestor", "Visibilidade", "Operador",
             "NotasTrace", "Tecnico", "VerAnaliseOrigem"],
    "Delta": ["LoginDemo", "XES", "SerieBruta", "SerieTratada", "HistoricoAnalises", "PlanoEssencial",
              "Administrador", "Gestor", "Visibilidade", "Operador", "NotasTrace"],
}

# ---------- utilidades ----------
def todos(n=MODELO, pai=None):
    yield n, pai
    for f in n["filhos"]:
        yield from todos(f, n)

NOS = {n["nome"]: n for n, _ in todos()}
PAI = {n["nome"]: (p["nome"] if p else None) for n, p in todos()}

# ---------- model.xml ----------
def xml_no(n, ind):
    tag = "feature" if not n["filhos"] else n["grupo"]
    attrs = []
    if n["abstrata"]: attrs.append('abstract="true"')
    if n["obrig"]: attrs.append('mandatory="true"')
    attrs.append(f'name="{n["nome"]}"')
    pad = "\t" * ind
    desc = f'{pad}\t<description>{escape(n["rotulo"])}</description>\n'
    if not n["filhos"]:
        return f'{pad}<feature {" ".join(attrs)}>\n{desc}{pad}</feature>\n'
    corpo = desc + "".join(xml_no(f, ind + 1) for f in n["filhos"])
    return f'{pad}<{tag} {" ".join(attrs)}>\n{corpo}{pad}</{tag}>\n'

def xml_expr(e, ind):
    pad = "\t" * ind
    if e[0] == "var":
        return f"{pad}<var>{e[1]}</var>\n"
    tag = {"imp": "imp", "and": "conj", "or": "disj", "not": "not"}[e[0]]
    return f"{pad}<{tag}>\n" + "".join(xml_expr(x, ind + 1) for x in e[1:]) + f"{pad}</{tag}>\n"

def gerar_model_xml():
    s = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<featureModel>\n\t<properties/>\n\t<struct>\n'
    s += xml_no(MODELO, 2)
    s += "\t</struct>\n\t<constraints>\n"
    for i, (e, just) in enumerate(RESTRICOES, 1):
        s += f'\t\t<rule>\n\t\t\t<description>R{i:02d}. {escape(just)}</description>\n' + xml_expr(e, 3) + "\t\t</rule>\n"
    s += "\t</constraints>\n</featureModel>\n"
    (AQUI / "model.xml").write_text(s, encoding="utf-8")

def completar(escolhidas):
    sel = set(escolhidas)
    for n in list(sel):  # sobe até a raiz
        while PAI[n]:
            n = PAI[n]; sel.add(n)
    mudou = True
    while mudou:  # desce pelos obrigatórios
        mudou = False
        for nome in list(sel):
            for f in NOS[nome]["filhos"]:
                if f["obrig"] and f["nome"] not in sel:
                    sel.add(f["nome"]); mudou = True
    return sel

def gerar_configs():
    pasta = AQUI / "configs"; pasta.mkdir(exist_ok=True)
    for emp, esc in EMPRESAS.items():
        sel = completar(esc)
        linhas = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>', "<configuration>"]
        for nome in NOS:
            estado = "selected" if nome in sel else "unselected"
            linhas.append(f'\t<feature manual="{estado}" name="{nome}"/>')
        linhas.append("</configuration>")
        (pasta / f"{emp}.xml").write_text("\n".join(linhas) + "\n", encoding="utf-8")

# ---------- SAT ----------
IDS = {nome: i for i, nome in zip(count(1), NOS)}

def cnf_arvore():
    cl = [[IDS["Deviante"]]]
    for n, p in todos():
        x = IDS[n["nome"]]
        if p:
            cl.append([-x, IDS[p["nome"]]])
            if n["obrig"] and p["grupo"] == "and":
                cl.append([-IDS[p["nome"]], x])
        if n["filhos"] and n["grupo"] in ("or", "alt"):
            fs = [IDS[f["nome"]] for f in n["filhos"]]
            cl.append([-x] + fs)
            if n["grupo"] == "alt":
                for i in range(len(fs)):
                    for j in range(i + 1, len(fs)):
                        cl.append([-fs[i], -fs[j]])
    return cl

aux = count(1000)
def tseitin(e, cl):
    if e[0] == "var": return IDS[e[1]]
    if e[0] == "not": return -tseitin(e[1], cl)
    if e[0] == "imp": return tseitin(("or", ("not", e[1]), e[2]), cl)
    lits = [tseitin(x, cl) for x in e[1:]]
    y = next(aux)
    if e[0] == "and":
        for l in lits: cl.append([-y, l])
        cl.append([y] + [-l for l in lits])
    else:
        cl.append([-y] + lits)
        for l in lits: cl.append([y, -l])
    return y

def cnf_restricao(e):
    cl = []; y = tseitin(e, cl); cl.append([y]); return cl, y

def sat(clausulas, supor=()):
    with Minisat22(bootstrap_with=clausulas) as s:
        return s.solve(assumptions=list(supor))

def validar():
    base = cnf_arvore()
    todas = list(base)
    for e, _ in RESTRICOES: todas += cnf_restricao(e)[0]
    erros = []
    assert sat(todas), "modelo vazio"
    for nome, x in IDS.items():
        if not sat(todas, [x]): erros.append(f"feature morta: {nome}")
        n, p = NOS[nome], PAI[nome]
        if p and not n["obrig"] and not sat(todas, [IDS[p], -x]):
            erros.append(f"falso-opcional: {nome}")
    for i, (e, _) in enumerate(RESTRICOES):
        resto = list(base)
        for j, (e2, _) in enumerate(RESTRICOES):
            if j != i: resto += cnf_restricao(e2)[0]
        neg, y = cnf_restricao(("not", e))
        if not sat(resto + neg): erros.append(f"restrição redundante: R{i+1:02d}")
    for emp, esc in EMPRESAS.items():
        sel = completar(esc)
        if not sat(todas, [IDS[n] if n in sel else -IDS[n] for n in IDS]):
            erros.append(f"configuração inválida: {emp}")
    return erros

def contar_produtos():
    todas = list(cnf_arvore())
    for e, _ in RESTRICOES: todas += cnf_restricao(e)[0]
    n = 0
    with Minisat22(bootstrap_with=todas) as s:
        for m in s.enum_models():
            n += 1
            s.add_clause([-l for l in m if abs(l) in IDS.values()])
    return n

if __name__ == "__main__":
    gerar_model_xml(); gerar_configs()
    erros = validar()
    print("features:", len(NOS), "restrições:", len(RESTRICOES))
    print("\n".join(erros) or "modelo válido: sem features mortas, falso-opcionais ou restrições redundantes; 5 configurações válidas")
    print("produtos possíveis:", contar_produtos())
