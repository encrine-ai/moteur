# -*- coding: utf-8 -*-
"""Le bloc de tête du README d'une classe, tiré de classe.yml.

Sur GitHub, le README est la première chose qu'on voit d'une classe. Ce
module y écrit, entre les marqueurs `<!-- encrine:debut -->` et
`<!-- encrine:fin -->`, en tête du fichier :

- le titre du projet, « La classe de <signature> » si l'enseignant signe ;
- le niveau, l'année et la zone de vacances ; l'accroche ;
- le lien du site de la classe : `site` dans classe.yml s'il est écrit (un
  domaine propre, comme la classe d'exemple sur encrine.ai), sinon
  l'adresse de GitHub Pages tirée de `depot`,
  https://<propriétaire>.github.io/<dépôt>/ ;
- la licence du contenu (`partage.licence`, sinon LICENCE-CONTENU.md) et,
  si elle permet la reprise (CC BY, CC BY-SA, CC0), le lien « Partir de
  cette classe » (github.com/new?template_owner=…&template_name=…) ;
- le crédit de la classe d'origine, si `origine` existe (CC BY et CC BY-SA
  l'exigent) ;
- le bandeau « Conçu avec Encrine ».

Le reste du README appartient à l'enseignant : `classe.py generer` ne
refait que le bloc, et le pose en tête s'il manque ; `classe.py verifier`
signale un bloc absent ou périmé. Un README qui est encore celui du moteur
(il porte le marqueur `<!-- encrine:moteur -->`, copié par « Use this
template ») est remplacé par un README de classe : le bloc, puis un court
texte que l'enseignant peut réécrire.

Le modèle n'a pas de bloc : son README décrit le moteur, et sa classe de
départ n'a pas de `depot` (« à définir »). Une classe sans `depot`, ou dont
le `depot` est celui du moteur, est laissée telle quelle.
"""
import pathlib
import re
import urllib.parse

RACINE = pathlib.Path(__file__).resolve().parent.parent
README = RACINE / "README.md"
LICENCE = RACINE / "LICENCE-CONTENU.md"
DEBUT, FIN = "<!-- encrine:debut -->", "<!-- encrine:fin -->"
# Les marqueurs comptent seuls sur leur ligne : un README qui les cite dans
# le texte (celui du moteur) n'a pas de bloc pour autant.
BLOC = re.compile(r"^%s$.*?^%s$\n?" % (re.escape(DEBUT), re.escape(FIN)), re.S | re.M)
# Le marqueur du README du moteur : une classe qui le porte encore a reçu le
# README du modèle avec « Use this template ».
MARQUE_MOTEUR = "<!-- encrine:moteur -->"
DU_MOTEUR = re.compile(r"^%s$" % re.escape(MARQUE_MOTEUR), re.M)
MODELE = "encrine-ai/moteur"
ENCRINE = "https://encrine.ai"
LOGO = ENCRINE + "/assets/logo-encrine.svg"
LOGO_SOMBRE = ENCRINE + "/assets/logo-encrine-craie.svg"
NON_DEFINI = (None, "", "à définir")
# « CC BY-SA 4.0 », « CC BY-NC-SA 4.0 », « CC0 1.0 »…
LICENCE_CC = re.compile(r"\bCC(?:0(?: \d\.\d)?| BY(?:-NC)?(?:-SA|-ND)?(?: \d\.\d)?)")


def depot(c):
    d = c.get("depot")
    return None if d in NON_DEFINI else d


def concerne(c):
    """Le bloc vaut pour une classe qui a son dépôt — pas pour le modèle."""
    d = depot(c)
    return bool(d) and d not in (MODELE, (c.get("moteur") or {}).get("depot"))


def site(c):
    if c.get("site"):
        return c["site"] if c["site"].endswith("/") else c["site"] + "/"
    proprietaire, nom = depot(c).split("/", 1)
    return "https://%s.github.io/%s/" % (proprietaire.lower(), nom)


def licence(c):
    """La licence du contenu : `partage.licence`, sinon la première licence
    Creative Commons que nomme LICENCE-CONTENU.md ; None si rien n'est dit
    (on n'en invente pas)."""
    lic = ((c.get("partage") or {}).get("licence") or "").strip()
    if lic:
        return lic
    if LICENCE.is_file():
        m = LICENCE_CC.search(LICENCE.read_text(encoding="utf-8"))
        if m:
            return m.group(0)
    return None


def reprenable(lic):
    """CC0, CC BY, CC BY-SA : la classe peut être reprise (« Partir de cette
    classe ») ; NC, ND, tous droits réservés ou rien : non."""
    return bool(lic) and bool(re.match(r"^CC(0| BY(-SA)?( |$))", lic)) and not re.search(r"NC|ND", lic)


def lien_licence(lic):
    """LICENCE-CONTENU.md s'il existe, sinon l'acte Creative Commons."""
    if LICENCE.is_file():
        return LICENCE.name
    m = re.match(r"^CC (BY(?:-NC)?(?:-SA|-ND)?) (\d\.\d)$", lic)
    if m:
        return "https://creativecommons.org/licenses/%s/%s/deed.fr" % (m.group(1).lower(), m.group(2))
    if re.match(r"^CC0", lic):
        return "https://creativecommons.org/publicdomain/zero/1.0/deed.fr"
    return None


def de(nom):
    """« de Mme Martin », « d’Aurélie »."""
    return ("d’" if re.match(r"[AEIOUYÀÂÉÈÊËÎÏÔÛÙÜaeiouyàâéèêëîïôûùü]", nom) else "de ") + nom


def bloc(c):
    """Le bloc, en Markdown (et quelques balises que GitHub garde)."""
    un = lambda t: " ".join(str(t or "").split())
    signature = un((c.get("enseignant") or {}).get("signature"))
    zone = (c.get("calendrier") or {}).get("zone")
    l = [DEBUT,
         "<!-- Écrit par scripts/classe.py generer, depuis classe.yml : ne pas retoucher à la main.",
         "     Le reste du fichier, sous le bloc, est à vous. -->",
         "", "# %s" % un(c["projet"]), ""]
    ligne = " · ".join(x for x in (c["niveau"]["libelle"], c["annee"], zone and "zone %s" % zone) if x)
    l.append("**La classe %s** · %s" % (de(signature), ligne) if signature else "**%s**" % ligne)
    if un(c.get("accroche")):
        l += ["", un(c["accroche"])]
    liens = ["**[Voir le site de la classe](%s)**" % site(c)]
    lic = licence(c)
    if reprenable(lic):
        proprietaire, nom = depot(c).split("/", 1)
        liens.append("[Partir de cette classe](https://github.com/new?%s)" % urllib.parse.urlencode(
            {"template_owner": proprietaire, "template_name": nom}))
    l += ["", " · ".join(liens)]
    if lic:
        lien = lien_licence(lic)
        l += ["", "Contenu sous licence %s." % ("[%s](%s)" % (lic, lien) if lien else lic)]
    o = c.get("origine")
    if isinstance(o, dict) and o.get("titre"):
        titre = "*[%s](%s)*" % (un(o["titre"]), o["site"]) if o.get("site") else "*%s*" % un(o["titre"])
        auteur = ", %s" % de(un(o["auteur"])) if o.get("auteur") else ""
        l += ["", "D’après %s%s, sous licence %s." % (titre, auteur, un(o.get("licence")))]
    l += ["",
          '<p><a href="%s"><picture><source media="(prefers-color-scheme: dark)" srcset="%s">'
          '<img src="%s" alt="Encrine" height="32" align="absmiddle"></picture></a>'
          '&nbsp; Conçu avec <a href="%s">Encrine</a>, le moteur qui fabrique l’année d’une classe.</p>'
          % (ENCRINE, LOGO_SOMBRE, LOGO, ENCRINE),
          "", "---", FIN]
    return "\n".join(l) + "\n"


def corps(c):
    """Le texte qui suit le bloc dans un README de classe neuf : à l'enseignant
    de le réécrire."""
    moteur = (c.get("moteur") or {}).get("depot") or MODELE
    return (
        "\n## Ce dépôt\n\n"
        "Tout le matériel de la classe : les documents de l’année "
        "([`01-projet-annuel.md`](01-projet-annuel.md), "
        "[`02-programmation-annuelle.md`](02-programmation-annuelle.md), "
        "`03-progressions/`, `04-evaluations/`), le site et ses cahiers à imprimer "
        "(`site/`), et la fiche de la classe, [`classe.yml`](classe.yml).\n\n"
        "Pour le faire évoluer, ouvrez ce dépôt dans Claude Code et dites ce que vous "
        "voulez, avec vos mots. Le fonctionnement du moteur est décrit dans son dépôt, "
        "[%s](https://github.com/%s).\n" % (moteur, moteur))


def poser(texte, c):
    """Le README avec le bloc à jour : à la place de l'ancien, en tête s'il
    n'y en a pas, ou à la place de tout le README du moteur."""
    b = bloc(c)
    if not texte.strip() or DU_MOTEUR.search(texte):
        return b + corps(c)
    if BLOC.search(texte):
        return BLOC.sub(lambda _: b, texte, count=1)
    return b + "\n" + texte.lstrip("\n")


def ecrire(c):
    if not concerne(c):
        return
    texte = README.read_text(encoding="utf-8") if README.is_file() else ""
    nouveau = poser(texte, c)
    if nouveau != texte:
        README.write_text(nouveau, encoding="utf-8")
    print("README.md : bloc de tête de la classe (%s)" % site(c))


def anomalies(c):
    a = []
    if c.get("site") is not None and not (isinstance(c["site"], str) and c["site"].startswith("https://")):
        a.append("site : « %s » — l'adresse du site de la classe, en https://" % c["site"])
    if not concerne(c):
        return a
    texte = README.read_text(encoding="utf-8") if README.is_file() else ""
    if DU_MOTEUR.search(texte):
        a.append("README.md : c'est encore celui du moteur — relancer  python3 scripts/classe.py generer")
    elif not BLOC.search(texte):
        a.append("README.md : il manque le bloc de la classe (%s … %s) — relancer  "
                 "python3 scripts/classe.py generer" % (DEBUT, FIN))
    elif poser(texte, c) != texte:
        a.append("README.md : le bloc de la classe est périmé — relancer  python3 scripts/classe.py generer")
    return a
