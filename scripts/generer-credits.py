# -*- coding: utf-8 -*-
"""Ajoute (ou régénère) la page « Crédits des images » à la fin de chaque
cahier de fiches, à partir des images réellement utilisées et de
site/fiches/img/credits.json (pictogrammes Mulberry Symbols et ARASAAC,
photographies Wikimedia Commons / Openverse).

Les cahiers sont ceux que déclare le matériel de classe.yml (évaluation et
entraînement) ; un cahier déclaré mais absent est sauté, et le script le dit.
"""
import json, os, re, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import classe  # noqa: E402

BASE = os.path.join(ICI, "..", "site", "fiches")
credits = json.load(open(os.path.join(BASE, "img", "credits.json"), encoding="utf-8"))
par_fichier = {v["fichier"]: dict(v, slug=k) for k, v in credits.items()}

FICHIERS = [os.path.relpath(source, "fiches") for cle in ("evaluation", "entrainement")
            for _, _, source, _ in classe.cahiers(cle=cle)]

for nom in FICHIERS:
    chemin = os.path.join(BASE, nom)
    if not os.path.exists(chemin):
        print(f"{nom} : déclaré dans classe.yml mais absent, sauté")
        continue
    txt = open(chemin, encoding="utf-8").read()
    txt = re.sub(r'\n?<!-- CREDITS -->.*?<!-- /CREDITS -->\n?', "\n", txt, flags=re.S)

    utilises = sorted(set(re.findall(r'src="img/([^"]+)"', txt)))
    infos = [par_fichier[f] for f in utilises if f in par_fichier]
    if not infos:
        open(chemin, "w", encoding="utf-8").write(txt)
        continue

    a_mulberry = any(i["source"].startswith("Mulberry") for i in infos)
    a_arasaac = any(i["source"] == "ARASAAC" for i in infos)
    # Les pictogrammes sont crédités collectivement ; on détaille le reste
    # (photographies, images adaptées).
    lignes = []
    for i in infos:
        if i["source"] == "Mulberry Symbols" or i["source"] == "ARASAAC":
            continue
        auteur = i["auteur"] or "auteur inconnu"
        source = i["source"].replace("File:", "")
        lignes.append(f'<li><strong>{i["slug"]}</strong> : {source} — {auteur}, licence {i["licence"] or "?"}.</li>')

    intro = []
    if a_mulberry:
        intro.append('des pictogrammes <strong>Mulberry Symbols</strong> '
                     '(Paxtoncrafts Charitable Trust, licence CC BY-SA 4.0, mulberrysymbols.org)')
    if a_arasaac:
        intro.append('des pictogrammes <strong>ARASAAC</strong> (auteur : Sergio Palao, '
                     'propriété du Gouvernement d’Aragon, Espagne, licence CC BY-NC-SA, arasaac.org)')
    phrase = 'Les illustrations de ce cahier sont ' + ' et '.join(intro) if intro else 'Illustrations'
    if lignes:
        phrase += ', complétés des images suivantes'
    phrase += '. Merci à leurs auteurs et autrices.'

    bloc = ('<!-- CREDITS -->\n<section class="fiche credits">\n'
            '<h2>Crédits des images</h2>\n'
            '<p>' + phrase + '</p>\n' +
            ('<ul>\n' + "\n".join(lignes) + '\n</ul>\n' if lignes else '') +
            '</section>\n<!-- /CREDITS -->\n')
    txt = txt.replace("</body>", bloc + "</body>")
    open(chemin, "w", encoding="utf-8").write(txt)
    print(f"{nom} : pictos {'M' if a_mulberry else ''}{'A' if a_arasaac else ''} + {len(lignes)} crédits détaillés")
