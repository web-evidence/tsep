# Intentions de présentation / Preview intent — google-preview-intent-v1

## Français

Draft.20 étend TS07-A01 et A03 par un choix préalable facultatif
`intent.presentation_reader = "google-preview-intent-v1"`. Sans ce champ, conserver
le lecteur historique et son refus des intentions de présentation. Champ nul,
inconnu ou objectif mal formé : indéterminé, aucun repli. Ce profil applique la
sémantique Googlebot textuelle à la représentation du client déclaré ; il ne
prouve pas ce que Googlebot a reçu ni ce que Google affiche.

### Intention et comparaison

L'intention, datée avant capture, contient un objet `presentation` non vide.
Ses seules dimensions sont `max_snippet`, `max_video_preview`, `max_image_preview`.
Chaque dimension contient `minimum`, `maximum`, ou les deux. Ces bornes portent
sur le **plafond de permission déclaré**, pas sur une longueur affichée minimale.
Une dimension omise n'est pas évaluée. Minimum supérieur au maximum, champ inconnu,
booléen, flottant, valeur nulle et ancien scalaire sont refusés.

```json
{
  "presentation_reader": "google-preview-intent-v1",
  "presentation": {
    "max_snippet": {"maximum": 160},
    "max_image_preview": {"minimum": "large"}
  }
}
```

L'ordre numérique est 0 à 2147483647, puis -1 (sans plafond numérique déclaré).
Texte en caractères, vidéo en secondes ; images : none < standard < large.
L'égalité est un intervalle réduit à un point. Un plafond texte de 50 satisfait
maximum 160, mais contredit minimum 160. Ce choix de comparaison est une politique
TSEP, pas un comportement attribué au moteur.

### Lecture et inconnues

Conserver toutes les valeurs meta applicables et tous les X-Robots-Tag finaux,
avec leur ordre, origine et portée. Une portée HTTP initiale unique est acceptée ;
un autre robot est exclu mais conservé. Une portée réintroduite après une virgule
est ambiguë, même dans un champ commençant par un autre robot. Le profil ne fusionne
pas des hypothèses source alternatives ou des états rendus différents.

Les directives historiques index/noindex/follow/nofollow/all/none sont combinées.
Le minimum dans l'ordre de restriction combine les plafonds explicites. nosnippet
fixe texte et vidéo à zéro sans imposer un plafond d'image. L'absence d'une limite
numérique ne fixe aucun plafond ; le défaut d'image reste un intervalle none..large,
sans équivalence supposée avec standard. L'effet vidéo de max-snippet:0 seul garde
les deux lectures possibles de la documentation, de zéro au plafond vidéo connu.
Un max-video-preview:0 explicite ou nosnippet lève cette incertitude à zéro.

Une valeur max-preview non qualifiée élargit l'intervalle de cette dimension de
zéro au plafond connu. Elle ne peut effacer une restriction explicite : nosnippet
reste incompatible avec minimum texte 1. Une directive inconnue rend toutes les
dimensions incertaines ; indexifembedded/unavailable_after rendent l'indexation
incertaine faute de contexte. Aucune syntaxe non prise en charge n'est déclarée
invalide selon Google. Le lecteur accepte uniquement les nombres ASCII entiers
-1 ou positifs dans sa borne, et les valeurs d'image fermées ; les autres formes
restent à qualifier. Les limites ne sont jamais des observations d'affichage.

Comparer l'ensemble des plafonds possibles à l'intervalle voulu : tous dedans →
pass ; tous dehors du même côté → fail ; sinon indéterminé. Les objectifs
d'indexation et de suivi gardent leurs comparaisons distinctes. Noindex/none
présent ne satisfait pas une intention de présentation : les dimensions d'aperçu
sont indéterminées ; une contradiction d'indexation certaine reste fail. Dans une
lecture, un fail indépendant prévaut sur une autre inconnue. Sans fail, toute
dimension évaluée inconnue empêche pass. Il n'y a pas d'exemption NA nouvelle.

### Attribution, bornes et intégration

Les préalables HTTP/UTF-8/HTML et l'intention du client restent obligatoires.
Le profil est combinable avec le lecteur source préalable html-tree-directives-v1
et les lecteurs rendus existants, sans les élargir. Deux hypothèses source doivent
converger selon leur contrat ; une contradiction rendue attribuable garde sa
priorité A03. États manquants, liaison invalide, erreur JavaScript et revue absente
ne sont pas comblés. Chaque observation conserve valeurs, décisions par dimension,
intervalles, limites et version ; l'adaptateur lie l'artefact au test et à l'entrée.

Bornes par lecture : 128 valeurs HTTP+meta, 256 Kio UTF-8, 4096 jetons séparés par
virgule. Dépassement → indéterminé sans conclusion d'absence sur un préfixe. Les
sources et observations du profil entrent dans l'intégrité/rejeu de l'adaptateur.
Les 74 cas figés sont synthétiques ; aucune observation de recherche, d'indexation,
de licence, de données structurées, de data-nosnippet, de disponibilité d'image ou
d'usage par une IA n'est établie. Une permission n'est pas une garantie d'aperçu.

Source primaire consultée le 11 octobre 2026 : [Google, robots meta](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag).
La tension entre le paragraphe max-snippet (sans effet vidéo) et sa valeur zéro
(équivalence nosnippet) est conservée, non résolue par supposition. La capture et
son empreinte sont référencées dans `provenance/preview-intent-v1.json`.
[Migration explicite](migration-draft.20.md).

## English

Draft.20 optionally extends TS07-A01/A03 through prior
`intent.presentation_reader="google-preview-intent-v1"`. Absence preserves the
historical reader and its refusal of presentation objectives; null/unknown profiles
and malformed objectives remain inconclusive without fallback. Googlebot text-result
semantics concern the declared client's representation, not an observed Google response.

Prior `presentation` is a nonempty object with only `max_snippet`,
`max_video_preview`, and `max_image_preview`. Each selected dimension has `minimum`,
`maximum`, or both. Bounds constrain the **declared permission cap**, never a minimum
display length. Omitted dimensions are unassessed. Reject reversed bounds, unknown
fields, booleans, floats, nulls and old scalar objectives. Numeric order is 0 through
2147483647, then -1 (no numeric cap); text uses characters, video seconds. Image order
is none < standard < large. Exact equality is a singleton interval. A cap of 50
satisfies maximum 160 but contradicts minimum 160. These comparisons are TSEP policy.

Retain applicable metadata values and all final X-Robots-Tag fields in order, with
origin and scope. One initial HTTP crawler scope is supported; another crawler is
excluded but retained. A later scope after a comma is ambiguous even after an excluded
crawler. Never merge alternative source hypotheses or different rendered states.

Combine historical indexing/following directives and take the most restrictive
explicit cap. nosnippet sets text/video caps to zero, not images. Missing numeric
limits imply no declared numeric cap. Unspecified image default remains none..large,
not silently standard. For max-snippet:0 without nosnippet, preserve both documented
video readings as zero..known-video-cap; explicit video zero resolves that interval.

An unqualified preview parameter makes its dimension zero..known-cap, without erasing
a certain explicit restriction. An unknown directive makes all dimensions uncertain;
indexifembedded/unavailable_after leave indexing uncertain without contextual review.
Unsupported spelling is not a claim of Google-invalid syntax. Only bounded ASCII
integers -1/nonnegative and the closed image vocabulary are qualified.

Compare all possible caps with the intended interval: entirely inside → pass;
entirely outside on one side → fail; otherwise inconclusive. Indexing/following
comparisons remain separate. Present noindex/none makes preview applicability
inconclusive, never an automatic preview pass; a certain indexing contradiction
still fails. Independent failure prevails over another unknown dimension. Without
failure, any assessed unknown prevents pass. No new NA exemption exists.

Existing complete HTTP/UTF-8/HTML and prior-client requirements remain. The profile
combines with html-tree-directives-v1 and existing DOM readers without broadening
their extraction coverage. Keep source-hypothesis consensus, A03 attributable-state
failure priority, missing/error/binding handling and human requirements. Observations
retain ordered values, dimension decisions, intervals, limitations and profile version;
the adapter links them to the test/input and includes them in integrity and replay.

Bounds per reading: 128 HTTP+meta values, 256 KiB UTF-8, 4096 comma-separated tokens.
Overflow is inconclusive, with no absence claim from a truncated prefix. Seventy-four
prefrozen cases are synthetic, not search observations. Actual display/indexing, licensed
or structured-data uses, data-nosnippet, image availability and AI usage are unassessed.
The cited October 11 Google source's max-snippet/video tension remains explicit;
capture attribution is in the provenance record. Migration is explicit and prior.
