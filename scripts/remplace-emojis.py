# -*- coding: utf-8 -*-
"""Remplace les émojis des fiches élève par de vraies images (site/fiches/img/)
ou par des glyphes texte, et supprime les émojis décoratifs.
- Passe 1 : remplacements contextuels (émojis ambigus, textes à nettoyer).
- Passe 2 : suppression des émojis dans les titres de fiches.
- Passe 3 : table de correspondance globale par fichier.
- Passe 4 : contrôle final (aucun émoji restant hors liste blanche).
"""
import json, os, re, sys

BASE = os.path.join(os.path.dirname(__file__), "..", "site", "fiches")
credits = json.load(open(os.path.join(BASE, "img", "credits.json"), encoding="utf-8"))

def IMG(slug, cls="pic"):
    if slug.endswith(".svg"):  # images auto-fabriquées
        return f'<img class="{cls}" src="img/{slug}" alt="">'
    fichier = credits[slug]["fichier"]
    return f'<img class="{cls}" src="img/{fichier}" alt="">'

VS = "️"

# ————— Passe 1 : contextuel (doit correspondre exactement) —————
CONTEXTE = {
"periode-2.html": [
    ('<span class="img">🌰</span>marron', f'<span class="img">{IMG("marron")}</span>marron'),
    ('<span class="img">🌰🌰🌰🌰🌰🌰</span>\n      <p style="font-size:10pt">Il reste : <span class="chiffre-case"></span> glands</p>',
     f'<span class="img">{IMG("gland")*6}</span>\n      <p style="font-size:10pt">Il reste : <span class="chiffre-case"></span> glands</p>'),
],
"periode-3.html": [
    ('<td class="img">🏔️ le glacier</td>', f'<td class="img">{IMG("glacier")} le glacier</td>'),
    ('(bouquetin 🐐 : 7 → −2)', f'(bouquetin {IMG("bouquetin")} : 7 → −2)'),
],
"periode-4.html": [
    ('<span class="img">🌱</span>RADIS', f'<span class="img">{IMG("radis")}</span>RADIS'),
    ('<span class="img">🥗</span>MENU', '<span class="img"></span>MENU'),
    ('<th>On ne le voit plus 👻</th><th>On le voit encore 👀</th>', '<th>On ne le voit plus</th><th>On le voit encore</th>'),
],
"periode-5.html": [
    ('il marche sur le sable 🦶', 'il marche sur le sable'),
    ('il vole dans le ciel ☁️', 'il vole dans le ciel'),
    ('il nage avec ses nageoires 🌊', 'il nage avec ses nageoires'),
    ('il nage et respire à la surface 💨', 'il nage et respire à la surface'),
    ('<th>flotte 🛟</th><th>coule ⬇️</th><th>flotte 🛟</th><th>coule ⬇️</th>', '<th>flotte</th><th>coule</th><th>flotte</th><th>coule</th>'),
],
"entrainement-periode-1.html": [
    ('3e étage : 🔵🔵🔵', '3e étage : ●●●'),
    ('2e étage : 🔵🔵', '2e étage : ●●'),
    ('1er étage : 🔵', '1er étage : ●'),
    ('<span class="img">🪖🪖🪖🪖</span>', f'<span class="img">{IMG("casque-velo")*4}</span>'),
    ('<div class="item">🐾 les animaux</div>', '<div class="item">les animaux</div>'),
    ('<div class="item">🏛️ les bâtiments</div>', '<div class="item">les bâtiments</div>'),
],
"entrainement-periode-2.html": [
    ('<div class="item">🐗 sanglier ? non… canard 🦆</div>', f'<div class="item">{IMG("canard")} canard</div>'),
    ('<div class="item">🧤 hérisson… non ! ourson 🧸</div>', f'<div class="item">{IMG("ourson")} ourson</div>'),
    ('<div class="item">🍂 …ver de terre 🪱</div>', f'<div class="item">{IMG("ver-de-terre")} ver de terre</div>'),
    ('<div class="item">le creux de l’arbre 🕳️🌳</div>', f'<div class="item">{IMG("arbre-creux")} le creux de l’arbre</div>'),
    ('<div class="item">la fourmilière ⛰️</div>', f'<div class="item">{IMG("fourmiliere")} la fourmilière</div>'),
    ('<div class="item">le terrier 🕳️</div>', f'<div class="item">{IMG("terrier")} le terrier</div>'),
    ('<div class="item">le nid dans le tronc 🪵</div>', f'<div class="item">{IMG("nid")} le nid dans l’arbre</div>'),
],
"entrainement-periode-3.html": [
    ('<div class="item">🛷 luge… non, ski ⛷️</div>', f'<div class="item">{IMG("ski")} ski</div>'),
    ('<div class="item">🏔️ cima… cime</div>', f'<div class="item">{IMG("montagne")} cime</div>'),
    ('<td class="img">🧤 moufle… igloo ? troupeau 🐑</td>', f'<td class="img">{IMG("mouton")} troupeau</td>'),
    ('<td class="img">🧊 igloo</td>', f'<td class="img">{IMG("igloo")} igloo</td>'),
    ('<td class="img">🏔️ sommet (« o » au début ?)</td>', f'<td class="img">{IMG("montagne")} sommet</td>'),
    ('il part vers les pays chauds ✈️', f'il part vers les pays chauds {IMG("oies-migration")}'),
    ('il reste actif, son pelage épaissit 🧥', 'il reste actif, son pelage épaissit'),
    ('elle dort tout l’hiver 😴', 'elle dort tout l’hiver'),
    ('la montagne du « a » 🅰️ ou la montagne du « i » ℹ️', 'la montagne du « a » ou la montagne du « i »'),
    ('<div class="item" style="font-size:20pt">🅰️ montagne du « a »</div>', '<div class="item"><span style="font-size:20pt;font-weight:700">A</span> montagne du « a »</div>'),
    ('<div class="item" style="font-size:20pt">ℹ️ montagne du « i »</div>', '<div class="item"><span style="font-size:20pt;font-weight:700">I</span> montagne du « i »</div>'),
    ('<p style="font-size:18pt;margin:2mm 0">🔺⚪ 🔺⚪⚪ 🔺⚪⚪⚪ …</p>',
     f'<p style="margin:2mm 0">{IMG("triangle.svg")}{IMG("rond.svg")} &nbsp; {IMG("triangle.svg")}{IMG("rond.svg")}{IMG("rond.svg")} &nbsp; {IMG("triangle.svg")}{IMG("rond.svg")}{IMG("rond.svg")}{IMG("rond.svg")} …</p>'),
    ('<p style="font-size:18pt;margin:4mm 0 2mm">⭐ ⭐⭐ ⭐⭐⭐ …</p>',
     f'<p style="margin:4mm 0 2mm">{IMG("etoile-jaune.svg")} &nbsp; {IMG("etoile-jaune.svg")}{IMG("etoile-jaune.svg")} &nbsp; {IMG("etoile-jaune.svg")}{IMG("etoile-jaune.svg")}{IMG("etoile-jaune.svg")} …</p>'),
    ('la frise 🔵 🔵🔵 🔵🔵🔵 continue…', f'la frise {IMG("rond-plein.svg")} &nbsp;{IMG("rond-plein.svg")}{IMG("rond-plein.svg")} &nbsp;{IMG("rond-plein.svg")}{IMG("rond-plein.svg")}{IMG("rond-plein.svg")} continue…'),
    ('<span class="img">⚪⚪⚪⚪</span>', f'<span class="img">{IMG("rond.svg")*4}</span>'),
],
"entrainement-periode-4.html": [
    ('<span class="img">🌱</span>RADIS', f'<span class="img">{IMG("radis")}</span>RADIS'),
    ('<span class="img">🥕</span>NAVET', f'<span class="img">{IMG("navet")}</span>NAVET'),
],
"entrainement-periode-5.html": [
    ('<div class="case"><span class="img">🧜</span>marin… sirène ? matelot !</div>', f'<div class="case"><span class="img">{IMG("matelot")}</span>matelot</div>'),
    ('<div class="case"><span class="img">🗼</span>phare… attention, piège de la maîtresse ! plage 🏖️</div>', f'<div class="case"><span class="img">{IMG("plage")}</span>plage</div>'),
    ('<td class="img">🦈 requin ? non : « riz » 🍚 (r-i)</td>', f'<td class="img">{IMG("riz")} riz (r-i)</td>'),
    ('<td class="img">🌊 mer (m-è-r)</td>', f'<td class="img">{IMG("vague")} mer (m-è-r)</td>'),
    ('<td class="img">⛵ mât (m-â)</td>', f'<td class="img">{IMG("voilier")} mât (m-â)</td>'),
    ('<td class="img">🏝️ île (i-l)</td>', f'<td class="img">{IMG("ile")} île (i-l)</td>'),
    ('comme un robot 🤖.', 'comme un robot.'),
    ('<div class="item">🏙️ la ville</div>', '<div class="item">la ville</div>'),
    ('<div class="item">🌳 la forêt</div>', '<div class="item">la forêt</div>'),
    ('<div class="item">⛰️ la montagne</div>', '<div class="item">la montagne</div>'),
    ('<div class="item">🌾 la campagne</div>', '<div class="item">la campagne</div>'),
    ('<div class="item">🌊 la mer</div>', '<div class="item">la mer</div>'),
    ('🎨 EXPO', 'EXPO'),
],
}

# ————— Passe 3 : correspondance globale (par défaut, puis surcharges par fichier) —————
GLOBAL = {
    # texte / suppression
    "⭐": ("txt", "★"), "✔": ("txt", "✓"), "✖": ("txt", "✗"),
    "➡": ("txt", "→"), "⬅": ("txt", "←"), "⬇": ("txt", "↓"),
    "🔵": ("txt", "●"), "😄": ("del",), "🌙": ("del",), "🎵": ("del",),
    "🐾": ("del",), "🏛": ("del",), "🛟": ("del",), "🦶": ("del",),
    "☁": ("del",), "💨": ("del",), "👻": ("del",), "👀": ("del",), "🤖": ("del",),
    # dés
    "⚀": ("img", "de-1.svg"), "⚁": ("img", "de-2.svg"), "⚂": ("img", "de-3.svg"),
    "⚃": ("img", "de-4.svg"), "⚄": ("img", "de-5.svg"), "⚅": ("img", "de-6.svg"),
    "⚪": ("img", "rond.svg"),
    # images
    "🚌": ("img", "bus"), "🚲": ("img", "velo"), "🕊": ("img", "pigeon"),
    "🐜": ("img", "fourmi"), "🐌": ("img", "escargot"), "🐞": ("img", "coccinelle"),
    "🏪": ("img", "magasin"), "🚦": ("img", "feu-tricolore"), "🏠": ("img", "maison"),
    "🚁": ("img", "helicoptere"), "🏢": ("img", "immeuble"), "🏫": ("img", "ecole"),
    "🏥": ("img", "hopital"), "🐋": ("img", "baleine"), "🧍": ("img", "personne"),
    "🪹": ("img", "nid"), "🏊": ("img", "piscine"), "🎬": ("img", "cinema"),
    "🩺": ("del",), "🦉": ("img", "hibou"), "🐺": ("img", "loup"),
    "🪨": ("img", "caillou"), "🦊": ("img", "renard"), "🌲": ("img", "sapin"),
    "🦵": ("img", "genou"), "🦔": ("img", "herisson"), "🍄": ("img", "champignon"),
    "🐿": ("img", "ecureuil"), "🍂": ("img", "feuille-morte"), "🍎": ("img", "pomme"),
    "🕳": ("img", "terrier"), "🦌": ("img", "cerf"), "🐗": ("img", "sanglier"),
    "🦆": ("img", "canard"), "🧸": ("img", "ourson"), "🪱": ("img", "ver-de-terre"),
    "🎈": ("img", "ballon"), "🪵": ("img", "bois"),
    "❄": ("img", "flocon"), "🛷": ("img", "luge"), "🐐": ("img", "chamois"),
    "🏍": ("img", "moto"), "🍫": ("img", "chocolat-chaud"), "🦙": ("img", "lama"),
    "🦅": ("img", "aigle"), "🐹": ("img", "marmotte"), "🧊": ("img", "glacon"),
    "⛷": ("img", "ski"), "🧤": ("img", "moufle"), "🏔": ("img", "montagne"),
    "🌧": ("img", "pluie"), "⛄": ("img", "neige"), "🚰": ("img", "robinet"),
    "💧": ("img", "goutte"), "☀": ("img", "soleil"), "🧣": ("img", "echarpe"),
    "🧥": ("img", "manteau"), "👒": ("img", "chapeau-soleil"), "🩴": ("img", "tongs"),
    "👙": ("img", "tee-shirt"), "🐑": ("img", "mouton"), "✈": ("img", "avion"),
    "🥬": ("img", "salade"), "🐛": ("img", "chenille"), "🐴": ("img", "cheval"),
    "🐤": ("img", "poussin"), "🐮": ("img", "vache"), "🐄": ("img", "vache"),
    "🐭": ("img", "souris"), "🥚": ("img", "oeuf"), "🐔": ("img", "poule"),
    "🌸": ("img", "fleur"), "🌻": ("img", "tournesol"), "🍒": ("img", "cerise"),
    "🍓": ("img", "fraise"), "🍅": ("img", "tomate"), "🥕": ("img", "carotte"),
    "🐰": ("img", "lapin"), "🪴": ("img", "pot-de-fleur"), "🦋": ("img", "papillon"),
    "🛌": ("img", "chrysalide"), "🍬": ("img", "sucre"), "🧂": ("img", "sel"),
    "🏖": ("img", "plage"), "🎃": ("img", "citrouille"), "🥔": ("img", "patate"),
    "🫘": ("img", "haricot"), "🐱": ("img", "chat"), "🚗": ("img", "voiture"),
    "🐍": ("img", "serpent"), "📺": ("img", "television"), "🌱": ("img", "pousse"),
    "🌿": ("img", "plante-jeune"), "🐣": ("img", "eclosion"), "🌼": ("img", "fleur"),
    "🗼": ("img", "phare"), "🌊": ("img", "vague"), "🐬": ("img", "dauphin"),
    "🥅": ("img", "filet-peche"), "⛵": ("img", "voilier"), "🚀": ("img", "fusee"),
    "🦀": ("img", "crabe"), "🐦": ("img", "moineau"), "🪣": ("img", "seau.svg"),
    "🥄": ("img", "pelle.svg"), "🐚": ("img", "coquillage"),
    "🐟": ("img", "poisson"), "🐠": ("img", "poisson"), "🔩": ("img", "fer"),
    "🍾": ("img", "bouchon-liege"), "🦑": ("img", "calamar"), "📿": ("img", "collier-perles"),
    "🏝": ("img", "ile"), "🍚": ("img", "riz"), "🌬": ("img", "vent"),
    "🌰": ("img", "noisette"),
}
PAR_FICHIER = {
    "periode-4.html": {"🌰": ("img", "graine"), "🍫": ("img", "chocolat"), "🏖": ("img", "sable")},
    "entrainement-periode-4.html": {"🌰": ("img", "graine"), "💨": ("img", "souffle")},
    "periode-5.html": {"⭐": ("img", "etoile-de-mer"), "🐦": ("img", "mouette")},
    "entrainement-periode-5.html": {"⭐": ("img", "etoile-de-mer"), "🐦": ("img", "mouette")},
    "entrainement-periode-3.html": {"⭐": ("img", "etoile-jaune.svg")},
    "periode-3.html": {"⭐": ("img", "etoile-jaune.svg")},
}

EMOJI_RE = re.compile('[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF\U0001F1E6-\U0001F1FF♀♂✈⛰-⛿⭐❤ℹ\U0001F170-\U0001F251‍]')
BLANC = set("★✓✗●▲☐✂→←↓·")

FICHIERS = ["periode-%d.html" % i for i in range(1, 6)] + ["entrainement-periode-%d.html" % i for i in range(1, 6)]

erreurs = []
for nom in FICHIERS:
    chemin = os.path.join(BASE, nom)
    txt = open(chemin, encoding="utf-8").read()

    # Pré-passe : marqueur de défi
    txt = txt.replace("⭐ Défi", "★ Défi").replace('<span class="etoile">⭐', '<span class="etoile">★')

    # Passe 1 : contextuel
    for old, new in CONTEXTE.get(nom, []):
        if old not in txt:
            erreurs.append(f"{nom}: contexte introuvable : {old[:70]!r}")
            continue
        txt = txt.replace(old, new)

    # Passe 2 : titres sans émoji
    def nettoie_titre(m):
        inner = EMOJI_RE.sub("", m.group(1)).replace(VS, "")
        return '<div class="titre">' + inner.lstrip()
    txt = re.sub(r'<div class="titre">(.*?)(?=<span class="niveau|</div>)', nettoie_titre, txt)

    # Passe 3 : global
    table = dict(GLOBAL); table.update(PAR_FICHIER.get(nom, {}))
    txt = txt.replace(VS, "").replace("‍♀", "").replace("‍☠", "")
    for ch, action in table.items():
        if ch not in txt:
            continue
        if action[0] == "img":
            txt = txt.replace(ch, IMG(action[1]))
        elif action[0] == "txt":
            txt = txt.replace(ch, action[1])
        else:
            txt = txt.replace(ch, "")
    txt = re.sub(r'[ \t]+</', '</', txt)

    # Passe 4 : contrôle
    restes = set(EMOJI_RE.findall(txt)) - BLANC - {"‍"}
    if restes:
        erreurs.append(f"{nom}: émojis restants : {' '.join(sorted(restes))}")

    open(chemin, "w", encoding="utf-8").write(txt)
    print(f"{nom} : OK")

if erreurs:
    print("\n—— À CORRIGER ——")
    for e in erreurs:
        print(" •", e)
    sys.exit(1)
print("\nTous les fichiers sont propres.")
