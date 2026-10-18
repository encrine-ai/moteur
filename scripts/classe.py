# -*- coding: utf-8 -*-
"""La classe : lire classe.yml, le fournir au site, et garder le moteur propre.

classe.yml est la seule source de ce qui distingue cette classe d'une autre
(année, niveau, thème, milieux, calendrier, documents). Le site ne lit pas le
YAML : il charge site/classe.js, fabriqué ici ; scripts/generer-pdf.sh lit
site/classe.json. La charte que chargent toutes les pages, site/charte/charte.css,
est elle aussi fabriquée ici : le socle commun (site/charte/socle.css) suivi du
style du thème choisi (site/charte/themes/<theme>/theme.css). Ces fichiers sont
versionnés, comme les cahiers.

Usage :
  python3 scripts/classe.py generer    # écrit site/classe.json, site/classe.js
                                       # et site/charte/charte.css
  python3 scripts/classe.py verifier   # code 1 si classe.js est périmé, si le
                                       # matériel déclaré et les pages fabriquées
                                       # ne concordent pas, ou si une donnée de
                                       # classe est écrite en dur dans le moteur
                                       # (site/*.js, *.html, *.css, scripts/)

Depuis un autre script :
  from classe import charger, milieux, chemin, manifeste, cahiers
"""
import datetime
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML requis :  pip install pyyaml")

RACINE = pathlib.Path(__file__).resolve().parent.parent
SOURCE = RACINE / "classe.yml"
JSON = RACINE / "site" / "classe.json"
JS = RACINE / "site" / "classe.js"
CHARTE = RACINE / "site" / "charte"


def _iso(v):
    """Les dates YAML deviennent des chaînes ISO ; le reste ne change pas."""
    if isinstance(v, datetime.date):
        return v.isoformat()
    if isinstance(v, dict):
        return {k: _iso(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_iso(x) for x in v]
    return v


# Les cahiers que le moteur sait fabriquer : la page de chaque période (dans
# site/), le nom de son PDF (dans pdf/), et le temps laissé au rendu avant
# l'impression — l'imagier et les cartes-corpus sont lourds en photographies.
CAHIERS = {
    "entrainement": ("fiches/entrainement-periode-{n}.html", "fiches-entrainement", 10000),
    "evaluation": ("fiches/periode-{n}.html", "fiches-eleve", 10000),
    "imagier": ("imagier/periode-{n}.html", "imagier", 30000),
    "cartes-corpus": ("cartes-corpus/periode-{n}.html", "cartes-corpus", 30000),
}


def charger():
    """classe.yml, dates en ISO, les titres des documents de période complétés,
    et chaque cahier du matériel muni de sa page source et de son PDF."""
    c = _iso(yaml.safe_load(SOURCE.read_text(encoding="utf-8")))
    for doc in c["documents"]:
        n = doc.get("fiches")
        if n:
            p = c["periodes"][n - 1]
            doc.setdefault("titre", "Période %d · %s" % (n, p["milieu"]))
            doc.setdefault("icone", p["icone"])
    c["materiel"] = c.get("materiel") or []
    for m in c["materiel"]:
        if m.get("cle") in CAHIERS:
            source, nom, budget = CAHIERS[m["cle"]]
            m["periodes"] = m.get("periodes") or []
            m.update(source=source, pdf="pdf/%s-periode-{n}.pdf" % nom, nom=nom, budget=budget)
    return c


def cahiers(c=None, cle=None):
    """Les cahiers déclarés, période par période : [(matériel, n, source, pdf)],
    chemins relatifs au site ; `cle` n'en garde qu'une sorte."""
    c = c or charger()
    return [(m, n, m["source"].replace("{n}", str(n)), m["pdf"].replace("{n}", str(n)))
            for m in c["materiel"] if "source" in m and cle in (None, m["cle"])
            for n in m["periodes"]]


def milieux():
    """Les milieux au format des générateurs : (n, clé, emoji, milieu, phrase de l'imagier)."""
    return [(i + 1, p["cle"], p["emoji"], p["milieu"], p["imagier"])
            for i, p in enumerate(charger()["periodes"])]


def chemin(cle, c=None):
    """Le fichier de contenu `cle` de la classe (section `contenu` de classe.yml)."""
    c = c or charger()
    return RACINE / c["contenu"][cle]


def manifeste(cle):
    """Exécute le manifeste Python `cle` (imagier, corpus) et rend son espace de noms."""
    f = chemin(cle)
    ns = {}
    exec(compile(f.read_text(encoding="utf-8"), str(f.relative_to(RACINE)), "exec"), ns)
    return ns


def en_tete(c=None):
    """« Ma Grande Section 2026-2027 — « À la découverte… » », pour les pieds de page."""
    c = c or charger()
    return "%s %s — « %s »" % (c["nom"], c["annee"], c["projet"])


def _contenus(c):
    texte = json.dumps(c, ensure_ascii=False, indent=2) + "\n"
    js = ("/* Fabriqué par scripts/classe.py depuis classe.yml : ne pas modifier à la main. */\n"
          "var CLASSE = " + texte.rstrip("\n") + ";\n")
    return texte, js


def _charte(c):
    """charte.css : le socle, puis le thème, ses url() réécrites depuis site/charte/.
    Un seul fichier plutôt qu'un @import : chaque page ne fait qu'une requête,
    et l'impression des PDF ne dépend pas d'une feuille chargée en cascade."""
    dossier = CHARTE / "themes" / c["theme"]
    theme = (dossier / "theme.css").read_text(encoding="utf-8")
    prefixe = "themes/%s/" % c["theme"]
    theme = re.sub(r'url\("(?![a-z]+:|/)([^"]+)"\)',
                   lambda m: 'url("%s%s")' % (prefixe, m.group(1)), theme)
    return ("/* Fabriqué par scripts/classe.py : socle.css, puis le thème « %s » "
            "(themes/%s/theme.css).\n   Ne pas modifier à la main : éditer ces deux fichiers, "
            "puis relancer  python3 scripts/classe.py generer */\n\n"
            % (c["theme"], c["theme"])
            + (CHARTE / "socle.css").read_text(encoding="utf-8") + "\n" + theme)


def generer():
    c = charger()
    texte, js = _contenus(c)
    JSON.write_text(texte, encoding="utf-8")
    JS.write_text(js, encoding="utf-8")
    (CHARTE / "charte.css").write_text(_charte(c), encoding="utf-8")
    print("site/classe.json, site/classe.js et site/charte/charte.css écrits depuis classe.yml")


# Ce que le moteur n'a pas le droit d'écrire en dur : chaque valeur de classe.yml
# qui identifie la classe. Les fichiers fabriqués (cahiers HTML, manifestes de
# contenu) n'en font pas partie : ils sont le contenu.
MOTEUR = ["site/*.js", "site/*.html", "site/*.css", "site/*/*.css", "scripts/generer-*.py", "scripts/generer-pdf.sh",
          "scripts/*-imagier.py"]
EXCLUS = {"site/classe.js", "site/marked.min.js", "site/charte/charte.css"}  # fabriqués ou tiers
# Ce que les pages de l'application ne comptent pas à la place de la classe :
# « 18 animaux », « 36 espèces » — le nombre vit dans classe.yml (`desc` du
# matériel). Les scripts, eux, peuvent porter les conventions de la classe.
NOMBRES = re.compile(r"\b\d+\s+(animaux|plantes|espèces)\b", re.I)
# L'adresse publiée d'une classe (« propriétaire.github.io/dépôt »).
ADRESSE = re.compile(r"[\w-]+\.github\.io/[\w-]+")


def _interdits(c):
    valeurs = {c["annee"], c["projet"], c["nom"], c["niveau"]["libelle"]}
    valeurs |= {p["milieu"] for p in c["periodes"]}
    # les années civiles de l'année scolaire (2026, 2027)
    valeurs |= set(re.findall(r"\d{4}", c["annee"]))
    # le dossier du thème : une page ne le nomme pas, elle charge charte.css
    valeurs.add("themes/" + c["theme"])
    # ce que rassemble chaque cahier (l'intitulé de l'imagier, par exemple)
    valeurs |= {m["intitule"] for m in c.get("materiel", []) if m.get("intitule")}
    return sorted(valeurs, key=len, reverse=True)


def verifier():
    anomalies = []
    c = charger()
    texte, js = _contenus(c)
    for chemin, attendu in ((JSON, texte), (JS, js)):
        if not chemin.exists() or chemin.read_text(encoding="utf-8") != attendu:
            anomalies.append("%s périmé : relancer  python3 scripts/classe.py generer"
                             % chemin.relative_to(RACINE))
    if not (CHARTE / "themes" / c.get("theme", "") / "theme.css").is_file():
        anomalies.append("theme : site/charte/themes/%s/theme.css n'existe pas" % c.get("theme"))
    elif (not (CHARTE / "charte.css").exists()
          or (CHARTE / "charte.css").read_text(encoding="utf-8") != _charte(c)):
        anomalies.append("site/charte/charte.css périmé : relancer  python3 scripts/classe.py generer")
    if c.get("ton", "tu") not in ("tu", "vous"):
        anomalies.append("ton : « %s » — `tu` ou `vous`" % c.get("ton"))
    moteur = c.get("moteur")
    if not isinstance(moteur, dict) or "depot" not in moteur or "version" not in moteur:
        anomalies.append("moteur : il faut `depot` et `version` (skill synchroniser-moteur)")
    galerie = c.get("galerie")
    if not isinstance(galerie, dict) or "depot" not in galerie:
        anomalies.append("galerie : il faut `depot` (skill partager-ma-classe)")
    partage = c.get("partage") or {}
    if not all(isinstance(p, str) for p in partage.get("prenoms_fictifs") or []):
        anomalies.append("partage.prenoms_fictifs : une liste de prénoms")
    for t in partage.get("textes_autorises") or []:
        if not (isinstance(t, dict) and t.get("debut") and t.get("raison")):
            anomalies.append("partage.textes_autorises : chaque passage a `debut` et `raison`")
    for cle, rel in c.get("contenu", {}).items():
        if not (RACINE / rel).exists():
            anomalies.append("contenu.%s : %s n'existe pas" % (cle, rel))
    # Le matériel : l'accueil annonce ce qui est déclaré, l'impression fabrique
    # ce qui est déclaré ; une page déclarée doit donc exister, et une page
    # fabriquée être déclarée.
    nb = len(c["periodes"])
    for m in c["materiel"]:
        if m.get("cle") not in CAHIERS:
            anomalies.append("materiel : « %s » n'est pas un cahier connu (%s)"
                             % (m.get("cle"), ", ".join(CAHIERS)))
            continue
        for n in m["periodes"]:
            if not (isinstance(n, int) and 1 <= n <= nb):
                anomalies.append("materiel.%s : période %r hors de 1…%d" % (m["cle"], n, nb))
    declares = {s for _, _, s, _ in cahiers(c)}
    for s in sorted(declares):
        if not (RACINE / "site" / s).is_file():
            anomalies.append("materiel : site/%s est déclaré mais n'existe pas — "
                             "le fabriquer, ou retirer la période de classe.yml" % s)
    for source, _, _ in CAHIERS.values():
        for n in range(1, nb + 1):
            s = source.replace("{n}", str(n))
            if (RACINE / "site" / s).is_file() and s not in declares:
                anomalies.append("materiel : site/%s existe mais n'est pas déclaré — "
                                 "l'ajouter aux périodes de son cahier dans classe.yml" % s)
    interdits = _interdits(c)
    fichiers = {f for motif in MOTEUR for f in RACINE.glob(motif)}
    for f in sorted(fichiers):
        rel = str(f.relative_to(RACINE))
        if rel in EXCLUS:
            continue
        for i, ligne in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            site = ADRESSE.search(ligne)
            if site:
                anomalies.append("%s:%d écrit l'adresse « %s » en dur — "
                                 "le moteur ne nomme pas le site d'une classe" % (rel, i, site.group(0)))
                continue
            nombre = NOMBRES.search(ligne) if rel.startswith("site/") else None
            if nombre:
                anomalies.append("%s:%d compte « %s » en dur — à lire dans classe.yml"
                                 % (rel, i, nombre.group(0)))
                continue
            for v in interdits:
                if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(v), ligne, re.I):
                    anomalies.append("%s:%d écrit « %s » en dur — à lire dans classe.yml"
                                     % (rel, i, v))
                    break
    for a in anomalies:
        print("✘ " + a)
    print("classe.yml : %d anomalie(s)" % len(anomalies))
    return 1 if anomalies else 0


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "verifier"
    if action == "generer":
        generer()
    elif action == "verifier":
        sys.exit(verifier())
    else:
        sys.exit(__doc__)
