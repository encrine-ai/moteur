---
name: capitaliser
description: Après une modification de Ma Grande Section, verser ce qu'elle a appris là où la prochaine session le trouvera — le bon skill, un script de contrôle, CLAUDE.md, le message de commit — au lieu de le laisser dans la conversation. À utiliser en fin de tâche dès qu'une correction de l'enseignante, une erreur, un piège d'une source d'images, un défaut d'impression ou une décision de pédagogie est apparu ; et quand la demande dit « retiens ça », « note-le pour la prochaine fois », « il ne faut plus que ça arrive », « mets à jour les skills », « qu'est-ce qu'on a appris ? ».
---

# Capitaliser

Ce dépôt s'est construit sur des leçons : une carte refaite, une licence
piégée, une fiche qui débordait. Chacune n'a servi qu'une fois quand elle est
restée dans une conversation, et pour toujours quand elle est entrée dans un
skill ou dans un script. Une session ne se souvient de rien ; le dépôt, si.

## Où va une leçon

| La leçon est… | Elle va dans… | Exemple réel |
|---|---|---|
| vérifiable par une machine | **un script de contrôle**, qui sort en code 1 | une espèce voisine dans le vivier → `verifier-imagier.py` refuse la carte ; un débordement → `verifier-pagination.py` |
| une manière de faire propre à un matériel | **le skill de ce matériel**, avec l'incident qui l'a fait naître | « chicken » était un poulet rôti → `fiches-illustrations` |
| un fait sur une source ou un outil | la section **Images** de `CLAUDE.md` si elle vaut pour tout le dépôt | le bridage de Wikimedia Commons, le filtre `commercial` d'Openverse qui laisse passer ND |
| une exigence du programme | `referentiel/cycle1-gs.yml`, relue contre le BO | — |
| une convention de la classe | **jamais** dans le référentiel : dans le script du matériel concerné | le nombre d'espèces de l'imagier, affirmé à tort comme une règle du programme |
| une préférence de l'enseignante | le skill qu'elle concerne, à la première personne de la règle | « une image doit convenir à des enfants de cinq ans » |

Ordre de préférence : **un contrôle automatique d'abord**, une phrase de
skill ensuite. Une règle écrite se lit quand on pense à la lire ; un contrôle
s'exécute.

## Comment l'écrire

- Donner **la règle et l'incident**, en une ou deux phrases : « Chercher par
  `taxon_id`, jamais par `taxon_name` : ce dernier a fait publier un blaireau
  d'Amérique pour « le blaireau ». » Sans l'incident, la règle a l'air
  arbitraire et finit supprimée.
- Ne pas recopier une règle d'un skill dans un autre : renvoyer vers lui. Une
  copie finit par diverger de l'original.
- Corriger la description d'un skill (le `description:` de son en-tête) quand
  il ne s'est pas ouvert alors qu'il aurait dû : c'est elle qui décide du
  déclenchement. Ajouter la demande manquée aux cas de `tests/` et la mesurer
  avec `scripts/mesurer-declenchement.py` — pas avec le banc d'essai du
  skill-creator, qui ne déclenche jamais rien dans cette version.
- Un chiffre annoncé (« 180 photographies », « 159 attendus », « 5
  vérifications ») est faux dès que la chose change : le faire calculer par le
  script qui l'affiche, ou le vérifier au moment de l'écrire.

## Un contrôle s'éprouve à l'envers

Avant de compter sur un contrôle, **casser la donnée** qu'il surveille (une
carte retirée, une licence ND, un chiffre faux) et vérifier qu'il sort en
code 1. Un contrôle qui ne détecte rien n'est pas un contrôle : celui de
l'imagier acceptait un cochon de ferme sous « le sanglier » (une sous-espèce
est normalement la bonne espèce) ; corrigé, il a été éprouvé en lui donnant
exprès la photographie du cochon, et il l'a refusée. Le message de commit
dit qu'il a été « éprouvé à l'envers », et comment.

Deux autres réflexes de la même famille :

- **aucune opération silencieuse** : un remplacement de texte scripté vérifie
  que sa cible existe (`assert t.count(a) == 1`), une règle `.gitignore` est
  un motif et non un nom recopié — une règle posée sur un nom inexistant a
  laissé committer un fichier de travail ;
- **un outil réécrit deux fois à la main entre dans `scripts/`** :
  `zoom-imagier.py` et `revoir-imagier.py` sont nés ainsi.

Pour essayer un skill avec un agent sans contexte, l'isoler dans un worktree
— et se méfier du répertoire courant, qui persiste d'un appel à l'autre et a
déjà envoyé des éditions dans le mauvais arbre.

## Le message de commit

Il est en français, et son titre dit **ce qui était faux ou ce qui change
pour la classe**, pas la manipulation : « Le navet de la fiche 4 montrait une
carotte », « Les étiquettes débordaient sur les crédits, et la garde sur une
page vide ». Le corps raconte la cause et ce qui l'empêchera de revenir.
Une décision de l'enseignante y est consignée telle quelle (« L'enseignante
tranche : … ») : c'est ce qui empêche une revue future de la « corriger ».
