# Liens source / Source links — html-tree-links-v1

## Français

Profil facultatif de draft.17 pour **TS10-A04 seulement**, sélectionné avant capture
par `intent.canonical.links.source_reader="html-tree-links-v1"`. Sans ce champ,
le lecteur historique reste inchangé. Nul, inconnu ou Node 24 absent : source
inconclusive sans repli. Le choix source n'étend aucun lecteur rendu et ne remplace
ni état requis, ni preuve de même navigation, ni revue d'exemption fournie.

### Attendu et population

A04 vérifie la convergence des liens vers une **famille déclarée**. Il n'exige pas
la présence d'un lien et n'évalue pas la suffisance du maillage. Zéro lien vers la
famille peut passer après examen complet de la population et des états exigés ;
une page manquante reste indéterminée. Le motif indique explicitement ce zéro pour
chaque hypothèse source, sans additionner deux lectures alternatives. La portée
et les comptes restent dans les observations, le motif atomique, le motif TS10,
le rapport HTML, EARL et `scope_notes` du gate JSON / résumé lisible.

Conserver sources prévues, contexte, dates préalables, famille/préférence, exceptions
source-destination motivées, traces GET complètes et octets. Les sources et leurs URL
finales restent limitées à l'origine interne déclarée. Une capture hors population
ajoute une inconnue. Aucune variante n'est inventée à partir d'un slash, paramètre
ou ressemblance : les destinations hors famille sont conservées et comptées à part.

Pour cette lecture source, toutes les URL de famille doivent déjà égaler leur
sérialisation par WHATWG URL de Node 24, en plus des exigences HTTP(S), absolues et
sans fragment existantes. Sinon la source est inconclusive, sans modifier l'intention.
Cette condition n'efface pas une contradiction indépendante dans un DOM recevable
selon son lecteur antérieur. A01/A02 gardent leurs comparaisons canonical littérales.

### Lecture et résolution

Le corps satisfait l'entrée UTF-8 explicite de source-http : une valeur Content-Type
`text/html; charset=utf-8`, variantes de casse/espaces/guillemets permises, pas d'autre
paramètre. Un BOM initial est consommé, les octets invalides sont refusés. Parse5
8.0.1 / entities 8.0.0 construit deux arbres complets, scripts activés/désactivés,
sans exécuter les scripts. Les hypothèses sont alternatives, pas deux visites.

L'observateur [d'éléments](link-elements-observer.md) conserve namespaces, attributs,
ordre, contexte, templates, balises et positions dans les octets. Sont candidats
les a/area HTML ordinaires avec href sans namespace, hors template. Un href absent
diffère d'un href vide. Les liens sans attribution, en contexte étranger ou avec
attributs dupliqués signalés sur leur balise restent inconnus. SVG href/xlink et
HTML sous ancêtre étranger ne sont pas évalués comme des liens HTML ordinaires.

Les attributs rel/nofollow, download, target, ping ou événements ne retirent aucun
candidat. Le calcul porte sur la destination statique de href, pas son activation,
la disponibilité d'une zone area, une soumission ou une action JavaScript. Form,
formaction, link et attributs de namespace restent dans l'inventaire hors de ce
calcul. Les schémas non HTTP sont comptés à part sans jugement de qualité ni exécution.

Résoudre contre l'URL **finale** reçue. Le premier base HTML hors template avec href
dans l'ordre de l'arbre fournit une base candidate. Un premier href invalide ou de
schéma data/javascript revient à l'URL finale ; ne jamais sélectionner le second
base à sa place. Un base contenant seulement target ne choisit pas la base URL.
Le fragment est retiré après résolution pour comparer à la famille ; query vide,
encodages, ports, caractères, antislashs et segments suivent la sérialisation du
résolveur qualifié, dont Node/V8/Ada/ICU/Unicode sont conservés séparément.

Une base présente avec CSP réponse ou meta, erreurs de parsing, attributs dupliqués
sur cette base ou contexte étranger conserve une incertitude de base. CSP n'est pas
simulée. Le lecteur de métadonnées complet est alors nécessaire pour examiner sa
présence ; une lecture manquante/incomplète conserve l'inconnue. Sans base, CSP
n'introduit pas à elle seule une incertitude de base dans cette lecture statique.

Seul un sous-ensemble fermé est reconnu indépendant d'une base incertaine : href
HTTP(S) absolu **déjà exactement égal à sa sérialisation autonome**. Une résolution
autonome réussie ne suffit pas : `https:variant` peut dépendre d'une base HTTPS.
Les autres href dépendants d'une base incertaine restent inconnus, même si leur
calcul conditionnel ressemble à une contradiction. Une URL absolue qualifiée peut
établir une contradiction distincte. Cette frontière conservatrice n'est pas une
implémentation complète de CSP ou de tous les cas d'indépendance d'URL.

### Décisions et limites

Pour chaque hypothèse, le parcours complet est obligatoire. Les erreurs signalées,
les hyperlinks étrangers non couverts et les déclarations shadow open/closed ou
template for ajoutent des inconnues. Les templates ordinaires sont conservés mais
inertes. Un lien qualifié vers un membre concurrent sans exception donne fail,
même si un autre lien reste inconnu. Sinon, toute inconnue empêche pass ; les liens
évalués convergents ou hors famille peuvent passer dans cette portée précise.
Les parse errors ne sont pas un certificat de validité HTML, dans aucun sens.

Deux pass source donnent pass, deux fail donnent fail ; toute autre combinaison
reste inconclusive. Aux autres niveaux, une contradiction attribuable dans une
autre page ou un état rendu complet subsiste malgré une lacune indépendante. Les
anciens lecteurs DOM gardent leur syntaxe, leur refus de base et leur rattachement
actuels. Une source passée n'est pas un DOM reçu ni une exemption inventée.

Conserver URL demandée et URL finale distinctes, inventaire complet, calculs URL, base candidate et limites, deux décisions,
comptes, href/destination, octets, erreurs et versions. Diagnostic formaté limité à
4 Mio par source : dépassement ou parcours incomplet rend cette source inconclusive,
même si une contradiction avait été calculée sans pièce conservable. Le corps
original reste une preuve distincte. Le rejeu recalcule et compare les observations.

Bornes des outils réutilisés : corps 8 Mio, arbre 200 000 nœuds/profondeur 256,
50 000 éléments, 1 000 erreurs, observation 32 Mio, worker 30 s / ancien tas 128 Mio.
Chaque lot URL : 50 000 requêtes, chaînes 64 Kio, entrée 4 Mio, sortie 16 Mio,
10 s / ancien tas 128 Mio. Deux résolutions par candidat peuvent atteindre la borne
avant celle des éléments ; le refus ne tronque pas une population pour la faire passer.
Les gardes API réseau ne sont pas une isolation système. Les empreintes établissent
l'intégrité, pas l'authenticité. Aucune indexation, sélection Google, conformité TS10
entière, certification ou standard reconnu n'en découle. [Migration](migration-draft.17.md).

## English

Draft.17 optionally selects `intent.canonical.links.source_reader="html-tree-links-v1"`
before capture for TS10-A04 source only. Absence keeps legacy behavior; null, unknown
or missing Node24 stays inconclusive without fallback. Earlier rendered readers,
required states, same-navigation attribution and supplied exemption reviews remain.

A04 tests convergence within a declared family, not link presence, sufficiency or
quality. Zero family links may pass only with complete planned coverage; missing
sources/states remain unknown. Per-hypothesis counts and explicit zero wording are
retained through atomic/control reasons, HTML, EARL and gate scope_notes/readable
summary. Alternative hypotheses are not added as independent visits. Outside-family
URLs are retained, never guessed duplicates from slash/query similarity.

Keep prior source population, family/preference, justified source-destination
exceptions, dates/context, complete GET traces and raw bytes. Internal sources/final
URLs remain within the declared origin. Unplanned captures add an unknown. Each
family URL must already equal its own Node24 WHATWG serialization and satisfy the
existing absolute fragment-free HTTP(S) constraints; otherwise source is unknown,
never silently normalize intent. An independent admissible legacy DOM contradiction
is not erased by that source refusal. A01/A02 literal canonical semantics are unchanged.

Use explicit HTTP UTF-8 HTML, one allowed content-type value, optional initial BOM,
no replacement decoding. Pinned parse5/entities produce two complete static scripting
alternatives. Retain the qualified link-element inventory and original byte spans.
Ordinary HTML a/area href outside templates are eligible. Missing href differs from
empty. Missing attribution, foreign ancestry or duplicate attributes on that tag
make the record unknown. Foreign hyperlinks including SVG href/xlink remain unknown.
Ordinary templates are inert; declared shadow/streaming template attachment is unknown.

Annotations such as nofollow/download/target/ping/events do not erase candidates.
This is static href convergence, not activation, area usability, forms, events or
JavaScript execution. form/formaction/link remain visible outside this calculation.
Non-HTTP schemes are counted separately without execution or a quality judgment.

Resolve against the final HTTP URL, then the first eligible HTML base href in tree
order. Invalid or data/javascript first base falls back, never selects a later base.
Target-only base does not select an URL base. Remove fragments after resolution;
other behavior follows the qualified WHATWG serializer, with Node/V8/Ada/ICU/Unicode
recorded separately. Existing canonical declaration readers do not inherit this resolution.

With a present base, unmodeled response/meta CSP, parsing errors, duplicate base
attributes, foreign context or unavailable metadata inventory make the base uncertain.
Without base, CSP alone does not introduce that uncertainty into static resolution.
Only an absolute HTTP(S) href already equal to its standalone serialization qualifies
as base independent here. URL(href) success alone is insufficient: https:variant is
a counterexample. Other links under uncertain base stay unknown; a qualified absolute
conflict may still fail. This is conservative, not a complete CSP implementation.

Complete traversal is mandatory. Within a hypothesis, a qualified competing family
destination without exception fails despite unrelated unknowns; otherwise unknowns
prevent pass. Reported parse errors prevent success without negating an independent
qualified conflict. Two source passes yield pass, two fails yield fail, otherwise
inconclusive. Distinct pages/rendered states retain the existing fail-over-unknown
aggregation. No missing rendered state/review is fabricated.

Retain requested and final URLs separately, inventory, URL runs, conditional base, decisions/counts, byte attribution,
errors/runtime and replay comparison. A formatted source diagnostic above 4 MiB
invalidates the source decision even when a conflict was calculated. Original body
is still retained separately. Reader bounds remain 8 MiB body, 200,000 nodes,
depth256, 50,000 records, 1,000 errors, 32 MiB observation, 30s worker/128MiB old space;
URL batches have 50,000 requests, 64KiB strings, 4MiB input/16MiB output, 10s/128MiB.
Two requests per candidate can hit the URL limit first; no favorable partial output.
API guards are not OS isolation, integrity is not authenticity, and no Google outcome
or whole-control/global conformity is implied.

Qualification : oracle initial 57 cas (56 attendus confirmés, un href mal encodé), correction tracée et régression ajoutée, corpus actif 58 cas. L’oracle initial et son échec restent conservés ; voir [provenance](../provenance/source-link-oracle-correction.json). Les sorties retenues pour les tests de transport ne sont pas des oracles indépendants.

Qualification: initial 57 cases matched 56 expectations; one incorrectly encoded href was corrected with retained provenance/failure, then one observed regression was added. Active corpus: 58 cases. Retained output fixtures support transport tests, not independent oracles.
