#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrôle le thème d'une classe : il habille, il ne restructure pas.

Le thème (site/charte/themes/<thème>/) donne son visage à la classe : ses
couleurs et ses polices (theme.css), l'habillage de ses composants
(habillage.css, facultatif), ses motifs et ses polices auto-hébergées,
déclarés dans theme.yml. Le moteur, lui, garantit ce que toutes les classes
partagent : la police de l'élève, la lisibilité, le papier. Ce script vérifie
que le thème s'en tient à son contrat — le skill charte-graphique le décrit
(« Le contrat du thème ») :

1. **les fichiers** : theme.yml déclare chaque police et chaque motif, avec
   une licence libre (OFL, CC0, CC BY, CC BY-SA, domaine public) ; chaque
   fichier déclaré existe, chaque fichier du dossier est déclaré, chaque url()
   des feuilles pointe sur un fichier déclaré, aucune ne sort sur le réseau
   (les PDF se fabriquent sans lui) ; un motif SVG ne contient ni script, ni
   image, ni texte ;
2. **les jetons** : tous ceux du thème sont définis dans les trois blocs
   (clair, sombre, impression) ; les polices de l'adulte sont auto-hébergées ;
3. **le contraste** : chaque texte tient 4,5:1 sur le fond que nomme son
   usage, 3:1 pour un bord de contrôle, dans les trois blocs — le bloc
   d'impression est celui de la photocopie en noir et blanc, où le rapport de
   luminance est tout ce qui reste ;
4. **le socle** : le thème ne redéfinit ni --police-enfant, ni les
   espacements, ni la mécanique des périodes ; il ne touche ni à la police, ni
   au corps, ni à l'espacement des mots que l'enfant lit ; il n'écrit ni
   @page, ni saut de page, ni !important ;
5. **les composants** : chaque règle part d'un composant nommé par le moteur
   (data-composant, data-orne, ou l'une des classes racines documentées) et
   ne nomme que ses parties ; sur le papier, elle ne change que l'apparence
   (couleurs, bordures, polices de l'adulte), jamais la géométrie, et un
   ornement y est toujours en position absolue — la pagination ne bouge pas ;
   un aplat sombre n'y est permis que sur la couverture, dont l'intérieur
   (à hauteur fixe) se compose librement ;
6. **le mini-site** : les images du thème (theme.yml, `images:`) ont une
   licence libre (CC0, domaine public, CC BY, CC BY-SA), un auteur, une
   source, et leur fichier ; les gabarits (gabarits.js), s'il y en a, se
   chargent, rendent chaque page de la vraie classe et posent les accroches
   du menu (scripts/verifier-gabarits.js, avec Node), sans réécrire la
   logique du moteur (ni fetch, ni stockage, ni route) ; l'habillage de leur
   HTML vit dans `@media screen` (il ne touche jamais le papier) ; tout
   mouvement est sous `prefers-reduced-motion: no-preference`.

Usage :
    python3 scripts/verifier-theme.py              # le thème de classe.yml
    python3 scripts/verifier-theme.py <thème> …    # un ou plusieurs thèmes
Code 1 s'il reste une anomalie. `classe.py verifier` le lance aussi.
"""
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML requis :  pip install pyyaml")

RACINE = pathlib.Path(__file__).resolve().parent.parent
THEMES = RACINE / "site" / "charte" / "themes"

LICENCES = {"OFL-1.1", "CC0-1.0", "PDM", "CC-BY-4.0", "CC-BY-SA-4.0", "CC-BY-3.0", "CC-BY-SA-3.0"}
# Les images (thème, projet de la classe) : libres et modifiables — une
# carte recadre, un écran retouche. Jamais NC ni ND.
LICENCES_IMAGES = {"CC0-1.0", "PDM", "CC-BY-4.0", "CC-BY-SA-4.0", "CC-BY-3.0", "CC-BY-SA-3.0",
                   "CC-BY-2.0", "CC-BY-SA-2.0"}
FEUILLES = ("theme.css", "habillage.css")
HORS_DECLARATION = {"theme.yml", "theme.css", "habillage.css", "gabarits.js", "LISEZ-MOI.md"}
# Ce qu'un gabarit ne fait pas : la logique (lire, stocker, router) est au moteur.
GABARIT_INTERDIT = [
    (r"\bfetch\s*\(|XMLHttpRequest|\bimport\s*\(|\beval\s*\(|new\s+Function\b", "lit ou exécute du code ou des données (fetch, import, eval)"),
    (r"localStorage|sessionStorage|indexedDB|document\.cookie", "garde des données (stockage) — c'est au moteur"),
    (r"location\.(hash|href|search)\s*=|location\.(assign|replace)\s*\(|history\.(push|replace)State", "change la route — c'est au moteur"),
    (r"addEventListener\s*\(\s*['\"](hashchange|popstate|keydown)['\"]", "écoute la route ou le clavier — le menu et Échap sont au moteur"),
    (r"document\.write", "écrit dans le document (document.write)"),
    (r"https?://(?!encrine\.ai)", "charge ou nomme une adresse extérieure — tout est auto-hébergé"),
]
MOUVEMENT_JS = re.compile(r"requestAnimationFrame|setInterval|\.animate\s*\(")

# ——— Les jetons ———————————————————————————————————————————————————————————
PERIODES = ["--p%d%s" % (n, s) for n in range(1, 6) for s in ("", "-trait", "-pale")]
COULEURS = ["--papier", "--feuille", "--feuille-creuse", "--trait", "--trait-fort",
            "--encre", "--encre-douce", "--sapin", "--sapin-pale", "--sur-sapin",
            "--bouton-dor", "--sur-bouton-dor", "--coquelicot", "--anneau",
            *PERIODES, "--sur-periode"]
# un thème les définit tous, dans chaque bloc où ils ont un sens
REQUIS = {
    "clair": COULEURS + ["--police-titre", "--police-texte", "--ombre-flotte",
                         "--rayon-s", "--rayon-m", "--rayon-l", "--rayon-pilule"],
    "sombre": COULEURS + ["--ombre-flotte"],
    "impression": [c for c in COULEURS if c not in ("--bouton-dor", "--sur-bouton-dor",
                                                     "--coquelicot", "--anneau")],
}
# Les jetons d'accroche : le moteur les lit avec une valeur par défaut
# (var(--x, défaut)) ; un thème peut les fournir. Skill charte-graphique.
ACCROCHES = {
    "--police-etiquette",
    "--consigne-fond", "--consigne-bord", "--consigne-encre", "--consigne-accent",
    "--sous-objectif-fond", "--sous-objectif-bord", "--sous-objectif-encre",
    "--defi-fond", "--defi-bord", "--defi-accent",
    "--fiche-cadre", "--trait-coupe", "--entete-planche-encre",
}
# ce que le socle porte, et qu'aucun thème ne redéfinit
SOCLE = re.compile(r"^--(police-enfant|esp-\d+|periode(-trait|-pale)?|repere-(taille|encre))$")
# les variables propres au thème : --t-…
PRIVEE = re.compile(r"^--t-[\w-]+$")
RAYONS = re.compile(r"^--rayon-[\w-]+$")

# ——— Les paires de contraste : (texte, fond, rapport minimal) ————————————
PAIRES = [
    ("--encre", "--papier", 4.5), ("--encre", "--feuille", 4.5), ("--encre", "--feuille-creuse", 4.5),
    ("--encre-douce", "--papier", 4.5), ("--encre-douce", "--feuille", 4.5),
    ("--encre-douce", "--feuille-creuse", 4.5),
    ("--sapin", "--papier", 4.5), ("--sapin", "--feuille", 4.5), ("--sapin", "--sapin-pale", 4.5),
    ("--sur-sapin", "--sapin", 4.5), ("--sur-bouton-dor", "--bouton-dor", 4.5),
    ("--coquelicot", "--feuille", 4.5),
    ("--trait-fort", "--feuille", 3.0), ("--trait-fort", "--papier", 3.0),
] + [x for n in range(1, 6) for x in (
    ("--p%d" % n, "--feuille", 4.5), ("--p%d" % n, "--p%d-pale" % n, 4.5),
    ("--sur-periode", "--p%d" % n, 4.5), ("--encre", "--p%d-pale" % n, 4.5))]
# les accroches qui vont par deux (seulement si le thème en fournit une)
PAIRES_ACCROCHES = [("--consigne-encre", "--consigne-fond", 4.5), ("--consigne-accent", "--consigne-fond", 4.5),
                    ("--sous-objectif-encre", "--sous-objectif-fond", 4.5), ("--defi-accent", "--defi-fond", 4.5)]
# sur le papier, un fond reste clair : l'encre va aux traits et aux mots
FONDS_PAPIER = ["--papier", "--feuille", "--feuille-creuse", "--sapin-pale",
                *["--p%d-pale" % n for n in range(1, 6)],
                "--consigne-fond", "--sous-objectif-fond", "--defi-fond"]
LUMINANCE_FOND_PAPIER = 0.70

# ——— Les composants : nom → (support, racine, parties, ornements) —————————
# La racine est l'accroche que le moteur garantit ; les parties, les classes
# que l'habillage peut nommer à l'intérieur. Tout le reste est interne au
# moteur et peut changer d'une version à l'autre.
DC = '[data-composant="%s"]'
COMPOSANTS = {
    # l'écran de l'enseignant
    "bandeau": ("ecran", DC % "bandeau", {"marque", "marque-frise", "m1", "m2", "m3", "m4", "m5",
                                         "marque-texte", "marque-titre", "marque-sous", "menu-toggle", "ic"}, {"bandeau"}),
    "menu": ("ecran", DC % "menu", {"menu-groupe", "groupe", "actif", "pastille", "ic", "ouvert"}, set()),
    "barre": ("ecran", DC % "barre", {"fil", "boutons", "btn", "btn-principal", "ic"}, set()),
    "accueil": ("ecran", DC % "accueil", {"contenu", "accueil"}, set()),
    "accueil-tete": ("ecran", DC % "accueil-tete", {"surtitre", "chapo"}, {"accueil"}),
    "bloc": ("ecran", DC % "bloc", {"bloc-tete", "zone-badge", "note", "vacances", "reprise",
                                   "materiels", "frise-total"}, set()),
    "frise": ("ecran", DC % "frise", {"frise-periode", "en-cours", "frise-bande", "frise-num", "frise-milieu",
                                     "frise-dates", "frise-sem", "frise-ici", "ic"}, {"frise"}),
    "materiel": ("ecran", DC % "materiel", {"materiel", "en-cours", "materiel-tete", "materiel-num",
                                           "materiel-liste", "ic"}, {"materiel"}),
    "documents": ("ecran", DC % "documents", {"docs-groupe", "docs", "ic"}, set()),
    "document": ("ecran", DC % "document", {"contenu", "zone-badge", "chargement"}, set()),
    "pied": ("ecran", DC % "pied", {"pied"}, set()),
    "invitation": ("ecran", DC % "invitation", {"invitation-icone", "invitation-texte", "invitation-fermer",
                                               "btn", "btn-principal", "ic"}, set()),
    "pastille": ("ecran", ".pastille", set(), set()),
    "bouton": ("ecran", ".btn", {"btn-principal", "ic"}, set()),
    # le papier de la classe
    "couverture": ("papier", DC % "couverture", {
        "planche", "couverture", "couverture-tete", "couverture-classe", "couverture-annee",
        "couverture-centre", "couverture-cahier", "couverture-titre", "couverture-sous",
        "couverture-pied", "couverture-periode", "couverture-num", "couverture-projet"},
        {"couverture-fond", "couverture-embleme", "couverture-tampon"}),
    "garde": ("papier", DC % "garde", {"planche", "garde", "sous-titre", "encadre", "titre-encadre",
                                      "trois-temps", "temps", "usages", "quand", "listes", "mot-script",
                                      "savant", "pied-garde", "note"}, {"garde"}),
    "entete-planche": ("papier", DC % "entete-planche", {"entete-planche", "milieu"}, set()),
    "carte-imagier": ("papier", DC % "carte-imagier", {"carte", "photo", "mot", "vide", "long",
                                                      "tres-long", "repere"}, set()),
    "carte-corpus": ("papier", DC % "carte-corpus", {"carte", "visuel", "photo", "dessin", "mot", "vide",
                                                    "long", "tres-long", "repere"}, set()),
    "etiquette": ("papier", DC % "etiquette", {"etiquette", "mot", "long", "tres-long", "repere"}, set()),
    "etiquette-tri": ("papier", DC % "etiquette-tri", {"tri", "mot-tri"}, set()),
    "credits": ("papier", DC % "credits", {"planche", "credits"}, set()),
    # la fiche élève est écrite à la main (skill fiches-eleve) : sa racine est
    # sa classe, et seul son cadre s'habille — jamais le matériel de l'exercice
    "fiche": ("papier", ".fiche", {"paysage", "entete", "idext", "champ", "trait", "cartouche", "ref", "dom",
                                  "titre", "niveau", "n1", "n2", "sous-objectif", "consigne", "exo", "num",
                                  "enonce", "defi", "etoile", "pied-fiche", "codage", "credits"}, set()),
    "bandeau-imprime": ("papier", DC % "bandeau-imprime", {"bandeau"}, set()),
    "document-imprime": ("papier", DC % "document-imprime", {"zone-badge"}, set()),
}
ORNEMENTS = {o: nom for nom, (_, _, _, ornes) in COMPOSANTS.items() for o in ornes}
# les mots que l'enfant lit : leur police, leur corps et leur espacement sont du socle
ENFANT = {"mot", "mot-tri", "mot-script", "couverture-titre", "repere", "mot-enfant"}
# attributs de contexte permis partout
CONTEXTE = {"data-periode", "data-theme", "data-support", "data-cahier", "data-bloc", "data-cle",
            "aria-current", "hidden"}

# ——— Les propriétés ———————————————————————————————————————————————————————
INTERDITES = re.compile(r"^(page|size|orphans|widows|(page-)?break-[\w-]+)$")
# Sur le papier, hors ornement : l'apparence seulement.
DECOR = re.compile(r"^(color|background(-color|-image|-position|-size|-repeat|-origin|-clip)?|"
                   r"border(-(top|right|bottom|left|block|inline)(-start|-end)?)?-(color|style)|"
                   r"border-(color|style)|border(-(top|bottom)-(left|right))?-radius|"
                   r"font-(family|weight|style|variant[\w-]*|feature-settings|kerning)|letter-spacing|"
                   r"text-transform|text-decoration[\w-]*|text-underline-offset|outline-(color|style)|"
                   r"fill|stroke|(-webkit-)?print-color-adjust|--[\w-]+)$")
POLICES_PERMISES = re.compile(r"^var\(--police-(titre|texte|etiquette|enfant)\)$")
TAILLE_MIN_ECRAN = 12  # px : en deçà, l'enseignant ne lit plus l'écran du téléphone


# ════════════════════════════════════════════════════════════════════════
# Lecture des feuilles
# ════════════════════════════════════════════════════════════════════════
def _sans_commentaires(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _regles(css, contexte=()):
    """[(contexte, prélude, corps)] — contexte : la pile des @media."""
    out, i = [], 0
    while True:
        j = css.find("{", i)
        if j < 0:
            break
        prelude = css[i:j].strip()
        k, prof = j + 1, 1
        while k < len(css) and prof:
            prof += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        corps = css[j + 1:k - 1]
        if prelude.startswith(("@media", "@supports", "@layer")):
            out += _regles(corps, contexte + (prelude,))
        else:
            out.append((contexte, prelude, corps))
        i = k
    return out


def _declarations(corps):
    out = []
    for d in re.split(r";(?![^(]*\))", corps):
        if ":" in d:
            p, v = d.split(":", 1)
            out.append((p.strip().lower(), v.strip()))
    return out


def _mode(contexte, prelude):
    """Le bloc de jetons d'une règle :root : clair, sombre ou impression."""
    if any("print" in c for c in contexte):
        return "impression"
    if any("dark" in c for c in contexte) or 'data-theme="dark"' in prelude:
        return "sombre"
    return "clair"


# ════════════════════════════════════════════════════════════════════════
# Couleurs
# ════════════════════════════════════════════════════════════════════════
def _couleur(v):
    v = v.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})", v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) == 8 and h[6:] != "ff":
            return None  # transparent : pas de contraste mesurable
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)\s*(?:[,/]\s*([\d.]+%?))?\s*\)", v)
    if m:
        if m.group(4) and m.group(4) not in ("1", "100%"):
            return None
        return tuple(int(m.group(i)) for i in (1, 2, 3))
    if v in ("white", "#fff"):
        return (255, 255, 255)
    if v == "black":
        return (0, 0, 0)
    return None


def luminance(rgb):
    def canal(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _resoudre(valeur, jetons, profondeur=0):
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,\s*(.+))?\)", valeur.strip())
    if not m or profondeur > 8:
        return valeur
    if m.group(1) in jetons:
        return _resoudre(jetons[m.group(1)], jetons, profondeur + 1)
    return _resoudre(m.group(2), jetons, profondeur + 1) if m.group(2) else valeur


# ════════════════════════════════════════════════════════════════════════
# Sélecteurs
# ════════════════════════════════════════════════════════════════════════
def _selecteurs(prelude):
    """Découpe une liste de sélecteurs à la virgule, hors parenthèses."""
    out, prof, cur = [], 0, ""
    for ch in prelude:
        prof += {"(": 1, ")": -1}.get(ch, 0)
        if ch == "," and not prof:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return out + [cur.strip()] if cur.strip() else out


def _analyse(sel):
    """→ (composants, ornement?, classes, attributs inconnus, cible enfant?, global?)"""
    composants = set(re.findall(r'\[data-composant="([\w-]+)"\]', sel))
    ornes = set(re.findall(r'\[data-orne="([\w-]+)"\]', sel))
    attributs = {a for a in re.findall(r"\[([\w-]+)", sel)} - {"data-composant", "data-orne"} - CONTEXTE
    sans_attr = re.sub(r"\[[^\]]*\]", "", sel)
    classes = set(re.findall(r"\.([\w-]+)", re.sub(r"\([^)]*\)", "", sans_attr)))
    classes |= set(re.findall(r"\.([\w-]+)", " ".join(re.findall(r"\(([^)]*)\)", sans_attr))))
    # racines par classe
    for nom, (_, racine, _, _) in COMPOSANTS.items():
        if racine.startswith(".") and racine[1:] in classes:
            composants.add(nom)
    for o in ornes:
        if o in ORNEMENTS:
            composants.add(ORNEMENTS[o])
    pseudo = bool(re.search(r"::?(before|after)\b", sel)) or bool(ornes)
    dernier = re.split(r"[\s>+~]+", sans_attr.strip())[-1]
    enfant = bool(set(re.findall(r"\.([\w-]+)", dernier)) & ENFANT) and not pseudo
    glob = re.fullmatch(r"(:root|html|body)(\[[^\]]*\]|:not\([^)]*\))*", sel.strip()) is not None
    return composants, ornes, pseudo, classes, attributs, enfant, glob


# ════════════════════════════════════════════════════════════════════════
# Le contrôle
# ════════════════════════════════════════════════════════════════════════
def anomalies(theme):
    a = []
    dossier = THEMES / theme
    if not (dossier / "theme.css").is_file():
        return ["themes/%s/theme.css n'existe pas" % theme]

    # — 1. Les fichiers déclarés —
    manifeste = {}
    if not (dossier / "theme.yml").is_file():
        a.append("theme.yml manque : il déclare les polices et les motifs du thème, et leur licence")
    else:
        manifeste = yaml.safe_load((dossier / "theme.yml").read_text(encoding="utf-8")) or {}
        for cle in ("nom", "description"):
            if not manifeste.get(cle):
                a.append("theme.yml : « %s » manque" % cle)
    declares = {}
    for e in manifeste.get("images") or []:
        if not isinstance(e, dict) or not e.get("fichier"):
            a.append("theme.yml : chaque image a `fichier`, `titre`, `auteur`, `source`, `licence`")
            continue
        f = e["fichier"]
        declares[f] = "images"
        if e.get("licence") not in LICENCES_IMAGES:
            a.append("theme.yml : image « %s » — licence « %s » ; seules %s (jamais NC ni ND)"
                     % (f, e.get("licence"), ", ".join(sorted(LICENCES_IMAGES))))
        for cle in ("titre", "auteur", "source"):
            if not e.get(cle):
                a.append("theme.yml : image « %s » — `%s` manque (crédit dû)" % (f, cle))
        if e.get("source") and not str(e["source"]).startswith("https://"):
            a.append("theme.yml : image « %s » — source « %s » : une adresse https://" % (f, e["source"]))
        if re.search(r"wiki(media|pedia)\.org", str(e.get("source") or "")):
            a.append("theme.yml : image « %s » — Wikimedia est exclu (AGENTS.md, « Images »)" % f)
        if not f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".avif", ".svg")):
            a.append("theme.yml : image « %s » — jpg, png, webp, avif ou svg" % f)
        if not (dossier / f).is_file():
            a.append("theme.yml déclare l'image %s, qui n'existe pas" % f)
    for genre in ("polices", "motifs"):
        for e in manifeste.get(genre) or []:
            fichiers = e.get("fichiers") or ([e["fichier"]] if e.get("fichier") else [])
            nom = e.get("famille") or e.get("fichier") or "?"
            if e.get("licence") not in LICENCES:
                a.append("theme.yml : %s « %s » — licence « %s » ; seules %s sont permises"
                         % (genre[:-1], nom, e.get("licence"), ", ".join(sorted(LICENCES))))
            if not e.get("auteur"):
                a.append("theme.yml : %s « %s » — l'auteur manque (crédit dû par la licence)" % (genre[:-1], nom))
            if not fichiers:
                a.append("theme.yml : %s « %s » sans fichier" % (genre[:-1], nom))
            for f in fichiers:
                declares[f] = genre
                if not (dossier / f).is_file():
                    a.append("theme.yml déclare %s, qui n'existe pas" % f)
    for f in sorted(dossier.rglob("*")):
        rel = str(f.relative_to(dossier))
        if f.is_file() and rel not in declares and rel not in HORS_DECLARATION:
            a.append("%s n'est déclaré nulle part dans theme.yml (licence inconnue)" % rel)
    for f, genre in declares.items():
        if genre == "motifs" and f.endswith(".svg") and (dossier / f).is_file():
            svg = (dossier / f).read_text(encoding="utf-8")
            for motif, quoi in ((r"<script", "un script"), (r"<image", "une image"),
                                (r"<foreignObject", "du HTML"), (r"<text", "du texte"),
                                (r"(?:xlink:)?href=\"(?!#)", "un lien externe")):
                if re.search(motif, svg, re.I):
                    a.append("%s contient %s : un motif est un tracé, rien d'autre" % (f, quoi))

    # — Les gabarits du mini-site —
    a += _gabarits(theme, dossier, manifeste)

    # — Lecture des feuilles —
    regles, polices_declarees, utilisees = [], set(), set()
    for feuille in FEUILLES:
        if not (dossier / feuille).is_file():
            continue
        brut = _sans_commentaires((dossier / feuille).read_text(encoding="utf-8"))
        for at in re.findall(r"@(import|page|namespace)\b", brut):
            a.append("%s : @%s interdit (le format des pages est du socle ; tout se charge par charte.css)"
                     % (feuille, at))
        if "!important" in brut:
            a.append("%s : !important interdit — l'habillage l'emporte déjà sur le moteur" % feuille)
        for u in re.findall(r"url\(\s*['\"]?([^'\")]+)", brut):
            if re.match(r"[a-z]+:|//|/", u):
                a.append("%s : url(%s) sort du thème — polices et motifs sont auto-hébergés, déclarés dans theme.yml"
                         % (feuille, u))
            elif u not in declares:
                a.append("%s : url(%s) — fichier non déclaré dans theme.yml" % (feuille, u))
            else:
                utilisees.add(u)
        for ctx, prelude, corps in _regles(brut):
            if prelude.startswith("@font-face"):
                fam = dict(_declarations(corps)).get("font-family", "").strip("\"' ")
                polices_declarees.add(fam)
                continue
            regles.append((feuille, ctx, prelude, _declarations(corps)))
    gab = (dossier / "gabarits.js").read_text(encoding="utf-8") if (dossier / "gabarits.js").is_file() else ""
    for f, genre in declares.items():
        if genre == "images" and f not in utilisees and f not in gab:
            a.append("image %s déclarée mais ni une feuille ni gabarits.js ne s'en sert" % f)
    for f in declares:
        if declares[f] != "images" and f not in utilisees and (f.endswith(".svg") or f.endswith(".woff2")):
            a.append("%s est déclaré mais aucune feuille ne s'en sert" % f)

    # — 2. Les jetons, bloc par bloc —
    blocs = {"clair": {}, "sombre": {}, "impression": {}}
    for feuille, ctx, prelude, decls in regles:
        if all(re.fullmatch(r"(:root|html)(\[[^\]]*\]|:not\([^)]*\))*", s) for s in _selecteurs(prelude)) \
                and not any('data-theme="light"' in s and ":not" not in s for s in _selecteurs(prelude)):
            mode = _mode(ctx, prelude)
            for p, v in decls:
                if p.startswith("--"):
                    blocs[mode][p] = v
    for mode, requis in REQUIS.items():
        manquants = [j for j in requis if j not in blocs[mode]]
        if manquants:
            a.append("bloc %s : jetons manquants %s — un jeton oublié retombe sur rien"
                     % (mode, ", ".join(manquants)))
    for j in ("--police-titre", "--police-texte", "--police-etiquette"):
        v = blocs["clair"].get(j)
        if v:
            premiere = v.split(",")[0].strip().strip("\"'")
            if premiere.startswith("var("):
                continue
            if premiere not in polices_declarees and premiere != "Andika":
                a.append("%s commence par « %s », qui n'a pas d'@font-face dans le thème : "
                         "le PDF se fabrique sans réseau, la police doit être auto-hébergée" % (j, premiere))

    # — 3. Le contraste —
    modes = {"clair": dict(blocs["clair"]),
             "sombre": {**blocs["clair"], **blocs["sombre"]},
             "impression": {**blocs["clair"], **blocs["impression"]}}
    paires = list(PAIRES) + [(t, f, r) for t, f, r in PAIRES_ACCROCHES
                             if t in blocs["clair"] or f in blocs["clair"]]
    for t, f in manifeste.get("contrastes") or []:
        paires.append((t, f, 4.5))
    for mode, jetons in modes.items():
        for t, f, mini in paires:
            ct, cf = (_couleur(_resoudre(jetons.get(x, ""), jetons)) for x in (t, f))
            if ct is None or cf is None:
                if (t in jetons or f in jetons) and mode == "clair":
                    a.append("contraste %s sur %s : couleur illisible pour le contrôle (%s / %s)"
                             % (t, f, jetons.get(t), jetons.get(f)))
                continue
            r = contraste(ct, cf)
            if r < mini:
                a.append("contraste %s : %s sur %s = %.2f:1, il faut %.1f:1"
                         % (mode, t, f, r, mini))
        if mode == "impression":
            for f in FONDS_PAPIER:
                c = _couleur(_resoudre(jetons.get(f, ""), jetons))
                if c and luminance(c) < LUMINANCE_FOND_PAPIER:
                    a.append("impression : %s = %s est un fond trop sombre pour le papier "
                             "(luminance %.2f < %.2f) — l'encre va aux traits et aux mots"
                             % (f, jetons[f], luminance(c), LUMINANCE_FOND_PAPIER))

    # — 4 et 5. Le socle et les composants —
    ornements_poses = {}
    for feuille, ctx, prelude, decls in regles:
        for p, v in decls:
            if p in ("animation", "animation-name") and v.strip() != "none" \
                    and not any("prefers-reduced-motion: no-preference" in c for c in ctx):
                a.append("%s : « %s » anime hors de @media (prefers-reduced-motion: no-preference) — "
                         "le mouvement s'arrête pour qui l'a demandé" % (feuille, prelude[:60]))
        if any(re.search(r"@media\b[^{]*\bscreen\b", c) for c in ctx) and feuille == "habillage.css":
            a += _ecran_du_theme(feuille, prelude, decls)
            continue
        for sel in _selecteurs(prelude):
            composants, ornes, pseudo, classes, attributs, enfant, glob = _analyse(sel)
            ou = "%s : « %s »" % (feuille, sel)
            for p, v in decls:
                if p.startswith("--"):
                    if SOCLE.match(p):
                        a.append("%s redéfinit %s, qui est du socle" % (ou, p))
                    elif p not in COULEURS + ["--police-titre", "--police-texte", "--ombre-flotte"] \
                            and p not in ACCROCHES and not PRIVEE.match(p) and not RAYONS.match(p):
                        a.append("%s : %s n'est ni un jeton du thème, ni une accroche du moteur, "
                                 "ni une variable propre (--t-…)" % (ou, p))
                if INTERDITES.match(p):
                    a.append("%s : %s — la mise en page du papier est du socle" % (ou, p))
                if p == "font-family" and not POLICES_PERMISES.match(v):
                    a.append("%s : font-family « %s » — passer par var(--police-titre|texte|etiquette)" % (ou, v))
                if enfant and (p.startswith("font") or p in ("letter-spacing", "word-spacing",
                                                              "text-transform", "line-height")):
                    a.append("%s : %s sur un mot que l'enfant lit — sa police, son corps et "
                             "son espacement sont du socle (Andika)" % (ou, p))
                if enfant and p == "color" and not re.fullmatch(r"var\(--(encre|periode|p\d|sapin)\)", v):
                    a.append("%s : la couleur d'un mot de l'enfant reste l'encre ou la période" % ou)
            if glob:
                if any(not p.startswith("--") and p != "color-scheme" for p, _ in decls):
                    if not ('data-support="ecran"' in sel and
                            all(p.startswith(("--", "background", "color-scheme")) for p, _ in decls)):
                        a.append("%s : sur la page entière, seul un fond d'écran "
                                 "(body[data-support=\"ecran\"]) ou des jetons sont permis" % ou)
                continue
            composants = {n for n in composants if n in COMPOSANTS}
            if not composants and re.search(r'\[data-composant=', sel):
                a.append("%s : composant inconnu" % ou)
                continue
            if not composants:
                a.append("%s ne part d'aucun composant nommé par le moteur (data-composant, data-orne, "
                         ".fiche, .pastille, .btn) — le moteur ne garantit pas ce nom" % ou)
                continue
            noms = set(re.findall(r'\[data-composant="([\w-]+)"\]', sel))
            if noms - set(COMPOSANTS) or any(COMPOSANTS[n][1] != DC % n for n in noms if n in COMPOSANTS):
                a.append("%s : composant inconnu %s" % (ou, ", ".join(sorted(
                    n for n in noms if n not in COMPOSANTS or COMPOSANTS[n][1] != DC % n))))
                continue
            inconnus = [o for o in ornes if o not in ORNEMENTS]
            if inconnus:
                a.append("%s : ornement inconnu %s" % (ou, ", ".join(inconnus)))
            permises = set().union(*(COMPOSANTS[c][2] for c in composants))
            permises |= {COMPOSANTS[c][1][1:] for c in composants if COMPOSANTS[c][1].startswith(".")}
            permises.add("orne")
            hors = sorted(classes - permises)
            if hors:
                a.append("%s : %s ne fait pas partie des composants %s — classe interne au moteur"
                         % (ou, ", ".join("." + c for c in hors), ", ".join(sorted(composants))))
            if attributs:
                a.append("%s : attribut %s non garanti par le moteur" % (ou, ", ".join(sorted(attributs))))
            papier = any(COMPOSANTS[c][0] == "papier" for c in composants)
            couverture = composants <= {"couverture"}
            if papier and pseudo:
                ornements_poses.setdefault(re.sub(r"\s+", " ", sel), []).extend(decls)
            elif couverture and not re.fullmatch(r'(\[data-composant="couverture"\]|\.planche|\.couverture|'
                                                 r'\[data-(periode|cle)="[\w-]+"\])+', sel.strip()):
                # l'intérieur de la couverture : une affiche à hauteur fixe, sa
                # géométrie est libre — elle ne peut pas déplacer la pagination
                continue
            elif papier:
                for p, v in decls:
                    if not DECOR.match(p):
                        a.append("%s : %s change la géométrie du papier — l'habillage ne change que "
                                 "l'apparence (la pagination est prouvée au PDF)" % (ou, p))
                    if p.startswith("background") and not couverture:
                        c = _couleur(_resoudre(v.split()[0] if v else "", modes["impression"]))
                        if c and luminance(c) < LUMINANCE_FOND_PAPIER:
                            a.append("%s : aplat sombre (%s) — sur le papier, seule la couverture en porte" % (ou, v))
            else:
                for p, v in decls:
                    if p == "font-size":
                        m = re.match(r"([\d.]+)(px|rem|em)", v)
                        if m and float(m.group(1)) * (16 if m.group(2) != "px" else 1) < TAILLE_MIN_ECRAN:
                            a.append("%s : font-size %s — %d px au moins à l'écran" % (ou, v, TAILLE_MIN_ECRAN))
    for sel, decls in ornements_poses.items():
        d = dict(decls)
        if d.get("content", "").strip() == "none" or d.get("display", "").strip() == "none":
            continue
        if d.get("position", "").strip() != "absolute":
            a.append("ornement « %s » : position absolute obligatoire sur le papier — "
                     "un ornement ne prend jamais de place dans la page" % sel)
    return a


# Les composants du papier, qu'une règle d'écran du thème ne nomme jamais.
PAPIER = {n for n, (support, _, _, _) in COMPOSANTS.items() if support == "papier"}
CLASSES_PAPIER = {"fiche", "planche", "carte", "etiquette", "couverture", "garde", "credits", "tri"}


def _ecran_du_theme(feuille, prelude, decls):
    """Une règle de `@media screen` dans habillage.css : l'habillage du HTML
    que rendent les gabarits du thème. Ses classes sont libres ; elle ne nomme
    aucun composant du papier, ne vise pas un élément nu (qui toucherait les
    fiches ouvertes à l'écran), passe par les jetons de police, garde le corps
    du texte lisible et laisse Andika aux mots de l'enfant."""
    a = []
    for sel in _selecteurs(prelude):
        ou = "%s : « %s »" % (feuille, sel)
        if sel.startswith("@") or sel in ("from", "to") or re.fullmatch(r"[\d.]+%", sel):
            continue
        comp = set(re.findall(r'\[data-composant="([\w-]+)"\]', sel))
        if comp & PAPIER or set(re.findall(r"\.([\w-]+)", sel)) & CLASSES_PAPIER:
            a.append("%s : une règle d'écran ne touche pas au papier" % ou)
        racine = re.split(r"[\s>+~]+", sel.strip())[0]
        if not re.search(r"[.#\[]", racine) and 'data-support="ecran"' not in sel:
            a.append("%s : une règle d'écran part d'une classe, d'un id ou d'un attribut "
                     "(ou de body[data-support=\"ecran\"]) — un élément nu toucherait les fiches" % ou)
        enfant = "mot-enfant" in re.findall(r"\.([\w-]+)", re.split(r"[\s>+~]+", sel.strip())[-1])
        for p, v in decls:
            if p == "font-family" and not POLICES_PERMISES.match(v):
                a.append("%s : font-family « %s » — passer par var(--police-…)" % (ou, v))
            if p == "font" and re.search(r"[\"']|\bserif\b|sans-serif", v) and "var(--police-" not in v:
                a.append("%s : font « %s » — la famille passe par var(--police-…)" % (ou, v))
            if enfant and (p in ("font-family", "letter-spacing", "word-spacing", "text-transform", "font-style")
                           or (p == "font" and "var(--police-enfant)" not in v)):
                a.append("%s : %s sur un mot de l'enfant — Andika, droite, sans espacement ajouté" % (ou, p))
            if p in ("font-size", "font"):
                m = re.search(r"(?<![\w.-])([\d.]+)(px|rem|em)\b", v)
                if m and float(m.group(1)) * (16 if m.group(2) != "px" else 1) < TAILLE_MIN_ECRAN:
                    a.append("%s : corps %s — %d px au moins à l'écran" % (ou, m.group(0), TAILLE_MIN_ECRAN))
            if p.startswith("--") and SOCLE.match(p):
                a.append("%s redéfinit %s, qui est du socle" % (ou, p))
    return a


def _gabarits(theme, dossier, manifeste):
    """gabarits.js : présent si theme.yml l'annonce, sans logique du moteur,
    et essayé sur la vraie classe par scripts/verifier-gabarits.js."""
    a = []
    f = dossier / "gabarits.js"
    annonce = manifeste.get("gabarits")
    if annonce and not f.is_file():
        return ["theme.yml annonce des gabarits (%s), mais gabarits.js n'existe pas" % annonce]
    js = f.read_text(encoding="utf-8") if f.is_file() else ""
    sans = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    sans = re.sub(r"(?m)^\s*//.*$", "", sans)
    for motif, quoi in GABARIT_INTERDIT:
        if re.search(motif, sans):
            a.append("gabarits.js %s" % quoi)
    if js and "GS.theme(" not in sans:
        a.append("gabarits.js n'appelle pas GS.theme({ … }) : rien n'est enregistré")
    if MOUVEMENT_JS.search(sans) and "mouvement" not in sans and "prefers-reduced-motion" not in sans:
        a.append("gabarits.js anime sans regarder m.mouvement (prefers-reduced-motion)")
    import shutil
    import subprocess
    node = shutil.which("node")
    if not node:
        print("⚠ Node absent : les gabarits ne sont pas essayés (scripts/verifier-gabarits.js)")
        return a
    site = RACINE / "site"
    if not (site / "classe.json").is_file():
        return a
    import json
    if json.loads((site / "classe.json").read_text(encoding="utf-8")).get("theme") != theme:
        return a  # on n'essaie un thème que sur la classe qui l'a choisi
    # sans gabarits.js, ce sont ceux du moteur qu'on essaie
    r = subprocess.run([node, str(RACINE / "scripts" / "verifier-gabarits.js"), str(site),
                        str(f) if f.is_file() else "-"],
                       capture_output=True, text=True)
    a += ["gabarits : " + l for l in r.stdout.splitlines() if l.strip()]
    if r.returncode and not r.stdout.strip():
        a.append("gabarits : l'essai a échoué (%s)" % r.stderr.strip()[:200])
    return a


def main():
    sys.path.insert(0, str(RACINE / "scripts"))
    if len(sys.argv) > 1:
        themes = sys.argv[1:]
    else:
        import classe
        themes = [classe.charger()["theme"]]
    total = 0
    for t in themes:
        res = anomalies(t)
        for x in res:
            print("✘ %s : %s" % (t, x))
        print("thème « %s » : %d anomalie(s)" % (t, len(res)))
        total += len(res)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
