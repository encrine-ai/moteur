# -*- coding: utf-8 -*-
"""Génère les cahiers de cartes-corpus, un par période.

Les fiches d'évaluation X.1 et X.3 réclamaient « 12 cartes-images des
corpus » que rien ne fabriquait. Un cahier par période, sur le modèle de
l'imagier — site/cartes-corpus/periode-N.html, imprimé en PDF par
scripts/generer-pdf.sh — contient :
  1. le mode d'emploi (à quoi servent ces cartes, comment les préparer) ;
  2. les cartes de contrôle  — image + mot en script ;
  3. les cartes-images       — la même image, emplacement du nom vide ;
  4. les étiquettes-mots     — le mot seul, pour le travail de lecture ;
  5. les étiquettes de tri   — les catégories à coller sur les boîtes ;
  6. les crédits des images.

Les images ne sont jamais dupliquées : une carte pointe vers la
photographie de l'imagier (../imagier/img/) ou vers le dessin des fiches
élève (../fiches/img/) quand il en existe déjà un, et seuls les
pictogrammes moissonnés et les dessins fabriqués pour ces cahiers vivent
dans site/cartes-corpus/.

Une période sans carte ou sans corpus dans le manifeste n'a pas de cahier :
elle est sautée, et le script le dit.

Usage : python3 scripts/generer-cartes-corpus.py
"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ICI, "..", "site", "cartes-corpus")
# Le manifeste est du contenu de la classe : son chemin vient de classe.yml.
sys.path.insert(0, ICI)
import classe  # noqa: E402
ns = classe.manifeste("corpus")
CARTES, CORPUS, TRI = ns["CARTES"], ns["CORPUS"], ns.get("TRI") or {}
# Le tri par milieu, s'il y en a un : la période dont le cahier le porte, le
# titre de son bloc, et les étiquettes (TRI_MILIEUX_PERIODE, …_TITRE, TRI_MILIEUX).
TRI_MILIEUX = ns.get("TRI_MILIEUX") or ()
TRI_MILIEUX_PERIODE = ns.get("TRI_MILIEUX_PERIODE")
TRI_MILIEUX_TITRE = ns.get("TRI_MILIEUX_TITRE")
entrees = ns["entrees"]

# Ce qui tient à la classe (milieux, niveau, en-tête) vient de classe.yml.
CLASSE = classe.charger()
MILIEUX = classe.milieux()
# « l’imagier » suivi de l'`intitule` de l'imagier dans le matériel.
IMAGIER = " ".join(["imagier"] + [m["intitule"] for m in CLASSE["materiel"]
                                  if m.get("cle") == "imagier" and m.get("intitule")][:1])

credits_imagier = json.load(open(os.path.join(ICI, "..", "site", "imagier", "img", "credits.json"),
                                 encoding="utf-8"))
credits_fiches = json.load(open(os.path.join(ICI, "..", "site", "fiches", "img", "credits.json"),
                                encoding="utf-8"))

NOM_COULEUR = {i + 1: p["couleur"] for i, p in enumerate(CLASSE["periodes"])}
GROUPE_LABEL = {"milieu": "le milieu", "faune": "la faune", "flore": "la flore"}
PAR_PLANCHE = 6


def echappe(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def classe_mot(nom):
    n = len(nom)
    return " tres-long" if n > 22 else (" long" if n > 16 else "")


def image(slug, source):
    """(chemin, classe) — deux provenances, et deux seulement.

    Les photographies de l'imagier remplissent la carte ; les pictogrammes de
    la banque partagée s'y inscrivent en entier, sur fond blanc, parce que les
    rogner couperait ce qui les rend reconnaissables."""
    genre, valeur = source
    if genre == "imagier":
        return "../imagier/img/%s.jpg" % valeur, "photo"
    c = credits_fiches.get(valeur)
    if not c:
        return "../fiches/img/%s" % valeur, "dessin"     # référence par fichier
    fichier = c["fichier"]
    classe = "photo" if fichier.lower().endswith((".jpg", ".jpeg")) else "dessin"
    return "../fiches/img/%s" % fichier, classe


def repere(p, milieu, groupe):
    """Mention de rangement, la même sur les trois séries : elle situe la
    carte sans jamais nommer le mot, qui est la réponse attendue."""
    return '<div class="repere">période %d · %s · %s</div>' % (
        p, milieu[0].lower() + milieu[1:], GROUPE_LABEL[groupe])


def carte(p, milieu, groupe, slug, nom, source, avec_nom):
    chemin, classe = image(slug, source)
    mot = ('<div class="mot%s">%s</div>' % (classe_mot(nom), echappe(nom))
           if avec_nom else '<div class="mot vide"></div>')
    return ('<div class="carte">'
            '<div class="visuel %s"><img src="%s" alt="%s"></div>'
            '%s%s</div>' % (classe, chemin, echappe(nom) if avec_nom else "",
                            mot, repere(p, milieu, groupe)))


def planches(p, milieu, lot_complet, avec_nom, intitule):
    out = []
    total = (len(lot_complet) + PAR_PLANCHE - 1) // PAR_PLANCHE
    for i in range(total):
        lot = lot_complet[i * PAR_PLANCHE:(i + 1) * PAR_PLANCHE]
        cartes = "\n    ".join(carte(p, milieu, g, s, n, src, avec_nom) for g, s, n, src in lot)
        out.append(
            '<section class="planche">\n'
            '  <div class="entete-planche"><span class="milieu">Période %d · %s</span>'
            '<span>%s — planche %d/%d</span>'
            '<span>Cartes-corpus · @NIVEAU@</span></div>\n'
            '  <div class="cartes">\n    %s\n  </div>\n'
            '</section>' % (p, milieu, intitule, i + 1, total, cartes))
    return "\n".join(out)


def planches_etiquettes(p, milieu, lot_complet):
    """Vingt étiquettes par page au plus, réparties également : 26 mots font
    deux planches de 13, et non une pleine suivie d'une presque vide."""
    out = []
    total = (len(lot_complet) + 19) // 20
    par_page = (len(lot_complet) + total - 1) // total
    for i in range(total):
        lot = lot_complet[i * par_page:(i + 1) * par_page]
        ets = "\n    ".join(
            '<div class="etiquette"><div class="mot%s">%s</div>%s</div>'
            % (classe_mot(n), echappe(n), repere(p, milieu, g)) for g, s, n, _ in lot)
        out.append('<section class="planche">\n'
                   '  <div class="entete-planche"><span class="milieu">Période %d · %s</span>'
                   '<span>Étiquettes-mots (à découper) — planche %d/%d</span>'
                   '<span>Cartes-corpus · @NIVEAU@</span></div>\n'
                   '  <div class="etiquettes">\n    %s\n  </div>\n'
                   '</section>' % (p, milieu, i + 1, total, ets))
    return "\n".join(out)


def planche_tri(p, milieu):
    """Les « boîtes-catégories » des fiches X.1 : des étiquettes à coller sur
    trois barquettes. Le cahier de la période TRI_MILIEUX_PERIODE, qui fait le
    tour des milieux de l'année, porte en plus les étiquettes-milieux."""
    def bloc(titre, intitules):
        cases = "".join('<div class="tri"><div class="mot-tri">%s</div></div>' % echappe(t)
                        for t in intitules)
        return '<h3 class="titre-tri">%s</h3>\n  <div class="tris">%s</div>' % (titre, cases)

    # La fiche de ce cahier-là ne trie pas par catégorie mais par milieu :
    # c'est le tour des corpus de l'année. Le renvoi à la fiche va donc au
    # second bloc dans ce cahier, et au premier partout ailleurs.
    if not TRI.get(p):
        return ""
    if p == TRI_MILIEUX_PERIODE and TRI_MILIEUX:
        corps = [bloc("Pour trier les cartes de ce cahier", TRI[p]),
                 bloc(TRI_MILIEUX_TITRE, TRI_MILIEUX)]
    else:
        corps = [bloc("Pour trier les cartes de ce cahier (fiche %d.1)" % p, TRI[p])]
    return ('<section class="planche">\n'
            '  <div class="entete-planche"><span class="milieu">Période %d · %s</span>'
            '<span>Étiquettes de tri (à coller sur les boîtes)</span>'
            '<span>Cartes-corpus · @NIVEAU@</span></div>\n'
            '  %s\n'
            '</section>' % (p, milieu, "\n  ".join(corps)))


def liste(titre, entrees_groupe):
    lis = "".join('<li><span class="mot-script">%s</span></li>' % echappe(n)
                  for _, _, n, _ in entrees_groupe)
    return '<div><h3>%s</h3><ol>%s</ol></div>' % (titre, lis)


def garde(p, milieu, groupes, total):
    c1, c2, c3 = CORPUS[p]
    return """<section class="planche garde">
  <h1>Les mots de {milieu_min}</h1>
  <p class="sous-titre">Cartes-corpus — période {p} · les trois corpus de vocabulaire de la période</p>

  <h2>Ce que contient ce cahier</h2>
  <p>Les <strong>{total} noms</strong> des trois corpus de la période — <em>{c1}</em>, <em>{c2}</em>, <em>{c3}</em> —
  en cartes à découper, dans les mêmes trois séries que l’imagier :</p>
  <ul>
    <li><strong>Les cartes de contrôle</strong> (image + mot) : modèle et <strong>autocorrection</strong>.</li>
    <li><strong>Les cartes-images</strong> (image seule) : l’emplacement du mot, en pointillés, attend l’étiquette.</li>
    <li><strong>Les étiquettes-mots</strong> (mot seul, en script) : à associer aux images — le travail de <strong>lecture</strong>.</li>
    <li><strong>Les étiquettes de tri</strong> : les catégories à coller sur les boîtes, pour la fiche d’évaluation {p}.1.</li>
  </ul>
  <p class="note">Les <strong>verbes et les adjectifs</strong> des corpus (<em>traverser, hiberner, rugueux…</em>) n’ont pas de carte :
  une image les ambiguïse plus qu’elle ne les enseigne. Ils s’enseignent et s’évaluent dans le <strong>réemploi</strong>, en situation.</p>

  <h2>Préparer le matériel</h2>
  <ol>
    <li>Imprimer en <strong>A4, à 100 %</strong> (sans « ajuster à la page »), sur papier épais (160 à 200 g).</li>
    <li>Découper sur les traits : les cartes sont jointives, un coup de massicot en sépare deux.</li>
    <li><strong>Plastifier</strong>, puis recouper en laissant 2 mm de plastique autour de chaque carte.</li>
    <li>Ranger par corpus, dans trois barquettes portant les <strong>étiquettes de tri</strong> et repérées par le filet {couleur} de la période {p}.</li>
  </ol>

  <div class="encadre">
    <div class="titre-encadre">À quoi servent ces cartes</div>
    <ul class="usages">
      <li><span class="quand">Chaque jour</span> le rituel du « mot du jour » : une carte tirée, nommée, employée dans une phrase.</li>
      <li><span class="quand">Chaque mois</span> le jeu de l’imagier de la grille de suivi : 10 cartes, désigner puis nommer.</li>
      <li><span class="quand">Fiche {p}.1</span> évaluation du vocabulaire : « montre-moi… », « qu’est-ce que c’est ? », puis tri dans les trois boîtes.</li>
      <li><span class="quand">Fiche {p}.3</span> phonologie : frapper les syllabes d’une carte, chercher les mots qui commencent pareil.</li>
    </ul>
  </div>

  <h2>La leçon en trois temps (groupes de 3 à 5 élèves)</h2>
  <ol>
    <li><strong>Je nomme</strong> — l’enseignante pose trois cartes de contrôle : « C’est {exemple}. »</li>
    <li><strong>Je montre</strong> — « Montre-moi {exemple}. » L’élève désigne et déplace la carte.</li>
    <li><strong>Je nomme seul</strong> — « Qu’est-ce que c’est ? »</li>
  </ol>
  <p>On n’introduit que <strong>trois cartes à la fois</strong>, et on ne passe au temps suivant que lorsque le précédent est réussi.</p>

  <h2>Prolongements</h2>
  <ul>
    <li><strong>Catégoriser</strong> : trier avec les étiquettes, puis justifier à l’oral (« comment le sais-tu ? ») — c’est le travail des <strong>hyperonymes</strong>.</li>
    <li><strong>Phonologie</strong> : compter les syllabes, chercher les mots qui riment, localiser un son.</li>
    <li><strong>Lecture</strong> : associer étiquette-mot et carte-image, puis vérifier seul avec les cartes de contrôle.</li>
    <li><strong>Écriture</strong> : copier le mot d’une carte sous son dessin d’observation.</li>
    <li><strong>Mémory</strong> : deux jeux de cartes-images mélangés, ou une carte-image contre son étiquette-mot.</li>
  </ul>

  <h2>Les {total} mots de ce cahier</h2>
  <div class="listes">
    {listes}
  </div>

  <p class="pied-garde">{en_tete}. Crédits des images en dernière page. Mots écrits en script (police Andika).</p>
</section>""".format(
        p=p, milieu_min=milieu[0].lower() + milieu[1:], total=total,
        c1=c1, c2=c2, c3=c3, couleur=NOM_COULEUR[p], en_tete=classe.en_tete(CLASSE),
        exemple=(groupes["milieu"] + groupes["faune"] + groupes["flore"])[0][2],
        listes="\n    ".join(liste("Le milieu", groupes["milieu"])
                             if g == "milieu" else
                             liste("La faune", groupes["faune"]) if g == "faune" else
                             liste("La flore", groupes["flore"]) for g in ("milieu", "faune", "flore")))


def page_credits(lot_complet):
    """Chaque image porte sa provenance. Les deux banques du dépôt sont
    créditées à leur source : iNaturalist pour les photographies d'espèces,
    credits.json des fiches pour les pictogrammes."""
    lignes = []
    for _, slug, nom, source in lot_complet:
        genre, valeur = source
        if genre == "imagier":
            c = credits_imagier.get(valeur, {})
            texte = "photographie %s, licence %s (iNaturalist)" % (
                c.get("auteur", "?"), c.get("licence") or "voir l’observation")
        else:
            c = credits_fiches.get(valeur) or credits_fiches.get(
                os.path.splitext(valeur)[0], {})
            texte = "%s — %s, licence %s" % (c.get("source", "?"),
                                             c.get("auteur", "?"), c.get("licence", "?"))
        lignes.append("<li><strong>%s</strong> — %s.</li>" % (echappe(nom), echappe(texte)))
    return ('<section class="planche credits">\n'
            '  <h2>Crédits des images</h2>\n'
            '  <p>Les <strong>photographies</strong> viennent de l’%s de ce '
            'site (observations d’<strong>iNaturalist</strong>, licences libres). Les '
            '<strong>pictogrammes</strong> viennent de la banque des fiches élève — '
            '<strong>Mulberry Symbols</strong> (CC BY-SA) et, à défaut, <strong>ARASAAC</strong> '
            '(CC BY-NC-SA, Sergio Palao — propriété du Gouvernement d’Aragon). Merci à leurs '
            'auteurs et autrices.</p>\n'
            '  <ul>\n    %s\n  </ul>\n'
            '</section>' % (IMAGIER, "\n    ".join(lignes)))


for p, cle, emoji, milieu, description in MILIEUX:
    groupes = {"milieu": [], "faune": [], "flore": []}
    for _, g, slug, nom, source in entrees(p):
        groupes[g].append((g, slug, nom, source))
    toutes = groupes["milieu"] + groupes["faune"] + groupes["flore"]
    if not toutes or len(CORPUS.get(p) or ()) != 3:
        print("periode-%d — %s : %s dans le manifeste, pas de cahier"
              % (p, milieu, "aucune carte" if not toutes else "pas les trois corpus"))
        continue
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>@NIVEAU@ — Cartes-corpus · Période {p} · {milieu}</title>
<link rel="stylesheet" href="../charte/charte.css">
<link rel="stylesheet" href="cartes-corpus.css">
</head>
<body data-periode="{p}">

{garde}

<!-- ═══ Cartes de contrôle : image + mot ═══ -->
{controle}

<!-- ═══ Cartes-images : l'emplacement du mot est vide ═══ -->
{images}

<!-- ═══ Étiquettes-mots ═══ -->
{etiquettes}

<!-- ═══ Étiquettes de tri ═══ -->
{tri}

{credits}

</body>
</html>
""".format(p=p, milieu=milieu,
           garde=garde(p, milieu, groupes, len(toutes)),
           controle=planches(p, milieu, toutes, True, "Cartes de contrôle (image + mot)"),
           images=planches(p, milieu, toutes, False, "Cartes-images (sans le mot)"),
           etiquettes=planches_etiquettes(p, milieu, toutes),
           tri=planche_tri(p, milieu),
           credits=page_credits(toutes))
    os.makedirs(BASE, exist_ok=True)
    html = html.replace("@NIVEAU@", CLASSE["niveau"]["code"])
    open(os.path.join(BASE, "periode-%d.html" % p), "w", encoding="utf-8").write(html)
    print("periode-%d.html — %s : %d cartes (%d milieu, %d faune, %d flore)"
          % (p, milieu, len(toutes), len(groupes["milieu"]),
             len(groupes["faune"]), len(groupes["flore"])))
