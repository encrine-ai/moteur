# -*- coding: utf-8 -*-
"""L'aperçu de lien : ce que montrent une messagerie, un réseau ou un moteur
de recherche quand on y colle l'adresse du site de la classe.

Les messageries (iMessage, WhatsApp, Signal, Slack…) n'exécutent pas le
JavaScript : elles lisent le <head> STATIQUE de index.html. Ce module y
écrit donc, entre les marqueurs `<!-- apercu:debut -->` et
`<!-- apercu:fin -->` :

- le <title> « Encrine – <projet> » (celui de l'accueil ; app.js donne aux
  autres routes « <page> · Encrine – <projet> ») et la meta description ;
- les balises Open Graph (og:type, og:locale, og:site_name, og:title,
  og:description, og:url, og:image et ses dimensions et son texte) et
  Twitter (summary_large_image).

La description est l'accroche de classe.yml, suivie de « La classe de
<signature>. » si l'enseignant signe sa classe.

Deux temps :

- `classe.py generer` écrit le bloc en adresses RELATIVES (og:url « ./ »,
  og:image « partage.png ») : le dépôt ne connaît pas son adresse publique ;
  `classe.py verifier` contrôle qu'il est à jour ;
- `classe.py estampiller <site> --adresse <url>` (le déploiement, avec
  l'adresse que donne actions/configure-pages) fabrique l'image de partage
  <site>/partage.png puis réécrit le bloc du site assemblé en adresses
  ABSOLUES, comme l'exige Open Graph. Sans adresse, le bloc reste relatif et
  un avertissement le dit.

L'image de partage, 1200 × 630 : le haut de l'accueil du mini-site, rendu
par Chromium (celui des PDF) à 1200 × 630, sans l'invitation à installer ni
le service worker (appli.js n'est pas chargé), avec une discrète signature
« Conçu avec Encrine ». Un thème peut dessiner la sienne : un gabarit
`partage` dans son gabarits.js (GS.theme({ partage: function (m) { … } })),
qui rend le HTML d'une vignette de 1200 × 630. Elle est compressée (palette
de couleurs, Pillow) pour rester sous 300 Ko. Skill site-et-calendrier,
« L'aperçu de lien ».
"""
import hashlib
import html
import os
import pathlib
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import functools
import http.server

import typographie

RACINE = pathlib.Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
INDEX = "index.html"
IMAGE = "partage.png"
LARGEUR, HAUTEUR = 1200, 630
POIDS_MAX = 300 * 1024
MARQUE = "Encrine"
SIGNATURE = "Conçu avec Encrine"
DEBUT, FIN = "<!-- apercu:debut -->", "<!-- apercu:fin -->"
BLOC = re.compile(r"[ \t]*%s.*?%s" % (re.escape(DEBUT), re.escape(FIN)), re.S)
# La description si la classe n'a pas d'accroche.
DESCRIPTION = ("Les progressions, la programmation et les évaluations de l'année, "
               "aux dates des vacances de la classe, à consulter et à imprimer en PDF.")


def titre(c):
    return "%s – %s" % (MARQUE, c["projet"])


def de(nom):
    """« de Mme Martin », « d’Anaïs » (comme readme.py)."""
    return ("d’" if re.match(r"[AEIOUYÀÂÉÈÊËÎÏÔÛÙÜaeiouyàâéèêëîïôûùü]", nom) else "de ") + nom


def description(c):
    texte = " ".join(str(c.get("accroche") or "").split()) or DESCRIPTION
    signature = ((c.get("enseignant") or {}).get("signature") or "").strip()
    if signature:
        texte = "%s%s La classe %s." % (texte, "" if texte.endswith((".", "!", "?", "…")) else ".", de(signature))
    return texte


def texte_image(c):
    """og:image:alt : ce que montre l'image, pour qui ne la voit pas."""
    return "L’accueil du site de la classe « %s » : %s, %s." % (
        c["projet"], c["niveau"]["libelle"], c["annee"])


def normaliser(adresse):
    """« https://encrine.ai/tour-du-monde » → « https://encrine.ai/tour-du-monde/ »."""
    if not adresse:
        return None
    if not re.match(r"^https?://[^/\s]+", adresse):
        raise ValueError("l'adresse « %s » n'est pas une adresse web (https://…)" % adresse)
    return adresse if adresse.endswith("/") else adresse + "/"


def bloc(c, adresse=None, image=IMAGE):
    """Le bloc de balises, indenté pour le <head> de index.html."""
    adresse = normaliser(adresse)
    url = adresse or "./"
    img = (adresse or "") + image
    e = lambda t: html.escape(t, quote=True)
    f = typographie.francais
    t, d, alt = e(f(titre(c))), e(f(description(c))), e(f(texte_image(c)))
    lignes = [
        DEBUT,
        "<!-- L'aperçu de lien (scripts/apercu.py) : écrit par classe.py generer,",
        "     en adresses absolues au déploiement (estampiller --adresse). Ne pas",
        "     retoucher à la main : les messageries lisent ces balises sans JavaScript. -->",
        "<title>%s</title>" % t,
        '<meta name="description" content="%s">' % d,
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="fr_FR">',
        '<meta property="og:site_name" content="%s">' % MARQUE,
        '<meta property="og:title" content="%s">' % t,
        '<meta property="og:description" content="%s">' % d,
        '<meta property="og:url" content="%s">' % e(url),
        '<meta property="og:image" content="%s">' % e(img),
        '<meta property="og:image:type" content="image/png">',
        '<meta property="og:image:width" content="%d">' % LARGEUR,
        '<meta property="og:image:height" content="%d">' % HAUTEUR,
        '<meta property="og:image:alt" content="%s">' % alt,
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % t,
        '<meta name="twitter:description" content="%s">' % d,
        '<meta name="twitter:image" content="%s">' % e(img),
        '<meta name="twitter:image:alt" content="%s">' % alt,
    ]
    if adresse:
        lignes.append('<link rel="canonical" href="%s">' % e(adresse))
    lignes.append(FIN)
    return "\n".join("  " + l for l in lignes)


def poser(texte, b):
    """index.html avec le bloc `b` à la place de l'ancien (ValueError s'il n'y en a pas)."""
    if not BLOC.search(texte):
        raise ValueError("site/index.html n'a pas les marqueurs %s … %s dans son <head>" % (DEBUT, FIN))
    return BLOC.sub(lambda _: b, texte, count=1)


def sans_bloc(texte):
    """index.html sans le bloc fabriqué : ce que contrôle la chasse aux données
    de classe écrites en dur (le bloc, lui, les porte par construction)."""
    return BLOC.sub(lambda m: "\n" * m.group(0).count("\n"), texte)


# ═══════════════════════════════════════════════════════════════════════
# generer, verifier
# ═══════════════════════════════════════════════════════════════════════
def ecrire(c):
    f = SITE / INDEX
    texte = f.read_text(encoding="utf-8")
    nouveau = poser(texte, bloc(c))
    if nouveau != texte:
        f.write_text(nouveau, encoding="utf-8")
    print("site/index.html : titre « %s » et aperçu de lien" % titre(c))


def anomalies(c):
    a = []
    texte = (SITE / INDEX).read_text(encoding="utf-8")
    if not BLOC.search(texte):
        a.append("site/index.html : il manque le bloc de l'aperçu de lien (%s … %s)" % (DEBUT, FIN))
    elif poser(texte, bloc(c)) != texte:
        a.append("site/index.html : le titre ou l'aperçu de lien est périmé — relancer  "
                 "python3 scripts/classe.py generer")
    if len(re.findall(r"<title>", texte)) != 1:
        a.append("site/index.html : il faut un seul <title>, celui du bloc de l'aperçu")
    return a


# ═══════════════════════════════════════════════════════════════════════
# estampiller : l'image, puis les adresses absolues
# ═══════════════════════════════════════════════════════════════════════
def chromium():
    """Le Chromium des PDF : CHROME_BIN, google-chrome (le runner GitHub), ou
    celui de Playwright dans une session Claude Code."""
    if os.environ.get("CHROME_BIN"):
        return os.environ["CHROME_BIN"]
    for nom in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(nom):
            return shutil.which(nom)
    for f in sorted(pathlib.Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome")):
        return str(f)
    return None


# La page de capture : l'accueil, sans appli.js (ni service worker, ni
# invitation à installer), cadré à 1200 × 630, signé « Conçu avec Encrine » ;
# le gabarit `partage` du thème, s'il en a un, remplace l'accueil.
CAPTURE = """
<style>
  html, body { width: %(l)dpx; height: %(h)dpx; overflow: hidden !important; }
  body { margin: 0; }
  .saut, [data-menu-panneau] { display: none !important; }
  .apercu-vignette { position: fixed; inset: 0; width: %(l)dpx; height: %(h)dpx; overflow: hidden; z-index: 2147483000; }
  .apercu-signature {
    position: fixed; right: 20px; bottom: 18px; z-index: 2147483647;
    padding: 6px 14px; border-radius: 999px;
    font: 600 17px/1.2 var(--police-texte, system-ui, sans-serif);
    color: #fff; background: rgba(20, 22, 30, .62); letter-spacing: .01em;
  }
</style>
<script>
  document.addEventListener('encrine:page', function () {
    var theme = GS.gabarits && GS.gabarits.theme && GS.gabarits.theme.partage;
    if (theme) {
      var v = document.createElement('div');
      v.className = 'apercu-vignette';
      v.innerHTML = theme(GS.modele());
      document.body.appendChild(v);
    }
    window.scrollTo(0, 0);
    var s = document.createElement('div');
    s.className = 'apercu-signature';
    s.textContent = %(signature)s;
    document.body.appendChild(s);
    document.documentElement.dataset.apercu = theme ? 'theme' : 'accueil';
  }, { once: true });
</script>
"""


def _page_capture(index):
    texte = re.sub(r'[ \t]*<script\b[^>]*\bsrc="appli\.js[^"]*"[^>]*>\s*</script>\n?', "", index)
    texte = re.sub(r'[ \t]*<link rel="manifest"[^>]*>\n?', "", texte)
    import json
    ajout = CAPTURE % {"l": LARGEUR, "h": HAUTEUR, "signature": json.dumps(SIGNATURE)}
    return texte.replace("</body>", ajout + "</body>", 1)


class _Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def _servir(site):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Silencieux, directory=str(site)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _compresser(png):
    """Une palette de 256 couleurs (Pillow), si l'image dépasse le poids voulu
    ou si elle y gagne ; sans Pillow, l'image reste telle quelle."""
    try:
        from PIL import Image
    except ImportError:
        return "Pillow absent : image ni recadrée ni compressée (pip install pillow)"
    im = Image.open(png).convert("RGB")
    if im.size != (LARGEUR, HAUTEUR):  # la bande de la barre fantôme, en bas
        im = im.crop((0, 0, LARGEUR, HAUTEUR))
        im.save(png)
    tmp = png.with_suffix(".tmp.png")
    # 256 couleurs, puis moins tant que l'image dépasse le poids voulu (une
    # page chargée de photographies)
    for couleurs in (256, 192, 128, 96, 64):
        im.quantize(colors=couleurs, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(
            tmp, optimize=True)
        if tmp.stat().st_size <= POIDS_MAX:
            break
    if tmp.stat().st_size < png.stat().st_size:
        tmp.replace(png)
    else:
        tmp.unlink()
    return None


def _drapeaux(chrome, profil):
    return [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--no-proxy-server",
            "--force-device-scale-factor=1", "--user-data-dir=" + profil]


def _ecart(chrome, profil):
    """Ce que le nouveau mode sans tête de Chrome retranche de --window-size
    pour sa barre fantôme (87 px en Chromium 141 ; 0 pour headless_shell) :
    on le mesure, pour que la page voie bien 630 px de haut."""
    sonde = pathlib.Path(profil) / "sonde.html"
    sonde.write_text("<html><body><script>document.body.textContent = 'VH=' + innerHeight</script></body></html>")
    r = subprocess.run(_drapeaux(chrome, profil) + ["--window-size=%d,%d" % (LARGEUR, HAUTEUR), "--dump-dom",
                                                     sonde.as_uri()],
                       capture_output=True, text=True, timeout=60)
    m = re.search(r"VH=(\d+)", r.stdout)
    return max(0, HAUTEUR - int(m.group(1))) if m else 0


def image(site, c):
    """<site>/partage.png, ou None (avec la raison) si Chromium manque."""
    site = pathlib.Path(site)
    chrome = chromium()
    if not chrome:
        return None, "Chromium introuvable (CHROME_BIN) : pas d'image de partage"
    capture = site / "_apercu.html"
    sortie = site / IMAGE
    capture.write_text(_page_capture((site / INDEX).read_text(encoding="utf-8")), encoding="utf-8")
    srv = _servir(site)
    try:
        with tempfile.TemporaryDirectory() as profil:
            ecart = _ecart(chrome, profil)
            subprocess.run(_drapeaux(chrome, profil) + [
                            "--window-size=%d,%d" % (LARGEUR, HAUTEUR + ecart), "--virtual-time-budget=10000",
                            "--screenshot=%s" % sortie,
                            "http://127.0.0.1:%d/_apercu.html#/accueil" % srv.server_address[1]],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    finally:
        srv.shutdown()
        capture.unlink()
    if not sortie.is_file() or not sortie.stat().st_size:
        return None, "Chromium n'a pas produit %s" % sortie
    note = _compresser(sortie)
    return sortie, note


def estampiller(site, c, adresse=None):
    """Sur le site assemblé : l'image de partage, puis le bloc en adresses
    absolues. Renvoie la liste des avertissements."""
    site = pathlib.Path(site)
    w = []
    adresse = normaliser(adresse)
    img, note = image(site, c)
    if note:
        w.append(note)
    nom = IMAGE
    if img:
        poids = img.stat().st_size
        print("%s : %d × %d, %d Ko" % (img, LARGEUR, HAUTEUR, round(poids / 1024)))
        if poids > POIDS_MAX:
            w.append("%s pèse %d Ko (plus de %d Ko) : certaines messageries ne l'afficheront pas"
                     % (IMAGE, poids // 1024, POIDS_MAX // 1024))
        # l'empreinte dans l'adresse : une messagerie qui garde l'ancienne
        # image en cache voit une adresse nouvelle quand elle change
        nom = "%s?v=%s" % (IMAGE, hashlib.sha256(img.read_bytes()).hexdigest()[:8])
    if not adresse:
        w.append("pas d'adresse publique (--adresse https://…/) : l'aperçu de lien garde des "
                 "adresses relatives, que les messageries n'acceptent pas")
    f = site / INDEX
    f.write_text(poser(f.read_text(encoding="utf-8"), bloc(c, adresse, nom)), encoding="utf-8")
    print("index.html : aperçu de lien %s" % ("en " + adresse if adresse else "relatif"))
    for a in w:
        print("⚠ aperçu : " + a)
    return w
