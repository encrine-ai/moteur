# -*- coding: utf-8 -*-
"""Génère les planches de l'imagier Montessori de la classe.

Une page par période (milieu) : site/imagier/periode-N.html, imprimée en PDF
par scripts/generer-pdf.sh. Chaque cahier contient, pour les animaux et les
plantes du milieu que liste le manifeste de l'imagier (classe.yml, `contenu`) :
  1. le mode d'emploi (leçon en trois temps, préparation du matériel) ;
  2. les cartes de contrôle    — photographie + nom en script ;
  3. les cartes-photos         — la même photographie, emplacement du nom vide ;
  4. les étiquettes-mots       — les noms seuls, à associer aux photographies ;
  5. les crédits des images.

Une période sans espèce dans le manifeste n'a pas de cahier : elle est sautée,
et le script le dit.

Usage : python3 scripts/generer-imagier.py
"""
import json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ICI, "..", "site", "imagier")
# Le manifeste est du contenu de la classe : son chemin vient de classe.yml.
sys.path.insert(0, ICI)
import classe  # noqa: E402
ns = classe.manifeste("imagier")
IMAGIER = ns["IMAGIER"]
# Ce qui tient à la classe (milieux, niveau, en-tête) vient de classe.yml.
CLASSE = classe.charger()
MILIEUX = classe.milieux()
COULEURS = [p["couleur"] for p in CLASSE["periodes"]]
# Ce que rassemble l'imagier, dans ses titres (« Imagier » et l'intitulé) :
# l'`intitule` du cahier dans le matériel de classe.yml.
INTITULE = " ".join(["Imagier"] + [m["intitule"] for m in CLASSE["materiel"]
                                   if m.get("cle") == "imagier" and m.get("intitule")][:1])
# Les fragments assemblés portent ce repère, remplacé à l'écriture du cahier.

chemin_credits = os.path.join(BASE, "img", "credits.json")
credits = json.load(open(chemin_credits, encoding="utf-8")) if os.path.exists(chemin_credits) else {}
# le nom scientifique de chaque espèce est porté par le manifeste
taxons = {slug: taxon for _, _, slug, _, taxon in ns["entrees"]()}

GROUPES = {"faune": "faune", "flore": "flore"}
PAR_PLANCHE = 6
# Les étiquettes tiennent en deux colonnes de neuf : au-delà, la planche
# déborde de la page et vient s'imprimer par-dessus les crédits. Le défaut
# est resté invisible tant qu'une période comptait dix-huit espèces.
ETIQUETTES_PAR_PLANCHE = 18


def echappe(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def classe_mot(nom):
    n = len(nom)
    return " tres-long" if n > 22 else (" long" if n > 16 else "")


def repere(p, milieu, groupe):
    """Mention de rangement, identique sur les trois séries : elle situe la
    carte sans jamais nommer l'espèce (ce serait la réponse attendue)."""
    return '<div class="repere">période %d · %s · %s</div>' % (
        p, milieu[0].lower() + milieu[1:], groupe)


def carte(p, milieu, groupe, slug, nom, avec_nom):
    mot = ('<div class="mot%s">%s</div>' % (classe_mot(nom), echappe(nom))
           if avec_nom else '<div class="mot vide"></div>')
    return ('<div class="carte">'
            '<div class="photo"><img src="img/%s.jpg" alt="%s"></div>'
            '%s%s</div>' % (slug, echappe(nom) if avec_nom else "", mot,
                            repere(p, milieu, groupe)))


def planches(p, milieu, entrees, avec_nom, intitule):
    """Découpe la série en pages de 6 cartes."""
    out = []
    total = (len(entrees) + PAR_PLANCHE - 1) // PAR_PLANCHE
    for i in range(total):
        lot = entrees[i * PAR_PLANCHE:(i + 1) * PAR_PLANCHE]
        cartes = "\n    ".join(carte(p, milieu, g, s, n, avec_nom) for g, s, n in lot)
        out.append(
            '<section class="planche">\n'
            '  <div class="entete-planche"><span class="milieu">Période %d · %s</span>'
            '<span>%s — planche %d/%d</span>'
            '<span>%s · @NIVEAU@</span></div>\n'
            '  <div class="cartes">\n    %s\n  </div>\n'
            '</section>' % (p, milieu, intitule, i + 1, total, INTITULE, cartes))
    return "\n".join(out)


def planche_etiquettes(p, milieu, entrees):
    """Découpe la série d'étiquettes en pages, comme les cartes."""
    out = []
    total = (len(entrees) + ETIQUETTES_PAR_PLANCHE - 1) // ETIQUETTES_PAR_PLANCHE
    for i in range(total):
        lot = entrees[i * ETIQUETTES_PAR_PLANCHE:(i + 1) * ETIQUETTES_PAR_PLANCHE]
        ets = "\n    ".join(
            '<div class="etiquette"><div class="mot%s">%s</div>%s</div>'
            % (classe_mot(n), echappe(n), repere(p, milieu, GROUPES[g])) for g, s, n in lot)
        rang = " — planche %d/%d" % (i + 1, total) if total > 1 else ""
        out.append('<section class="planche">\n'
                   '  <div class="entete-planche"><span class="milieu">Période %d · %s</span>'
                   '<span>Étiquettes-mots (à découper)%s</span>'
                   '<span>%s · @NIVEAU@</span></div>\n'
                   '  <div class="etiquettes">\n    %s\n  </div>\n'
                   '</section>' % (p, milieu, rang, INTITULE, ets))
    return "\n".join(out)


def liste(titre, entrees):
    lis = []
    for g, s, n in entrees:
        savant = taxons.get(s, "")
        lis.append('<li><span class="mot-script">%s</span>%s</li>'
                   % (echappe(n), ' <span class="savant">%s</span>' % echappe(savant) if savant else ""))
    return '<div><h3>%s</h3><ol>%s</ol></div>' % (titre, "".join(lis))


def garde(p, milieu, description, faune, flore):
    return """<section class="planche garde">
  <h1>L’imagier de {milieu_min}</h1>
  <p class="sous-titre">Cartes de nomenclature Montessori — période {p} · {description}</p>

  <h2>Ce que contient ce cahier</h2>
  <p>{nf} animaux et {nl} plantes du milieu — arbres, arbustes, fleurs, fougères, mousses, algues ou cultures selon le paysage — en trois séries de cartes à découper :</p>
  <ul>
    <li><strong>Les cartes de contrôle</strong> (photographie + nom) : elles servent de modèle et permettent à l’élève de <strong>vérifier seul</strong> son travail.</li>
    <li><strong>Les cartes-photos</strong> (photographie seule) : l’emplacement du nom, en pointillés, attend l’étiquette.</li>
    <li><strong>Les étiquettes-mots</strong> (nom seul, en script) : à associer aux photographies — c’est le travail de <strong>lecture</strong>.</li>
  </ul>

  <h2>Préparer le matériel</h2>
  <ol>
    <li>Imprimer en <strong>A4, à 100 %</strong> (sans « ajuster à la page »), de préférence sur papier épais (160 à 200 g).</li>
    <li>Découper sur les traits : les cartes sont jointives, un seul coup de massicot sépare deux cartes.</li>
    <li><strong>Plastifier</strong> puis recouper en laissant 2 mm de plastique autour de chaque carte.</li>
    <li>Ranger chaque série dans une enveloppe ou une barquette repérée par le filet de couleur {couleur_nom} de la période {p}.</li>
  </ol>

  <div class="encadre">
    <div class="titre-encadre">La leçon en trois temps (petits groupes de 3 à 5 élèves)</div>
    <ul class="trois-temps">
      <li><span class="temps">1. Je nomme</span> l’enseignante pose trois cartes de contrôle : « C’est {exemple}. »</li>
      <li><span class="temps">2. Je montre</span> « Montre-moi {exemple}. » — l’élève désigne, manipule, déplace la carte.</li>
      <li><span class="temps">3. Je nomme seul</span> « Qu’est-ce que c’est ? » — l’élève dit le mot.</li>
    </ul>
    <p style="margin:1.5mm 0 0">On n’introduit que <strong>trois cartes à la fois</strong>, et on ne passe au temps suivant que lorsque le précédent est réussi.</p>
  </div>

  <h2>Le travail de lecture ({niveau_min})</h2>
  <ol>
    <li>L’élève étale les <strong>cartes-photos</strong>, puis pioche une <strong>étiquette-mot</strong> et la lit.</li>
    <li>Il pose l’étiquette dans l’emplacement pointillé de la photographie qui convient.</li>
    <li>Quand tout est placé, il retourne les <strong>cartes de contrôle</strong> et corrige lui-même : <strong>l’erreur n’est pas sanctionnée, elle est vue</strong>.</li>
  </ol>
  <p><strong>Différenciation :</strong> commencer par 4 à 6 paires seulement ; pour les élèves les plus à l’aise, mélanger la faune et la flore, ou deux milieux (celui-ci et celui d’une autre période), puis demander de trier avant d’associer.</p>

  <h2>Prolongements</h2>
  <ul>
    <li><strong>Tri</strong> : « les animaux » / « les plantes », puis justification orale (« comment le sais-tu ? ») ; trier ensuite les plantes entre <strong>les arbres</strong> et <strong>les autres</strong>.</li>
    <li><strong>Langage</strong> : décrire une photographie pour que les autres devinent de quelle carte il s’agit (jeu du portrait).</li>
    <li><strong>Phonologie</strong> : chercher les mots qui commencent par le même son, compter les syllabes.</li>
    <li><strong>Écriture</strong> : copier le nom d’une carte sous son dessin d’observation.</li>
    <li><strong>Sortie</strong> : emporter quelques cartes pour retrouver l’espèce sur le terrain (arbre du quartier, fleur du talus, algue de la plage).</li>
  </ul>

  <h2>Les {total} espèces de ce cahier</h2>
  <div class="listes">
    {liste_faune}
    {liste_flore}
  </div>

  <p class="pied-garde">{en_tete}. Photographies : iNaturalist, sous licence libre (crédits en dernière page). Noms écrits en script (police Andika, SIL Open Font License).</p>
</section>""".format(
        p=p, milieu_min=milieu[0].lower() + milieu[1:],
        description=description, nf=len(faune), nl=len(flore), total=len(faune) + len(flore),
        couleur_nom=COULEURS[p - 1], niveau_min=CLASSE["niveau"]["libelle"].lower(),
        en_tete=classe.en_tete(CLASSE),
        exemple=(faune + flore)[0][2], liste_faune=liste("La faune", faune), liste_flore=liste("La flore", flore))


def page_credits(p, entrees):
    lignes = []
    for g, s_, n in entrees:
        c = credits.get(s_)
        if not c:
            continue
        lignes.append("<li><strong>%s</strong> (<em>%s</em>) — %s, licence %s.</li>"
                      % (echappe(n), echappe(c.get("taxon", "")), echappe(c["auteur"]),
                         echappe(c["licence"] or "voir la page de l’observation")))
    return ('<section class="planche credits">\n'
            '  <h2>Crédits des photographies</h2>\n'
            '  <p>Les photographies de cet imagier proviennent d’<strong>iNaturalist</strong> '
            '(inaturalist.org). Ce sont des observations de <strong>qualité recherche</strong> — '
            'l’espèce a été confirmée par plusieurs naturalistes — dont les photographies sont '
            'placées sous licence libre (CC0, CC BY ou CC BY-SA). Elles ont été recadrées au format '
            'des cartes ; aucune autre modification n’a été apportée. Merci à leurs auteurs et '
            'autrices.</p>\n'
            '  <ul>\n    %s\n  </ul>\n'
            '</section>' % "\n    ".join(lignes))


for p, cle, emoji, milieu, description in MILIEUX:
    especes = IMAGIER.get(p) or {}
    faune = [("faune", s, n) for s, n, _ in especes.get("faune") or []]
    flore = [("flore", s, n) for s, n, _ in especes.get("flore") or []]
    toutes = faune + flore
    if not toutes:
        print("periode-%d — %s : aucune espèce dans le manifeste, pas de cahier" % (p, milieu))
        continue
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>@NIVEAU@ — {intitule_titre} · Période {p} · {milieu}</title>
<link rel="stylesheet" href="../charte/charte.css">
<link rel="stylesheet" href="imagier.css">
</head>
<body data-periode="{p}">

{garde}

<!-- ═══ Cartes de contrôle : photographie + nom ═══ -->
{controle}

<!-- ═══ Cartes-photos : l'emplacement du nom est vide ═══ -->
{photos}

<!-- ═══ Étiquettes-mots ═══ -->
{etiquettes}

{credits}

</body>
</html>
""".format(p=p, milieu=milieu, intitule_titre=INTITULE.replace("Imagier", "Imagier Montessori", 1),
           garde=garde(p, milieu, description, faune, flore),
           controle=planches(p, milieu, toutes, True, "Cartes de contrôle (photo + nom)"),
           photos=planches(p, milieu, toutes, False, "Cartes-photos (sans le nom)"),
           etiquettes=planche_etiquettes(p, milieu, toutes),
           credits=page_credits(p, toutes))
    chemin = os.path.join(BASE, "periode-%d.html" % p)
    html = html.replace("@NIVEAU@", CLASSE["niveau"]["code"])
    open(chemin, "w", encoding="utf-8").write(html)
    print("periode-%d.html — %s : %d cartes de contrôle, %d cartes-photos, %d étiquettes"
          % (p, milieu, len(toutes), len(toutes), len(toutes)))
