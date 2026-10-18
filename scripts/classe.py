# -*- coding: utf-8 -*-
"""La classe : lire classe.yml, le fournir au site, et garder le moteur propre.

classe.yml est la seule source de ce qui distingue cette classe d'une autre
(année, niveau, thème, milieux, zone de vacances, documents). Les dates des
vacances, elles, sont nationales : referentiel/calendrier-<année>.yml les porte
pour les trois zones, et `generer` n'y prend que celles de la zone de la classe. Le site ne lit pas le
YAML : il charge site/classe.js, fabriqué ici ; scripts/generer-pdf.sh lit
site/classe.json. La charte que chargent toutes les pages, site/charte/charte.css,
est elle aussi fabriquée ici : le socle commun (site/charte/socle.css), les
composants communs du moteur (site/charte/composants.css), puis le thème choisi
(site/charte/themes/<theme>/theme.css et, s'il en a un, son habillage.css).
Ces fichiers sont versionnés, comme les cahiers.

Usage :
  python3 scripts/classe.py generer    # écrit site/classe.json, site/classe.js
                                       # et site/charte/charte.css
  python3 scripts/classe.py verifier   # code 1 si classe.js est périmé, si le
                                       # matériel déclaré et les pages fabriquées
                                       # ne concordent pas, ou si une donnée de
                                       # classe est écrite en dur dans le moteur
                                       # (site/*.js, *.html, *.css, scripts/),
                                       # ou si le thème enfreint son contrat
                                       # (scripts/verifier-theme.py), ou si
                                       # `depot` ou `origine` sont mal formés

L'identité de la classe : `depot` (« propriétaire/dépôt », le dépôt GitHub de
cette classe) et, si elle est partie d'une autre classe par « Use this
template », `origine` (depot, titre, auteur, licence, site, reprise_le).
classe.json transmet l'une et l'autre : le pied du site crédite l'original
(skill nouvelle-classe, « Partir d'une classe »).

Depuis un autre script :
  from classe import charger, milieux, chemin, manifeste, cahiers, couverture
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
ZONES = ("A", "B", "C")
# Ce que classe.yml peut dire du calendrier : sa zone, et les ponts propres à
# l'école, qui s'ajoutent aux ponts nationaux. Tout le reste vient du moteur.
CLES_CALENDRIER = {"zone", "ponts"}


def fichier_calendrier(annee):
    """Le calendrier officiel de l'année scolaire, dans le moteur."""
    return RACINE / "referentiel" / ("calendrier-%s.yml" % annee)


def calendrier(c):
    """Les dates de la classe : celles de sa zone, tirées du calendrier
    national de son année, plus ses ponts propres. None si l'année n'a pas de
    fichier ou si la zone n'est pas A, B ou C (`verifier` le dit)."""
    propre = c.get("calendrier") or {}
    zone = propre.get("zone")
    f = fichier_calendrier(c.get("annee"))
    if zone not in ZONES or not f.is_file():
        return None
    nat = _iso(yaml.safe_load(f.read_text(encoding="utf-8")))
    return {
        "zone": zone,
        "rentree": nat["rentree"],
        "fin": nat["fin"],
        "toussaint": nat["toussaint"],
        "noel": nat["noel"],
        "hiver": nat["hiver"][zone],
        "printemps": nat["printemps"][zone],
        "ponts": (nat.get("ponts") or []) + (propre.get("ponts") or []),
    }


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
    c["calendrier"] = calendrier(c) or c.get("calendrier")
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
            # la couverture du cahier : l'imagier et les cartes-corpus en ont
            # une, sauf `couverture: false` (une page de plus par cahier)
            if m["cle"] in COUVERTURES:
                m.setdefault("couverture", True)
    return c


# Les cahiers qui s'ouvrent sur une couverture (ceux qu'on range et qu'on
# reprend : les fiches élève, photocopiées une à une, n'en ont pas).
COUVERTURES = ("imagier", "cartes-corpus")


def couverture(c, n, cahier, sous_titre=""):
    """La couverture d'un cahier de la période n : une `section.planche`, la
    première page du PDF. La structure est fixe et documentée (skill
    charte-graphique, « Les composants ») : le thème l'habille par ses
    classes et remplit ses ornements, il ne la réécrit pas."""
    p = c["periodes"][n - 1]
    def e(t):
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    orne = '<span class="orne" data-orne="%s" aria-hidden="true"></span>'
    return (
        '<section class="planche couverture" data-composant="couverture" data-periode="%d" data-cle="%s">\n'
        '  %s\n'
        '  <div class="couverture-tete"><span class="couverture-classe">%s</span>'
        '<span class="couverture-annee">%s · %s</span></div>\n'
        '  <div class="couverture-centre">\n'
        '    %s\n'
        '    <p class="couverture-cahier">%s</p>\n'
        '    <h1 class="couverture-titre">%s</h1>\n'
        '    %s\n'
        '  </div>\n'
        '  <div class="couverture-pied"><span class="couverture-periode">'
        '<span class="couverture-num">%d</span>Période %d</span>'
        '<span class="couverture-projet">« %s »</span></div>\n'
        '  %s\n'
        '</section>' % (
            n, e(p["cle"]), orne % "couverture-fond",
            e(c["nom"]), e(c["niveau"]["libelle"]), e(c["annee"]),
            orne % "couverture-embleme", e(cahier), e(p["milieu"]),
            '<p class="couverture-sous">%s</p>' % e(sous_titre) if sous_titre else "",
            n, n, e(c["projet"]), orne % "couverture-tampon"))


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


# Les feuilles d'un thème, dans l'ordre : ses jetons, puis l'habillage de ses
# composants (facultatif). skill charte-graphique, « Le contrat du thème ».
FEUILLES_THEME = ("theme.css", "habillage.css")


def _charte(c):
    """charte.css : le socle, les composants communs du moteur, puis les
    feuilles du thème, leurs url() réécrites depuis site/charte/.
    Un seul fichier plutôt qu'un @import : chaque page ne fait qu'une requête,
    et l'impression des PDF ne dépend pas d'une feuille chargée en cascade."""
    dossier = CHARTE / "themes" / c["theme"]
    prefixe = "themes/%s/" % c["theme"]
    feuilles = [f for f in FEUILLES_THEME if (dossier / f).is_file()]
    theme = ""
    for f in feuilles:
        css = (dossier / f).read_text(encoding="utf-8")
        css = re.sub(r'url\("(?![a-z]+:|/)([^"]+)"\)',
                     lambda m: 'url("%s%s")' % (prefixe, m.group(1)), css)
        theme += "\n/* ——— themes/%s/%s ——— */\n" % (c["theme"], f) + css
    return ("/* Fabriqué par scripts/classe.py : socle.css, composants.css, puis le thème « %s » "
            "(themes/%s/ : %s).\n   Ne pas modifier à la main : éditer ces fichiers, "
            "puis relancer  python3 scripts/classe.py generer */\n\n"
            % (c["theme"], c["theme"], ", ".join(feuilles))
            + (CHARTE / "socle.css").read_text(encoding="utf-8") + "\n"
            + (CHARTE / "composants.css").read_text(encoding="utf-8") + theme)


def generer():
    c = charger()
    if calendrier(_iso(yaml.safe_load(SOURCE.read_text(encoding="utf-8")))) is None:
        sys.exit("✘ calendrier : il faut `calendrier: {zone: A|B|C}` dans classe.yml, et "
                 "referentiel/calendrier-%s.yml dans le moteur — python3 scripts/classe.py verifier"
                 % c.get("annee"))
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
# Les restes du temps où chaque classe portait les trois zones : un sélecteur
# mémorisé, des PDF rangés par zone, la liste des zones lue dans classe.json.
ANCIEN = re.compile(r"zone-vacances|pdf/zone-|zone-\$|\['zones'\]|calendrier\.zones")


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


def _verifier_calendrier(anomalies):
    """La zone, le fichier de l'année, et plus aucune date dans classe.yml."""
    brut = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    propre = brut.get("calendrier")
    if not isinstance(propre, dict):
        anomalies.append("calendrier : il faut `calendrier: {zone: A|B|C}` (skill site-et-calendrier)")
        return
    if propre.get("zone") not in ZONES:
        anomalies.append("calendrier.zone : « %s » — la zone de vacances de la classe, A, B ou C"
                         % propre.get("zone"))
    for cle in sorted(set(propre) - CLES_CALENDRIER):
        anomalies.append("calendrier.%s : ancienne clé — les dates des trois zones viennent de "
                         "referentiel/calendrier-<année>.yml ; classe.yml ne garde que `zone` "
                         "(et ses ponts propres, `ponts`)" % cle)
    for p in propre.get("ponts") or []:
        if not (isinstance(p, dict) and p.get("nom") and p.get("du") and p.get("au")):
            anomalies.append("calendrier.ponts : chaque pont a `nom`, `du` et `au`")
    f = fichier_calendrier(brut.get("annee"))
    if not f.is_file():
        anomalies.append("annee %s : %s n'existe pas — le calendrier officiel de l'année entre "
                         "dans le moteur (skill site-et-calendrier)"
                         % (brut.get("annee"), f.relative_to(RACINE)))
        return
    nat = yaml.safe_load(f.read_text(encoding="utf-8"))
    if str(nat.get("annee")) != str(brut.get("annee")):
        anomalies.append("%s : annee « %s » au lieu de « %s »"
                         % (f.relative_to(RACINE), nat.get("annee"), brut.get("annee")))
    for cle in ("rentree", "fin"):
        if not isinstance(nat.get(cle), datetime.date):
            anomalies.append("%s : `%s` doit être une date" % (f.relative_to(RACINE), cle))
    vacances = [(cle, nat.get(cle)) for cle in ("toussaint", "noel")]
    vacances += [("%s.%s" % (cle, z), (nat.get(cle) or {}).get(z))
                 for cle in ("hiver", "printemps") for z in ZONES]
    for nom, v in vacances:
        if not (isinstance(v, dict) and all(isinstance(v.get(k), datetime.date)
                                             for k in ("debut", "reprise"))):
            anomalies.append("%s : `%s` doit avoir `debut` et `reprise`" % (f.relative_to(RACINE), nom))


# « propriétaire/dépôt », comme GitHub les écrit.
DEPOT = re.compile(r"^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$")
# Ce que `origine` peut dire de la classe d'où celle-ci est partie.
CLES_ORIGINE = {"depot", "titre", "auteur", "licence", "site", "reprise_le"}
NON_DEFINI = (None, "", "à définir")


def _verifier_identite(anomalies, avertissements):
    """`depot` (le dépôt de cette classe) et `origine` (la classe d'où elle
    est partie). Une classe d'avant ces clés n'a pas de `depot` : on prévient
    seulement ; une valeur écrite, elle, doit être bien formée."""
    brut = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    depot = brut.get("depot")
    if depot in NON_DEFINI:
        avertissements.append("depot : non renseigné — le dépôt de cette classe, "
                              "« propriétaire/dépôt » (skill nouvelle-classe)")
    elif not (isinstance(depot, str) and DEPOT.match(depot)):
        anomalies.append("depot : « %s » — il faut « propriétaire/dépôt »" % depot)
    if "origine" not in brut:
        return
    o = brut["origine"]
    if not isinstance(o, dict):
        anomalies.append("origine : il faut un bloc (depot, titre, auteur, licence, site, reprise_le)")
        return
    for cle in sorted(set(o) - CLES_ORIGINE):
        anomalies.append("origine.%s : clé inconnue (%s)" % (cle, ", ".join(sorted(CLES_ORIGINE))))
    for cle in ("titre", "licence"):
        if not (isinstance(o.get(cle), str) and o[cle].strip()):
            anomalies.append("origine.%s : manquant — CC BY et CC BY-SA obligent à "
                             "créditer l'original (titre, auteur, licence)" % cle)
    if not o.get("auteur"):
        avertissements.append("origine.auteur : non renseigné — le crédit de l'original le nomme")
    od = o.get("depot")
    if od is not None and not (isinstance(od, str) and DEPOT.match(od)):
        anomalies.append("origine.depot : « %s » — il faut « propriétaire/dépôt »" % od)
    elif od and od == depot:
        anomalies.append("origine.depot : c'est le dépôt de cette classe — `depot` doit "
                         "passer au nouveau dépôt (skill nouvelle-classe)")
    site = o.get("site")
    if site is not None and not (isinstance(site, str) and site.startswith("https://")):
        anomalies.append("origine.site : « %s » — une adresse en https://" % site)
    if "reprise_le" in o and not isinstance(o["reprise_le"], datetime.date):
        anomalies.append("origine.reprise_le : « %s » — une date AAAA-MM-JJ" % o["reprise_le"])


def verifier():
    anomalies = []
    avertissements = []
    _verifier_calendrier(anomalies)
    _verifier_identite(anomalies, avertissements)
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
            ancien = ANCIEN.search(ligne)
            if ancien:
                anomalies.append("%s:%d garde « %s » — une classe n'a plus qu'une zone, "
                                 "celle de classe.yml (GS.CAL.zone)" % (rel, i, ancien.group(0)))
                continue
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
    # Le thème : son contrat (polices de l'élève, contrastes, papier, fichiers
    # déclarés), contrôlé par scripts/verifier-theme.py.
    if (CHARTE / "themes" / c.get("theme", "") / "theme.css").is_file():
        sys.path.insert(0, str(RACINE / "scripts"))
        import importlib
        vt = importlib.import_module("verifier-theme")
        anomalies += ["thème « %s » : %s" % (c["theme"], a) for a in vt.anomalies(c["theme"])]
    for a in avertissements:
        print("⚠ " + a)
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
