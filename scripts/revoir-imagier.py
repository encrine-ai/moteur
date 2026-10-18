# -*- coding: utf-8 -*-
"""Assemble les cartes d'une période telles qu'elles seront imprimées.

scripts/verifier-imagier.py contrôle ce qui se mesure — l'espèce, les
crédits, les bandes blanches. Le reste ne se voit qu'à l'œil : un second
animal au fond, une bête vue de dessus, un sujet noyé dans le décor. Cette
planche montre les dix-huit images d'une période **après recadrage**, donc
telles qu'elles paraîtront sur les cartes, avec leur nom dessous.

À regarder après toute moisson, avant de publier.

Usage : python3 scripts/revoir-imagier.py [periode ...]   (défaut : les cinq)
Sortie : <DOSSIER>/revue-periode-N.jpg
         (DOSSIER : variable d'environnement REVUE_DIR, /tmp par défaut)
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ICI, "..", "site", "imagier", "img")
DOSSIER = os.environ.get("REVUE_DIR", "/tmp")
LARGEUR, HAUTEUR, LEGENDE = 380, 260, 34

credits = json.load(open(os.path.join(IMG, "credits.json"), encoding="utf-8"))
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)

periodes = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5]
for p in periodes:
    cartes = sorted((v for v in credits.values() if v["periode"] == p),
                    key=lambda v: (v["groupe"], v["nom"]))
    if not cartes:
        print("période %d : aucune carte" % p)
        continue
    colonnes = 6
    lignes = (len(cartes) + colonnes - 1) // colonnes
    img = Image.new("RGB", (colonnes * LARGEUR, lignes * (HAUTEUR + LEGENDE)), "white")
    d = ImageDraw.Draw(img)
    for i, v in enumerate(cartes):
        x, y = (i % colonnes) * LARGEUR, (i // colonnes) * (HAUTEUR + LEGENDE)
        chemin = os.path.join(IMG, v["fichier"])
        if os.path.exists(chemin):
            im = Image.open(chemin).convert("RGB")
            im.thumbnail((LARGEUR - 8, HAUTEUR - 8), Image.LANCZOS)
            img.paste(im, (x + (LARGEUR - im.width) // 2, y + (HAUTEUR - im.height) // 2))
        else:
            d.text((x + 10, y + 10), "fichier absent", fill="#c00", font=F)
        d.rectangle([x, y, x + LARGEUR - 1, y + HAUTEUR - 1], outline="#999")
        d.text((x + 6, y + HAUTEUR + 6), v["nom"], fill="black", font=F)
    chemin = os.path.join(DOSSIER, "revue-periode-%d.jpg" % p)
    img.save(chemin, "JPEG", quality=88)
    print("période %d : %d cartes → %s" % (p, len(cartes), chemin))
