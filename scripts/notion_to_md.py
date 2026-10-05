#!/usr/bin/env python3
"""Converte o conteúdo da página arc42 do Notion (fonte de verdade) em
architecture/arc42.md.

Uso: python3 scripts/notion_to_md.py notion.txt > architecture/arc42.md

A entrada é o texto entre <content> e </content> devolvido pela leitura da
página no Notion (Markdown estendido do Notion).
"""
import re
import sys

HEADER = """# Arquitetura do Deviante — arc42

"""


def cells(row):
    return [c.strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]


def table_to_md(block):
    rows = [cells(r) for r in re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S)]
    rows = [r for r in rows if r]
    if not rows:
        return ""
    clean = lambda c: inline(c.replace("\n", " ")).replace("|", "\\|")
    out = ["| " + " | ".join(clean(c) for c in rows[0]) + " |",
           "|" + "|".join("---" for _ in rows[0]) + "|"]
    out += ["| " + " | ".join(clean(c) for c in r) + " |" for r in rows[1:]]
    return "\n".join(out)


def inline(text):
    # [Fly.io](http://Fly.io) -> Fly.io (autolink que o Notion cria)
    text = re.sub(r"\[([^\]]+)\]\(https?://\1/?\)", r"\1", text)
    # menções a páginas do Notion viram link
    text = re.sub(r'(?:página )?<mention-page url="([^"]+)"\s*/>', r"[página no Notion](\1)", text)
    text = re.sub(r'<mention-page url="([^"]+)">([^<]*)</mention-page>', r"[\2](\1)", text)
    return text


def convert(src):
    src = src.strip()
    src = re.sub(r"^<content>\s*|\s*</content>$", "", src)
    src = re.sub(r"<callout[^>]*>.*?</callout>\s*", "", src, flags=re.S)
    src = re.sub(r"<empty-block\s*/>", "", src)
    # imagens do Notion (render do diagrama para quem lê no Notion) não vão
    # para o site, que renderiza o Mermaid; toggles são desembrulhados
    src = re.sub(r"^!\[[^\]]*\]\(notion-file-block://[^)]*\)\s*$", "", src, flags=re.M)
    src = re.sub(r"^</?details[^>]*>\s*$|^<summary>.*</summary>\s*$", "", src, flags=re.M)
    src = re.sub(r"^\t+(```)", r"\1", src, flags=re.M)
    out, lines, i = [], src.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("\n".join(lines[i:j + 1]))
            i = j + 1
        elif line.lstrip().startswith("<table"):
            j = i
            while j < len(lines) and "</table>" not in lines[j]:
                j += 1
            out.append(table_to_md("\n".join(lines[i:j + 1])))
            i = j + 1
        elif line.strip():
            out.append(inline(line.strip()))
            i += 1
        else:
            i += 1
    body = "\n\n".join(out)
    # títulos de nível 2 separados por regra, como no padrão arc42
    body = re.sub(r"\n\n## ", "\n\n---\n\n## ", body)
    return HEADER + body + "\n"


if __name__ == "__main__":
    sys.stdout.write(convert(open(sys.argv[1], encoding="utf-8").read()))
