# -*- coding: utf-8 -*-
"""Contrôle les cartes-corpus avant publication.

Cinq vérifications :

- **la couverture** : chaque nom des trois corpus de `01-projet-annuel.md`
  doit avoir une carte, ou être déclaré dans NON_ILLUSTRES (les verbes et les
  adjectifs). Un mot ajouté à un corpus sans carte fait échouer le contrôle
  au lieu de passer inaperçu — c'est le même filet que `couverture.py` pour
  le programme ;
- **les fichiers** : l'image de chaque carte doit exister là où le manifeste
  la désigne ;
- **les crédits de la banque** : source, licence et auteur renseignés. C'est
  `chercher-pictos.py verifier` qui juge si la licence est *admissible* — ne
  pas dédoubler cette règle ici, elle finirait par diverger ;
- **les doublons** : deux cartes ne peuvent pas porter les mêmes octets. Deux
  mots voisins finissent par recevoir le même pictogramme sans qu'on le voie —
  « la châtaigne » avait ainsi hérité de l'image du marron, avec des crédits
  parfaitement corrects. Le seul signe visible était que les deux fichiers
  pesaient exactement pareil ;
- **la fraîcheur des pages** : le nombre de cartes du HTML correspond au
  manifeste, donc la génération a bien été relancée après modification.

Une période sans carte n'a pas de cahier (generer-cartes-corpus.py la saute) :
elle est sautée ici aussi, et le script le dit.

Usage : python3 scripts/verifier-cartes-corpus.py
Sortie : code 1 s'il reste quelque chose à corriger.
"""
import json
import hashlib
import os
import re
import sys
import unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ICI, "..", "site")
BASE = os.path.join(SITE, "cartes-corpus")

# Le manifeste est du contenu de la classe : son chemin vient de classe.yml.
sys.path.insert(0, ICI)
import classe  # noqa: E402
ns = classe.manifeste("corpus")
entrees, CARTES, GROUPES = ns["entrees"], ns["CARTES"], ns["GROUPES"]
NON_ILLUSTRES = ns.get("NON_ILLUSTRES") or {}
CLASSE = classe.charger()
NB_PERIODES = len(CLASSE["periodes"])

credits_fiches = json.load(open(os.path.join(SITE, "fiches", "img", "credits.json"),
                                encoding="utf-8"))

ennuis = []
# md5 → slugs : deux cartes qui partagent leurs octets sont un accident
empreintes = {}


def normalise(mot):
    """« l'écureuil » et « écureuil » sont le même mot ; les corpus écrivent
    l'article, pas toujours le même."""
    m = mot.strip().lower().replace("’", "'")
    m = re.sub(r"^(le |la |les |l'|un |une )", "", m)
    return "".join(c for c in unicodedata.normalize("NFD", m)
                   if unicodedata.category(c) != "Mn")


# ── 1. Couverture des corpus ──────────────────────────────────────────────
# Le projet annuel est le document `projet-annuel` de classe.yml ; son chemin
# dans le site assemblé (content/…) est celui du dépôt sans content/.
doc = next((d for d in CLASSE["documents"] if d["id"] == "projet-annuel" and d.get("md")), None)
chemin_projet = os.path.join(ICI, "..", re.sub(r"^content/", "", doc["md"])) if doc else None
mots_corpus = {}
if not (chemin_projet and os.path.exists(chemin_projet)):
    print("couverture des corpus sautée : pas de projet annuel (document projet-annuel de classe.yml)")
else:
    projet = open(chemin_projet, encoding="utf-8").read()
    nom_projet = os.path.basename(chemin_projet)
    if "## 3. Corpus de vocabulaire" not in projet:
        print("couverture des corpus sautée : %s n'a pas encore de section « 3. Corpus de vocabulaire »"
              % nom_projet)
    else:
        section = projet.split("## 3. Corpus de vocabulaire")[1].split("## 4.")[0]
        for ligne in section.split("\n"):
            m = re.match(r"\| P(\d) \w+ \|(.*)\|\s*$", ligne)
            if m:
                mots_corpus[int(m.group(1))] = [w.strip() for c in m.group(2).split("|")
                                                for w in c.split(",") if w.strip()]
        if len(mots_corpus) != NB_PERIODES:
            ennuis.append("le tableau des corpus de %s a %d ligne(s) pour %d périodes"
                          % (nom_projet, len(mots_corpus), NB_PERIODES))

for p, mots in sorted(mots_corpus.items()):
    cartes = {normalise(nom) for _, _, _, nom, _ in entrees(p)}
    declares = {normalise(m) for m in NON_ILLUSTRES.get(p, ())}
    for mot in mots:
        if normalise(mot) not in cartes and normalise(mot) not in declares:
            ennuis.append("P%d  « %s » : ni carte ni mot déclaré non illustrable" % (p, mot))
    for mot in declares - {normalise(m) for m in mots}:
        ennuis.append("P%d  « %s » déclaré non illustrable mais absent du corpus" % (p, mot))

# ── 2. Les images : deux provenances, et la banque partagée ──────────────
# Pas de banque propre aux cartes-corpus : les pictogrammes viennent de
# site/fiches/img/, alimentée par scripts/chercher-pictos.py (skill
# fiches-illustrations). Un mot dont le slug n'y est pas encore est signalé
# comme « à installer », avec la commande qui le fait.
a_installer, vus = [], set()
for p, groupe, slug, nom, source in entrees():
    if slug in vus:
        continue
    vus.add(slug)
    genre, valeur = source
    if genre == "imagier":
        chemin = os.path.join(SITE, "imagier", "img", valeur + ".jpg")
        if not os.path.exists(chemin):
            ennuis.append("%-16s photographie d'imagier absente : %s" % (slug, valeur))
        continue
    credit = credits_fiches.get(valeur)
    if not credit:
        # peut-être une référence par nom de fichier plutôt que par slug
        credit = credits_fiches.get(os.path.splitext(valeur)[0])
    if not credit:
        a_installer.append(slug)
        continue
    for champ in ("source", "licence", "auteur"):
        if not credit.get(champ):
            ennuis.append("%-16s crédit incomplet dans la banque (%s)" % (slug, champ))
    chemin = os.path.join(SITE, "fiches", "img", credit["fichier"])
    if not os.path.exists(chemin):
        ennuis.append("%-16s image absente : %s" % (slug, credit["fichier"]))
    else:
        empreintes.setdefault(hashlib.md5(open(chemin, "rb").read()).hexdigest(),
                              []).append(slug)

for slugs in empreintes.values():
    if len(slugs) > 1:
        ennuis.append("images identiques au bit près : %s" % ", ".join(sorted(slugs)))

# ── 3. Les pages sont-elles à jour ? ──────────────────────────────────────
cahiers = 0
for p in sorted(CARTES):
    page = os.path.join(BASE, "periode-%d.html" % p)
    if not any(True for _ in entrees(p)):
        print("periode-%d : aucune carte dans le manifeste, pas de cahier — sautée" % p)
        continue
    cahiers += 1
    if not os.path.exists(page):
        ennuis.append("periode-%d.html absent — lancer generer-cartes-corpus.py" % p)
        continue
    html = open(page, encoding="utf-8").read()
    attendu = sum(1 for _ in entrees(p))
    trouve = html.count('<div class="carte">')
    if trouve != attendu * 2:          # cartes de contrôle + cartes-images
        ennuis.append("periode-%d.html : %d cartes pour %d mots — page à régénérer"
                      % (p, trouve, attendu))

if a_installer:
    print("%d mot·s dont l'image reste à installer dans la banque partagée :"
          % len(a_installer))
    print("  " + ", ".join(sorted(a_installer)))
    print("  → python3 scripts/chercher-pictos.py chercher <slug> \"<mots anglais>\"")
    print("  → puis  installer <slug> mulberry:<nom>  (skill fiches-illustrations)")
    ennuis.append("%d image·s manquent encore" % len(a_installer))

for e in ennuis:
    print("✗ " + e)
print("%d cartes contrôlées sur %d cahiers, %d anomalie(s)" % (len(vus), cahiers, len(ennuis)))
sys.exit(1 if ennuis else 0)
