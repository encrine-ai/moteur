# -*- coding: utf-8 -*-
"""Assemble un cahier de cartes-corpus tel qu'il s'imprimera, page par page.

Le contrôle automatique (scripts/verifier-cartes-corpus.py) sait dire qu'une
image existe et que sa licence convient. Il ne sait pas dire qu'un dessin est
illisible à la taille de la carte, ni qu'un pictogramme montre autre chose que
le mot. **Cela se regarde.** Ce script rend les pages en images, à regarder
avant de publier.

Il contrôle en outre la **pagination** : une page de garde qui déborde d'une
ligne pousse tout le cahier d'une page, ce qui ne se voit pas dans le HTML mais
gâche l'impression. Le nombre de pages attendu se calcule, et l'écart est
signalé.

    REVUE_DIR=/tmp python3 scripts/revoir-cartes-corpus.py        # les 5 cahiers
    REVUE_DIR=/tmp python3 scripts/revoir-cartes-corpus.py 1 4    # deux cahiers

Sortie : <REVUE_DIR>/cartes-corpus-pN.pdf et une image par page.
Code 1 si un cahier n'a pas le nombre de pages attendu.

Dépendances : Chromium (CHROME_BIN, sinon cherché aux emplacements usuels) et
pypdfium2 pour la conversion en images (facultatif : sans lui, seul le PDF est
produit et la pagination reste contrôlée).
"""
import math
import os
import shutil
import subprocess
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ICI, "..", "site")
# Le manifeste est du contenu de la classe : son chemin vient de classe.yml.
sys.path.insert(0, ICI)
import classe  # noqa: E402
ns = classe.manifeste("corpus")
entrees, CARTES = ns["entrees"], ns["CARTES"]
COUVERTURE = int(bool(next((m for m in classe.charger()["materiel"] if m.get("cle") == "cartes-corpus"),
                           {"couverture": True}).get("couverture")))

REVUE = os.environ.get("REVUE_DIR", "/tmp")
PORT = int(os.environ.get("PORT", "8932"))
os.makedirs(REVUE, exist_ok=True)

CHEMINS_CHROME = ("google-chrome", "chromium", "chromium-browser",
                  "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")


def chrome():
    if os.environ.get("CHROME_BIN"):
        return os.environ["CHROME_BIN"]
    for c in CHEMINS_CHROME:
        trouve = shutil.which(c) or (c if os.path.exists(c) else None)
        if trouve:
            return trouve
    raise SystemExit("Chromium introuvable — renseigner CHROME_BIN.")


def pages_attendues(p):
    """la couverture (si le cahier en a une) + 1 garde + les planches de
    cartes + les étiquettes + le tri + 1 crédits.

    Les constantes viennent de generer-cartes-corpus.py : 6 cartes par planche,
    20 étiquettes par planche."""
    n = sum(1 for _ in entrees(p))
    return COUVERTURE + 1 + 2 * math.ceil(n / 6) + math.ceil(n / 20) + 1 + 1


cibles = [int(a) for a in sys.argv[1:]] or sorted(CARTES)
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--directory", SITE],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
ennuis = []
try:
    for p in cibles:
        pdf = os.path.join(REVUE, "cartes-corpus-p%d.pdf" % p)
        subprocess.run([chrome(), "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--no-pdf-header-footer",
                        "--virtual-time-budget=30000", "--print-to-pdf=" + pdf,
                        "http://127.0.0.1:%d/cartes-corpus/periode-%d.html" % (PORT, p)],
                       stderr=subprocess.DEVNULL, check=False)
        if not os.path.exists(pdf) or os.path.getsize(pdf) == 0:
            ennuis.append("période %d : le PDF n'a pas été produit" % p)
            continue
        try:
            import pypdfium2 as pdfium
        except ImportError:
            print("période %d → %s (pypdfium2 absent : pas d'images)" % (p, pdf))
            continue
        doc = pdfium.PdfDocument(pdf)
        attendu = pages_attendues(p)
        etat = "✔" if len(doc) == attendu else "✗"
        print("%s période %d → %s : %d pages (attendu %d)"
              % (etat, p, os.path.basename(pdf), len(doc), attendu))
        if len(doc) != attendu:
            ennuis.append("période %d : %d pages au lieu de %d — une page déborde "
                          "(la garde, le plus souvent)" % (p, len(doc), attendu))
        for n in range(len(doc)):
            doc[n].render(scale=1.5).to_pil().save(
                os.path.join(REVUE, "cartes-corpus-p%d-%02d.png" % (p, n + 1)))
finally:
    srv.terminate()

for e in ennuis:
    print("✗ " + e)
print("Pages à regarder dans %s" % REVUE)
sys.exit(1 if ennuis else 0)
