#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrôle de couverture : ce que l'année couvre du programme.

On confronte le référentiel (`referentiel/cycle1-gs.yml`, une ligne par
exigence du programme) aux accroches déclarées par l'année
(le fichier `contenu.annotations` de `classe.yml`), et l'on dit ce qui manque.

    python3 scripts/couverture.py             # le rapport
    python3 scripts/couverture.py --manques   # seulement ce qui cloche
    python3 scripts/couverture.py --domaine math
    python3 scripts/couverture.py --fragiles

Sort en code 1 s'il manque un attendu ou si une annotation cite un
identifiant inconnu — de quoi en faire un contrôle de chaîne de publication.

C'est une **jointure**, pas une recherche de mots : chaque bloc de l'année
cite les identifiants qu'il sert, on soustrait. Le contrôle est donc exact —
il ne peut ni rater un trou, ni en inventer un. Il donne en plus ce qu'aucune
relecture humaine ne donne : les attendus rencontrés **une seule fois dans
l'année**, qui sont formellement couverts et pédagogiquement fragiles.

Dépendance : PyYAML.
"""

import collections
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML requis :  pip install pyyaml")

RACINE = pathlib.Path(__file__).resolve().parent.parent
VERT, ORANGE, ROUGE, GRIS, GRAS, RAZ = (
    "\033[32m", "\033[33m", "\033[31m", "\033[90m", "\033[1m", "\033[0m")


def lire(chemin):
    p = RACINE / chemin
    return p.read_text(encoding="utf-8") if p.exists() else ""


def charger(cle):
    """Le référentiel ou les annotations : leurs chemins viennent de classe.yml."""
    sys.path.insert(0, str(RACINE / "scripts"))
    import classe
    return yaml.safe_load(classe.chemin(cle).read_text(encoding="utf-8"))


# ——— Contrôles de cadre ———————————————————————————————————————————————

def evar_seances(regle):
    n = len(re.findall(r"^## Séance spécifique n°",
                       lire("03-progressions/07-evar.md"), re.M))
    return n >= regle["minimum"], f"{n} séances spécifiques"


def eps_unites(regle):
    texte = lire("03-progressions/03-activites-physiques.md")
    unites = re.findall(r"^### Unité \d+", texte, re.M)
    comptees = re.findall(r"^### Unité \d+[^\n]*\((\d+) séances", texte, re.M)
    hors = [int(n) for n in comptees if not 6 <= int(n) <= 8]
    muettes = len(unites) - len(comptees)
    detail = f"{len(unites)} unités, {len(comptees)} chiffrées"
    if muettes:
        detail += f", {muettes} muettes"
    if hors:
        detail += f", hors 6-8 : {hors}"
    return not hors and not muettes, detail


def corpus_par_periode(regle):
    # Borner à la bonne section : les tableaux des albums et des arts ont les
    # mêmes en-têtes de ligne, et une recherche non bornée les compte aussi.
    section = re.search(r"^## 3\. Corpus de vocabulaire.*?(?=^## )",
                        lire("01-projet-annuel.md"), re.M | re.S)
    lignes = re.findall(r"^\| P(\d) [^|]*\|([^\n]*)$",
                        section.group(0) if section else "", re.M)
    n = sum(len([c for c in reste.split("|") if c.strip()][:3]) for _, reste in lignes)
    return n >= regle["minimum"], f"{n} corpus"


def oeuvres_patrimoniales(regle):
    n = len(re.findall(r"œuvre patrimoniale \d", lire("01-projet-annuel.md")))
    return n >= regle["minimum"], f"{n} œuvres marquées"


def non_verifiable(regle):
    return None, regle.get("raison", "").strip()


# Ne sont contrôlées ici que les exigences du programme. Le nombre d'espèces
# de l'imagier est une convention de ce dépôt, pas une règle du BO : il a
# longtemps figuré parmi ces règles, ce qui laissait croire que le programme
# le prescrivait. Il est vérifié par scripts/verifier-imagier.py.
CONTROLES = {f.__name__: f for f in (evar_seances, eps_unites, corpus_par_periode,
                                     oeuvres_patrimoniales, non_verifiable)}


# ——— Rapport ——————————————————————————————————————————————————————————

def main():
    seuls_manques = "--manques" in sys.argv
    filtre = None
    if "--domaine" in sys.argv:
        filtre = sys.argv[sys.argv.index("--domaine") + 1].lower()

    ref = charger("referentiel")
    ann = charger("annotations")
    attendus = {a["id"]: a for a in ref["attendus"]}

    # Jointure : qui sert quoi, et depuis quelles périodes.
    rencontres = collections.defaultdict(set)
    inconnus = collections.Counter()
    for bloc in ann["blocs"]:
        for aid in bloc["attendus"]:
            if aid in attendus:
                rencontres[aid].add(bloc["periode"])
            else:
                inconnus[aid] += 1

    if inconnus:
        print(f"\n  {ROUGE}Identifiants annotés qui n'existent pas au référentiel :{RAZ}")
        for aid, n in inconnus.most_common():
            print(f"    {aid}  ({n}×)")

    couverts = [a for a in ref["attendus"] if a["id"] in rencontres]
    manquants = [a for a in ref["attendus"] if a["id"] not in rencontres]
    fragiles = [a for a in couverts if len(rencontres[a["id"]]) == 1]

    print(f"\n  {GRAS}Couverture du programme — {ann['classe']}, {ann['annee']}{RAZ}")
    print(f"  {GRIS}{ann['projet']} · référentiel « {ref['statut']} »{RAZ}\n")
    part = 100 * len(couverts) / len(ref["attendus"])
    couleur = VERT if part >= 95 else ORANGE if part >= 85 else ROUGE
    print(f"  {couleur}{GRAS}{len(couverts)} attendus couverts sur "
          f"{len(ref['attendus'])}{RAZ}  ({part:.0f} %)\n")

    # — Par domaine —
    par_domaine = collections.defaultdict(lambda: [0, 0])
    for a in ref["attendus"]:
        par_domaine[a["domaine"]][1] += 1
        if a["id"] in rencontres:
            par_domaine[a["domaine"]][0] += 1
    for domaine, (n, total) in par_domaine.items():
        if filtre and filtre not in domaine.lower():
            continue
        barre = "█" * round(18 * n / total) + "·" * (18 - round(18 * n / total))
        marque = VERT if n == total else ROUGE
        print(f"    {marque}{barre}{RAZ} {n:>2}/{total:<3} {domaine}")

    # — Les trous —
    if manquants:
        print(f"\n  {ROUGE}{GRAS}Non couverts — {len(manquants)}{RAZ}")
        for a in manquants:
            if filtre and filtre not in a["domaine"].lower():
                continue
            print(f"    {ROUGE}✘{RAZ} {a['libelle']}")
            print(f"      {GRIS}{a['id']} · {a['domaine']} › {a['sous_domaine']}{RAZ}")

    # — Les fragiles —
    if fragiles and not seuls_manques:
        montrer = [a for a in fragiles
                   if not filtre or filtre in a["domaine"].lower()]
        tout = "--fragiles" in sys.argv
        print(f"\n  {ORANGE}{GRAS}Rencontrés dans une seule période — "
              f"{len(fragiles)}{RAZ}")
        print(f"  {GRIS}À cette maille — le document et la période — le signal reste"
              f" faible : une\n  séance d'EVAR est unique par construction, et un"
              f" attendu peut être repris\n  plusieurs fois dans la même période."
              f" Il deviendra exploitable quand les\n  accroches seront portées par"
              f" les séances elles-mêmes.{RAZ}")
        for a in montrer[: len(montrer) if tout else 10]:
            per = next(iter(rencontres[a["id"]]))
            print(f"    {ORANGE}~{RAZ} P{per}  {a['libelle'][:64]}")
        if not tout and len(montrer) > 10:
            print(f"    {GRIS}… et {len(montrer) - 10} autres (--fragiles){RAZ}")

    # — Répartition par période —
    if not seuls_manques and not filtre:
        print(f"\n  {GRAS}Charge par période{RAZ}")
        for p in range(1, 6):
            n = sum(1 for aid in rencontres if p in rencontres[aid])
            print(f"    P{p}  {'▪' * round(n / 2):<28} {n} attendus travaillés")

    # — Règles de cadre —
    print(f"\n  {GRAS}Règles de cadre{RAZ}")
    for r in ref["regles"]:
        ok, detail = CONTROLES[r["controle"]](r)
        if seuls_manques and ok:
            continue
        marque = {True: f"{VERT}✔{RAZ}", False: f"{ROUGE}✘{RAZ}", None: f"{GRIS}?{RAZ}"}[ok]
        print(f"    {marque} {r['libelle'][:60]:60} {GRIS}{detail[:60]}{RAZ}")

    print()
    return 1 if (manquants or inconnus) else 0


if __name__ == "__main__":
    sys.exit(main())
