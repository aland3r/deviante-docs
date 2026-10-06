#!/usr/bin/env python3
"""Aplica páginas do arc42 lidas do Notion em architecture/arc42.md.

Uso: python3 scripts/sync_arc42.py <pasta> [architecture/arc42.md]

A pasta tem um arquivo por página lida, com o nome igual ao número da
seção: 00.txt é a página pai (linha do grupo), 01.txt a 12.txt são as
subpáginas. Cada arquivo traz o texto devolvido pela leitura da página no
Notion, com o trecho <content>...</content>; o resto é ignorado. Só as
seções presentes na pasta são trocadas, as demais ficam como estão.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from notion_to_md import HEADER, convert  # noqa: E402

SEP = "\n\n---\n\n"


def content(path):
    text = path.read_text(encoding="utf-8")
    m = re.search(r"<content>.*</content>", text, re.S)
    if not m:
        sys.exit(f"{path}: sem <content>...</content>")
    return m.group(0)


def body(src):
    return convert(src)[len(HEADER):].strip()


def main():
    folder = pathlib.Path(sys.argv[1])
    md_path = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "architecture/arc42.md")
    md = md_path.read_text(encoding="utf-8")
    head, *sections = md.rstrip("\n").split(SEP)
    by_num = {}
    for s in sections:
        m = re.match(r"## (\d+)\. ", s)
        if not m:
            sys.exit("seção sem título '## N. ' no arc42.md")
        by_num[int(m.group(1))] = s

    changed = []
    parent = folder / "00.txt"
    if parent.exists():
        # a página pai só contribui a linha do grupo (o aviso e os links das
        # subpáginas não vão para o site)
        src = re.sub(r"^\s*<page [^>]*>.*?</page>\s*$", "", content(parent), flags=re.M)
        new_head = (HEADER + body(src)).rstrip()
        if new_head != head:
            head = new_head
            changed.append("cabeçalho")

    for n in range(1, 13):
        f = folder / f"{n:02d}.txt"
        if not f.exists():
            continue
        title = by_num[n].split("\n", 1)[0]
        new = title + "\n\n" + body(content(f))
        if new != by_num[n]:
            by_num[n] = new
            changed.append(f"§{n}")

    out = SEP.join([head] + [by_num[n] for n in sorted(by_num)]) + "\n"
    md_path.write_text(out, encoding="utf-8")
    print("alteradas: " + (", ".join(changed) if changed else "nenhuma"))


if __name__ == "__main__":
    main()
