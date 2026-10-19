---
name: imagier-photos
description: Choisir, fabriquer et vérifier les photographies des cartes de nomenclature de l'imagier Montessori (site/imagier/). À utiliser dès qu'il faut ajouter une espèce, remplacer une image jugée mauvaise, refaire une carte ou une période entière, ou toucher à classe/imagier.py, scripts/chercher-images-imagier.py, scripts/candidats-imagier.py et scripts/verifier-imagier.py. Se déclenche aussi quand la demande ne nomme aucun fichier : « on ne voit pas bien la taupe », « il y a deux animaux sur la carte », « cette photo est trop chargée », « change l'image du hérisson », « refais les images de la période 3 », « il manque le blaireau ». Charger ce skill AVANT de télécharger la moindre image : les pièges décrits ici ont déjà fait publier cinq cartes montrant la mauvaise espèce.
---

# Les photographies de l'imagier

L'imagier est un jeu de cartes de nomenclature Montessori : cinq cahiers A4,
un par période et par milieu, trente-six espèces chacun — dix-huit de faune,
dix-huit de flore. Chaque espèce donne trois cartes : photo + nom, photo seule,
nom seul. Les enfants ont cinq ans et **ne savent pas encore lire** : la
photographie porte seule le sens. Une image ambiguë ne fait pas une carte
médiocre, elle fait une carte fausse.

Les images vivent dans `site/imagier/img/`, en 1100 × 753 px (environ 300 dpi
sur la zone photo des cartes), avec `credits.json` pour l'auteur et la
licence de chacune.

## Les cinq critères d'une bonne carte

Chacun vient d'une carte qu'il a fallu refaire. Les garder en tête pendant
la sélection évite d'y revenir.

1. **Un seul individu.** Deux chevreuils, deux renards qui se battent, une
   poule au milieu de ses poussins, une moule dans une main : l'enfant ne
   sait pas lequel on nomme. Un autre animal au second plan compte aussi —
   le cheval qui portait un héron garde-bœufs sur le dos a été écarté.
   **Une exception, tranchée par l'enseignante** : un second animal *flou*,
   loin derrière, se tolère quand le cliché est nettement plus net et plus
   serré que les autres candidats (« je préfère quand même le premier, même
   s'il y a un autre sanglier derrière » — commit « Le sanglier : la netteté
   l'emporte sur le second animal du fond »). Ne pas « corriger » cette
   carte.
2. **Une image qui convient à des enfants de cinq ans.** Ni saillie, ni
   prédation, ni animal mort, ni crâne. Le vivier d'iNaturalist en est plein
   pour le blaireau, le cochon et le renard : c'est même ce que le tri par
   popularité remonte en premier.
3. **L'animal entier, de face ou de profil.** La taupe vue de dessus n'était
   qu'une masse noire ; de trois quarts, on lui voit le museau pointu et la
   patte-pelle, et elle redevient nommable. Un portrait de tête passe quand
   le trait distinctif y est (les cornes du bouquetin), mais l'animal entier
   vaut mieux.
4. **L'image remplit la carte.** Le recadrage s'en charge et ne laisse plus
   jamais de bande blanche, mais un cliché en hauteur perd beaucoup à la
   coupe : à qualité égale, préférer une photographie en largeur.
5. **Rien autour du sujet.** Le pigeon photographié dans une galerie
   marchande se perdait dans les vitrines. Fond simple, sujet occupant le
   cadre. Pour la flore, viser la plante entière ou l'organe qui l'identifie :
   la feuille palmée et la « bougie » du marronnier, l'écorce blanche du
   bouleau, la feuille piquante et les baies du houx, l'épi du blé.

Pour les animaux de la ferme, un sixième, demandé pour le cochon : **l'animal
doit avoir l'air de la ferme** — un cochon rose plutôt qu'un cochon
sombre et poilu qui ressemble au sanglier, et assez grand dans l'image (le
premier remplaçant était « tout petit »).

## Montrer à l'enseignante

Elle tranche les cas limites, et elle veut voir. Ne lui montrer que les
**candidats réellement en lice, recadrés comme la carte les affichera**
(`CADRE=1 zoom-imagier.py`) : une comparaison qui contenait un cochon déjà
écarté l'a fait choisir une image qui n'était plus proposée.

## La boucle de travail

Quatre étapes, toujours dans cet ordre. Ne jamais sauter la planche de
candidats : **aucun tri automatique ne convient à un imagier** (voir plus
bas), et une image choisie sans être regardée est une image à refaire.

```sh
# 1 — regarder ce qui existe : huit candidates par espèce, numérotées
CANDIDATS_DIR=/tmp/cand python3 scripts/candidats-imagier.py taupe-europe cochon
#    (aussi : « 3-faune », « 5-flore » pour une planche entière ; sans
#     argument, les dix planches)
#    Vivier pauvre — troupeaux et zébus pour « la vache », rosettes
#    hivernales pour « la digitale » ? L'élargir plutôt que se rabattre :
PLACE=97391 MOIS=5,6,7 PAGES=4 NB_CANDIDATS=12 \
  CANDIDATS_DIR=/tmp/cand python3 scripts/candidats-imagier.py digitale

# 2 — départager deux clichés proches, en grand ; CADRE=1 les montre tels
#     que la carte les rognera, ce qui départage souvent à soi seul
CADRE=1 python3 scripts/zoom-imagier.py /tmp/zoom.jpg 291736892 114935359

# 3 — inscrire le choix dans OVERRIDES de classe/imagier.py,
#     puis fabriquer l'image
FORCE=1 python3 scripts/chercher-images-imagier.py taupe-europe cochon

# 4 — contrôler : espèce, crédits, cadrage
python3 scripts/verifier-imagier.py
```

Puis regarder les cartes telles qu'elles s'imprimeront, ce que le contrôle
automatique ne sait pas juger :

```sh
REVUE_DIR=/tmp python3 scripts/revoir-imagier.py 4
```

Cette planche a rattrapé, sur des vignettes que le contrôle déclarait
conformes, deux chats sur un perron, deux ânes lointains, un mètre de
couturière dans la vigne et un bouleau nu en hiver.

Enfin, si le manifeste a changé, régénérer les pages :

```sh
python3 scripts/generer-imagier.py
```

Les PDF ne sont pas versionnés : `scripts/generer-pdf.sh` les refabrique au
déploiement.

## Toujours finir par le PDF, jamais par le HTML

Les deux pires défauts de ce matériel n'existaient pas à l'écran : la page
d'un navigateur s'allonge, une feuille A4 non. Après toute modification du
manifeste ou du gabarit, fabriquer le PDF et le regarder page à page :

```sh
(cd site && python3 -m http.server 8901 &) ; sleep 2
CH=$(ls -d /opt/pw-browsers/chromium*/chrome-linux/chrome | head -1)
"$CH" --headless --no-sandbox --no-pdf-header-footer \
      --print-to-pdf=/tmp/p4.pdf http://127.0.0.1:8901/imagier/periode-4.html
python3 -c "
import pypdfium2 as p
d = p.PdfDocument('/tmp/p4.pdf')
for i in range(len(d)):
    t = d[i].get_textpage().get_text_range().strip()
    print('page %2d : %4d caractères' % (i + 1, len(t)))"
```

**Une page presque vide trahit un débordement.** Le compte de caractères
suffit à la repérer sans tout regarder : une planche de cartes-photos en
fait environ 250, une page à 200 qui n'est pas la dernière est un accident.

Deux pièges, tous deux apparus en doublant le nombre d'espèces :

**Toute série doit se paginer.** Les planches de cartes le faisaient depuis
toujours — six par page —, les étiquettes-mots non : les trente-six tenaient
dans une seule planche, qui dépassait la page et s'imprimait par-dessus les
crédits. Le défaut dormait tant qu'une période comptait dix-huit espèces.
Si une série nouvelle apparaît, la paginer d'emblée
(`ETIQUETTES_PAR_PLANCHE`, `PAR_PLANCHE` dans `generer-imagier.py`).

**Les pages de texte ne prennent pas la hauteur d'une page.** Les planches
de cartes sont une grille de découpe et valent `height: 277mm`. La garde et
les crédits sont du texte : leur imposer cette hauteur exacte ne laisse
aucune tolérance d'arrondi — le pied de la garde de la période 5 partait
seul sur une deuxième page — et un contenu plus long déborde alors sur la
planche voisine au lieu de passer à la page suivante. Elles valent
`height: auto`. Garder une vraie marge plutôt qu'un ajustement au
millimètre : la garde la plus chargée fait 255 mm pour 277 disponibles.

Pour mesurer un débordement plutôt que de rogner au jugé, injecter un script
dans une copie de la page qui écrit la hauteur du contenu dans le titre, puis
lire le titre avec `--dump-dom`.

## Les pièges d'iNaturalist

La source est `https://api.inaturalist.org/v1/observations`, sans limitation
gênante — une période entière de l'imagier se fabrique en quelques
minutes. Trois pièges, tous vérifiés à leurs dépens :

**Chercher par `taxon_id`, jamais par `taxon_name`.** Le paramètre
`taxon_name` accroche aussi les noms vernaculaires et rend des espèces d'un
autre continent : `Meles meles` ramenait le blaireau d'Amérique
(*Taxidea taxus*), `Capreolus capreolus` un rhebok d'Afrique du Sud
(*Pelea capreolus*), `Marmota marmota` une marmotte d'Amérique. Cinq cartes
fausses sont passées ainsi. Les scripts résolvent désormais le nom en
identifiant de taxon ; il reste que le vivier contient des espèces voisines,
que les planches encadrent en rouge — **ne pas choisir une vignette
encadrée de rouge**. Une sous-espèce ou un renommage accepté ne sont pas
encadrés : le loup d'Italie est un loup, *Anemonoides nemorosa* est le nom
actuel de l'anémone des bois.

**Les animaux de la ferme se cherchent avec `captive=true`.** Sans ce
filtre, iNaturalist ne remonte que des populations retournées à l'état
féral : des cochons impossibles à distinguer d'un sanglier, des poules de
rue. Les espèces concernées sont listées dans `DOMESTIQUES`
(`classe/imagier.py`).

**Attention quand une carte est la sous-espèce d'une autre.** Le cochon
(*Sus scrofa domesticus*) est une sous-espèce du sanglier (*Sus scrofa*) :
une recherche `captive=true` sur le sanglier rend neuf cochons de ferme sur
douze candidats. Les planches ne les encadrent pas — une sous-espèce est
normalement la bonne espèce —, et le contrôle les laissait passer pour la
même raison. Il refuse désormais qu'une carte prenne l'espèce d'une autre,
mais **regarder l'animal reste le seul vrai garde-fou** : lire la colonne
« espèce » de l'index des candidats avant de choisir.

**Les plantes cultivées aussi.** Un champ est « captive » au sens
d'iNaturalist. Sans ce filtre, `Beta vulgaris` ne rend que la betterave
maritime sauvage, la vigne aucune grappe et le noyer aucune noix — que des
pieds échappés en bord de route. Les planches acceptent `CAPTIVE=1` pour
cela.

**Le nom scientifique doit se résoudre.** Le résolveur ajoute un filtre de
rang : sans lui, `Glis glis` — le loir — ne se résolvait pas du tout, la
recherche floue rendant des fougères et des graminées avant l'espèce
demandée. Si un ajout d'espèce échoue sur « taxon introuvable », c'est là
qu'il faut regarder.

**Le classement par popularité met en avant le spectaculaire, pas
l'illustratif** : un ours mangeant des pissenlits pour « le pissenlit », un
renard argenté pour « le renard roux », un bourgeon en gros plan pour « le
marronnier ». C'est la raison d'être des planches de candidats.

**Pour une plante, penser à la saison.** Le tri par votes remonte volontiers
des rosettes de feuilles hivernales ou des pieds défleuris : la digitale
n'était qu'une touffe verte sur les quarante premières candidates. `MOIS=5,6,7`
(les mois de floraison de l'espèce) fait apparaître un vrai éventail. Même
remarque pour les arbres : la feuille, la fleur et le fruit ne se
photographient pas au même moment.

Le script ne garde déjà qu'**un cliché par observateur** — sans quoi
quarante candidates sont parfois quarante photos du même pied, prises le
même jour par la même personne.

Quand une espèce résiste, deux filtres sauvent souvent la mise :
`place_id=97391` (l'Europe), qui écarte les espèces voisines d'autres
continents, et `captive=true`, qui rend les animaux de parcs animaliers,
photographiés en plein jour. Le détail des paramètres est dans
[references/inaturalist.md](references/inaturalist.md).

## Ne pas aller sur Wikimedia Commons

`upload.wikimedia.org` limite l'adresse de sortie mutualisée à environ cinq
fichiers par tranche de dix minutes (`429` avec `Retry-After: 600`), et
l'API `commons.wikimedia.org` finit par répondre `429` elle aussi. Une
moisson de l'imagier entier y prendrait des jours. Ni le parallélisme,
ni le regroupement des appels n'y changent rien : la limite porte sur
l'adresse. Le moindre `curl` de vérification relance le compteur.

## Ce que le contrôle vérifie, et ce qu'il ne voit pas

`scripts/verifier-imagier.py` couvre cinq choses : l'espèce de chaque
photographie, la présence de l'auteur et de la licence, le cadrage qui doit
remplir la carte, le **minimum de neuf espèces par groupe** — une convention
de ce dépôt, pas une règle du programme —, et les **chiffres annoncés** dans
le site et les documents.

Ce dernier contrôle vient d'une mésaventure : en doublant l'imagier, seules
les pages générées ont suivi, parce qu'elles comptent le manifeste. Le site
a continué d'annoncer « 9 espèces de faune et 9 de flore » devant un cahier
qui en contenait dix-huit de chaque. Le contrôle compare donc `site/app.js`,
le README, le projet annuel, la programmation et `AGENTS.md` au manifeste.
**Changer le nombre d'espèces oblige à relire ces cinq fichiers** — le
contrôle dira lesquels.

Ce qu'il ne voit pas, et qui demande l'œil : la qualité de l'image (les cinq
critères ci-dessus) et la mise en page imprimée. D'où les deux étapes qui
suivent la moisson, `revoir-imagier.py` et le PDF.

## Licences

Seules CC0, CC BY et CC BY-SA sont acceptées : une carte recadre la
photographie, et une classe partagée doit pouvoir être reprise par une autre
sans condition cachée, donc **une clause NC ou ND est disqualifiante**. L'auteur et la licence sont obligatoires — le script de
moisson refuse une photographie dont il ne retrouve pas les crédits, et
`verifier-imagier.py` le contrôle avant publication.

## Ajouter une espèce

Ajouter le triplet `(slug, nom, taxon)` dans `IMAGIER` de
`classe/imagier.py`, avec le **nom scientifique** — la recherche
par nom vernaculaire est bien moins fiable. Le `nom` est ce qui s'écrit sur
l'étiquette, article compris (« le hérisson »). Puis dérouler la boucle
ci-dessus.

La flore ne se réduit pas aux fleurs : elle comprend arbres, arbustes,
fougères, mousses, graminées, algues et cultures, et chaque période doit
rester variée — un milieu représenté par neuf fleurs serait faux.
**Remplacer une espèce, c'est aussi garder cette variété** : un agent de
test qui remplaçait la fougère par la digitale privait la forêt de sa seule
fougère.

Choisir l'espèce elle-même :

- **caractéristique du milieu et observable en sortie** par la classe ;
- **la forme type plutôt qu'une sous-espèce lointaine** : le loup des
  Alpes, pas le loup grec ;
- une espèce **toxique** reste possible, mais se signale à l'enseignante
  avec la consigne qui va avec (la digitale : on ne la cueille pas) ; une espèce **qui peut faire peur ou mordre**
  (la vipère aspic, dans une Grande Section sur la montagne) se soumet à
  l'enseignant — et l'on **attend sa réponse** au lieu de trancher seul. Sa
  décision est propre à la classe : elle s'écrit dans la section « Propre à
  cette classe », à la fin de ce skill (skill capitaliser), jamais dans le
  texte du moteur.

Changer le nombre d'espèces change le **volume d'impression** — passer de
neuf à dix-huit espèces par groupe a fait passer l'imagier d'environ 45 à 80
pages A4 par an, à plastifier. Le dire à l'enseignante au moment de le
faire, pas après.
