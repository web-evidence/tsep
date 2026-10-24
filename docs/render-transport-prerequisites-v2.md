# Préalables du rendu et du transport / Render and transport prerequisites — v2

Normatif dès / Normative from **0.3.0-draft.5**, interpréteur / interpreter 51,
lecteur / reader 2. Le format d'entrée `render-transport-v1` reste identique /
the `render-transport-v1` input format is unchanged. This amendment supplements
[v1](render-transport-evidence.md); all other rules and evidence limits remain.

## Français

**TS30-A01 et TS30-A02.** Le périmètre reste le corpus préalable de sources HTML,
avec les cinq champs attendus, les originaux, dates, contexte et revues liés.
Avant de qualifier le H1, examiner les drapeaux de l'élément **et de ses textes
descendants**, comme pour les autres contenus sélectionnés. Un contexte hidden,
inert, aria-hidden, style, details, dialog, noscript, template ou étranger non
qualifié ne prouve pas le contenu éditorial visible : conserver NT. Ne pas
supprimer ce H1 de l'inventaire pour fabriquer une absence NC. Vérifier les
autres champs séparément : une divergence native indépendante de title ou d'une
autre métadonnée demeure NC malgré ce H1 indéterminé.

**TS37-A03.** Conserver le périmètre strict de HAR/console et source HTML fournis.
Repérer les éléments base avec href hors des contextes template/étrangers. Ce
lecteur ne qualifie pas leur résolution : en présence d'une telle base, une URL
intégrée sans schéma HTTP(S) absolu reste NT. Ne pas la résoudre silencieusement
contre l'URL de la page. Les URL HTTP(S) absolues restent interprétables
indépendamment de la base. Les surfaces CSS/srcset et schémas spéciaux restent
NT, mais ne terminent plus l'examen des autres URL : un src HTTP natif qualifié,
sur le même élément ou plus loin dans la source, conserve NC. Les observations
HAR qualifiées gardent aussi leur rôle indépendant.

Les preuves, bornes, provenance déclarative et revues restent celles du dossier
v1. Une revue positive ne remplace pas une résolution ou visibilité non qualifiée.
L'absence de drapeau HTML ne prouve toujours pas la visibilité CSS calculée,
l'exécution navigateur, une collecte exhaustive, l'indexation ou la sécurité
globale. Aucun nouveau contrôle, aucune NA atomique, aucune méthode générale de
résolution de base, de CSS ou de navigateur n'est ajouté. Les cas de test sont
tous **synthétiques**, sans audit de site réel.

**TS29 conservé.** L'attendu reste une alternative : fonctionnement principal
entièrement étayé **ou** repli préalable entièrement étayé dans le même état
qualifié, avec revue liée. Un principal indéterminé n'invalide pas un repli
indépendamment qualifié. En revanche, une capture globale incomplète ou une
revue absente demeure NT. Le lecteur ne crée ni ce repli ni son jugement.

## English

**TS30-A01 and TS30-A02.** Scope remains the prior HTML-source corpus with five
expected fields, originals, dates, context and bound reviews. Before qualifying
H1, inspect flags on both the element **and descendant text**, as for other
selected content. Unqualified hidden, inert, aria-hidden, style, details, dialog,
noscript, template or foreign contexts do not establish visible editorial
content: retain NT. Do not discard the H1 to manufacture an absent-H1 NC.
Check other fields separately: an independent native title or metadata conflict
remains NC despite that inconclusive H1.

**TS37-A03.** Retain the strict supplied HAR/console and HTML-source scope.
Identify base elements with href outside template/foreign contexts. This reader
does not qualify their resolution: with such a base, an embedded URL without an
absolute HTTP(S) scheme remains NT. Never silently resolve it against the page
URL. Absolute HTTP(S) URLs remain independently interpretable. CSS/srcset
surfaces and special schemes remain NT but no longer stop other URL checks:
a qualified native HTTP src on the same element or later in the source retains
NC. Qualified HAR observations likewise remain independent.

Evidence, bounds, declared provenance and reviews remain those of dossier v1.
A positive review cannot replace unqualified resolution or visibility. Lack of
an HTML flag still proves neither computed CSS visibility, browser execution,
exhaustive collection, indexing nor overall security. No new control, atomic NA,
general base-resolution, CSS or browser method is introduced. All test cases are
**synthetic**, without a real-site audit.

**TS29 preserved.** The expectation remains an alternative: fully supported main
operation **or** fully supported prior fallback in the same qualified state,
with a bound review. An unknown main branch does not invalidate an independently
qualified fallback. An incomplete global capture or missing review still yields
NT. The reader generates neither the alternative nor its human judgment.

See [migration](migration-0.3.0-draft.5.md) and the
[dated HTML base reference](source-captures/document-base-2026-10-19.md).
