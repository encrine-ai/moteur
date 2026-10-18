#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cherche un remplaçant libre de droits commerciaux aux pictogrammes « NC ».

Les fiches élève utilisent 26 pictogrammes ARASAAC, publiés en CC BY-NC-SA :
la clause « non commercial » les rend inutilisables dans un service payant.
Elle ne gêne pas le site gratuit d'aujourd'hui : elle bloque tout usage
commercial ultérieur du matériel.

Ce script interroge le registre Global Symbols (globalsymbols.com), qui
fédère une trentaine de jeux de pictogrammes en indiquant la licence de
chacun, et propose pour chaque concept les candidats issus des seuls jeux
dont la licence autorise l'usage commercial (CC0, CC BY, CC BY-SA).

    python3 scripts/pictos-libres.py              # rapport de couverture
    python3 scripts/pictos-libres.py --json       # sortie exploitable

Il ne télécharge rien : le choix d'une image reste un geste humain, comme
pour les photographies de l'imagier.
"""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
import unicodedata

API = "https://globalsymbols.com/api/v1"

# Licences compatibles avec un usage commercial, telles que le registre les
# nomme. Tout ce qui porte « nc » est écarté sans discussion.
LICENCES_OK = {"by", "by-sa", "cc0", "pd", "public-domain"}

# Les 26 pictogrammes à remplacer, avec le ou les mots à chercher.
# Clé = nom de fichier dans site/fiches/img/ (sans extension).
A_REMPLACER = {
    "aigle":          ["aigle", "eagle"],
    "baleine":        ["baleine", "whale"],
    "bouchon-liege":  ["bouchon", "liège", "cork"],
    "calamar":        ["calmar", "calamar", "squid"],
    "chamois":        ["chamois", "chamois goat", "mountain goat"],
    "chrysalide":     ["chrysalide", "chrysalis", "cocoon"],
    "cinema":         ["cinéma", "cinema", "movie theatre"],
    "coccinelle":     ["coccinelle", "ladybird", "ladybug"],
    "coquillage":     ["coquillage", "shell", "seashell"],
    "fourmiliere":    ["fourmilière", "ant hill", "anthill"],
    "glacon":         ["glaçon", "ice cube", "ice"],
    "goutte":         ["goutte", "drop", "water drop"],
    "igloo":          ["igloo"],
    "ile":            ["île", "island"],
    "lama":           ["lama", "llama"],
    "marmotte":       ["marmotte", "marmot", "groundhog"],
    "neige":          ["neige", "snow"],
    "phare":          ["phare", "lighthouse"],
    "pigeon":         ["pigeon", "dove"],
    "pirate":         ["pirate"],
    "poule":          ["poule", "hen", "chicken"],
    "sanglier":       ["sanglier", "wild boar", "boar"],
    "terrier":        ["terrier", "burrow", "den"],
    "tournesol":      ["tournesol", "sunflower"],
    "vague":          ["vague", "wave"],
    "vent":           ["vent", "wind"],
}


def api(chemin, **params):
    url = f"{API}/{chemin}?" + urllib.parse.urlencode(params)
    for essai in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            if essai == 2:
                print(f"  ! {chemin} {params} : {e}", file=sys.stderr)
                return []
            time.sleep(2 * (essai + 1))


def jeux_compatibles():
    """id → (nom, licence) des jeux dont la licence autorise le commerce."""
    jeux = {}
    for s in api("symbolsets"):
        licence = s.get("licence") or {}
        proprietes = (licence.get("properties") or "").lower()
        nom_licence = (licence.get("name") or "").lower()
        libre = proprietes in LICENCES_OK or (
            not proprietes and "public domain" in nom_licence
        )
        if libre and "nc" not in proprietes:
            jeux[s["id"]] = (s["name"], licence.get("name") or "domaine public")
    return jeux


def sans_accents(t):
    return "".join(c for c in unicodedata.normalize("NFD", t.lower())
                   if unicodedata.category(c) != "Mn")


def qualite(libelle, mot):
    """3 = le libellé est le mot ; 2 = le mot y figure entier ; 1 = sous-chaîne.

    Le registre cherche en sous-chaîne : « lama » ramène *flamant*, « vague »
    ramène *microwave*, « pirate » ramène *aspirateur*. Sans ce filtre, le
    rapport est faux.
    """
    lib, m = sans_accents(libelle), sans_accents(mot)
    if lib == m:
        return 3
    if re.search(r"\b" + re.escape(m) + r"\b", lib):
        return 2
    return 1 if m in lib else 0


def candidats(mots, jeux):
    """Cherche chaque mot, ne garde que les pictos des jeux compatibles."""
    trouves, vus = [], set()
    for mot in mots:
        for langue in ("fra", "eng"):
            for label in api("labels/search", query=mot, language=langue, limit=30) or []:
                picto = label.get("picto") or {}
                jeu = picto.get("symbolset_id")
                if jeu not in jeux or picto.get("id") in vus:
                    continue
                q = qualite(label.get("text") or "", mot)
                if q < 2:                      # simple sous-chaîne : du bruit
                    continue
                vus.add(picto["id"])
                trouves.append({
                    "jeu": jeux[jeu][0],
                    "licence": jeux[jeu][1],
                    "libelle": label.get("text"),
                    "langue": label.get("language"),
                    "qualite": q,
                    "format": picto.get("native_format"),
                    "url": picto.get("image_url"),
                })
    # D'abord la justesse du libellé, puis Mulberry — déjà le style de maison
    # des fiches — puis le vectoriel, qui s'imprime à toute taille.
    trouves.sort(key=lambda c: (-c["qualite"],
                                not c["jeu"].startswith("Mulberry"),
                                c["format"] != "svg"))
    return trouves


def main():
    en_json = "--json" in sys.argv
    jeux = jeux_compatibles()
    if not en_json:
        print(f"{len(jeux)} jeux de pictogrammes compatibles avec un usage "
              f"commercial :\n  " + "\n  ".join(sorted(n for n, _ in jeux.values())) + "\n")

    resultat, couverts = {}, 0
    for slug, mots in A_REMPLACER.items():
        trouves = candidats(mots, jeux)
        resultat[slug] = trouves
        if trouves:
            couverts += 1
        if not en_json:
            if trouves:
                tete = trouves[0]
                sur = "=" if tete["qualite"] == 3 else "~"
                print(f"  ✔ {slug:16} {sur} {tete['libelle'][:22]:22} {tete['jeu']} "
                      f"({tete['format']}, {len(trouves)} candidat·s)")
            else:
                print(f"  ✘ {slug:16} aucun candidat — à dessiner")

    if en_json:
        json.dump(resultat, sys.stdout, ensure_ascii=False, indent=1)
    else:
        manquants = [s for s, c in resultat.items() if not c]
        print(f"\n{couverts}/{len(A_REMPLACER)} concepts couverts par un jeu libre.")
        if manquants:
            print("À dessiner soi-même : " + ", ".join(manquants))


if __name__ == "__main__":
    main()
