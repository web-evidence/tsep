# Texte source v6 / Source text v6

## Français

Interpréteur **6**, adaptateur **7**, collecteur TS01 **7** ; protocole
`0.1.0-draft.7` inchangé. Cette extension de couverture applique les règles de
texte source existantes à des sélections et tableaux explicitement structurés.
Elle ne promeut ni le lecteur expérimental noscript ni le candidat DOM.

Dans un body explicite, hors head et SVG : select contient option ou optgroup ;
optgroup contient option ; option contient seulement du texte et des commentaires.
Chaque fermeture est explicite. Les conteneurs select/optgroup n'admettent que
des espaces HTML littéraux entre enfants. Le texte des options compte, jamais
leurs attributs/value ni leur état selected. Select dans datalist est hors portée.

Table accepte, dans cet ordre : au plus un caption, des colgroup contenant col,
un thead optionnel, des tbody, un tfoot optionnel. Les groupes contiennent des tr
explicites, chacun contenant td/th. Les cellules et caption peuvent contenir le
balisage ordinaire déjà accepté, y compris select. Les conteneurs n'admettent que
des espaces HTML littéraux ; aucune création implicite de tbody, fermeture omise,
réparation de parent, déplacement de texte, table imbriquée ou table dans p.
Ce sont des limites d'outil, pas une déclaration de validité HTML générale.

L'extraction demeure intégrale : une construction inconnue après un marqueur
interdit rend l'ensemble indéterminé. Les segments restent séparés, avec casse,
espaces et fins de ligne exacts et références de caractères décodées. Script,
style, commentaires et attributs ne fournissent aucun marqueur. Toutes les bornes
v5 restent inchangées. Noscript, template et textarea non vides restent NT dans
la branche des marqueurs. Une empreinte complète identique conserve sa priorité.
Ni visibilité, fonctionnement du formulaire, DOM réel ni indexation ne sont établis.

### Vérification et migration

Les 52 cas de `tests/fixtures/source-text-v6-cases.json` sont rédigés et empreintés
avant la modification du lecteur. Le fichier conserve l'empreinte du corpus v4
et explicite **un seul remplacement d'attente**, `select-context` : inconclusive
vers pass pour le texte Expected dans une option correctement fermée. Les fichiers
v4/v5 et leurs manifestes restent intacts. Le tableau historique contenant du
texte directement sous table reste inconclusive. Les 199 cas cumulés et 312
attentes externes de références de caractères sont vérifiables avec :

```sh
python3 scripts/source_text_check.py
```

Une réévaluation de capture conservée produit un nouveau paquet avec les mêmes
entrées et des outils distincts ; elle est rétrospective. Conserver les paquets,
critères et résultats antérieurs, et rejouer ceux-ci avec leurs outils d'origine.
Toute nouvelle collecte guidée exige une nouvelle référence avec le collecteur 7.
Les formats d'intention et de rapport ne changent pas. TS07/TS10, les neuf règles
et les 216 cas normatifs restent inchangés. Ces tests internes ne valent pas revue
indépendante ni preuve d'équivalence navigateur.

## English

Interpreter **6**, adapter **7**, guided TS01 collector **7**; protocol draft.7
unchanged. This extends implementation coverage under the existing source-text
contract, without promoting experimental noscript readings or the DOM candidate.

Inside explicit body, outside head/SVG, select accepts option/optgroup, optgroup
accepts option, and option accepts only text/comments. Closures are explicit;
container separators are literal HTML whitespace. Option text counts, attributes,
value and selection state do not. Select inside datalist is unsupported.

Tables accept at most one caption, colgroup/col, optional thead, tbody groups,
optional tfoot, explicit tr and td/th. Cell/caption contents use the existing
ordinary subset, including select. Container text must be literal whitespace.
No implicit tbody, omitted closure, recovery, foster parenting, nested table or
table inside p. These are tool boundaries, not general HTML validity claims.

The whole source must succeed, including unsupported content after a forbidden
marker. Exact segment separation, whitespace/case/newlines, reference decoding,
script/style/comment/attribute exclusion and v5 bounds remain unchanged. Nonempty
noscript/template/textarea remains inconclusive for markers. Equal complete-body
hash retains precedence. No visibility, form operation, actual DOM or indexing claim.

52 authored cases were frozen before implementation. One explicit migration
changes the historical `select-context` expectation from inconclusive to pass.
Original v4/v5 files and manifests remain untouched; the malformed historical
table remains inconclusive. The command above checks 199 synthetic cases and
312 retained external character-reference expectations. These are not independent
review or browser-equivalence tests. New retrospective assessments preserve inputs,
criteria and old reports; historical replay uses historical tools. New guided
collection requires collector 7 references. Intent/report formats, TS07/TS10,
nine atomic rules and 216 normative cases remain unchanged.
