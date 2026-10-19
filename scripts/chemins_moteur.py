# -*- coding: utf-8 -*-
"""Les chemins du moteur : la seule liste de ce qui, dans le dépôt d'une
classe, appartient au moteur.

Deux skills et un agent s'en servent, et aucun ne la recopie :
  - synchroniser-moteur copie ces fichiers-là, et eux seuls, depuis le moteur ;
  - remonter-au-moteur ne montre que leur diff dans une remontée ;
  - l'agent moteur (sa procédure, trier-remontees, vit dans encrine-ai/agents)
    ne reprend qu'eux du commit d'une classe.

Une liste écrite dans un skill vieillit : celle de la commande de copie
oubliait `site/modele.js`, `site/gabarits.js`, `site/appli.js` et
`site/marque/`, que sa propre table annonçait (« site/*.js sauf classe.js »).
D'où ce fichier, lu par tous.

Usage (à la racine du dépôt) :
  python3 scripts/chemins_moteur.py ou                  # « moteur » si ce dépôt EST le moteur, sinon « classe »
  python3 scripts/chemins_moteur.py chemins             # les chemins, au format de git, pour « git … -- $(…) »
  python3 scripts/chemins_moteur.py fichiers [<commit>] # les fichiers du moteur, ici ou dans un commit
  python3 scripts/chemins_moteur.py ecarts <commit>     # les fichiers du moteur qui diffèrent ici de <commit>
  python3 scripts/chemins_moteur.py version [<réf>] [--ecrire]
                                     # le commit de <réf> (moteur/main) dont les fichiers du moteur
                                     # égalent le mieux ceux d'ici ; --ecrire le met dans moteur.version
                                     # (une classe dont moteur.version est null : la copie d'un modèle
                                     # par « Use this template » n'a aucun historique commun avec lui)
  python3 scripts/chemins_moteur.py ecrire-version <sha>  # moteur.version, après une synchronisation
  python3 scripts/chemins_moteur.py copier <commit> [--depuis <version>]
                                     # copie la couche moteur de <commit> (index compris) ; refuse dans le moteur
  python3 scripts/chemins_moteur.py verifier            # dans une classe : rien de ce qui est propre au moteur
  python3 scripts/chemins_moteur.py bilan [--depuis <version>]
                                     # après une synchronisation : chaque fichier changé (depuis HEAD) est-il
                                     # du moteur, refait, ou du contenu ? code 1 si contenu ; avec --depuis,
                                     # signale aussi une retouche locale du moteur que la copie écrase

« Ce dépôt est le moteur » : `depot` de classe.yml, ou à défaut le dépôt de
`git remote get-url origin`, est `moteur.depot`. On n'y synchronise rien et
on n'y remonte rien : on corrige sur place.

Depuis un autre script :  from chemins_moteur import ou, est_du_moteur
"""
import fnmatch
import pathlib
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML requis :  pip install pyyaml")

RACINE = pathlib.Path(__file__).resolve().parent.parent

# La couche moteur. Un chemin qui finit par « / » est un dossier, entier ;
# un « * » ne passe pas d'un dossier à l'autre (site/*.js ne prend pas
# site/charte/gabarits.js, qui est fabriqué).
MOTEUR = [
    "scripts/",
    "referentiel/",                 # la liste du programme et le calendrier officiel de chaque année
    ".agents/skills/",              # les skills, au standard ouvert
    ".claude/skills",               # le lien symbolique qui y renvoie, pour Claude Code
    ".github/workflows/",
    "tests/",
    "site/*.js",
    "site/*.html",
    "site/*.css",
    "site/marque/",                 # le logo et les polices d'Encrine (« Conçu avec Encrine »)
    "site/charte/socle.css",
    "site/charte/composants.css",
    "site/charte/polices/",         # Andika, la police de l'élève
    "site/fiches/fiches.css",
    "site/imagier/imagier.css",
    "site/cartes-corpus/cartes-corpus.css",
]

# Dans les motifs, mais fabriqués pour la classe : jamais copiés, refaits
# par `python3 scripts/classe.py generer`.
FABRIQUES = [
    "site/classe.js",
    "site/sw.js",
]

# Propre au dépôt du moteur : n'arrive jamais dans une classe. (La boîte du
# moteur — qualifier, intégrer, propager — n'est plus un skill d'ici : c'est
# la procédure de l'agent moteur, dans encrine-ai/agents, jamais chez un
# enseignant.)
PROPRES_AU_MOTEUR = [
    ".github/workflows/controles.yml",          # les contrôles des demandes de fusion du moteur
]

NON_DEFINI = (None, "", "à définir")

# Ce que `classe.py generer` refait pour la classe après une copie : un
# changement y est attendu (le bloc de tête du README, lui, se relit).
REFAITS = [
    "site/classe.json", "site/classe.js", "site/sw.js", "site/manifest.webmanifest",
    "site/favicon.ico", "site/icones/", "site/charte/charte.css",
    "site/charte/gabarits.js", "site/charte/icones.svg", "README.md",
    "PRISE-EN-MAIN.md",             # le guide de l'enseignant (scripts/prise_en_main.py), section propre gardée
]


def _correspond(chemin, motif):
    if "*" in motif:
        return (chemin.count("/") == motif.count("/")
                and fnmatch.fnmatchcase(chemin, motif))
    base = motif.rstrip("/")
    return chemin == base or chemin.startswith(base + "/")


def est_du_moteur(chemin):
    """Ce fichier (relatif à la racine) est-il de la couche moteur copiée ?"""
    return (any(_correspond(chemin, m) for m in MOTEUR)
            and not any(_correspond(chemin, m) for m in FABRIQUES + PROPRES_AU_MOTEUR))


def chemins():
    """Les chemins au format de git (pathspec), exclusions comprises."""
    sortie = []
    for m in MOTEUR:
        sortie.append(":(glob)" + m if "*" in m else m.rstrip("/"))
    for m in FABRIQUES + PROPRES_AU_MOTEUR:
        sortie.append(":(exclude,glob)" + m if "*" in m else ":(exclude)" + m.rstrip("/"))
    return sortie


def _git(*args, entree=None, ok=(0,)):
    r = subprocess.run(["git", "-C", str(RACINE)] + list(args), input=entree,
                       capture_output=True, text=True)
    if r.returncode not in ok:
        sys.exit("git %s : %s" % (" ".join(args[:3]), r.stderr.strip()))
    return r.stdout


def fichiers(commit=None):
    """Les fichiers du moteur suivis ici, ou dans l'arbre d'un commit."""
    if commit:
        tous = _git("ls-tree", "-r", "--name-only", commit).splitlines()
    else:
        tous = _git("ls-files").splitlines()
    return sorted(f for f in tous if est_du_moteur(f))


def _classe():
    return yaml.safe_load((RACINE / "classe.yml").read_text(encoding="utf-8")) or {}


def depot_du_remote(url):
    """« propriétaire/dépôt » depuis une adresse de remote (https, ssh, proxy)."""
    if not url:
        return None
    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    morceaux = [m for m in re.split(r"[/:]", url) if m]
    return "/".join(morceaux[-2:]) if len(morceaux) >= 2 else None


def ou(c=None):
    """« moteur » si ce dépôt est le moteur lui-même, sinon « classe »."""
    c = c if c is not None else _classe()
    moteur = (c.get("moteur") or {}).get("depot")
    r = subprocess.run(["git", "-C", str(RACINE), "remote", "get-url", "origin"],
                       capture_output=True, text=True)
    origin = depot_du_remote(r.stdout) if r.returncode == 0 else None
    courants = {d for d in (c.get("depot"), origin) if d not in NON_DEFINI}
    return "moteur" if moteur and moteur in courants else "classe"


# La section propre à la classe d'un skill : ce que la classe a appris pour
# elle seule (son thème, une décision de l'enseignant sur une espèce…), à la
# fin du SKILL.md, entre deux marqueurs seuls sur leur ligne. Le moteur n'en
# porte jamais ; `copier` la garde et la repose à la fin du skill neuf, si
# bien qu'une synchronisation ne l'écrase pas, et l'agent la lit avec le
# skill. Elle commence par un titre « ## Propre à cette classe ».
CLASSE_DEBUT, CLASSE_FIN = "<!-- classe:debut -->", "<!-- classe:fin -->"
SECTION_CLASSE = re.compile(r"\n*^%s$.*?^%s$\n?" % (re.escape(CLASSE_DEBUT), re.escape(CLASSE_FIN)),
                            re.S | re.M)
SKILL = re.compile(r"^\.agents/skills/[^/]+/SKILL\.md$")


def sans_classe(texte):
    """Le SKILL.md sans sa section propre à la classe."""
    return SECTION_CLASSE.sub("\n", texte).rstrip("\n") + "\n"


def section_classe(texte):
    m = SECTION_CLASSE.search(texte)
    return m.group(0).strip("\n") if m else None


def _hors_fabrique(f, texte):
    """Le fichier sans ce que la classe y ajoute par construction : le bloc
    du titre et de l'aperçu de lien d'index.html (refait par `classe.py
    generer`), la section propre à la classe d'un skill."""
    if SKILL.match(f):
        return sans_classe(texte)
    if f == "site/index.html":
        try:
            sys.path.insert(0, str(RACINE / "scripts"))
            import apercu
            return apercu.sans_bloc(texte)
        except Exception:
            return texte
    return texte


def _retouche(f):
    return f == "site/index.html" or bool(SKILL.match(f))


def _meme_hors_bloc(commit, f):
    ici = (RACINE / f).read_text(encoding="utf-8")
    la = _git("show", "%s:%s" % (commit, f))
    return _hors_fabrique(f, ici) == _hors_fabrique(f, la)


def _meme_hors_bloc_head(commit, f):
    return (_hors_fabrique(f, _git("show", "HEAD:%s" % f))
            == _hors_fabrique(f, _git("show", "%s:%s" % (commit, f))))


def ecarts(commit):
    """[(état, fichier)] : M modifié ici, A présent ici seulement, D absent ici."""
    sortie = _git("diff", "--no-renames", "--name-status", commit, "--", *chemins())
    lignes = [tuple(l.split("\t", 1)) for l in sortie.splitlines() if l.strip()]
    return [(e, f) for e, f in lignes
            if not (e == "M" and _retouche(f) and _meme_hors_bloc(commit, f))]


def version(ref="moteur/main", limite=1000):
    """Le commit de `ref` dont les fichiers du moteur égalent le mieux ceux
    d'ici : le moins d'écarts, et à égalité le plus récent. (sha court, écarts)"""
    meilleur = None
    for sha in _git("rev-list", "--max-count=%d" % limite, ref).split():
        n = len(ecarts(sha))
        if meilleur is None or n < meilleur[1]:
            meilleur = (sha, n)
            if n == 0:
                break
    if meilleur is None:
        sys.exit("%s : aucun commit — git fetch moteur main d'abord" % ref)
    return _git("rev-parse", "--short=7", meilleur[0]).strip(), meilleur[1]


def ecrire_version(sha):
    """moteur.version dans classe.yml, sans toucher au reste du fichier."""
    f = RACINE / "classe.yml"
    lignes = f.read_text(encoding="utf-8").split("\n")
    dans = False
    for i, l in enumerate(lignes):
        if re.match(r"^moteur:\s*$", l):
            dans = True
            continue
        if dans and not l.startswith((" ", "\t")) and l.strip():
            break
        if dans and re.match(r"^\s+version:", l):
            lignes[i] = re.sub(r"version:.*$", "version: %s" % sha, l)
            f.write_text("\n".join(lignes), encoding="utf-8")
            return True
    return False


def copier(commit, depuis=None):
    if ou() == "moteur":
        sys.exit("Ce dépôt est le moteur : rien à synchroniser, on corrige sur place.")
    nouveaux = fichiers(commit)
    # les sections propres à la classe, gardées avant la copie
    sections = {}
    for f in fichiers():
        if SKILL.match(f) and (RACINE / f).is_file():
            sec = section_classe((RACINE / f).read_text(encoding="utf-8"))
            if sec:
                sections[f] = sec
    lien = RACINE / ".claude" / "skills"
    if lien.is_dir() and not lien.is_symlink():
        # une classe d'avant le lien : son vrai dossier cède la place au lien
        # (ses leçons propres ont été remontées à l'étape 0)
        _git("rm", "-rq", ".claude/skills")
        subprocess.run(["rm", "-rf", str(lien)], check=True)
    _git("checkout", commit, "--pathspec-from-file=-", "--pathspec-file-nul", "--",
         entree="\0".join(nouveaux))
    _git("rm", "-rqf", "--ignore-unmatch", "--", *[m.rstrip("/") for m in PROPRES_AU_MOTEUR])
    reposees, orphelines = [], []
    for f, sec in sorted(sections.items()):
        cible = RACINE / f
        if not cible.is_file():
            # le skill a disparu du moteur : la section se garde à part
            cible = RACINE / "classe" / ("notes-%s.md" % f.split("/")[2])
            cible.write_text(sec + "\n", encoding="utf-8")
            orphelines.append(str(cible.relative_to(RACINE)))
            _git("add", "--", str(cible.relative_to(RACINE)))
            continue
        cible.write_text(sans_classe(cible.read_text(encoding="utf-8")) + "\n" + sec + "\n",
                         encoding="utf-8")
        _git("add", "--", f)
        reposees.append(f)
    retires, gardes = [], []
    if depuis:
        # ce que le moteur a retiré depuis la version de la classe : retiré
        # ici aussi, s'il n'a pas été retouché dans la classe
        ici = set(fichiers())
        for f in sorted(set(fichiers(depuis)) - set(nouveaux)):
            if f not in ici:
                continue
            r = subprocess.run(["git", "-C", str(RACINE), "diff", "--quiet", depuis, "--", f])
            if r.returncode == 0:
                _git("rm", "-q", "--", f)
                retires.append(f)
            else:
                gardes.append(f)
    seuls_ici = sorted(set(fichiers()) - set(nouveaux))
    print("%d fichiers du moteur copiés depuis %s" % (len(nouveaux), commit))
    for f in reposees:
        print("  section propre à la classe gardée : %s" % f)
    for f in orphelines:
        print("  ⚠ skill disparu du moteur : sa section propre à la classe est gardée dans %s" % f)
    for f in retires:
        print("  retiré (le moteur l'a retiré) : %s" % f)
    for f in gardes:
        print("  ⚠ gardé : %s — le moteur l'a retiré, mais il a été retouché ici" % f)
    for f in seuls_ici:
        if f not in gardes:
            print("  · seulement dans cette classe : %s" % f)


def _sections_mal_formees(moteur):
    anomalies = []
    for f in fichiers():
        if not SKILL.match(f) or not (RACINE / f).is_file():
            continue
        t = (RACINE / f).read_text(encoding="utf-8")
        n_debut = len(re.findall(r"^%s$" % re.escape(CLASSE_DEBUT), t, re.M))
        n_fin = len(re.findall(r"^%s$" % re.escape(CLASSE_FIN), t, re.M))
        if moteur and (n_debut or n_fin):
            anomalies.append("%s : une section propre à une classe dans le moteur — elle vit dans "
                             "la classe, jamais ici" % f)
        elif (n_debut, n_fin) not in ((0, 0), (1, 1)):
            anomalies.append("%s : la section propre à la classe doit avoir un %s et un %s"
                             % (f, CLASSE_DEBUT, CLASSE_FIN))
        elif n_debut and sans_classe(t) + "\n" + section_classe(t) + "\n" != t:
            anomalies.append("%s : la section propre à la classe doit finir le fichier "
                             "(la synchronisation l'y repose)" % f)
    return anomalies


def verifier():
    if ou() == "moteur":
        anomalies = _sections_mal_formees(True)
        for a in anomalies:
            print("✘ " + a)
        print("Dépôt du moteur : %d anomalie(s)" % len(anomalies))
        return 1 if anomalies else 0
    anomalies = ["%s : propre au dépôt du moteur, à retirer (git rm -r)" % m.rstrip("/")
                 for m in PROPRES_AU_MOTEUR if (RACINE / m.rstrip("/")).exists()]
    anomalies += _sections_mal_formees(False)
    for a in anomalies:
        print("✘ " + a)
    print("Couche moteur : %d anomalie(s)" % len(anomalies))
    return 1 if anomalies else 0


def bilan(depuis=None):
    """Chaque fichier changé depuis HEAD (index et arbre) : moteur, refait, ou
    contenu de la classe. classe.yml ne peut changer que par moteur.version.
    Avec `depuis` (l'ancienne moteur.version), un fichier du moteur que la
    classe avait retouché (HEAD ≠ depuis) est signalé : la copie l'écrase."""
    sortie = _git("status", "--porcelain", "--untracked-files=all", "--no-renames")
    retouches = set()
    if depuis:
        retouches = {f for e, f in (tuple(l.split("\t", 1)) for l in _git(
            "diff", "--no-renames", "--name-status", depuis, "HEAD", "--", *chemins()).splitlines()
            if l.strip()) if e == "M" and not (_retouche(f) and _meme_hors_bloc_head(depuis, f))}
    contenu = 0
    for l in sortie.splitlines():
        f = l[3:]
        if est_du_moteur(f) or any(_correspond(f, m) for m in PROPRES_AU_MOTEUR):
            genre = "moteur"
            if f in retouches:
                genre += " ⚠ retouché ici depuis %s : la copie l'écrase (remonté ? à réappliquer ?)" % depuis
        elif any(_correspond(f, m) for m in REFAITS):
            genre = "refait" + {"README.md": " (relire : seul le bloc de tête change)",
                                "PRISE-EN-MAIN.md": " (relire : la section propre à la classe est gardée)"}.get(f, "")
        elif f == "classe.yml":
            avant = yaml.safe_load(_git("show", "HEAD:classe.yml")) or {}
            apres = _classe()
            for c in (avant, apres):
                (c.get("moteur") or {}).pop("version", None)
            genre = "moteur.version seulement" if avant == apres else "✘ CONTENU (classe.yml)"
        else:
            genre = "✘ CONTENU"
        if genre.startswith("✘"):
            contenu += 1
        print("%-2s %-60s %s" % (l[:2].strip(), f, genre))
    print("Contenu de la classe touché : %d fichier(s)" % contenu)
    return 1 if contenu else 0


def main(args):
    if not args:
        sys.exit(__doc__)
    cmd, reste = args[0], args[1:]
    if cmd == "ou":
        print(ou())
    elif cmd == "chemins":
        print("\n".join(chemins()))
    elif cmd == "fichiers":
        print("\n".join(fichiers(reste[0] if reste else None)))
    elif cmd == "ecarts" and reste:
        for etat, f in ecarts(reste[0]):
            print("%s\t%s" % (etat, f))
    elif cmd == "version":
        refs = [a for a in reste if not a.startswith("--")]
        sha, n = version(refs[0] if refs else "moteur/main")
        print(sha)
        print("%s : %s" % (sha, "les fichiers du moteur sont identiques" if n == 0
                           else "%d fichier(s) du moteur diffèrent — voir  ecarts %s" % (n, sha)),
              file=sys.stderr)
        if "--ecrire" in reste:
            if not ecrire_version(sha):
                sys.exit("classe.yml : pas de `moteur.version` à remplir")
            print("moteur.version : %s écrit dans classe.yml" % sha, file=sys.stderr)
    elif cmd == "ecrire-version" and reste:
        sha = _git("rev-parse", "--short=7", reste[0]).strip()
        if not ecrire_version(sha):
            sys.exit("classe.yml : pas de `moteur.version` à remplir")
        print("moteur.version : %s écrit dans classe.yml" % sha)
    elif cmd == "copier" and reste:
        depuis = reste[reste.index("--depuis") + 1] if "--depuis" in reste else None
        copier(reste[0], depuis)
    elif cmd == "verifier":
        return verifier()
    elif cmd == "bilan":
        return bilan(reste[reste.index("--depuis") + 1] if "--depuis" in reste else None)
    else:
        sys.exit(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
