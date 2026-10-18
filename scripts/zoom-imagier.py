# -*- coding: utf-8 -*-
"""Agrandit quelques photographies candidates, pour trancher entre elles.

Les planches de scripts/candidats-imagier.py servent à écarter vite ; mais
sur une vignette de 330 px, deux clichés proches se ressemblent, et l'on ne
voit ni qu'un second animal traîne au fond, ni que le grillage d'un enclos
barre l'image. Ce script rappelle les candidates retenues en grand.

Usage : python3 scripts/zoom-imagier.py <sortie.jpg> <id> [<id> ...]
        CADRE=1 applique le recadrage des cartes, pour voir ce que la carte
        montrera vraiment et non ce que le photographe a cadré
        (les identifiants sont ceux affichés sur les planches, relevés dans
        <CANDIDATS_DIR>/candidats-index.json)
"""
import io, os, ssl, sys, urllib.error, urllib.request
from PIL import Image, ImageDraw, ImageFont

CELL = int(os.environ.get("ZOOM_CELL", "520"))
# CADRE=1 montre les candidates telles que la carte les rognera : une photo
# séduisante en entier peut perdre son sujet à la coupe.
CADRE = os.environ.get("CADRE") == "1"
RATIO = 1.46            # proportion de la zone photo des cartes
HOTES = ("https://inaturalist-open-data.s3.amazonaws.com/photos",
         "https://static.inaturalist.org/photos")

cafile = "/root/.ccr/ca-bundle.crt"
ctx = ssl.create_default_context(cafile=cafile) if os.path.exists(cafile) else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "imagier-scolaire/1.0 (cartes de nomenclature pour l'école maternelle)")]
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)


def telecharge(photo_id, taille="medium"):
    """iNaturalist sert ses fichiers depuis deux hôtes et sous plusieurs
    extensions : on les essaie tous."""
    for hote in HOTES:
        for ext in ("jpeg", "jpg", "png"):
            try:
                with opener.open("%s/%s/%s.%s" % (hote, photo_id, taille, ext), timeout=45) as r:
                    return io.BytesIO(r.read())
            except urllib.error.HTTPError:
                continue
    return None


def rogne(im):
    """Le même recadrage que les cartes : le plus grand rectangle au format,
    décalé vers le haut quand il faut couper haut et bas (le sujet y est le
    plus souvent). Voir cadre() dans scripts/chercher-images-imagier.py."""
    l, h = im.size
    if l / float(h) > RATIO:
        nl = int(round(h * RATIO))
        return im.crop(((l - nl) // 2, 0, (l - nl) // 2 + nl, h))
    nh = int(round(l / RATIO))
    y = int(round((h - nh) * 0.35))
    return im.crop((0, y, l, y + nh))


if len(sys.argv) < 3:
    sys.exit(__doc__)
sortie, ids = sys.argv[1], sys.argv[2:]
colonnes = min(3, len(ids))
lignes = (len(ids) + colonnes - 1) // colonnes
img = Image.new("RGB", (CELL * colonnes, CELL * lignes), "white")
d = ImageDraw.Draw(img)
for i, pid in enumerate(ids):
    x, y = (i % colonnes) * CELL, (i // colonnes) * CELL
    flux = telecharge(pid)
    if flux:
        im = Image.open(flux).convert("RGB")
        if CADRE:
            im = rogne(im)
        im.thumbnail((CELL - 10, CELL - 10), Image.LANCZOS)
        img.paste(im, (x + (CELL - im.width) // 2, y + (CELL - im.height) // 2))
    else:
        d.text((x + 10, y + CELL // 2), "introuvable", fill="#c00", font=F)
    d.rectangle([x, y, x + CELL - 1, y + CELL - 1], outline="#999")
    d.text((x + 8, y + 6), str(pid), fill="#c00", font=F)
img.save(sortie, "JPEG", quality=90)
print(sortie)
