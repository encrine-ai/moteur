#!/usr/bin/env python3
"""Fabrique site/charte/icones.svg, le sprite des icônes de l'application.

Les icônes de l'interface (menu, boutons, milieux) viennent de Lucide
(licence ISC, usage commercial et modification permis), au trait de 2 px,
couleur héritée du texte. Elles ne vont jamais sur une fiche élève : celles-ci
portent des pictogrammes Mulberry ou ARASAAC (skill fiches-illustrations).

Les icônes génériques (navigation, matériel) sont du socle et listées ici ;
celles des milieux viennent de la classe (`periodes[].icone` dans classe.yml),
si bien qu'un autre thème apporte les siennes sans toucher à ce script.

Ajouter une icône : l'inscrire dans ICONES (ou dans classe.yml pour un milieu),
relancer le script, l'appeler par
<svg class="ic"><use href="charte/icones.svg#i-NOM"/></svg>.
"""
import pathlib
import re
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import classe  # noqa: E402

VERSION = "0.468.0"
ICONES = [
    # navigation et documents
    "house", "calendar-range", "target", "message-circle", "shapes",
    "person-standing", "palette", "compass", "sprout", "heart-handshake",
    "clipboard-list", "file-text", "map-pin", "menu", "x", "star",
    # matériel à imprimer
    "download", "printer", "image", "layers", "pencil",
]
# les milieux de la classe, dans l'ordre des périodes
ICONES += [p["icone"] for p in classe.charger()["periodes"] if p["icone"] not in ICONES]
SORTIE = pathlib.Path(__file__).resolve().parent.parent / "site/charte/icones.svg"


def symbole(nom):
    url = f"https://cdn.jsdelivr.net/npm/lucide-static@{VERSION}/icons/{nom}.svg"
    svg = urllib.request.urlopen(url, timeout=30).read().decode()
    corps = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    corps = re.sub(r"\s+", " ", corps).strip()
    return f'<symbol id="i-{nom}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{corps}</symbol>'


def main():
    symboles = "\n".join(symbole(n) for n in ICONES)
    SORTIE.write_text(
        f"<!-- Icônes Lucide v{VERSION} (ISC) — fabriqué par scripts/generer-icones.py -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\n'
        f"{symboles}\n</svg>\n",
        encoding="utf-8",
    )
    print(f"{len(ICONES)} icônes → {SORTIE}")


if __name__ == "__main__":
    main()
