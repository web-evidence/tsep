# Lexical SEO signal experiment / Expérience de signaux SEO lexicaux

**UNAPPLIED / NON APPLIQUÉE.** Version 2, separate from the active interpreter.
No TS07/TS10 assessment, new protocol version or normative migration is created.

## Français

Cette expérience relève les balises `meta` dont le nom décodé est `robots` ou
`googlebot`, et les `link` dont `rel` contient le jeton `canonical`. Elle prépare
des preuves à examiner ; elle ne calcule ni effet des directives ni validité
canonique. Elle ne lit pas les en-têtes HTTP, robots.txt, les états rendus ou une
intention. Les résultats TS07/TS10 existants restent inchangés.

```sh
python3 experiments/seo_signals.py source.txt --output observations.json
```

Python 3.9+, aucune dépendance installée, aucun réseau. La sortie doit être
nouvelle. Le fichier source UTF-8 est conservé par son empreinte ; ses octets,
ses CRLF et ses positions ne sont pas réécrits. Garder le fichier avec la sortie.

Chaque hypothèse globale `enabled`/`disabled` passe d'abord par la lecture
**intégrale** de l'expérience noscript 4. Sa liste positive, ses limites de
taille/profondeur et ses refus s'appliquent sans modification. Un refus livre
zéro signal pour ce mode, même si des balises étaient lisibles avant l'obstacle.
La seconde lecture conserve les frontières de commentaires et de textes bruts.
Une apparence de balise dans un script, style, titre ou attribut n'est pas un
signal. Dans noscript, les deux hypothèses peuvent produire des listes différentes.

Chaque observation contient la balise brute, ses attributs, ses positions en
caractères Unicode Python (début inclus, fin exclue) et ses **ancêtres lexicaux**.
Ce ne sont pas des positions DOM ni une preuve de la fin réelle du head. Une
balise après `</head>` mais avant `<body>` est refusée par le sous-ensemble, pas
déclarée dans le body. Les balises lexicalement dans le body sont conservées et
distinguées ; cela ne prouve pas que le moteur les utilise. Répétitions et valeurs
absentes sont visibles. Un attribut sans valeur explicite conserve `null`.

Le décodage des attributs suit une règle dédiée aux références de caractères :
une référence nommée sans point-virgule suivie d'un caractère ASCII alphanumérique
ou de `=` reste littérale. Les CRLF/CR littéraux deviennent LF dans **la valeur
d'attribut seulement**, pas dans la source ; `&#13;` reste CR. Les espaces ASCII
séparent les jetons rel ; NBSP n'est pas un séparateur. Aucune résolution d'URL
relative, application de base, combinaison de directives ou décision de validité.
La balise brute reste jointe pour examiner chaque transformation.

`inventory_comparison` vaut `identical`, `different` ou `unavailable`. Deux listes
vides identiques ne sont pas une réussite ; deux lectures concordantes ne prouvent
pas un comportement navigateur. Aucun résultat C/NC/NA/NT ou candidat de conformité
n'est produit. Les données ont la même confidentialité que la source.

### Attentes, correction et limites

Les 32 cas initiaux ont été enregistrés avant le premier code. Une première
exécution privée v1 employait le décodage Python HTMLParser, explicitement limité.
La revue avec Claude et la référence primaire ont motivé la version 2 avant
diffusion : 25 attentes d'attributs et un refus entre head/body ont été figés avant
le correctif. Un seul attendu v1 est remplacé explicitement : `?a&notit;=b` reste
littéral dans l'attribut, au lieu de `?a¬it;=b`. Les fichiers initiaux et la trace
privée v1 sont conservés. Aucun rapport TSEP n'est migré.

Ce corpus rédigé en interne n'est pas une validation indépendante ou une exécution
navigateur. Le lecteur ne répare pas les arbres HTML, ne traite pas tous les
contextes et ne prouve pas la visibilité, l'indexation, la sélection canonique ou
la couverture d'un site. Une éventuelle utilisation normative exige une décision
distincte, un périmètre justifié, les contrats bilingues, une migration et des cas
contradictoires ; aucune promotion n'est implicite.

## English

Version 2 inventories robots/googlebot meta and canonical link tags under the
unchanged noscript 4 whole-source lexical hypotheses. Every incomplete mode
returns zero signals; false tags in attributes, comments and raw text are ignored.
Observations retain exact raw tags, decoded attributes, Unicode source ranges and
lexical ancestors, never DOM positions. Repeated/missing values remain visible.
Relative hrefs are not resolved, including when base is present.

Attribute references use an attribute-specific decoder. A semicolon-less named
match followed by ASCII alphanumeric or equals stays literal. Literal CRLF/CR is
normalized only inside the decoded attribute value; original source bytes/ranges
remain intact. Numeric references are handled separately with bounded conversion.
Boolean attributes retain null; ASCII whitespace separates rel tokens, unlike NBSP.

The comparison is identical/different/unavailable, never a conformity outcome.
Identical empty inventories do not pass anything. No HTTP headers, robots access,
rendered states, intent or engine behavior are evaluated. Existing normative
pipelines, TS01–TS44 and draft.7 remain unchanged. Private v1's Python attribute
decoding is explicitly superseded for one frozen case; 25 new attribute cases and
one after-head refusal were frozen before v2. Original fixtures are retained.
These are authored examples, not independent/browser validation. Run the CLI on a
retained UTF-8 source and keep it with the new JSON result; no network is used.

## Reference / Référence

[WHATWG HTML, named character references](https://html.spec.whatwg.org/multipage/parsing.html#named-character-reference-state),
consulted 2026-10-10, attribute-context exception and numeric-reference states.
A dated **web-tool text extraction**, not a raw HTTP/HTML archive, is retained
privately; its SHA-256 is recorded in `seo-signals-attribute-v2-cases.json`.
This reference supports this bounded decoding rule, not full HTML conformance.
