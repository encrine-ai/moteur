# -*- coding: utf-8 -*-
"""Manifeste des cartes-corpus — vide tant que le thème n'est pas choisi.

Même forme que dans toute classe ; voir le skill cartes-corpus."""

CORPUS = {}
GROUPES = ("milieu", "faune", "flore")
CARTES = {p: {g: [] for g in GROUPES} for p in range(1, 6)}
RAPPELS = {}
NON_ILLUSTRES = {}
TRI = {}
TRI_MILIEUX = ()


def entrees(periode=None):
    """(période, groupe, slug, nom, source) pour toutes les cartes."""
    for p in sorted(CARTES):
        if periode and p != periode:
            continue
        for g in GROUPES:
            for slug, nom, source in CARTES[p][g]:
                yield p, g, slug, nom, source
