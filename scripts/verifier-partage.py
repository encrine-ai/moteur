# -*- coding: utf-8 -*-
"""Avant de partager une classe : rien d'un élève, rien d'une œuvre protégée.

Le skill partager-ma-classe le lance avant de proposer la classe à la galerie
de la plateforme. Une classe partagée est publique et d'autres enseignants
partent d'elle : ce contrôle refuse ce qui ne doit jamais s'y trouver.

  1. un prénom d'enfant — dans les documents de l'enseignant et les cahiers ;
     les personnages des énoncés (« Léa a 4 crabes ») se déclarent comme
     fictifs dans classe.yml (`partage.prenoms_fictifs`), un par un, après
     confirmation de l'enseignant ;
  2. une image hors des banques connues — une photo prise en classe, un scan
     de production d'élève ou de page d'album : toute image du dépôt doit être
     une image créditée de l'imagier ou des fiches, ou un fichier du moteur
     (icônes, sprite) ; aucun PDF versionné, aucune image collée en data: ;
  3. un texte reproduit — les paroles d'une chanson, une page d'album : au-delà
     de quatre lignes courtes à la suite, ou d'une citation de plus de 250
     signes, le passage doit être déclaré (`partage.textes_autorises`, avec ses
     premiers mots et la raison : domaine public, écrit par l'enseignant…).
     Citer un titre et son auteur est toujours permis.

Usage :
  python3 scripts/verifier-partage.py          # code 1 s'il reste une anomalie
  python3 scripts/verifier-partage.py tester   # le contrôle vu à l'envers : il
                                               # doit trouver les trois pièges
"""
import json
import pathlib
import re
import sys
import tempfile

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))

# Prénoms donnés le plus souvent aux enfants nés depuis 2015 (fichier des
# prénoms de l'INSEE), et quelques prénoms courants plus anciens. Ceux qui
# sont aussi des mots du matériel (Rose, Iris, Jade, Ambre, Capucine,
# Charlotte, Céleste, Victoire, Constance, Garance, Robin, Martin) en sont
# retirés : la fleur ou la pierre de l'imagier n'est pas un élève.
PRENOMS = """
Gabriel Raphaël Léo Louis Maël Noah Jules Arthur Adam Lucas Hugo Sacha Paul
Isaac Gabin Liam Aaron Nathan Tom Eden Mohamed Ayden Léon Timéo Noé Marius
Victor Mathis Théo Ethan Axel Naël Malo Valentin Antoine Clément Baptiste
Samuel Simon Nino Lenny Kaïs Ibrahim Rayan Enzo Mathéo Tiago Ilyes Amir Imran
Milo Elio Côme Augustin Gaspard Lino Owen Thomas Alexandre Maxime Romain
Nicolas Julien Kylian Mehdi Yanis Ismaël Ali Youssef Ryan Evan Diego Esteban
Lucien Basile Achille Oscar Wassim Joseph Charles Eliott Elliot Benjamin
Matthieu Mathieu Lyam Mattéo Sami Soan Kenzo
Louise Emma Alice Anna Alba Romy Mia Lina Léa Lou Julia Chloé Inès Ines
Agathe Jeanne Juliette Léna Mila Zoé Inaya Lucie Nina Eva Margaux Manon
Camille Sarah Léonie Adèle Clara Lola Romane Louna Mathilde Elena Gabrielle
Sofia Lya Alix Lise Olivia Margot Héloïse Apolline Joséphine Albane Valentine
Thaïs Nour Maëlys Maya Assia Lyana Ayla Elsa Lana Lily Amélia Giulia Mya Aya
Yasmine Fatima Julie Salomé Elise Élise Marie Pauline Laura Océane Anaïs Emilie
Émilie Lisa Noémie Justine Clémence Maëlle Elina Lilou Kenza Aliyah
""".split()

# Une ligne de crédits nomme des auteurs adultes, et doit les nommer.
CREDIT = re.compile(r"CC0|CC BY|licence|domaine public|iNaturalist|Wikimedia|Openverse|"
                    r"ARASAAC|Mulberry|Global Symbols|OpenMoji|SIL Open Font", re.I)
IMAGES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".heic", ".tif", ".tiff", ".bmp"}
IGNORES = {".git", ".agents", ".claude", "node_modules", "_site"}


# Les textes que lit l'enseignant, et que lira qui partira de la classe.
PROSE = ["0*.md", "README.md", "03-progressions/*.md", "04-evaluations/*.md",
         "site/fiches/*.html", "site/imagier/*.html", "site/cartes-corpus/*.html"]
# Plus les données de la classe, où un prénom n'a pas davantage sa place.
DONNEES = ["classe.yml", "classe/*"]


def _documents(racine, motifs=PROSE + DONNEES):
    """Les fichiers de la classe : ceux de l'enseignant et les cahiers fabriqués."""
    vus = set()
    for m in motifs:
        for f in sorted(racine.glob(m)):
            if f.is_file() and f not in vus:
                vus.add(f)
                yield f


def _sans_titres(ligne):
    """Retire ce qui est cité comme un titre : *L'école de Léon*, <em>…</em>."""
    ligne = re.sub(r"<(em|i|cite)\b[^>]*>.*?</\1>", " ", ligne)
    ligne = re.sub(r"(?<![\w*])\*[^*\n]+\*(?!\*)", " ", ligne)
    return re.sub(r"(?<!\w)_[^_\n]+_(?!\w)", " ", ligne)


def prenoms(racine, partage):
    fictifs = set(partage.get("prenoms_fictifs") or [])
    motif = re.compile(r"(?<![\w’'-])(%s)(?![\w-])" % "|".join(map(re.escape, PRENOMS)))
    trouves = {}
    for f in _documents(racine):
        for i, ligne in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if CREDIT.search(ligne):
                continue
            for m in motif.finditer(_sans_titres(ligne)):
                if m.group(1) not in fictifs:
                    trouves.setdefault(m.group(1), "%s:%d" % (f.relative_to(racine), i))
    return ["prénom « %s » (%s) : un élève ? Sinon, le déclarer dans "
            "partage.prenoms_fictifs" % (p, ou) for p, ou in sorted(trouves.items())]


def _auto_fiches(racine):
    """Les formes simples des fiches que chercher-pictos.py fabrique lui-même."""
    src = (racine / "scripts" / "chercher-pictos.py")
    if not src.exists():
        return set()
    m = re.search(r"AUTO = \{([^}]*)\}", src.read_text(encoding="utf-8"))
    return set(re.findall(r'"([^"]+)"', m.group(1))) if m else set()


def _credites(dossier):
    chemin = dossier / "credits.json"
    if not chemin.exists():
        return set()
    return {c.get("fichier", k) for k, c in json.loads(chemin.read_text(encoding="utf-8")).items()}


def images(racine):
    anomalies = []
    banques = {"site/fiches/img": _credites(racine / "site/fiches/img"),
               "site/imagier/img": _credites(racine / "site/imagier/img")}
    auto = _auto_fiches(racine)
    for f in sorted(racine.rglob("*")):
        rel = f.relative_to(racine)
        if not f.is_file() or rel.parts[0] in IGNORES:
            continue
        ext = f.suffix.lower()
        if ext == ".pdf":
            anomalies.append("%s : un PDF versionné (les PDF se fabriquent au déploiement ; "
                             "un scan ?)" % rel)
            continue
        if ext not in IMAGES:
            continue
        dossier = str(rel.parent)
        if dossier in banques:
            if f.name not in banques[dossier] and f.stem not in auto:
                anomalies.append("%s : image sans crédit dans la banque (photo de classe, "
                                 "scan ?)" % rel)
        elif dossier == "site/icones" and f.name.startswith("favicon"):
            pass
        elif rel.parts[:2] == ("site", "charte") and ext == ".svg":
            pass
        else:
            anomalies.append("%s : image hors des banques créditées (photo, scan ?)" % rel)
    for f in _documents(racine):
        texte = f.read_text(encoding="utf-8")
        if re.search(r"data:image/(png|jpe?g|webp|gif|heic)", texte, re.I):
            anomalies.append("%s : une image collée dans la page (data:) — photo ou scan ?"
                             % f.relative_to(racine))
        for src in re.findall(r'<img[^>]+src="(https?://[^"]+)"', texte):
            anomalies.append("%s : image chargée d'ailleurs (%s)" % (f.relative_to(racine), src))
    return anomalies


def _autorise(passage, autorises):
    debut = re.sub(r"\W+", " ", passage).strip().lower()
    return any(debut.startswith(re.sub(r"\W+", " ", a.get("debut", "")).strip().lower())
               and a.get("debut") for a in autorises)


def textes(racine, partage):
    autorises = partage.get("textes_autorises") or []
    anomalies = []
    for f in _documents(racine, PROSE):
        texte = f.read_text(encoding="utf-8")
        rel = f.relative_to(racine)
        if f.suffix == ".html":
            # des vers : au moins quatre segments courts séparés par <br> dans un même bloc
            for bloc in re.findall(r"<(?:p|div|li|td)\b[^>]*>(.*?)</(?:p|div|li|td)>", texte, re.S):
                segments = [re.sub(r"<[^>]+>", "", s).strip() for s in re.split(r"<br\s*/?>", bloc)]
                segments = [s for s in segments if s]
                if len(segments) >= 4 and all(len(s) <= 70 for s in segments) \
                        and not _autorise(segments[0], autorises):
                    anomalies.append("%s : %d vers à la suite (« %s… ») — des paroles "
                                     "reproduites ?" % (rel, len(segments), segments[0][:40]))
        else:
            run = []
            for i, ligne in enumerate(texte.split("\n") + [""], 1):
                t = ligne.strip()
                court = t and len(t) <= 70 and not re.match(r"^([#|*\-+]|\d+[.)]|```)", t)
                if court:
                    run.append((i, t.lstrip("> ")))
                    continue
                if len(run) >= 4 and not _autorise(run[0][1], autorises):
                    anomalies.append("%s:%d : %d lignes courtes à la suite (« %s… ») — des "
                                     "paroles ou une page d'album reproduites ?"
                                     % (rel, run[0][0], len(run), run[0][1][:40]))
                run = []
        for m in re.finditer(r"«([^»]{250,})»", texte):
            if not _autorise(m.group(1), autorises):
                anomalies.append("%s : une citation de %d signes (« %s… ») — un extrait "
                                 "d'album ?" % (rel, len(m.group(1)), m.group(1).strip()[:40]))
    return anomalies


def verifier(racine, partage):
    resultats = [("Prénoms", prenoms(racine, partage)),
                 ("Images", images(racine)),
                 ("Textes reproduits", textes(racine, partage))]
    total = 0
    for titre, anomalies in resultats:
        print("%s : %s" % (titre, "rien à signaler" if not anomalies else
                           "%d anomalie(s)" % len(anomalies)))
        for a in anomalies:
            print("  ✘ " + a)
        total += len(anomalies)
    print("Partage : %d anomalie(s)" % total)
    return total


def tester():
    """À l'envers : une classe piégée doit être refusée sur les trois points."""
    with tempfile.TemporaryDirectory() as d:
        r = pathlib.Path(d)
        (r / "03-progressions").mkdir()
        (r / "03-progressions" / "01-maths.md").write_text(
            "# Maths\n\nKenzo a gagné le jeu de l'oie.\n\n"
            "Il était un petit navire\nQui n'avait ja-ja-jamais navigué\n"
            "Ohé, ohé, matelot\nMatelot navigue sur les flots\n\nFin.\n", encoding="utf-8")
        (r / "site").mkdir()
        (r / "site" / "photo-de-classe.jpg").write_bytes(b"\xff\xd8\xff")
        nb = {"Prénoms": len(prenoms(r, {})), "Images": len(images(r)),
              "Textes": len(textes(r, {}))}
        fictif = len(prenoms(r, {"prenoms_fictifs": ["Kenzo"]}))
        ok = all(nb.values()) and fictif == 0
        print("Test à l'envers :", nb, "— prénom déclaré fictif :", fictif)
        print("le contrôle voit les trois pièges" if ok else "✘ le contrôle laisse passer un piège")
        return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "tester":
        sys.exit(tester())
    import classe
    sys.exit(1 if verifier(classe.RACINE, classe.charger().get("partage") or {}) else 0)
