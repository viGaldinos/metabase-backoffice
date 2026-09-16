#!/usr/bin/env python3
"""Gera metabase-backoffice.zip no layout que o Claude.ai espera.

O pacote precisa de uma pasta-raiz com o nome da skill, contendo SKILL.md e
reference/. README, GUIA e este script ficam de fora.

Usa apenas a stdlib — não depende de `zip` instalado no sistema.
"""
import pathlib
import zipfile

SKILL = "metabase-backoffice"
ROOT = pathlib.Path(__file__).resolve().parent
DEST = ROOT / f"{SKILL}.zip"

INCLUIR = ["SKILL.md", "reference"]

def arquivos():
    for nome in INCLUIR:
        alvo = ROOT / nome
        if alvo.is_file():
            yield alvo
        else:
            yield from sorted(p for p in alvo.rglob("*") if p.is_file())

def main():
    with zipfile.ZipFile(DEST, "w", zipfile.ZIP_DEFLATED) as z:
        for caminho in arquivos():
            z.write(caminho, f"{SKILL}/{caminho.relative_to(ROOT)}")
    print(f"Gerado: {DEST}\n")
    with zipfile.ZipFile(DEST) as z:
        for info in z.infolist():
            print(f"{info.file_size:>7}  {info.filename}")

if __name__ == "__main__":
    main()
