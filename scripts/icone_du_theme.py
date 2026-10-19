# -*- coding: utf-8 -*-
"""L'icône d'appli que dessine le thème (theme.yml, `icone:`).

L'icône de l'écran d'accueil fait partie du design system de la classe : un
thème « atlas » la veut en rose des vents gravée ou en sceau de cire, pas en
bandes de couleur. Le thème la déclare dans theme.yml :

    icone:
      svg: icone/rose.svg          # un tracé du thème (viewBox carré)
      licence: CC0-1.0             # licence et auteur du tracé
      auteur: tracé pour le thème
      fond: --feuille              # couleur ou jeton du thème (défaut --feuille)
      marge_maskable: 0.1          # Android : le motif réduit dans la zone sûre
      petite: icone/rose-petite.svg  # facultatif : la version ≤ 48 px (onglet)

ou une image libre déjà déclarée dans `images:`, recadrée en carré (pixels
de l'image source) :

    icone:
      image: images/carte-monde.jpg
      recadrage: {x: 1200, y: 290, cote: 680}
      retouche: {saturation: 2.4, contraste: 1.3}   # facultatif : raviver
                                   # une gravure pâle, lisible à 60 px
      svg: icone/medaillon.svg     # facultatif : le cadre, avec sa place
                                   # <image id="image" x= y= width= height=/>

Le SVG du thème suit les règles des motifs (ni script, ni texte, ni lien
externe) ; son seul élément <image> est la place vide `id="image"` que le
moteur remplit avec le recadrage. Un élément `id="fond"` (le fond du carré)
garde toute la surface dans la version maskable, où le reste est réduit dans
les 80 % centraux — la zone sûre qu'Android découpe en disque, en goutte ou en
carré selon le téléphone.

Le moteur rend ces SVG par Chromium (celui des PDF), à 1024 px, et Pillow les
réduit à chaque taille. Sans Chromium, `classe.py generer` le dit et garde
les icônes existantes. Sans `icone:`, l'icône reste celle du moteur (les
bandes des périodes et l'initiale, scripts/appli.py).
"""
import base64
import hashlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

CLES = {"svg", "image", "recadrage", "retouche", "fond", "marge_maskable", "petite", "licence", "auteur", "source"}
RETOUCHES = {"saturation", "contraste", "luminosite"}
MARGE_DEFAUT = 0.1
MARGE_MAX = 0.25
RENDU = 1024
# coins de l'icône « arrondie » (onglet, bureau, boîte d'installation)
COINS = 0.22
PLACE = re.compile(r"<image\b(?=[^>]*\bid=\"image\")[^>]*?/>", re.S)
INTERDITS = ((r"<script", "un script"), (r"<foreignObject", "du HTML"), (r"<text\b", "du texte"),
             (r"\bon[a-z]+\s*=", "un gestionnaire d'événement"),
             (r"(?:xlink:)?href\s*=\s*\"(?!#)", "un lien externe"), (r"url\(\s*['\"]?(?!#)", "une url() externe"),
             (r"@import", "un @import"))


# ═══════════════════════════════════════════════════════════════════════
# La déclaration
# ═══════════════════════════════════════════════════════════════════════
def declaration(manifeste):
    """Le bloc `icone:` de theme.yml (dict), ou None."""
    d = (manifeste or {}).get("icone")
    return d if isinstance(d, dict) else (None if d is None else {"(pas un bloc)": d})


def fichiers(decl):
    """Les fichiers du thème que l'icône déclare elle-même (ses SVG)."""
    return [decl[k] for k in ("svg", "petite") if isinstance((decl or {}).get(k), str)]


def _images_declarees(manifeste):
    return {e.get("fichier"): e for e in (manifeste.get("images") or []) if isinstance(e, dict)}


def _controle_svg(texte, nom, avec_image):
    a = []
    sans_place = PLACE.sub("", texte)
    for motif, quoi in INTERDITS:
        if re.search(motif, sans_place, re.I):
            a.append("icone : %s contient %s — l'icône est un tracé du thème" % (nom, quoi))
    if re.search(r"<image\b", sans_place, re.I):
        a.append("icone : %s contient une image — la seule permise est la place vide "
                 "<image id=\"image\" …/>, que le moteur remplit avec `image:`" % nom)
    place = PLACE.search(texte)
    if place and re.search(r"href\s*=", place.group(0)):
        a.append("icone : %s — la place <image id=\"image\"> reste vide (pas de href)" % nom)
    if place and not avec_image:
        a.append("icone : %s a une place d'image, mais `image:` n'est pas déclarée" % nom)
    m = re.search(r"<svg\b[^>]*\bviewBox=\"\s*([-\d.]+)[ ,]+([-\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)", texte)
    if not m:
        a.append("icone : %s sans viewBox" % nom)
    elif abs(float(m.group(3)) - float(m.group(4))) > 1e-6:
        a.append("icone : %s — viewBox %s×%s, l'icône est carrée" % (nom, m.group(3), m.group(4)))
    return a


def anomalies(dossier, manifeste, licences, couleur):
    """Les anomalies de la déclaration `icone:` (verifier-theme.py).
    `licences` : celles permises aux tracés ; `couleur(valeur)` : rgb ou None."""
    decl = declaration(manifeste)
    if decl is None:
        return []
    a = []
    for cle in sorted(set(decl) - CLES):
        a.append("icone.%s : clé inconnue (%s)" % (cle, ", ".join(sorted(CLES))))
    if not decl.get("svg") and not decl.get("image"):
        return a + ["icone : `svg:` (un tracé du thème) ou `image:` (une image de `images:`), au moins l'un"]
    images = _images_declarees(manifeste)
    if decl.get("image"):
        im = decl["image"]
        if im not in images:
            a.append("icone.image « %s » n'est pas déclarée dans `images:` (licence, auteur, source)" % im)
        r = decl.get("recadrage")
        if not (isinstance(r, dict) and set(r) == {"x", "y", "cote"}
                and all(isinstance(r[k], int) and r[k] >= 0 for k in r) and r["cote"] > 0):
            a.append("icone.recadrage : {x, y, cote} en pixels entiers de l'image (un carré)")
        elif (dossier / im).is_file():
            try:
                from PIL import Image
                larg, haut = Image.open(dossier / im).size
                if r["x"] + r["cote"] > larg or r["y"] + r["cote"] > haut:
                    a.append("icone.recadrage sort de l'image (%d×%d px)" % (larg, haut))
                elif r["cote"] < 512:
                    a.append("icone.recadrage : %d px de côté, 512 au moins (l'icône de 512 px)" % r["cote"])
            except ImportError:
                pass
    elif decl.get("recadrage") or decl.get("retouche"):
        a.append("icone.recadrage et icone.retouche demandent `image:`")
    if "retouche" in decl:
        r = decl["retouche"]
        if not (isinstance(r, dict) and r and set(r) <= RETOUCHES
                and all(isinstance(v, (int, float)) and 0.5 <= v <= 3 for v in r.values())):
            a.append("icone.retouche : {saturation, contraste, luminosite}, chacun entre 0.5 et 3 (1 : inchangé)")
    for cle in ("svg", "petite"):
        f = decl.get(cle)
        if f is None:
            continue
        if not isinstance(f, str) or not f.endswith(".svg"):
            a.append("icone.%s : un fichier .svg du dossier du thème" % cle)
            continue
        if not (dossier / f).is_file():
            a.append("icone.%s : %s n'existe pas" % (cle, f))
            continue
        texte = (dossier / f).read_text(encoding="utf-8")
        a += _controle_svg(texte, f, bool(decl.get("image")))
        if cle == "svg" and decl.get("image") and not PLACE.search(texte):
            a.append("icone : %s sert de cadre à l'image, il lui faut sa place <image id=\"image\" "
                     "x= y= width= height=/>" % f)
    if fichiers(decl):
        if decl.get("licence") not in licences:
            a.append("icone : licence « %s » du tracé ; seules %s" % (decl.get("licence"), ", ".join(sorted(licences))))
        if not decl.get("auteur"):
            a.append("icone : l'auteur du tracé manque (« tracé pour le thème », ou son auteur)")
    if "fond" in decl and couleur(decl["fond"]) is None:
        a.append("icone.fond « %s » : une couleur (#rrggbb) ou un jeton du thème (--feuille)" % decl["fond"])
    m = decl.get("marge_maskable", MARGE_DEFAUT)
    if not isinstance(m, (int, float)) or not 0 <= m <= MARGE_MAX:
        a.append("icone.marge_maskable « %s » : entre 0 et %s (part du côté, de chaque bord)" % (m, MARGE_MAX))
    return a


# ═══════════════════════════════════════════════════════════════════════
# Les SVG : la source, puis chaque forme
# ═══════════════════════════════════════════════════════════════════════
def _data(mime, octets):
    return "data:%s;base64,%s" % (mime, base64.b64encode(octets).decode())


def _recadrage(dossier, decl):
    from PIL import Image
    r = decl["recadrage"]
    im = Image.open(dossier / decl["image"]).convert("RGB")
    im = im.crop((r["x"], r["y"], r["x"] + r["cote"], r["y"] + r["cote"]))
    im = im.resize((min(RENDU, r["cote"]),) * 2, Image.LANCZOS)
    from PIL import ImageEnhance
    reglages = decl.get("retouche") or {}
    for cle, outil in (("saturation", ImageEnhance.Color), ("contraste", ImageEnhance.Contrast),
                       ("luminosite", ImageEnhance.Brightness)):
        if cle in reglages:
            im = outil(im).enhance(reglages[cle])
    t = io.BytesIO()
    im.save(t, "JPEG", quality=90, optimize=True)
    return _data("image/jpeg", t.getvalue())


def _sans_prologue(texte):
    texte = re.sub(r"<\?xml.*?\?>", "", texte, flags=re.S)
    return re.sub(r"<!DOCTYPE.*?>", "", texte, flags=re.S).strip()


def source(dossier, decl, fond, petite=False):
    """Le SVG de l'icône, autonome (l'image éventuelle incluse)."""
    f = decl.get("petite") if petite and decl.get("petite") else decl.get("svg")
    image = _recadrage(dossier, decl) if decl.get("image") else None
    if f:
        texte = _sans_prologue((dossier / f).read_text(encoding="utf-8"))
        if image:
            texte = PLACE.sub(lambda m: m.group(0)[:-2].rstrip() + ' href="%s"/>' % image, texte, count=1)
        if "xmlns=" not in texte.split(">", 1)[0]:
            texte = texte.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        return texte
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
            '<rect id="fond" width="512" height="512" fill="%s"/>'
            '<image width="512" height="512" preserveAspectRatio="xMidYMid slice" href="%s"/></svg>'
            % (fond, image))


def _avec_style(svg, css):
    return re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + "<style>%s</style>" % css, svg, count=1)


def _img(svg, x=0, y=0, cote=512):
    return '<image x="%g" y="%g" width="%g" height="%g" href="%s"/>' % (
        x, y, cote, cote, _data("image/svg+xml", svg.encode("utf-8")))


def forme(src, nom, fond, marge, empreinte=""):
    """Le SVG d'une forme, 512 de côté : « pleine » (le carré entier, que le
    système arrondit), « arrondie » (coins arrondis, transparent autour) ou
    « maskable » (le fond partout, le motif dans la zone sûre)."""
    tete = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">'
            '<!-- fabriqué par scripts/icone_du_theme.py (classe.py generer) ; empreinte %s -->' % empreinte)
    if nom == "pleine":
        return tete + _img(src) + "</svg>\n"
    if nom == "arrondie":
        return (tete + '<defs><clipPath id="coins"><rect width="512" height="512" rx="%g"/></clipPath></defs>'
                '<g clip-path="url(#coins)">%s</g></svg>\n' % (512 * COINS, _img(src)))
    if nom == "maskable":
        corps = '<rect width="512" height="512" fill="%s"/>' % fond
        if re.search(r"\bid=\"fond\"", src):
            corps += _img(_avec_style(src, "svg>:not(#fond):not(defs):not(style){display:none}"))
            motif = _avec_style(src, "#fond{display:none}")
        else:
            motif = src
        m = 512 * marge
        corps += _img(motif, m, m, 512 - 2 * m)
        return tete + corps + "</svg>\n"
    raise ValueError(nom)


# ═══════════════════════════════════════════════════════════════════════
# Le rendu
# ═══════════════════════════════════════════════════════════════════════
def chrome():
    """Chromium ou Chrome : CHROME_BIN, google-chrome, chromium, ou celui de
    Playwright (comme scripts/generer-pdf.sh)."""
    for c in (os.environ.get("CHROME_BIN"), shutil.which("google-chrome"), shutil.which("chromium"),
              shutil.which("chromium-browser")):
        if c and pathlib.Path(c).is_file():
            return c
    for racine in ("/opt/pw-browsers", os.path.expanduser("~/.cache/ms-playwright")):
        trouves = sorted(pathlib.Path(racine).glob("chromium-*/chrome-linux*/chrome"))
        if trouves:
            return str(trouves[-1])
    return None


def rendre(svg, cote=RENDU):
    """Le SVG en image Pillow RGBA de `cote` px (rendu par Chromium sans tête,
    fond transparent). La fenêtre compte une barre que la capture n'a pas :
    on la prend plus haute, puis on recadre."""
    from PIL import Image
    binaire = chrome()
    if not binaire:
        raise RuntimeError("Chromium introuvable (CHROME_BIN)")
    with tempfile.TemporaryDirectory() as tmp:
        page = pathlib.Path(tmp) / "icone.svg"
        png = pathlib.Path(tmp) / "icone.png"
        page.write_text(re.sub(r'width="512" height="512"', 'width="%d" height="%d"' % (cote, cote), svg, count=1),
                        encoding="utf-8")
        subprocess.run([binaire, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--default-background-color=00000000",
                        "--user-data-dir=%s" % (pathlib.Path(tmp) / "profil"),
                        "--window-size=%d,%d" % (cote, cote + 300), "--screenshot=%s" % png, page.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        return Image.open(png).convert("RGBA").crop((0, 0, cote, cote))


def empreinte(dossier, decl, fond):
    """Ce dont l'icône est faite : la déclaration, ses fichiers, l'image."""
    h = hashlib.sha256(b"icone-du-theme-1")
    h.update(json.dumps({**decl, "fond": fond}, sort_keys=True, default=str).encode())
    for f in fichiers(decl) + ([decl["image"]] if decl.get("image") else []):
        p = dossier / f
        h.update(p.read_bytes() if p.is_file() else b"?")
    return h.hexdigest()[:16]


def images(dossier, decl, fond):
    """{forme: image Pillow 1024 px} pour « pleine », « arrondie »,
    « maskable » et « petite » (l'arrondie de la version ≤ 48 px), et le SVG
    de l'icône (l'arrondie)."""
    marge = decl.get("marge_maskable", MARGE_DEFAUT)
    e = empreinte(dossier, decl, fond)
    src = source(dossier, decl, fond)
    svgs = {nom: forme(src, nom, fond, marge, e) for nom in ("pleine", "arrondie", "maskable")}
    svgs["petite"] = forme(source(dossier, decl, fond, petite=True), "arrondie", fond, marge, e) \
        if decl.get("petite") else svgs["arrondie"]
    rendus = {}
    for nom, svg in svgs.items():
        rendus[nom] = rendus["arrondie"] if nom == "petite" and svg is svgs["arrondie"] else rendre(svg)
    return rendus, svgs["arrondie"]
