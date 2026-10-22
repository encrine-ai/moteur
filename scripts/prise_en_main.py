# -*- coding: utf-8 -*-
"""PRISE-EN-MAIN.md : le guide de l'enseignant pour prendre en main sa
classe, fabriqué depuis classe.yml par `classe.py generer`.

Il dit, en mots simples : ce qu'est la classe (le site, les PDF, le dépôt)
et Encrine ; le premier lancement après un transfert du dépôt (skill
reprendre-ma-classe) ; ce qu'on peut demander ensuite ; ce qui est protégé ;
les règles de prudence ; à qui demander quand ça bloque. Il reprend le guide
écrit à la main pour la première classe passée à son enseignante, rendu
générique : tout ce qui est propre à une classe vient de classe.yml —

- `enseignant.signature` (« Bienvenue, Anaïs ») ; le guide vouvoie, comme la
  page d'accueil d'encrine.ai et le README (décidé le 22 octobre 2026) ;
- `projet`, `niveau`, `annee`, `depot` (le nom du dépôt, la nouvelle
  adresse), `site` ; `materiel` (les cahiers nommés) et `periodes` (un
  exemple de demande) ;
- `valide_le`, facultatif : la date où l'enseignant a validé le contenu ;
- `accompagnant`, facultatif (`nom`, `github`) : celui qui a préparé la
  classe pour l'enseignant (skill nouvelle-classe, « Pour quelqu'un
  d'autre ») ; sans lui, les phrases qui le nomment disparaissent ;
- `partage.prenoms_fictifs` : les prénoms des énoncés, inventés.

Le guide peut être enrichi par la classe : ce qui s'écrit à la fin, entre
`<!-- classe:debut -->` et `<!-- classe:fin -->` (un titre « ## Propre à
cette classe », comme dans les skills), est gardé à chaque `generer`.
`classe.py verifier` signale un guide absent ou périmé. Le moteur n'en a
pas : sa classe de départ n'a pas de `depot` (comme pour le bloc du README).
"""
import datetime
import pathlib
import re
import textwrap

import readme
import typographie

RACINE = pathlib.Path(__file__).resolve().parent.parent
GUIDE = RACINE / "PRISE-EN-MAIN.md"
NOM = GUIDE.name
CLASSE_DEBUT, CLASSE_FIN = "<!-- classe:debut -->", "<!-- classe:fin -->"
SECTION_CLASSE = re.compile(r"^%s$.*?^%s$" % (re.escape(CLASSE_DEBUT), re.escape(CLASSE_FIN)), re.S | re.M)
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]
CLES_ACCOMPAGNANT = {"nom", "github"}


def concerne(c):
    return readme.concerne(c)


def publiee_par_encrine(c):
    """La classe est publiée par Encrine — la démonstration, ou la copie
    relue d'une classe de la galerie — et non par un enseignant : le même
    test que hebergeeParEncrine() (site/modele.js), sur `depot`, `site` et,
    pour une copie qui garde le `depot` de son auteur, le remote `origin`."""
    return bool(readme.depot_encrine(c)) or str(c.get("site") or "").startswith(readme.ENCRINE + "/")


def copie_relue(c):
    """Une copie relue de la galerie : publiée par Encrine, elle garde dans
    classe.yml le `depot` de l'enseignant dont elle vient."""
    return publiee_par_encrine(c) and not (readme.depot(c) or "").startswith(readme.ORGANISATION)


def _un(t):
    return " ".join(str(t or "").split())


def date_longue(d):
    return "%s %s %d" % ("1er" if d.day == 1 else d.day, MOIS[d.month - 1], d.year)


def date_validation(c):
    """`valide_le`, en date (classe.charger() rend les dates en ISO), ou None."""
    v = c.get("valide_le")
    if isinstance(v, datetime.date):
        return v
    try:
        return datetime.date.fromisoformat(str(v)) if v else None
    except ValueError:
        return None


def envelopper(md):
    """Les paragraphes et les puces à 78 colonnes, comme les fichiers écrits à
    la main ; les titres, tableaux, citations et commentaires tels quels."""
    sortie = []
    for ligne in md.split("\n"):
        m = re.match(r"^((?:- |\d+\. )?)(.*)$", ligne)
        if len(ligne) <= 78 or ligne.startswith(("#", "|", "<!--", "     ", "   >")):
            sortie.append(ligne)
            continue
        retrait = " " * len(m.group(1))
        sortie.extend(textwrap.wrap(ligne, 78, initial_indent="", subsequent_indent=retrait,
                                    break_long_words=False, break_on_hyphens=False))
    return "\n".join(sortie)


def accompagnant(c):
    a = c.get("accompagnant")
    return a if isinstance(a, dict) and _un(a.get("nom")) else None


def _liste(mots):
    mots = list(mots)
    return mots[0] if len(mots) == 1 else ", ".join(mots[:-1]) + " et " + mots[-1]


def texte(c, propre=None):
    """Le guide, en Markdown. `propre` : la section propre à la classe, gardée."""
    ens = c.get("enseignant") or {}
    signature = _un(ens.get("signature"))
    acc = accompagnant(c)
    acc_nom = _un(acc["nom"]) if acc else ""
    nom_depot = (readme.depot(c) or "/classe").split("/", 1)[1]
    cahiers = [_un(m.get("titre")).lower() for m in c.get("materiel") or [] if m.get("periodes")]
    imagier = any(m.get("cle") == "imagier" and m.get("periodes") for m in c.get("materiel") or [])
    periodes = c.get("periodes") or []
    exemple_p = 2 if len(periodes) >= 2 else 1
    fictifs = [p for p in (c.get("partage") or {}).get("prenoms_fictifs") or [] if _un(p)]
    valide = date_validation(c)
    encrine = publiee_par_encrine(c)

    l = []
    a = l.append
    a("# Prendre en main votre classe")
    a("")
    a("<!-- Écrit par scripts/classe.py generer, depuis classe.yml : ne pas retoucher à la main.")
    a("     Ce qui est propre à cette classe s'écrit à la fin, entre les marqueurs")
    a("     classe:debut et classe:fin (un titre « ## Propre à cette classe ») : c'est gardé. -->")
    a("")
    a("Bienvenue%s. Cette page vous explique, en mots simples, ce qu'est votre classe, "
        "« %s » (%s, %s), comment la reprendre à votre nom, et ce que vous pouvez "
        "demander ensuite. Vous n'avez rien à apprendre de technique : vous parlez "
        "à Claude comme à un collègue, et c'est lui qui fait."
      % ((", " + signature) if signature else "", _un(c["projet"]), _un(c["niveau"]["libelle"]), c["annee"]))
    a("")
    a("## Votre classe, c'est quoi ?")
    a("")
    a("Votre classe tient en trois choses, qui vont ensemble :")
    a("")
    a("- **votre site** : la page web de votre classe, avec le projet de l'année, la "
        "programmation, les progressions, les évaluations et tous les cahiers. Il s'ouvre sur un "
        "ordinateur, une tablette ou un téléphone, et s'installe comme une appli ;")
    a("- **les PDF** : chaque document%s, prêts à imprimer en A4. Ils sont refabriqués à chaque "
        "publication, vous n'avez jamais à les faire vous-même ;"
      % ((" et chaque cahier (%s)" % _liste(cahiers)) if cahiers else ""))
    a("- **le dépôt** : l'endroit, sur GitHub, qui garde tout — les textes, les images, "
        "l'historique de chaque changement. %s"
      % ("Le site et les PDF en sont tirés." if encrine else
         ("C'est lui que vous possédez ; le site et les PDF en sont tirés.")))
    a("")
    a("**Encrine** est l'outil qui a fabriqué votre classe : un « moteur » qui sait écrire une "
        "année conforme au programme, mettre en page les fiches, choisir les photos, fabriquer les PDF. "
        "Il s'améliore avec les retours des enseignants qui s'en servent, et votre classe peut "
        "recevoir ses nouveautés quand vous le souhaitez. %s"
      % ("Le bas du site porte la mention « Conçu avec Encrine » et renvoie aux mentions légales "
         "d'Encrine, qui publie cette classe." if encrine else
         ("Le bas de votre site porte la mention « Conçu avec Encrine », et ses mentions "
           "légales vous nomment comme éditeur%s.") % ((" (« %s »)" % signature) if signature else "")))
    if copie_relue(c):
        a("")
        a("Cette page est celle de la copie publiée sur encrine.ai ; la classe d'origine reste chez "
          "son auteur, qui a la sienne.")
    if valide:
        a("")
        a("Le contenu de votre classe (projet, progressions, évaluations, fiches%s, textes) a été "
            "relu et **validé le %s**. Il ne change que si vous le demandez."
          % (", espèces de l'imagier, mots" if imagier else "", date_longue(valide)))
    a("")
    a("## Le premier lancement, après le transfert")
    a("")
    if acc:
        debut = ("%s va vous transférer votre classe : elle passera de son compte GitHub "
                  "au vôtre.") % acc_nom
    else:
        debut = ("Si votre classe passe d'un compte GitHub à un autre (un transfert, depuis "
                  "celui de la personne qui l'a préparée, par exemple), voici la marche à suivre.")
    if not c.get("site"):
        debut += (" À partir de là, **l'adresse de votre site change** : elle devient "
                   "`https://<votre-identifiant>.github.io/%s/` (l'ancienne adresse ne "
                   "marchera plus).") % nom_depot
    a(debut)
    a("")
    a("1. Ouvrez une session Claude Code sur votre classe (votre dépôt "
        "`<votre-identifiant>/%s`)." % nom_depot)
    a("2. Dites simplement :")
    a("")
    a("   > Je reprends ma classe.")
    a("")
    a("Claude fera alors, sans vous demander de détail technique :")
    a("")
    a("- **la nouvelle adresse** : il écrit votre dépôt dans la fiche d'identité de votre "
        "classe (`classe.yml`, la ligne `depot`), ce qui refait le lien « Voir le site de la classe » "
        "en haut de la page d'accueil du dépôt, le contact des mentions légales du site, et l'aperçu "
        "qui s'affiche quand on colle le lien du site dans un message ;")
    a("- **les contrôles** : la classe est complète et cohérente, l'année couvre toujours tout le "
        "programme, chaque fiche tient sur une page, chaque image a sa licence et son auteur, rien ne "
        "désigne un élève ;")
    a("- **les PDF** : il les fabrique tous et vérifie qu'ils s'impriment bien, une page par fiche "
      "et par planche ;")
    a("- **la publication** : il enregistre et publie, attend que le site soit en ligne à sa "
        "nouvelle adresse, l'ouvre et ouvre un PDF pour s'en assurer, puis vous donne le lien.")
    a("")
    a("**Un réglage à vérifier une fois** : pour que votre site se publie, GitHub doit savoir "
        "qu'il est fabriqué par l'outil. Dans votre dépôt, sur GitHub : *Settings* → *Pages* → "
        "*Build and deployment* → *Source* doit être **GitHub Actions**. Claude le vérifie pendant ce "
        "premier lancement ; s'il ne peut pas le régler lui-même, il vous dit exactement où cliquer.")
    a("")
    a("Si vous aviez installé le site sur votre téléphone, ou donné son lien (à des "
        "collègues, aux familles, dans un code QR), refaites-le avec la nouvelle adresse.")
    a("")
    a("## Ce que vous pouvez dire ensuite")
    a("")
    a("Parlez avec vos mots, depuis votre téléphone si vous voulez, "
        "photos et captures à l'appui. Claude ne vous pose que les "
        "questions qui vous reviennent (pédagogie, goût, diffusion), **une à la fois**, et "
        "vous montre ce qu'il a fait avant de le publier.")
    a("")
    a("| Vous voulez… | Vous dites, par exemple… |")
    a("|---|---|")
    image = ("« Change cette photo de l'imagier », « on ne voit pas bien l'animal »" if imagier
             else "« Change l'image de cette fiche »")
    a("| faire des retours sur une fiche, une image, une séance | « J'ai des retours sur la "
        "période %d », « la consigne de la fiche %d.2 n'est pas claire », « les cases sont trop "
        "petites pour écrire » |" % (exemple_p, exemple_p))
    a("| changer une image | %s, « ce dessin ne va pas sur la fiche » |" % image)
    a("| ajouter ou déplacer quelque chose dans l'année | « Ajoute la comptine jusqu'à 30 en "
      "période %d », « il manque un mot dans les cartes de la période %d » |" % (exemple_p, exemple_p))
    a("| signaler un problème de l'outil, ou une idée pour tous | « Transmets ça à l'outil », « ce "
      "serait bien pour tout le monde », « signale ce problème » |")
    a("| recevoir les nouveautés de l'outil | « Mets l'outil à jour » |")
    a("| partager votre classe avec d'autres enseignants | « Je voudrais partager ma classe » |")
    a("| imprimer | « Refais les PDF », « vérifie que tout s'imprime bien avant que j'imprime la "
      "période %d », « la fiche déborde sur deux pages » |" % exemple_p)
    a("| savoir où vous en êtes | « Qu'est-ce qui a changé depuis la dernière fois ? », "
        "« est-ce que l'année couvre tout le programme ? » |")
    a("")
    a("Ce qui se passe derrière ces phrases :")
    a("")
    a("- **Vos retours** : Claude les trie un par un. Ce qui concerne votre classe, il le "
        "corrige ici, vous le montre et le publie. Ce qui viendrait d'un défaut de l'outil, il le "
        "corrige aussi s'il le peut, et vous propose de le signaler.")
    a("- **« Transmets ça à l'outil »** : Claude rédige un signalement, sans jamais rien qui désigne "
        "un élève, vous le relit et, avec votre accord, l'envoie au moteur Encrine. Quand "
        "une amélioration en sort, toutes les classes peuvent la recevoir.")
    a("- **« Mets l'outil à jour »** : Claude récupère la dernière version de l'outil (les programmes "
        "qui fabriquent les pages, les contrôles, les savoir-faire de Claude), sans toucher à "
        "votre contenu, refait tous les contrôles jusqu'aux PDF, et ne publie que si tout est juste.")
    a("- **« Je voudrais partager ma classe »** : Claude relit d'abord tout ce qui doit l'être "
        "(programme couvert, impression, licences des images, aucun prénom d'élève, aucune photo de "
        "classe, aucun album ni chanson recopié), prépare la présentation de votre classe et "
        "vous demande votre accord. Vous envoyez vous-même la proposition "
        "depuis votre compte. Après une relecture, une **copie relue** de votre classe est "
        "montrée dans « Les classes », la galerie d'encrine.ai ; votre classe et votre site "
        "restent à vous. Vous pouvez la retirer à tout moment : « retire ma classe de "
        "la galerie ».")
    a("")
    a("## Ce qui reste à vous, et ce qui est protégé")
    a("")
    a("- **Votre contenu ne bouge que sur votre demande.** Claude peut proposer, jamais "
        "décider à votre place.")
    a("- **Une mise à jour de l'outil ne touche jamais votre contenu** : ni votre fiche "
        "d'identité (`classe.yml`), ni vos documents, ni vos fiches, ni vos cahiers, "
        "ni votre style.")
    a("- **Vos notes sont gardées.** Quand Claude apprend quelque chose qui ne vaut que pour "
        "votre classe (une décision sur une image, une habitude de la classe), il l'écrit dans la "
        "section « Propre à cette classe » de ses savoir-faire, ou de cette page ; les mises à jour "
        "de l'outil la conservent.")
    a("- **Rien n'est perdu** : chaque changement est enregistré, et peut être défait. Si quelque "
        "chose vous déplaît, dites-le : « reviens à la version d'avant ».")
    a("")
    a("## Les règles de prudence")
    a("")
    a("- **Votre site et votre classe sont publics** : n'importe qui peut les lire, même "
        "ce qui n'est pas encore publié. N'y mettez donc rien de privé.")
    if fictifs:
        a("- **Aucun prénom d'élève réel.** Les prénoms des énoncés (%s) sont inventés ; si "
            "vous en ajoutez, choisissez-les inventés aussi, et "
            "dites-le à Claude." % _liste(fictifs))
    else:
        a("- **Aucun prénom d'élève réel.** Si des énoncés portent des prénoms, "
            "choisissez-les inventés, et dites-le à Claude.")
    a("- **Aucune photo d'élève**, ni de la classe, ni d'un travail d'élève.")
    if signature:
        a("- Ni le nom de l'école, ni la ville : votre signature (« %s ») suffit." % signature)
    else:
        a("- Ni le nom de l'école, ni la ville : le site n'en a pas besoin.")
    a("")
    a("## Si quelque chose ne va pas")
    a("")
    a("1. **Demandez d'abord à Claude**, avec vos mots : « le site ne s'ouvre plus », "
        "« le PDF de la période %d a une page blanche », « je ne comprends pas ce que tu as fait ». Il "
        "cherche, explique sans jargon, et répare." % exemple_p)
    if acc:
        a("2. **Si ça bloque encore, demandez à %s** : %s peut rester parmi les "
            "collaborateurs de votre classe pour vous aider, et ouvrir une session de son "
            "côté. Les décisions sur votre classe restent les vôtres." % (acc_nom, acc_nom))
    else:
        a("2. **Si ça bloque encore**, dites « signale ce problème » : Claude le transmet à "
            "l'outil avec votre accord. Ou écrivez à hello@encrine.ai.")
    # Les insécables avant la coupure à 78 colonnes : textwrap ne coupe
    # qu'aux espaces ordinaires, si bien qu'un « » » ou un « : » reste au
    # mot qu'il accompagne (encrine-ai/moteur#2).
    corps = envelopper(typographie.francais("\n".join(l))) + "\n"
    if propre:
        corps += "\n" + propre.strip("\n") + "\n"
    return corps


def propre(texte_actuel):
    m = SECTION_CLASSE.search(texte_actuel or "")
    return m.group(0) if m else None


def attendu(c):
    actuel = GUIDE.read_text(encoding="utf-8") if GUIDE.is_file() else ""
    return texte(c, propre(actuel))


def ecrire(c):
    if not concerne(c):
        return
    actuel = GUIDE.read_text(encoding="utf-8") if GUIDE.is_file() else ""
    nouveau = texte(c, propre(actuel))
    if nouveau != actuel:
        GUIDE.write_text(nouveau, encoding="utf-8")
    print("%s : le guide de l'enseignant" % NOM)


def anomalies(c):
    a = []
    v = c.get("valide_le")
    if v is not None and not date_validation(c):
        a.append("valide_le : « %s » — la date où l'enseignant a validé le contenu, AAAA-MM-JJ" % v)
    acc = c.get("accompagnant")
    if acc is not None:
        if not (isinstance(acc, dict) and _un(acc.get("nom"))):
            a.append("accompagnant : il faut un bloc avec `nom` (et `github`, facultatif)")
        else:
            for cle in sorted(set(acc) - CLES_ACCOMPAGNANT):
                a.append("accompagnant.%s : clé inconnue (%s)" % (cle, ", ".join(sorted(CLES_ACCOMPAGNANT))))
            g = acc.get("github")
            if g and not re.match(r"^[A-Za-z0-9-]{1,39}$", str(g)):
                a.append("accompagnant.github : « %s » — un identifiant GitHub" % g)
    if not concerne(c):
        return a
    if not GUIDE.is_file():
        a.append("%s : absent — relancer  python3 scripts/classe.py generer" % NOM)
    elif GUIDE.read_text(encoding="utf-8") != attendu(c):
        a.append("%s : périmé — relancer  python3 scripts/classe.py generer (la section "
                 "« Propre à cette classe » est gardée)" % NOM)
    else:
        # ce que le moteur a écrit, sans la section propre à la classe
        a += typographie.anomalies(NOM, SECTION_CLASSE.sub("", GUIDE.read_text(encoding="utf-8")))
    return a
