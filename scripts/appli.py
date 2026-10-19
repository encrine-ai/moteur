# -*- coding: utf-8 -*-
"""L'appli installable : le site de la classe sur l'écran d'accueil.

L'enseignant installe le site de SA classe sur son téléphone ou sa tablette
(« Ajouter à l'écran d'accueil »), et l'ouvre en classe comme une appli, même
sans réseau. Ce module fabrique, pour chaque classe et depuis son thème :

- site/manifest.webmanifest : le nom et le nom court (classe.yml), l'adresse
  de départ et la portée relatives (le site vit dans un sous-dossier,
  https://<propriétaire>.github.io/<dépôt>/), les couleurs du thème ;
- site/icones/ : l'icône de la classe, en SVG et en PNG (192, 512, maskable
  512, apple-touch 180, favicon 32) et site/favicon.ico — celle que dessine
  le thème (theme.yml, `icone:` : un tracé ou une image libre recadrée,
  scripts/icone_du_theme.py, rendue par Chromium), ou à défaut celle du
  moteur : les cinq bandes des périodes et l'initiale, dans la police des
  titres du thème ;
- site/sw.js : le service worker, tiré de scripts/modele-sw.js, avec la liste
  de ce qu'il met en cache à l'installation et la version du site (une
  empreinte du contenu) : à chaque publication, l'ancien cache est remplacé.

`classe.py generer` appelle fabriquer() ; `classe.py verifier` appelle
anomalies() ; le déploiement appelle estampiller() sur le site assemblé, pour
que la version tienne compte des documents copiés dans content/.

Les PNG demandent Pillow, fontTools et brotli (la police du thème est en
woff2) : sans eux, `generer` le dit et garde les icônes existantes ;
`verifier` n'en a pas besoin (il lit l'empreinte inscrite dans chaque icône).
"""
import hashlib
import importlib
import io
import json
import pathlib
import re
import struct
import sys
import zlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
CHARTE = SITE / "charte"
ICONES = SITE / "icones"
MANIFESTE = SITE / "manifest.webmanifest"
SW = SITE / "sw.js"
MODELE_SW = RACINE / "scripts" / "modele-sw.js"
# Change quand le dessin de l'icône change : les icônes sont alors à refaire.
DESSIN = "bandes-initiale-1"

# Les icônes : (fichier, côté, forme). « arrondie » : un carré aux coins
# arrondis, transparent autour (onglet, bureau, boîte d'installation) ;
# « pleine » : le carré entier, que le système découpe lui-même (iOS arrondit
# l'apple-touch-icon ; Android découpe la maskable dans sa zone sûre, un
# disque de 80 % du côté).
PNG = [
    ("icones/appli-192.png", 192, "arrondie"),
    ("icones/appli-512.png", 512, "arrondie"),
    ("icones/appli-maskable-512.png", 512, "pleine"),
    ("icones/apple-touch-icon.png", 180, "pleine"),
    ("icones/favicon-32.png", 32, "arrondie"),
]
SVG = "icones/appli.svg"
ICO = "favicon.ico"

ARTICLES = re.compile(r"^(le|la|les|l['’]|un|une|des|à la|à l['’]|au|aux)\s*", re.I)


# ═══════════════════════════════════════════════════════════════════════
# Ce que la classe et son thème disent de l'appli
# ═══════════════════════════════════════════════════════════════════════
def identite(c):
    """{nom, nom_court, initiale} : `appli` dans classe.yml s'il les donne,
    sinon tirés du nom et du projet. Le nom court est l'étiquette sous
    l'icône (une douzaine de lettres) ; l'initiale, celle de l'icône."""
    propre = c.get("appli") or {}
    nom = propre.get("nom") or "%s — %s" % (c["nom"], c["projet"])
    court = propre.get("nom_court")
    if not court:
        projet = ARTICLES.sub("", c["projet"]).strip()
        if len(c["nom"]) <= 12:
            court = c["nom"]
        elif len(projet) <= 15:
            court = projet[:1].upper() + projet[1:]
        else:
            court = "%s %s" % (c["niveau"]["code"], c["annee"])
    initiale = propre.get("initiale") or next((x for x in court if x.isalpha()), "?")
    return {"nom": nom, "nom_court": court, "initiale": initiale[:1].upper()}


def _theme_module():
    sys.path.insert(0, str(RACINE / "scripts"))
    return importlib.import_module("verifier-theme")


def _jetons_clairs(theme):
    vt = _theme_module()
    css = vt._sans_commentaires((CHARTE / "themes" / theme / "theme.css").read_text(encoding="utf-8"))
    jetons = {}
    for contexte, prelude, corps in vt._regles(css):
        if prelude.strip() == ":root" and vt._mode(contexte, prelude) == "clair":
            jetons.update(dict(vt._declarations(corps)))
    return jetons


def couleur_du_theme(theme, valeur):
    """« #rrggbb » ou un jeton clair du thème (« --feuille ») → (r, g, b), ou None."""
    vt = _theme_module()
    valeur = str(valeur).strip()
    if valeur.startswith("--"):
        valeur = "var(%s)" % valeur
    return vt._couleur(vt._resoudre(valeur, _jetons_clairs(theme)))


def couleurs(c):
    """Les jetons clairs du thème : --papier, --feuille, --sapin, --p1…--p5."""
    vt = _theme_module()
    jetons = _jetons_clairs(c["theme"])
    out = {}
    for nom in ("papier", "feuille", "sapin", "encre", "p1", "p2", "p3", "p4", "p5"):
        v = vt._resoudre(jetons.get("--" + nom, ""), jetons)
        rgb = vt._couleur(v)
        if rgb is None:
            raise ValueError("le thème « %s » n'a pas de couleur lisible pour --%s (« %s »)"
                             % (c["theme"], nom, v))
        out[nom] = "#%02x%02x%02x" % rgb
    return out


def police_titre(c):
    """Le fichier de la police des titres du thème (theme.yml, rôle
    --police-titre), ou Andika en gras, celle du socle."""
    import yaml
    dossier = CHARTE / "themes" / c["theme"]
    t = yaml.safe_load((dossier / "theme.yml").read_text(encoding="utf-8")) or {}
    for p in t.get("polices") or []:
        if "--police-titre" in (p.get("role") or "") and p.get("fichiers"):
            f = dossier / p["fichiers"][0]
            if f.is_file():
                return f
    return CHARTE / "polices" / "andika-latin-700.woff2"


def icone_theme(c):
    """(dossier, déclaration, fond) si le thème dessine l'icône (theme.yml,
    `icone:`), sinon None : l'icône est alors celle du moteur."""
    import yaml
    import icone_du_theme
    dossier = CHARTE / "themes" / c["theme"]
    f = dossier / "theme.yml"
    t = yaml.safe_load(f.read_text(encoding="utf-8")) if f.is_file() else {}
    decl = icone_du_theme.declaration(t or {})
    if not decl:
        return None
    rgb = couleur_du_theme(c["theme"], decl.get("fond", "--feuille"))
    return dossier, decl, "#%02x%02x%02x" % (rgb or (255, 255, 255))


def empreinte_icones(c):
    """Ce dont l'icône est faite : le dessin, les couleurs, l'initiale, la
    police — ou la déclaration et les fichiers de l'icône du thème. Inscrite
    dans chaque icône, relue par `verifier`."""
    it = icone_theme(c)
    if it:
        import icone_du_theme
        return icone_du_theme.empreinte(*it)
    h = hashlib.sha256()
    h.update(DESSIN.encode())
    h.update(json.dumps([couleurs(c), identite(c)["initiale"]], sort_keys=True).encode())
    h.update(police_titre(c).read_bytes())
    return h.hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════
# L'icône : cinq bandes de période et l'initiale dans un disque
# ═══════════════════════════════════════════════════════════════════════
def _glyphe(c, initiale):
    """Le contour de l'initiale (chemin SVG, unités de la police) et ses
    bornes, dans la police des titres, à la graisse la plus forte (≤ 800)."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.boundsPen import BoundsPen
    police = TTFont(str(police_titre(c)))
    if "fvar" in police:
        from fontTools.varLib import instancer
        axes = {a.axisTag: a for a in police["fvar"].axes}
        reglage = {t: a.defaultValue for t, a in axes.items()}
        if "wght" in axes:
            reglage["wght"] = min(800, axes["wght"].maxValue)
        police = instancer.instantiateVariableFont(police, reglage)
    cmap = police.getBestCmap()
    nom = cmap.get(ord(initiale)) or cmap.get(ord(initiale.upper()))
    if not nom:
        raise ValueError("la police des titres n'a pas la lettre « %s »" % initiale)
    glyphes = police.getGlyphSet()
    stylo = SVGPathPen(glyphes)
    glyphes[nom].draw(stylo)
    bornes = BoundsPen(glyphes)
    glyphes[nom].draw(bornes)
    tampon = io.BytesIO()
    police.flavor = None
    police.save(tampon)
    return stylo.getCommands(), bornes.bounds, police["head"].unitsPerEm, tampon.getvalue(), nom


def _geometrie(cote, forme):
    """Le rayon des coins et le rayon du disque, pour un côté donné."""
    coins = round(cote * 0.22) if forme == "arrondie" else 0
    # dans la maskable, le disque reste dans la zone sûre (rayon 40 %)
    disque = cote * (0.27 if forme == "pleine" and cote >= 512 else 0.31)
    if cote <= 32:
        disque = cote * 0.36   # en favicon, la lettre avant les bandes
    return coins, disque


def svg_icone(c, cote=512, forme="arrondie"):
    """L'icône en SVG : rien que des tracés (la lettre est un contour), si
    bien qu'elle se dessine pareil partout, sans police à charger."""
    k = couleurs(c)
    ini = identite(c)["initiale"]
    chemin, (x0, y0, x1, y1), upm, _, _ = _glyphe(c, ini)
    coins, r = _geometrie(cote, forme)
    # la lettre occupe 1,15 r en hauteur, centrée sur ses propres bornes
    echelle = (1.15 * r) / max(y1 - y0, 1)
    largeur = (x1 - x0) * echelle
    if largeur > 1.4 * r:
        echelle *= 1.4 * r / largeur
    cx = cy = cote / 2
    tx = cx - (x0 + x1) / 2 * echelle
    ty = cy + (y0 + y1) / 2 * echelle
    bande = cote / 5
    bandes = "".join('<rect x="%.2f" y="0" width="%.2f" height="%d" fill="%s"/>'
                     % (i * bande, bande + 0.5, cote, k["p%d" % (i + 1)]) for i in range(5))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {c} {c}" width="{c}" height="{c}">'
        '<!-- fabriqué par scripts/appli.py (classe.py generer) ; empreinte {e} -->'
        '<defs><clipPath id="forme"><rect width="{c}" height="{c}" rx="{rx}"/></clipPath></defs>'
        '<g clip-path="url(#forme)">{bandes}'
        '<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="{feuille}"/>'
        '<path transform="translate({tx:.2f} {ty:.2f}) scale({s:.5f} {ms:.5f})" fill="{sapin}" d="{d}"/>'
        '</g></svg>\n'
    ).format(c=cote, e=empreinte_icones(c), rx=coins, bandes=bandes, cx=cx, cy=cy, r=r,
             feuille=k["feuille"], tx=tx, ty=ty, s=echelle, ms=-echelle, sapin=k["sapin"], d=chemin)


def _png(c, cote, forme, empreinte):
    """L'icône en PNG, dessinée par Pillow à quatre fois sa taille puis
    réduite (bords lisses), l'empreinte inscrite dans un bloc tEXt."""
    from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
    k = couleurs(c)
    ini = identite(c)["initiale"]
    _, (x0, y0, x1, y1), upm, ttf, _ = _glyphe(c, ini)
    f = 4
    C = cote * f
    coins, r = _geometrie(cote, forme)
    coins, r = coins * f, r * f
    def rgb(h):
        return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    img = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bande = C / 5
    for i in range(5):
        d.rectangle([round(i * bande), 0, round((i + 1) * bande), C], fill=rgb(k["p%d" % (i + 1)]))
    cx = cy = C / 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(k["feuille"]))
    # la lettre : même taille que dans le SVG (1,15 r de haut, ≤ 1,4 r de large)
    taille_em = (1.15 * r) / max(y1 - y0, 1) * upm
    if (x1 - x0) * taille_em / upm > 1.4 * r:
        taille_em *= 1.4 * r / ((x1 - x0) * taille_em / upm)
    police = ImageFont.truetype(io.BytesIO(ttf), max(1, round(taille_em)))
    bx0, by0, bx1, by1 = d.textbbox((0, 0), ini, font=police, anchor="ls")
    d.text((cx - (bx0 + bx1) / 2, cy - (by0 + by1) / 2), ini, font=police,
           fill=rgb(k["sapin"]), anchor="ls")
    if coins:
        masque = Image.new("L", (C, C), 0)
        ImageDraw.Draw(masque).rounded_rectangle([0, 0, C - 1, C - 1], radius=coins, fill=255)
        img.putalpha(masque)
    img = img.resize((cote, cote), Image.LANCZOS)
    if forme == "pleine":
        img = img.convert("RGB")   # iOS noircit la transparence
    info = PngImagePlugin.PngInfo()
    info.add_text("encrine-empreinte", empreinte)
    sortie = io.BytesIO()
    img.save(sortie, "PNG", pnginfo=info, optimize=True)
    return sortie.getvalue(), img


def _png_info_texte(img, empreinte):
    from PIL import PngImagePlugin
    info = PngImagePlugin.PngInfo()
    info.add_text("encrine-empreinte", empreinte)
    sortie = io.BytesIO()
    img.save(sortie, "PNG", pnginfo=info, optimize=True)
    return sortie.getvalue()


def icones_du_theme(c, it):
    """Les icônes que dessine le thème : rendues une fois par forme, à
    1024 px, puis réduites à chaque taille."""
    try:
        from PIL import Image
        import icone_du_theme
    except ImportError as e:
        print("⚠ icônes de l'appli non refaites (%s) : pip install pillow" % e.name)
        return False
    if not icone_du_theme.chrome():
        print("⚠ icônes de l'appli non refaites : l'icône du thème se rend avec Chromium "
              "(CHROME_BIN, google-chrome, ou celui de Playwright)")
        return False
    e = icone_du_theme.empreinte(*it)
    rendus, svg = icone_du_theme.images(*it)
    ICONES.mkdir(exist_ok=True)
    (SITE / SVG).write_text(svg, encoding="utf-8")

    def taille(nom, cote):
        img = rendus[nom].resize((cote, cote), Image.LANCZOS)
        return img.convert("RGB") if nom in ("pleine", "maskable") else img   # iOS noircit la transparence
    for rel, cote, forme in PNG:
        nom = "maskable" if "maskable" in rel else ("petite" if cote <= 48 else forme)
        (SITE / rel).write_bytes(_png_info_texte(taille(nom, cote), e))
    petites = [taille("petite", cote) for cote in (16, 32, 48)]
    petites[-1].save(SITE / ICO, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)],
                     append_images=petites[:-1])
    return True


def icones(c):
    """Écrit les icônes de la classe ; rend False (et le dit) s'il manque
    Pillow, fontTools ou brotli (ou Chromium, pour l'icône d'un thème) — les
    icônes existantes restent alors."""
    it = icone_theme(c)
    if it:
        return icones_du_theme(c, it)
    try:
        import PIL  # noqa: F401
        import fontTools  # noqa: F401
        import brotli  # noqa: F401
    except ImportError as e:
        print("⚠ icônes de l'appli non refaites (%s) : pip install pillow fonttools brotli" % e.name)
        return False
    e = empreinte_icones(c)
    ICONES.mkdir(exist_ok=True)
    (SITE / SVG).write_text(svg_icone(c), encoding="utf-8")
    petites = []
    for rel, cote, forme in PNG:
        donnees, img = _png(c, cote, forme, e)
        (SITE / rel).write_bytes(donnees)
    for cote in (16, 32, 48):
        petites.append(_png(c, cote, "arrondie", e)[1])
    petites[-1].save(SITE / ICO, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)],
                     append_images=petites[:-1])
    return True


def _png_info(chemin):
    """(largeur, hauteur, empreinte) d'un PNG, sans Pillow."""
    b = chemin.read_bytes()
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    larg, haut = struct.unpack(">II", b[16:24])
    i, empreinte = 8, None
    while i < len(b):
        n, = struct.unpack(">I", b[i:i + 4])
        genre = b[i + 4:i + 8]
        if genre == b"tEXt":
            cle, _, val = b[i + 8:i + 8 + n].partition(b"\0")
            if cle == b"encrine-empreinte":
                empreinte = val.decode()
        elif genre == b"zTXt":
            cle, _, val = b[i + 8:i + 8 + n].partition(b"\0")
            if cle == b"encrine-empreinte":
                empreinte = zlib.decompress(val[1:]).decode()
        i += 12 + n
    return larg, haut, empreinte


# ═══════════════════════════════════════════════════════════════════════
# Le manifeste
# ═══════════════════════════════════════════════════════════════════════
def manifeste(c):
    i = identite(c)
    k = couleurs(c)
    icones_ = [{"src": rel, "sizes": "%dx%d" % (cote, cote), "type": "image/png",
                "purpose": "maskable" if "maskable" in rel else "any"}
               for rel, cote, _ in PNG if cote >= 192]
    icones_.append({"src": SVG, "sizes": "any", "type": "image/svg+xml", "purpose": "any"})
    # Pas d'`id` : il vaudrait l'adresse de départ, mais résolu contre la
    # seule origine (« ./ » donnerait https://<propriétaire>.github.io/), si
    # bien que deux classes d'un même domaine seraient une seule appli.
    m = {
        "name": i["nom"],
        "short_name": i["nom_court"],
        "description": c.get("accroche") or c["projet"],
        "lang": "fr",
        "dir": "ltr",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "orientation": "any",
        "theme_color": k["feuille"],      # la couleur du bandeau
        "background_color": k["papier"],  # l'écran de lancement
        "categories": ["education"],
        "icons": icones_,
    }
    return json.dumps(m, ensure_ascii=False, indent=2) + "\n"


# ═══════════════════════════════════════════════════════════════════════
# Le service worker
# ═══════════════════════════════════════════════════════════════════════
def _polices_et_motifs(c):
    """Les fichiers de la charte que les pages chargent : polices du socle
    et de la marque, polices et motifs du thème."""
    out = sorted(p.relative_to(SITE).as_posix() for p in (CHARTE / "polices").glob("*.woff2"))
    # celles de la marque Encrine (marque/marque.css, la vue d'impression)
    out += sorted(p.relative_to(SITE).as_posix() for p in (SITE / "marque" / "polices").glob("*.woff2"))
    dossier = CHARTE / "themes" / c["theme"]
    out += sorted(p.relative_to(SITE).as_posix() for p in dossier.rglob("*")
                  if p.is_file() and p.suffix in (".woff2", ".svg", ".png", ".webp"))
    return out


def precache(c):
    """Ce que l'appli met en cache à l'installation : l'application, ses
    polices et ses icônes, classe.json, et les documents Markdown du menu.
    Ni les PDF, ni les cahiers, ni les photographies : ceux-là entrent en
    cache quand on les ouvre."""
    liste = ["./", "index.html", "imprimer.html", "app.css", "impression.css", "app.js",
             "appli.js", "commun.js", "modele.js", "gabarits.js", "charte/gabarits.js",
             "classe.js", "classe.json", "marked.min.js",
             "manifest.webmanifest", "charte/charte.css", "marque/marque.css", "charte/icones.svg",
             "favicon.ico", SVG] + [rel for rel, _, _ in PNG]
    liste += _polices_et_motifs(c)
    liste += [d["md"] for d in c["documents"] if d.get("md")]
    return liste


def _source(rel, site):
    """Le fichier d'un chemin publié. Dans le dépôt, content/ est la racine
    (les documents y sont copiés au déploiement) ; dans un site assemblé,
    tout est sous le site."""
    if site is None and rel.startswith("content/"):
        return RACINE / rel[len("content/"):]
    return (site or SITE) / rel


def version(c, site=None):
    """L'empreinte de tout ce qui se publie (hors PDF, fabriqués au
    déploiement, et hors sw.js lui-même) : elle change à chaque publication
    qui change quelque chose, et avec elle le cache."""
    racine = site or SITE
    h = hashlib.sha256()
    fichiers = sorted(p for p in racine.rglob("*") if p.is_file()
                      and p.relative_to(racine).parts[0] not in ("pdf", "content")
                      and p.name != "sw.js" and "__pycache__" not in p.parts)
    for p in fichiers:
        rel = p.relative_to(racine).as_posix()
        h.update(rel.encode() + b"\0")
        donnees = p.read_bytes()
        if rel in PAGES:   # la version qu'y écrit estampiller ne compte pas
            donnees = ESTAMPE.sub(b"", donnees)
        h.update(donnees)
    for d in c["documents"]:
        if d.get("md"):
            f = _source(d["md"], site)
            h.update(d["md"].encode() + b"\0")
            h.update(f.read_bytes() if f.is_file() else b"?")
    return h.hexdigest()[:12]


def service_worker(c, v):
    modele = MODELE_SW.read_text(encoding="utf-8")
    return (modele
            .replace("'@VERSION@'", json.dumps(v))
            .replace("['@PRECACHE@']", json.dumps(precache(c), ensure_ascii=False, indent=2)))


VERSION_SW = re.compile(r'^var VERSION = "([0-9a-f]+)";$', re.M)

# Les pages dont estampiller versionne les scripts et les feuilles de style.
PAGES = ("index.html", "imprimer.html")
ESTAMPE = re.compile(rb"\?v=[0-9a-f]+")
BALISE = re.compile(r"<(script|link)\b[^>]*>", re.I)
ATTRIBUT = re.compile(r'\b(src|href)="([^"]*)"', re.I)
DISTANTE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|/|#)", re.I)


def versionner(html, v):
    """Chaque <script src> et <link rel=stylesheet href> locaux de la page,
    suivis de ?v=<v> (une version déjà écrite est remplacée)."""
    def balise(m):
        tag = m.group(0)
        if m.group(1).lower() == "link" and not re.search(r'\brel="stylesheet"', tag, re.I):
            return tag
        def attr(a):
            if (m.group(1).lower() == "script") != (a.group(1).lower() == "src"):
                return a.group(0)
            adresse = re.sub(r"\?v=[0-9a-f]+$", "", a.group(2))
            if not adresse or DISTANTE.match(adresse) or "?" in adresse:
                return a.group(0)
            return '%s="%s?v=%s"' % (a.group(1), adresse, v)
        return ATTRIBUT.sub(attr, tag)
    return BALISE.sub(balise, html)


# ═══════════════════════════════════════════════════════════════════════
# generer, verifier, estampiller
# ═══════════════════════════════════════════════════════════════════════
def fabriquer(c):
    faites = icones(c)
    MANIFESTE.write_text(manifeste(c), encoding="utf-8")
    SW.write_text(service_worker(c, version(c)), encoding="utf-8")
    print("appli : manifest.webmanifest, sw.js%s écrits" % (" et les icônes" if faites else ""))


def estampiller(site, c):
    """Sur le site assemblé (déploiement) : la version de sw.js recalculée
    sur ce qui sera publié, documents de content/ compris, et la même
    version sur chaque script et chaque feuille de style d'index.html et
    d'imprimer.html (`app.js?v=<version>`). Une page ne demande ainsi que
    les scripts de sa publication : ni le cache HTTP (max-age=600 sur
    GitHub Pages) ni la copie du service worker ne peuvent lui rendre ceux
    d'une autre. Rien de cela n'est écrit dans le dépôt."""
    site = pathlib.Path(site)
    sw = site / "sw.js"
    texte = sw.read_text(encoding="utf-8")
    v = version(c, site)
    sw.write_text(VERSION_SW.sub('var VERSION = "%s";' % v, texte, count=1), encoding="utf-8")
    for nom in PAGES:
        page = site / nom
        if page.is_file():
            page.write_text(versionner(page.read_text(encoding="utf-8"), v), encoding="utf-8")
    print("sw.js, %s : version %s" % (", ".join(PAGES), v))


def anomalies(c):
    """(anomalies, avertissements) : manifeste, icônes et sw.js présents,
    cohérents (chemins relatifs, tailles) et à jour."""
    a, w = [], []
    import yaml
    propre = yaml.safe_load((RACINE / "classe.yml").read_text(encoding="utf-8")).get("appli") or {}
    if not isinstance(propre, dict):
        propre = {"(pas un bloc)": None}
    for cle in sorted(set(propre) - {"nom", "nom_court", "initiale"}):
        a.append("appli.%s : clé inconnue (nom, nom_court, initiale)" % cle)
    if len(identite(c)["nom_court"]) > 15:
        w.append("appli : le nom court « %s » sera coupé sous l'icône — `appli: {nom_court: …}` "
                 "dans classe.yml (une douzaine de lettres)" % identite(c)["nom_court"])
    try:
        attendu = manifeste(c)
    except ValueError as e:
        return ["appli : %s" % e], w
    if not MANIFESTE.is_file() or MANIFESTE.read_text(encoding="utf-8") != attendu:
        a.append("site/manifest.webmanifest périmé : relancer  python3 scripts/classe.py generer")
    m = json.loads(attendu)
    if "id" in m:
        a.append("manifest : pas d'`id` — résolu contre l'origine seule, il confondrait "
                 "les classes publiées sur un même domaine")
    for cle in ("start_url", "scope"):
        if m[cle] != "./":
            a.append("manifest : %s « %s » — relatif au dossier du site, « ./ »" % (cle, m[cle]))
    for ic in m["icons"]:
        if re.match(r"^(/|[a-z]+:)", ic["src"]):
            a.append("manifest : l'icône « %s » n'est pas un chemin relatif" % ic["src"])
    e = empreinte_icones(c)
    for rel, cote, forme in PNG:
        f = SITE / rel
        if not f.is_file():
            a.append("site/%s manque : relancer  python3 scripts/classe.py generer "
                     "(Pillow, fontTools et brotli)" % rel)
            continue
        info = _png_info(f)
        if not info or info[:2] != (cote, cote):
            a.append("site/%s : %s au lieu de %d×%d px" % (rel, info and "%d×%d" % info[:2], cote, cote))
        elif info[2] != e:
            a.append("site/%s périmée (le thème, son icône, l'initiale ou la police ont changé) : "
                     "relancer  python3 scripts/classe.py generer" % rel)
    svg = SITE / SVG
    if not svg.is_file() or ("empreinte %s" % e) not in svg.read_text(encoding="utf-8"):
        a.append("site/%s manque ou est périmée : relancer  python3 scripts/classe.py generer" % SVG)
    if not (SITE / ICO).is_file():
        a.append("site/%s manque : relancer  python3 scripts/classe.py generer" % ICO)
    for rel in precache(c):
        if rel != "./" and not _source(rel, None).is_file():
            a.append("sw.js met en cache %s, qui n'existe pas" % rel)
    if not SW.is_file():
        a.append("site/sw.js manque : relancer  python3 scripts/classe.py generer")
    else:
        texte = SW.read_text(encoding="utf-8")
        trouve = VERSION_SW.search(texte)
        v = version(c)
        if not trouve or service_worker(c, trouve.group(1)) != texte:
            a.append("site/sw.js périmé (modèle ou liste du cache) : relancer  "
                     "python3 scripts/classe.py generer")
        elif trouve.group(1) != v:
            w.append("site/sw.js : version %s, le contenu est en %s — le déploiement la "
                     "recalcule ; relancer  python3 scripts/classe.py generer" % (trouve.group(1), v))
    for page in ("index.html", "imprimer.html"):
        html = (SITE / page).read_text(encoding="utf-8")
        if 'rel="manifest" href="manifest.webmanifest"' not in html:
            a.append("site/%s ne lie pas le manifeste (manifest.webmanifest)" % page)
        if ESTAMPE.search(html.encode()):
            a.append("site/%s : une version en dur (?v=…) — c'est le déploiement qui "
                     "l'écrit (classe.py estampiller)" % page)
    index = (SITE / "index.html").read_text(encoding="utf-8")
    if 'id="garde-fou"' not in index or index.find('id="garde-fou"') > index.find("<script src="):
        a.append("site/index.html : il manque le garde-fou (<script id=\"garde-fou\">), "
                 "avant les autres scripts — sans lui, une erreur laisse « Chargement… » à l'écran")
    for attendu_ in ('src="appli.js"', 'rel="apple-touch-icon" href="icones/apple-touch-icon.png"',
                     'name="apple-mobile-web-app-capable"', 'name="apple-mobile-web-app-title"'):
        if attendu_ not in index:
            a.append("site/index.html : il manque %s" % attendu_)
    return a, w
