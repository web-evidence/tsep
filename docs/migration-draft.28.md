# Migration draft.27 → draft.28

## Français

TS01-A02 reçoit un [lecteur HTML parsé facultatif](source-markers.md), sélectionné
par `identity_reader: "html-tree-markers-v1"` dans l'intention préalable. Ce profil
est distinct du lecteur lexical historique et de l'ancienne proposition noscript.
Les 44 identifiants/titres/provenances, les 12 contrôles exécutables et les 33 règles
restent conservés. Interpréteur 27, adaptateur 28, HTML 11 ; rejeu 3 inchangé.
Les 1 181 anciens cas restent intacts et dans leur ordre. 76 cas atomiques s'ajoutent.

Sans champ identity_reader, les résultats historiques de TS01 et ses refus restent
inchangés. Le nouveau profil ne change pas les priorités URL finale, empreinte
complète identique et stabilité exigée. Il intervient seulement dans la branche
de variation d'empreinte avec marqueurs. Son indisponibilité ne déclenche pas le
lecteur historique. Un nom de profil erroné ne modifie pas les décisions antérieures.

La différence doit être comprise **avant** la collecte : CRLF/CR bruts deviennent
LF ; les critères restent littéraux. Les textes title/textarea/options/masqués sont
admis, les scripts/styles HTML/SVG et templates inactifs exclus. Le contenu noscript
est comparé sous deux hypothèses globales. Les lectures divergentes, erreurs
rapportées et contextes hors portée restent indéterminés. La migration ne convertit
aucun marqueur, ne prouve pas leur pertinence et ne crée pas de revue humaine.

Conserver chaque ancien rapport, capture, archive et tag avec ses outils exacts.
Pour appliquer ce profil à un site réel : définir une **nouvelle intention** nommant
le profil et des références/marqueurs pertinents, datée avant une **nouvelle capture**.
Ne pas ajouter le champ à une vieille intention en conservant sa date. Les diagnostics
rétrospectifs d'Edikka du jalon précédent, sans critères, ne deviennent pas des
verdicts. Une analyse rétrospective distincte ne constitue pas une évaluation
prospective conforme à ces exigences et ne remplace pas les pièces historiques.

Le rapport HTML affiche le lecteur fourni. Les diagnostics regroupent seulement
les contextes d'ancêtres identiques : tous les segments, exclusions, positions,
résultats et erreurs restent conservés. Les arbres complets sont reconstructibles
avec le corps, les outils épinglés et l'environnement Node/V8 consigné, sous réserve
de disponibilité ; ils ne sont pas dupliqués dans chaque pièce. Les contextes
regroupent uniquement les noms/espaces de noms ; identifiants de nœuds et hypothèses
restent distincts. Chaque évaluation vérifie la restitution exacte de sa projection.
Un diagnostic trop volumineux reste inconclusif, jamais tronqué pour produire pass.

## English

TS01-A02 gains an [optional parsed HTML reader](source-markers.md), selected by
identity_reader=html-tree-markers-v1 in prior intent. It is distinct from the
historical lexical reader and the unapplied lexical noscript proposal. All44
IDs/titles/provenance, 12 executable controls and33 rules remain. Interpreter27,
adapter28, HTML11; replay3 unchanged. Preserve the1,181 existing case objects and
order; add76 authored atomic cases.

Absent identity_reader preserves historical TS01 results/refusals. Final URL,
equal complete hash and required stability keep precedence. Only the changed-body
marker branch uses this profile; unavailable or unknown profiles never fall back.
An invalid profile does not override earlier decisions.

Understand the semantics before collection: raw CRLF/CR become LF; literal criteria
are unchanged. title/textarea/options/hidden text count; HTML/SVG scripts/styles and
inactive templates do not. noscript uses two whole-document alternatives. Divergent
readings, reported errors and unsupported contexts remain inconclusive. Migration
does not convert criteria, establish their relevance or create human review.

Keep every historical report/capture/archive/tag with its exact tools. Real-site use
requires new explicit profile/reference/marker intent followed by a new capture.
Never add the field to an old intent while retaining its date. Prior Edikka diagnostics
without criteria are not converted to verdicts. Separately labeled retrospective
analysis is not a prospective assessment satisfying these requirements and never
replaces historical evidence.

HTML reports identify the supplied reader. Diagnostics only intern repeated ancestry
contexts, preserving all segments/exclusions/positions/results/errors. Full trees
are reconstructible from bytes, pinned tools and the recorded Node/V8 environment,
subject to availability, not duplicated in each artifact. Contexts intern only
names/namespaces; node IDs and hypotheses remain distinct. Every assessment checks
exact expansion against its attributed projection.
Excessive diagnostics are inconclusive, never truncated into pass.
