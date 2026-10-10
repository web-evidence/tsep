# Liens source v2 — base invalide / Source links v2 — invalid base

## Français

Profil facultatif **html-tree-links-v2**, ajouté par draft.18 à TS10-A04 seulement.
Le sélectionner dans `intent.canonical.links.source_reader` avant la capture.
Il reprend toutes les exigences du [profil v1](source-link-policy.md), avec la
seule différence de décision définie ci-dessous. Une absence de sélection garde
le lecteur historique ; une sélection v1 garde v1, sans migration implicite.
Sélection inconnue, Node24 absent ou preuve manquante : inconclusive, sans repli.
A01 conserve sa comparaison littérale et A02 sa revue manuelle ; aucun test de
destination de canonical relative, 404 ou redirection n'est ajouté.

### Première base non analysable

Pour chacune des deux hypothèses source, sélectionner le premier élément base
HTML éligible avec href, dans l'ordre défini par v1. Si l'analyse WHATWG de ce
href contre l'URL finale HTTP échoue (`ok=false` du résolveur qualifié), ajouter
une **incertitude de base**. Ne pas sélectionner une seconde base à sa place.
La base candidate conserve l'URL finale pour un calcul explicitement conditionnel,
avec `basis=first-invalid-base-unknown` et le motif dans `candidate_base.unknowns`.
Cette valeur ne décrit pas une base effective observée dans un navigateur.

Tout href dépendant de cette base reste `unknown-base`. Ne pas déduire de son
calcul conditionnel une destination, une appartenance à la famille, une exception,
un pass ou un fail. Les octets, le href, les deux calculs URL et l'inconnue restent
dans l'observation. Une exception de destination ne résout pas l'incertitude.

Le sous-ensemble indépendant reste exactement celui de v1 : href HTTP(S) absolu,
égal à sa sérialisation autonome. Une URL qui requiert normalisation, `https:x`,
un href relatif ou un schéma non HTTP reste hors de ce sous-ensemble, même si
un humain estime son résultat indépendant. Cette limite conservatrice ne prétend
pas couvrir toutes les URL indépendantes d'une base.

Une URL indépendante qualifiée vers un concurrent non exempté reste fail, même
si d'autres liens sont inconnus. Sinon les inconnues empêchent pass. Deux pass
source donnent pass, deux fail donnent fail ; les autres combinaisons restent
inconclusive. Les contradictions recevables d'une autre page ou d'un état rendu
ne disparaissent pas. Les exigences de rendu et de revue restent celles de v1.

### Distinctions à conserver

- Un href de base vide ou composé d'espaces n'est pas, à lui seul, un échec de
  parsing WHATWG. Conserver le résultat du résolveur au lieu d'un test de vérité
  sur la chaîne. L'absence de href et un base avec seulement target sont distincts.
- Les schémas data/javascript analysables gardent le repli v1 ; ils ne sont pas
  assimilés à cet échec. Les règles CSP, contexte étranger, attributs dupliqués et
  erreurs HTML restent inchangées. Un échec URL n'est pas une erreur de parsing HTML.
- Les deux lectures noscript sont des hypothèses alternatives. Une première base
  peut différer entre elles ; ne pas fusionner les bases ni les populations.
- Une page complètement examinée sans href peut toujours passer dans la portée
  de convergence, même si une base serait incertaine pour un lien absent. Le zéro
  de famille reste explicite jusqu'aux rapports et au gate. Une page ou un état
  requis manquant ne devient pas ce zéro observé.

### Preuves et limites

Conserver le choix préalable v2, famille/préférence/population, octets HTTP exacts,
inventaire complet, attribution des balises, première base, résultat de son analyse,
calculs conditionnels/autonomes, décisions/comptes par hypothèse et versions.
Les observations portent `reader=html-tree-links-v2`, `policy_version=2` ; leur
motif identifie v2 jusque dans le contrôle, HTML, EARL et scope_notes du gate.
Les bornes de v1, dont le diagnostic de 4 Mio, restent intégralement applicables.
Un diagnostic incomplet ne fournit pas de contradiction sans pièce conservable.

Le [diagnostic navigateur](base-uri-diagnostic.md) motive cette frontière : dans
une session synthétique, douze états avec base invalide divergent de l'attente
initiale, aussi en navigation principale. Ce résultat ne prouve ni une divergence
universelle de navigateur ni un comportement Google. La politique v2 conserve
l'incertitude au lieu de transposer une valeur de ce navigateur dans la source.
Les anciennes attentes et les captures restent inchangées. La correction ne vaut
ni réparation d'Edikka, ni validation de TS10 entier, ni certification.

La qualification emploie 39 cas rédigés et figés avant l'implémentation v2, après
ce diagnostic. Les revues et DOM fournis sont fictifs et étiquetés synthétiques.
Les sorties retenues pour les tests de transport ne sont pas des oracles indépendants.
[Migration explicite](migration-draft.18.md).

## English

Optional **html-tree-links-v2** is introduced by draft.18 for TS10-A04 only.
Select it in `intent.canonical.links.source_reader` before capture. All [v1
requirements](source-link-policy.md) remain, except for the decision delta below.
Absent selection keeps the legacy reader; explicit v1 remains v1. Unknown selection,
missing Node24 or missing evidence stays inconclusive without fallback. A01 literal
comparison and A02 manual review are unchanged; no relative canonical destination,
404 or redirect test is introduced.

For each static hypothesis, select the first eligible HTML base href in v1 order.
If the qualified WHATWG parser returns `ok=false` for that href against the final
HTTP URL, add **base uncertainty**. Never select a later base instead. Retain the
final URL as an explicitly conditional candidate, with
`basis=first-invalid-base-unknown` and the reason in `candidate_base.unknowns`.
This does not describe an observed browser's effective base.

Every base-dependent href stays `unknown-base`; its conditional calculation cannot
establish a destination, family membership, exception, pass or fail. Retain bytes,
href, conditional/standalone URL calculations and the unknown. A destination
exception does not resolve uncertainty.

The independent subset is unchanged: an absolute HTTP(S) href already equal to
its standalone serialization. Non-normalized absolute strings, relative or same-scheme
references and non-HTTP schemes stay outside this closed subset, even when they
might independently resolve in a broader algorithm. A qualified independent
competing destination still fails despite unrelated unknowns; otherwise unknowns
prevent pass. Two source passes yield pass, two failures yield fail, otherwise
inconclusive. Admissible contradictions from other pages/rendered states survive.
Required rendering and reviews stay unchanged.

Empty/whitespace base href is not inherently a WHATWG parse failure; use the actual
parser result. Missing href and target-only base differ. Parseable data/javascript
bases keep v1 fallback; CSP, foreign contexts, duplicate attributes and reported
HTML errors retain their existing treatment. URL parse failure is not an HTML
parse error. Alternative noscript hypotheses retain their own first bases and
populations. Complete zero-href coverage can still pass limited convergence,
with zero counts exposed through reports/gates, without a link-presence requirement.
Missing pages/states never become an observed zero.

Retain the prior v2 selection, declared family/population, exact HTTP bytes,
complete attributed inventory, first base and parse result, conditional/standalone
calculations, per-hypothesis decisions/counts and versions. Observations identify
reader v2/policy_version2 through atomic/control reasons, HTML, EARL and gate notes.
All v1 limits apply, including the 4 MiB diagnostic bound; an incomplete diagnostic
cannot establish a conflict without retainable evidence.

The [browser diagnostic](base-uri-diagnostic.md) motivates a conservative boundary,
not a universal browser claim or a new source base value copied from that browser.
Old expectations and captures remain. Thirty-nine authored cases were frozen before
v2 implementation, after that diagnostic; supplied reviews/DOMs are synthetic.
Retained transport outputs are not independent oracles. No site repair, Google
behavior, whole-control conformity or certification is implied. See [migration](migration-draft.18.md).
