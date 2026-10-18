#!/usr/bin/env python3
"""Contrôle que chaque cahier imprimé a exactement une page par fiche ou par planche.

Le HTML ne dit rien de la pagination : un navigateur s'allonge, une feuille A4
non. Les deux pires défauts de ce matériel — des étiquettes qui s'imprimaient
par-dessus les crédits, le pied de la garde seul sur une page — n'existaient
pas à l'écran. Ce script compte les sections de chaque cahier HTML et les pages
du PDF fabriqué, et refuse tout écart.

Usage :
    bash scripts/generer-pdf.sh /tmp/site      # le site assemblé, PDF compris
    python3 scripts/verifier-pagination.py /tmp/site
Code de sortie 1 s'il reste un cahier dont une section déborde (ou est vide).
"""
import json
import pathlib
import re
import subprocess
import sys

# la balise qui fait une page, selon le cahier
BALISE = {"entrainement": "fiche", "evaluation": "fiche", "imagier": "planche", "cartes-corpus": "planche"}


def cahiers(site):
    """cahier HTML (relatif au site) → PDF fabriqué par generer-pdf.sh, et la
    balise qui fait une page : le matériel que déclare classe.json."""
    c = json.loads((site / "classe.json").read_text(encoding="utf-8"))
    if "materiel" not in c:
        sys.exit("✘ classe.json ne déclare pas le matériel : relancer  python3 scripts/classe.py generer")
    return [(m["source"].replace("{n}", str(n)), m["pdf"].replace("{n}", str(n)), BALISE[m["cle"]])
            for m in c.get("materiel", []) if m.get("cle") in BALISE for n in m["periodes"]]


def pages(pdf):
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf)).pages)
    except ImportError:
        sortie = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
        return int(re.search(r"^Pages:\s+(\d+)", sortie, re.M).group(1))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    site = pathlib.Path(sys.argv[1])
    anomalies = 0
    CAHIERS = cahiers(site)
    for html, pdf, classe in CAHIERS:
        source, fabrique = site / html, site / pdf
        if not fabrique.exists():
            print(f"✘ {pdf} : absent (lancer d'abord scripts/generer-pdf.sh)")
            anomalies += 1
            continue
        attendu = len(re.findall(rf'<section class="{classe}\b', source.read_text(encoding="utf-8")))
        obtenu = pages(fabrique)
        if obtenu == attendu:
            print(f"✔ {pdf} : {obtenu} pages")
        else:
            print(f"✘ {pdf} : {obtenu} pages pour {attendu} {classe}s — une section déborde sur la page suivante")
            anomalies += 1
    print(f"{len(CAHIERS)} cahiers contrôlés, {anomalies} anomalie(s)")
    sys.exit(1 if anomalies else 0)


if __name__ == "__main__":
    main()
