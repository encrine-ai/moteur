#!/usr/bin/env python3
"""Contrôle que chaque cahier imprimé a exactement une page par fiche ou par planche,
et que chaque document a son PDF, aux dates de la zone de la classe.

Le HTML ne dit rien de la pagination : un navigateur s'allonge, une feuille A4
non. Les deux pires défauts de ce matériel — des étiquettes qui s'imprimaient
par-dessus les crédits, le pied de la garde seul sur une page — n'existaient
pas à l'écran. Ce script compte les sections de chaque cahier HTML et les pages
du PDF fabriqué, et refuse tout écart.

Il contrôle aussi la mention de la marque, « Conçu avec Encrine · encrine.ai »,
au pied de CHAQUE page de chaque PDF (documents et cahiers), par extraction
du texte (pdftotext, ou pypdf) : elle est dans la marge basse (charte/socle.css,
impression.css), et une police qui n'a pas chargé à temps l'efface sans bruit.

Usage :
    bash scripts/generer-pdf.sh /tmp/site      # le site assemblé, PDF compris
    python3 scripts/verifier-pagination.py /tmp/site
Code de sortie 1 s'il reste un cahier dont une section déborde (ou est vide), un
document sans PDF, une page sans la mention de la marque, ou un dossier pdf/zone-X/ d'avant (une classe n'a qu'une zone :
les PDF sont à plat dans pdf/).
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


def documents(site):
    """Les PDF des documents : pdf/<doc>.pdf, et pdf/<doc>-periode-N.pdf pour
    les progressions — ce que fabrique generer-pdf.sh, ce que lie app.js."""
    c = json.loads((site / "classe.json").read_text(encoding="utf-8"))
    nb = len(c["periodes"])
    pdfs = ["pdf/%s.pdf" % d["id"] for d in c["documents"] if d.get("md")]
    pdfs += ["pdf/%s-periode-%d.pdf" % (d["id"], n) for d in c["documents"]
             if d.get("par_periode") for n in range(1, nb + 1)]
    return c["calendrier"].get("zone"), pdfs


# La mention de la marque, au pied de chaque page imprimée
MENTION = "Conçu avec Encrine · encrine.ai"


def textes(pdf):
    """Le texte de chaque page du PDF, dans l'ordre."""
    try:
        sortie = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                                capture_output=True, text=True, check=True).stdout
        return sortie.split("\f")[:pages(pdf)]
    except (FileNotFoundError, subprocess.CalledProcessError):
        from pypdf import PdfReader
        return [p.extract_text() or "" for p in PdfReader(str(pdf)).pages]


def sans_mention(pdf):
    """Les numéros des pages (à partir de 1) où la mention manque."""
    return [i + 1 for i, t in enumerate(textes(pdf)) if MENTION not in " ".join(t.split())]


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
    total = 0
    controlees = 0

    def mention(pdf):
        nonlocal anomalies, controlees
        manque, n = sans_mention(site / pdf), pages(site / pdf)
        controlees += n
        if manque:
            ou = ("sur ses %d pages" % n if len(manque) == n
                  else "page(s) " + ", ".join(map(str, manque[:12])) + (" …" if len(manque) > 12 else ""))
            print(f"✘ {pdf} : la mention « {MENTION} » manque {ou}")
            anomalies += 1

    zone, DOCUMENTS = documents(site)
    for pdf in DOCUMENTS:
        if not (site / pdf).exists():
            print(f"✘ {pdf} : absent (lancer d'abord scripts/generer-pdf.sh)")
            anomalies += 1
        else:
            total += pages(site / pdf)
            mention(pdf)
    for vieux in sorted((site / "pdf").glob("zone-*")):
        print(f"✘ pdf/{vieux.name}/ : une classe n'a plus qu'une zone, les PDF sont à plat dans pdf/")
        anomalies += 1
    print(f"{len(DOCUMENTS)} documents (zone {zone}), {total} pages")
    CAHIERS = cahiers(site)
    for html, pdf, classe in CAHIERS:
        source, fabrique = site / html, site / pdf
        if not fabrique.exists():
            print(f"✘ {pdf} : absent (lancer d'abord scripts/generer-pdf.sh)")
            anomalies += 1
            continue
        attendu = len(re.findall(rf'<section class="{classe}\b', source.read_text(encoding="utf-8")))
        obtenu = pages(fabrique)
        total += obtenu
        mention(pdf)
        if obtenu == attendu:
            print(f"✔ {pdf} : {obtenu} pages")
        else:
            print(f"✘ {pdf} : {obtenu} pages pour {attendu} {classe}s — une section déborde sur la page suivante")
            anomalies += 1
    print(f"mention « {MENTION} » cherchée au pied de {controlees} pages")
    print(f"{len(CAHIERS)} cahiers contrôlés, {anomalies} anomalie(s)")
    print(f"{len(DOCUMENTS) + len(CAHIERS)} PDF, {total} pages en tout")
    sys.exit(1 if anomalies else 0)


if __name__ == "__main__":
    main()
