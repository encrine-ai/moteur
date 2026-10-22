# -*- coding: utf-8 -*-
"""La typographie française des textes que le moteur écrit lui-même.

En français, le signe qui accompagne un mot ne s'en sépare pas : l'espace
devant « ; ? ! », devant « : » et à l'intérieur des guillemets est
insécable. Avec une espace ordinaire, une coupure de ligne peut laisser un
« » » ou un « : » seul en tête de ligne — c'est arrivé dans le guide
PRISE-EN-MAIN.md de la démonstration (encrine-ai/moteur#2) :

    défait. Si quelque chose te déplaît, dis-le : « reviens à la version d'avant
    ».

- `francais(texte)` pose les insécables : l'espace fine insécable (U+202F)
  devant ; ? ! et dans « … », l'insécable (U+00A0) devant : ;
- `anomalies(nom, texte)` refuse, dans un texte fabriqué, une ligne qui
  commence par l'un de ces signes, ou une espace ordinaire à leur place ;
- `anomalies_js(nom, source)` fait de même dans les chaînes entre
  apostrophes des scripts du site (app.js, modele.js, gabarits.js…), qui
  écrivent leurs insécables en \\u202f et \\u00a0.

Seul ce que le moteur écrit passe par ici (le guide, le bloc de tête du
README, l'aperçu de lien, les textes des scripts du site) : jamais le
contenu de la classe, ses documents ou ses cahiers. `classe.py verifier`
appelle les deux contrôles.
"""
import re

FINE = " "   # espace fine insécable : devant ; ? ! et dans « … »
INSECABLE = " "  # espace insécable : devant :
ESPACES = "[ \t%s%s]" % (FINE, INSECABLE)
# Les scripts du site qui écrivent du texte (ceux du moteur ; les gabarits
# d'un thème sont à la classe).
SCRIPTS_DU_SITE = ("app.js", "modele.js", "gabarits.js", "commun.js", "appli.js")

# Un « : » suivi d'une espace ou de la fin : pas celui d'une adresse
# (https://) ni d'une heure (8:30).
_DEUX_POINTS = re.compile(r"%s+:(?=\s|$)" % ESPACES, re.M)
_PONCTUATION = re.compile(r"%s+([;?!])" % ESPACES)
_OUVRANT = re.compile(r"«%s+" % ESPACES)
_FERMANT = re.compile(r"%s+»" % ESPACES)


def francais(texte):
    """Le texte avec ses espaces insécables, sans rien changer d'autre."""
    t = _DEUX_POINTS.sub(INSECABLE + ":", texte)
    t = _PONCTUATION.sub(FINE + r"\1", t)
    t = _OUVRANT.sub("«" + FINE, t)
    return _FERMANT.sub(FINE + "»", t)


# Une espace ordinaire là où il en faut une insécable.
_ORDINAIRE = re.compile(r"[ \t](?=:(?:\s|$)|[;?!»])|(?<=«)[ \t]", re.M)
_EN_TETE = re.compile(r"^\s*([»:;?!])")


def anomalies(nom, texte):
    """Ce qui ne va pas dans un texte fabriqué, ligne par ligne."""
    a = []
    for i, ligne in enumerate(texte.split("\n"), 1):
        m = _EN_TETE.match(ligne)
        if m:
            a.append("%s, ligne %d : « %s » en début de ligne — une espace insécable doit le tenir "
                     "au mot qui le précède (scripts/typographie.py)" % (nom, i, m.group(1)))
        elif _ORDINAIRE.search(ligne):
            a.append("%s, ligne %d : une espace ordinaire devant « : ; ? ! » ou dans « … » — "
                     "passer le texte par typographie.francais()" % (nom, i))
    return a


def _chaines(source):
    """Les chaînes entre apostrophes d'un script, (ligne, contenu brut) : les
    commentaires, les chaînes entre guillemets droits, les gabarits `…` et
    les expressions régulières sont sautés."""
    i, n, ligne = 0, len(source), 1
    prec = ""  # le dernier caractère significatif hors chaîne
    while i < n:
        ch = source[i]
        if ch == "\n":
            ligne += 1
            i += 1
            continue
        if source.startswith("//", i):
            j = source.find("\n", i)
            i = n if j < 0 else j
            continue
        if source.startswith("/*", i):
            j = source.find("*/", i + 2)
            j = n if j < 0 else j + 2
            ligne += source.count("\n", i, j)
            i = j
            continue
        if ch == "/" and (prec in "(,=:[!&|?{};+" or prec == ""):
            # une expression régulière : jusqu'au / qui la ferme
            j, classe = i + 1, False
            while j < n and source[j] != "\n":
                if source[j] == "\\":
                    j += 2
                    continue
                if source[j] == "[":
                    classe = True
                elif source[j] == "]":
                    classe = False
                elif source[j] == "/" and not classe:
                    break
                j += 1
            i, prec = j + 1, "/"
            continue
        if ch in "'\"`":
            j, debut = i + 1, ligne
            while j < n and source[j] != ch:
                if source[j] == "\\":
                    j += 1
                elif source[j] == "\n":
                    ligne += 1
                j += 1
            if ch == "'":
                yield debut, source[i + 1:j]
            i, prec = j + 1, ch
            continue
        if not ch.isspace():
            prec = ch
        i += 1


def anomalies_js(nom, source):
    """Les chaînes d'un script du site où une espace ordinaire précède
    « : ; ? ! » ou suit « (un « : » d'un style, comme « flex-grow: », n'est
    pas visé : rien ne le précède)."""
    a = []
    for ligne, s in _chaines(source):
        if re.search(r" (?::(?: |$)|[;?!»])|« ", s):
            a.append("%s, ligne %d : « %s » — une espace insécable (\\u00a0 devant :, \\u202f devant "
                     "; ? ! et dans « … ») au lieu de l'espace ordinaire" % (nom, ligne, s.strip()))
    return a
