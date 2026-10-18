# -*- coding: utf-8 -*-
"""Manifeste de l'imagier — vide tant que le thème n'est pas choisi.

Même forme que dans toute classe : IMAGIER[période] = {"faune": [...], "flore": [...]},
chaque entrée (slug, nom, taxon). Voir le skill imagier-photos."""

IMAGIER = {p: {"faune": [], "flore": []} for p in range(1, 6)}
DOMESTIQUES = set()
OVERRIDES = {}


def entrees(periode=None):
    """Itère sur (periode, groupe, slug, nom, taxon)."""
    for p, groupes in sorted(IMAGIER.items()):
        if periode and p != periode:
            continue
        for groupe in ("faune", "flore"):
            for slug, nom, taxon in groupes[groupe]:
                yield p, groupe, slug, nom, taxon
