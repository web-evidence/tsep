# Structured rendered states — draft.10 / États rendus structurés

## Français

Le lecteur `structured-inventory-v2` devient une méthode exécutable de TS07-A03,
TS10-A01/A02/A04. Il interprète des captures **fournies**, ne lance aucun navigateur
et ne remplace pas le HTML source. Les 39 nouveaux cas sont des arbres rédigés,
figés avant l'implémentation, pas des captures réelles. La méthode ne démontre pas
l'application à Edikka, la véracité d'une revue ni le rendu par Google.

### Choix préalable et entrées

Chaque plan de rendu concerné déclare `dom_reader: "structured-inventory-v2"`
avant la collecte, en plus de `mode: "required"` et `required_states`. Pour TS07,
il s'agit de `intent.rendering` ; pour TS10, des plans des membres et des pages
sources de liens. Le choix vaut pour tous les états du plan. Sans champ, le
lecteur historique `legacy-serialized-v1` reste fixe. Un payload structuré sans
choix explicite est indéterminé, même accompagné d'une sérialisation favorable.
Aucun lecteur ne réessaie automatiquement avec l'autre après un refus.

Les champs historiques d'un état restent nécessaires : id, URL finale exacte,
contexte, date au plus tôt à la source, empreinte de toute la trace HTTP,
JavaScript activé, capture complète, interactions/attente identiques au plan,
erreurs explicitement vides. TS10 impose aussi l'intervalle de campagne.
L'état ajoute `structured_dom` avec exactement :

- `snapshot`: `{script_sha256, tree}` selon l'[inventaire 2](rendered-metadata-inventory.md),
  script exact `collectors/rendered_metadata.js` ; aucune conversion des anciens relevés ;
- `snapshot_sha256`: SHA-256 de la représentation JSON du snapshot, clés triées,
  séparateurs `,` et `:`, Unicode UTF-8 non échappé, sans saut de ligne final ;
- `known_integrity_issues`: liste explicitement vide pour conclure ; absente, nulle
  ou contenant une anomalie connue donne indéterminé ;
- `acquisition`: `kind`, `navigation_id` non blanc, `user_agent` exactement égal
  au robot déclaré, `http_sha256` égal au digest de la trace liée, `support`.

Chaque support comprend `name`, `content` et SHA-256 du contenu UTF-8, 1 à 16 pièces,
64 Kio par contenu au plus. Ces enregistrements étayent la déclaration de navigation ;
ils ne l'authentifient pas. Un auteur peut fabriquer un ensemble cohérent. Le résultat structuré interprété
indique le type d'acquisition et cette limite à côté de l'issue structurée.

`kind: "authored-synthetic"` désigne un arbre rédigé ; l'adaptateur exige alors
`access: "synthetic"`. `kind: "same-navigation"` est une déclaration étayée que le
DOM et la trace appartiennent à la même navigation. Elle exige un reçu avec
identifiant de navigation, contexte, agent et pièces source, produit par la chaîne
de collecte ; l'interpréteur ne vérifie que les valeurs et empreintes fournies.
`separate-acquisition` ou une origine inconnue reste indéterminée. Une trace curl
et un DOM obtenu lors d'une visite distincte ne deviennent pas une même navigation
par l'ajout du digest. Une future capture réelle doit réellement fournir ces pièces.

Le libellé historique `scripting: "enabled-by-laboratory-plan"` du transport 2
est conservé littéralement ; il ne certifie ni l'exécution ni l'origine. Son emploi
hors laboratoire exige une nouvelle méthode de capture documentée ; cette intégration
n'établit pas une chaîne de collecte réelle. Les exemples synthétiques ne valent
pas validation de cette future chaîne.

### Couverture et décisions

L'arbre doit passer le validateur d'inventaire sans réparation : 1 024 nœuds,
profondeur 64, 512 Kio pour les nœuds, 256 Kio pour la sérialisation, budget coopératif
2 secondes et invocation prévue à 5 secondes. **Tout le parcours et sa sérialisation
compagnon sont requis**, pas seulement une sélection de balises. La borne atteinte
produit indéterminé ; aucune pagination ni troncature silencieuse. `loading` est
indéterminé ; `interactive`/`complete` décrivent un instant, jamais une stabilité.
Un seul élément HTML racine et un seul head HTML directement enfant sont nécessaires.
Si `dom` est fourni en plus, il doit égaler la sérialisation compagnon. L'outil ne
reparse pas cette dernière pour remplacer les faits de l'arbre ; leur concordance
sémantique dépend de la collecte. Les deux restent disponibles à la revue.

- TS07 : meta robots/googlebot HTML directement dans le head réel, doublons conservés,
  combinées avec les X-Robots-Tag finaux par la sémantique bornée existante. Une meta
  ailleurs ou dans le shadow ouvert reste indéterminée. Les noms SVG ne deviennent
  pas des meta HTML. Un noindex initial retiré ne donne toujours pas pass à A03.
- TS10 canonical : valeur brute exacte, position conservée, doublons conservés.
  Canonical relative ou hors head ordinaire : fail selon le critère TSEP existant.
  Shadow ouvert, propriété résolue manquante ou différence brut/résolu absolue :
  inconclusive sur cette surface. La comparaison n'efface ni normalise la différence.
  Elle ne prouve pas une différence de ressource pour Google. Les méthodes requises
  restent déclarées : une absence n'est fail que si cette surface était requise.
- TS10 liens : ancres HTML ordinaires avec href brut, sans élément base et avec
  baseURI égale à l'URL finale. Résolution existante `urljoin`, retrait du fragment,
  sous-ensemble ASCII sans espaces, contrôles, antislash ou échappement incomplet.
  Le shadow ouvert ou un autre contexte de base donne indéterminé. Aucun traitement
  des ancres SVG, frames, fragments template ou shadow fermés n'est revendiqué.
- TS10 contenu : revue manuelle motivée, population complète et empreinte incluant
  les arbres et pièces d'acquisition. Un changement rend l'ancienne revue périmée.
  Une lecture de métadonnées n'est pas une comparaison automatique de contenu.

Une inconnue sur un état ne supprime pas un fail établi dans une autre surface,
un autre état ou membre. L'arbre incomplet lui-même ne fournit aucun fail normatif,
à la différence de certains diagnostics du candidat expérimental. Un état imprévu ajoute une inconnue sans effacer le défaut attribuable d’un état prévu. Les résultats
expérimentaux antérieurs ne sont donc pas renommés en résultats TSEP.
Le lecteur source strict reste une limite distincte : un arbre bien lu ne rend
pas automatiquement le HTML initial interprétable. Les exigences d'accès, robots,
sitemap, population, revue et sources restent présentes.

### Vérification et rejeu

`tests/fixtures/structured-rendering-v1-cases.json` contient 39 cas rédigés avant
code (empreinte dans le fichier voisin), copiés sans modification dans le corpus.
Le test ciblé ajoute intégrité, provenance synthétique, conservation des défauts,
revue périmée et rejeu sans réseau. Il n'authentifie aucune capture navigateur.

```sh
python3 -m unittest discover -s tests -p test_structured_dom.py -v
python3 scripts/verify.py
python3 adapters/replay.py bundle --output replay-new
```

Conserver outils et empreintes d'origine avec chaque paquet. Une réévaluation avec
la nouvelle version est un nouveau paquet, jamais le rejeu historique du précédent.
Voir [migration](migration-draft.10.md).

## English

Draft.10 adds the predeclared `structured-inventory-v2` reader to TS07-A03 and
TS10-A01/A02/A04. It interprets supplied records without browser execution, source
HTML replacement or engine inference. The 39 prefrozen cases are authored trees,
not actual browser captures or human acceptance. No real Edikka capture chain is
established by this integration.

Declare `dom_reader` in each required rendering plan before capture. Missing field
means fixed `legacy-serialized-v1`; structured payloads cannot use that path and
there is no fallback after refusal. Existing state URL, context, HTTP digest,
time, completeness, JavaScript, exact scenario and empty errors remain required.
TS10 retains the campaign interval constraint.

`structured_dom` has exactly `snapshot`, `snapshot_sha256`,
`known_integrity_issues`, `acquisition`. Snapshot is `{script_sha256, tree}` using
unchanged inventory 2 and its exact script. The snapshot digest uses sorted-key,
compact UTF-8 JSON, literal Unicode, no trailing newline. Integrity issues must be
explicitly empty. Acquisition contains kind, nonblank navigation_id, user_agent
equal to the declared HTTP crawler, http_sha256 bound to the trace and 1–16 support
records. Each support has name/content/UTF-8 SHA-256, content at most 64 KiB.

`authored-synthetic` requires synthetic evidence access. `same-navigation` declares
that the DOM and HTTP evidence belong to one navigation, supported by retained
collection receipts. These are checked for supplied consistency, not independently
authenticated; coherent fabrication is possible. `separate-acquisition` and unknown
provenance remain inconclusive. Binding a curl trace to an independently obtained
DOM is not sufficient. Every interpreted structured result states acquisition kind and this
attribution limitation. Inventory 2 retains its historical laboratory scripting
label; use outside a laboratory needs a separately documented real capture method,
not established here. An authored fixture does not prove such a method works.

The full tree and serialization companion are mandatory: 1024 nodes, depth 64,
512 KiB node JSON, 256 KiB serialization, 2-second cooperative collection budget,
5-second planned invocation timeout. Reaching a bound is inconclusive, never silent
truncation. Loading documents are inconclusive; interactive/complete records cover
one instant only. Require one real HTML root and direct HTML head. Any extra `dom`
field must equal the retained serialization. The reader does not reparse it to
replace tree facts; their semantic agreement depends on collection and review.

Robots meta must be direct children of the real head; other placement/open shadow
is inconclusive. Retain duplicates and combine with final X-Robots-Tag under the
existing bounded semantics. Removing initial noindex still cannot pass A03.
Canonical values remain exact raw strings with positions: ordinary out-of-head or
relative declarations fail the existing TSEP criterion; open shadow, missing resolved
href or absolute raw/resolved disagreement is inconclusive for that surface. Neither
value is substituted. Absence fails only when the method was required.

Links use ordinary HTML anchors, raw href, no base element and baseURI equal to final
URL; existing urljoin plus fragment removal, bounded ASCII without whitespace,
controls, backslash or incomplete percent escapes. Shadow anchors and changed base
are inconclusive. No frame, template fragment, SVG-anchor or closed-shadow coverage
is claimed. No elements are filtered by a supposed page/extension origin.

Content judgments remain manual, complete and bound to the exact family documents,
including snapshots/receipts. Changing a record invalidates the previous review.
An unplanned state adds an unknown without erasing a planned-state failure. Unknowns never erase an established failure in another surface/state/member. An
incomplete tree itself yields no normative failure, unlike some experimental
candidate diagnostics; old experimental outcomes are not relabeled. The strict source
HTML reader remains a separate limit, and access/robots/sitemap/population/review
requirements remain unchanged. Tests and offline replay do not authenticate capture.

La fiche de revue 3 nomme chaque URL/état, navigation déclarée, empreinte du snapshot
et empreinte UTF-8 de sa sérialisation. Le fichier de preuve complet reste lié à la réponse humaine.
Review workflow 3 lists each URL/state, declared navigation, snapshot digest and UTF-8
serialization digest; the full evidence file remains bound to the supplied human response.
