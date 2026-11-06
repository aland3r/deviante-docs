"""Renderiza o modelo de características (gerar.py) em SVG e PNG,
na notação do FeatureIDE, em layout da esquerda para a direita."""
import math, subprocess
from pathlib import Path
from PIL import ImageFont
from gerar import MODELO, RESTRICOES, AQUI

FONTE = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
F_NO, F_REST, F_TIT = 14, 13.5, 20
med = ImageFont.truetype(FONTE, 100)
def largura(txt, tam): return med.getlength(txt) * tam / 100

ROW, BOX_H, GAP_X, PAD = 36, 26, 64, 16
COR = dict(conc_f="#dce8fb", conc_s="#2f5fa8", abs_f="#f1f3f6", abs_s="#8a94a6",
           linha="#3d4656", texto="#1b2230", fraco="#5b6577")

# ---- layout ----
def prof(n, d=0):
    n["d"] = d
    for f in n["filhos"]: prof(f, d + 1)
prof(MODELO)
def nos(n):
    yield n
    for f in n["filhos"]: yield from nos(f)
for n in nos(MODELO):
    n["w"] = largura(n["nome"], F_NO) + 2 * PAD
larg_col = {}
for n in nos(MODELO): larg_col[n["d"]] = max(larg_col.get(n["d"], 0), n["w"])
x_col, x = {}, 40
for d in sorted(larg_col): x_col[d] = x; x += larg_col[d] + GAP_X

linha = [0]
def posicionar(n, topo=False):
    n["x"] = x_col[n["d"]]
    if not n["filhos"]:
        n["y"] = 110 + linha[0] * ROW; linha[0] += 1
    else:
        for f in n["filhos"]:
            posicionar(f)
            if n is MODELO: linha[0] += 0.35  # respiro entre ramos
        n["y"] = (n["filhos"][0]["y"] + n["filhos"][-1]["y"]) / 2
posicionar(MODELO)
fim_arvore = max(n["y"] for n in nos(MODELO)) + BOX_H

# ---- restrições em texto ----
SIMB = {"imp": " ⇒ ", "and": " ∧ ", "or": " ∨ "}
def texto(e, top=True):
    if e[0] == "var": return e[1]
    if e[0] == "not": return "¬" + texto(e[1], False)
    s = SIMB[e[0]].join(texto(x, False) for x in e[1:])
    return s if top else f"({s})"

W = int(max(n["x"] + n["w"] for n in nos(MODELO)) + 40)
W = max(W, 1180)
y_rest = fim_arvore + 70
col_w = (W - 80 - 24) / 2
por_col = math.ceil(len(RESTRICOES) / 2)
H = int(y_rest + 18 + por_col * 34 + 64)

out = []
A = out.append
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Inter, Segoe UI, Arial, sans-serif">')
A(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
A(f'<text x="40" y="46" font-size="{F_TIT}" font-weight="600" fill="{COR["texto"]}">Modelo de características do Deviante</text>')
A(f'<text x="40" y="72" font-size="13.5" fill="{COR["fraco"]}">36 características · 11 restrições · notação FeatureIDE</text>')

def grupo(px, py, pts, tipo, r):
    a = [math.atan2(y - py, x - px) for x, y in pts]
    x1, y1 = px + r * math.cos(a[0]), py + r * math.sin(a[0])
    x2, y2 = px + r * math.cos(a[1]), py + r * math.sin(a[1])
    if tipo == "or":
        return f'<path d="M{px:.1f} {py:.1f} L{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f} Z" fill="{COR["linha"]}"/>'
    return f'<path d="M{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{COR["linha"]}" stroke-width="1.8"/>'

def ancora_dir(n): return n["x"] + n["w"], n["y"] + BOX_H / 2
def ancora_esq(n): return n["x"], n["y"] + BOX_H / 2

for n in nos(MODELO):
    if not n["filhos"]: continue
    px, py = ancora_dir(n)
    for f in n["filhos"]:
        cx, cy = ancora_esq(f)
        A(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{cx:.1f}" y2="{cy:.1f}" stroke="{COR["linha"]}" stroke-width="1.3"/>')
    if n["grupo"] in ("or", "alt"):
        pts = [ancora_esq(f) for f in (n["filhos"][0], n["filhos"][-1])]
        A(grupo(px, py, pts, n["grupo"], 46))

circulos = []
for n in nos(MODELO):
    if n["filhos"] and n["grupo"] == "and":
        for f in n["filhos"]:
            cx, cy = ancora_esq(f)
            fill = COR["linha"] if f["obrig"] else "#ffffff"
            circulos.append(f'<circle cx="{cx-6:.1f}" cy="{cy:.1f}" r="5.5" fill="{fill}" stroke="{COR["linha"]}" stroke-width="1.5"/>')

for n in nos(MODELO):
    abs_ = n["abstrata"]
    f, s = (COR["abs_f"], COR["abs_s"]) if abs_ else (COR["conc_f"], COR["conc_s"])
    A(f'<rect x="{n["x"]:.1f}" y="{n["y"]:.1f}" width="{n["w"]:.1f}" height="{BOX_H}" rx="5" fill="{f}" stroke="{s}" stroke-width="1.3"/>')
    style = ' font-style="italic"' if abs_ else ""
    A(f'<text x="{n["x"] + n["w"]/2:.1f}" y="{n["y"] + BOX_H/2 + 5:.1f}" font-size="{F_NO}" font-weight="500" text-anchor="middle" fill="{COR["texto"]}"{style}>{n["nome"]}</text>')

out.extend(circulos)

# restrições
A(f'<line x1="40" y1="{y_rest - 34}" x2="{W-40}" y2="{y_rest - 34}" stroke="#d7dbe2"/>')
A(f'<text x="40" y="{y_rest}" font-size="15" font-weight="600" fill="{COR["texto"]}">Restrições entre ramos</text>')
for i, (e, _) in enumerate(RESTRICOES):
    col, lin = divmod(i, por_col)
    x0 = 40 + col * (col_w + 24); y0 = y_rest + 18 + lin * 34
    A(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{col_w:.1f}" height="26" rx="5" fill="#f7f8fa" stroke="#d7dbe2"/>')
    A(f'<text x="{x0+12:.1f}" y="{y0+18:.1f}" font-size="{F_REST}" fill="{COR["fraco"]}">R{i+1:02d}</text>')
    A(f'<text x="{x0+50:.1f}" y="{y0+18:.1f}" font-size="{F_REST}" fill="{COR["texto"]}">{texto(e)}</text>')

# legenda
ly = H - 32; lx = 40
def leg(txt, desenho, w):
    global lx
    A(desenho(lx, ly)); A(f'<text x="{lx+30}" y="{ly+5}" font-size="13" fill="{COR["fraco"]}">{txt}</text>'); lx += w
leg("Obrigatória", lambda x, y: f'<circle cx="{x+10}" cy="{y}" r="5" fill="{COR["linha"]}"/>', 120)
leg("Opcional", lambda x, y: f'<circle cx="{x+10}" cy="{y}" r="5" fill="#fff" stroke="{COR["linha"]}" stroke-width="1.4"/>', 105)
def mini(x, y, tipo):
    linhas = f'<path d="M{x} {y} L{x+24} {y-9} M{x} {y} L{x+24} {y+9}" stroke="{COR["linha"]}" stroke-width="1.3"/>'
    return linhas + grupo(x, y, [(x+24, y-9), (x+24, y+9)], tipo, 16)
leg("Grupo Or", lambda x, y: mini(x, y, "or"), 120)
leg("Grupo Alternative", lambda x, y: mini(x, y, "alt"), 180)
leg("Concreta", lambda x, y: f'<rect x="{x}" y="{y-9}" width="22" height="18" rx="4" fill="{COR["conc_f"]}" stroke="{COR["conc_s"]}"/>', 110)
leg("Abstrata", lambda x, y: f'<rect x="{x}" y="{y-9}" width="22" height="18" rx="4" fill="{COR["abs_f"]}" stroke="{COR["abs_s"]}"/>', 110)
A("</svg>")

svg = AQUI / "modelo-de-caracteristicas.svg"
svg.write_text("\n".join(out), encoding="utf-8")
print(W, H)
