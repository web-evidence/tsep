# HTTP canonical context / Contexte canonical HTTP — version 1

## Français

Draft.19 ajoute le choix préalable `intent.canonical.http_reader: "http-link-context-v1"`
à TS10-A01/A02. Sans ce champ, le lecteur historique demeure strictement inchangé.
Une sélection nulle/inconnue reste indéterminée, sans repli. A01 reste semiAuto et
A02 manual ; aucune revue humaine, capture rendue ou intention n'est déduite.

**Entrées et portée.** Famille, préférence et méthodes requises sont déclarées
avant les captures. La réponse finale GET 200 doit être complète, datée et
attribuable selon la chaîne HTTP existante. Seuls ses champs Link sont évalués ;
les champs des sauts intermédiaires restent dans les captures originales. Une
redirection conserve également le contrôle séparé de sa destination. Le diagnostic
porte URL demandée/finale, date et empreinte de la chaîne source. Une empreinte
contrôle le rattachement, sans authentifier le collecteur ni l'auteur.

**Lecture.** Les champs, liens et paramètres restent ordonnés, avec les valeurs
brutes et les répétitions. Virgules hors chevrons/guillemets séparent les liens ;
les éléments vides de liste sont ignorés. Les noms de paramètres sont abaissés,
les paires échappées sont décodées dans les valeurs citées. Le premier rel gouverne
la relation ; les suivants sont conservés comme ignorés. Plusieurs relations sont
séparées par des espaces ; leur casse ne crée pas une nouvelle relation canonical.
Une relation URI d'extension ne devient pas canonical par son dernier segment.
Un rel absent, vide, syntaxiquement ambigu ou contenant une tabulation reste inconnu.

**Contexte.** Sans anchor, le contexte est l'URL finale. Avec un seul anchor, sa
référence est résolue selon les composants RFC3986, en conservant les queries et
fragments vides, les doubles slashs et les caractères encodés. Ni base HTML ni
Content-Location ne remplace la base de cette réponse GET 200. Deux anchor, même
identiques, ou un anchor sans valeur restent inconnus. Le contexte résolu identique
à l'URL finale concerne cette page. Un contexte différent n'est exclu du jugement
sur cette page que si **les deux URL** ont un schéma http/https minuscule, un hôte
ASCII minuscule sans port, adresse IP littérale entre crochets ou point terminal,
un chemin commençant par slash sans segment . ou .., aucun caractère encodé et aucune query/fragment
vide. Les formes hors de ce sous-ensemble restent inconnues : leur équivalence
potentielle ne doit pas masquer une contradiction. Un fragment non vide peut
désigner un autre contexte ; il n'est pas supprimé. La déclaration exclue reste
visible et n'est jamais transférée à un autre membre de la famille.

**Destination et décision.** Sur le contexte courant, la cible canonical est
comparée littéralement à la préférence absolue sans fragment. Une référence relative
peut être légale en HTTP et échouer à ce critère TSEP ; aucune invalidité RFC ou
conséquence Google n'en est déduite. Les paramètres autres que rel/anchor restent
inconnus, y compris title et title*. Le registre commun des modificateurs canonical identifie notamment
lang/hreflang/media/type ; les attributs HTML ordinaires ne sont pas automatiquement
admis dans la grammaire HTTP. Les autres relations et contextes ne satisfont pas une
méthode HTTP exigée. Son absence donne fail seulement après lecture complète.

Une contradiction certaine d'un item complet donne fail malgré une autre inconnue.
Sinon, toute inconnue empêche pass. Un item non terminé n'est pas réparé en devinant
une virgule interne ; les items précédemment délimités et les champs indépendants
restent utilisables. Une déclaration étrangère au contexte ne crée pas de défaut
sur la page examinée. Les erreurs HTML/DOM indépendantes restent visibles, sans
effacer une contradiction HTTP attribuable. Aucun résultat isolé ne clôt TS10.

**Bornes et limites.** Au plus 100 champs, 65 536 octets UTF-8 au total, 1 000 items,
100 paramètres par item, 8 192 caractères par référence URI, diagnostic de 1 Mio.
Les bornes de population/champs/octets et de diagnostic refusent toute cette
lecture ; celles d'un item/reférence rendent cet item inconnu. Caractères de contrôle
(hors tabulation syntaxique), non-ASCII, repli de ligne, URI mal formée, extensions
et contextes non qualifiés sont indéterminés. Le sous-ensemble n'est pas un validateur
RFC exhaustif ni un modèle de Google. Revues, états rendus, contenu, sitemaps et liens
conservent leurs exigences. [Migration](migration-draft.19.md).

## English

Draft.19 adds prior `intent.canonical.http_reader: "http-link-context-v1"` for
TS10-A01/A02. An absent field keeps the fixed historical reader; null/unknown
selection is inconclusive without fallback. A01 remains semiAuto, A02 manual.

Inputs are a prior family/preference/method plan and attributable, complete, dated
final GET 200 evidence. Only final Link fields are assessed; intermediate fields
remain in original captures, with redirect destination assessed separately. The
diagnostic binds requested/final URLs and observation time to the source trace
digest; this is not collector/author authentication.

Retain ordered raw fields, items and parameters, including repetitions. Commas
outside quoted strings/angle brackets delimit items; empty list elements are
ignored. Parameter names are case-folded and quoted pairs unescaped. Use the first
rel, retain later occurrences as ignored. Space-separated relation names are
case-insensitive; an extension URI is not canonical because of its last segment.
Absent/empty/ambiguous or tab-containing rel stays unknown.

Default context is the final URL. Resolve a single anchor by RFC3986 components,
preserving empty query/fragment, doubled slash and percent encodings. HTML base and
Content-Location do not replace this GET 200 base. Repeated or valueless anchor is
unknown. An exactly equal context applies. A different context is excluded only
when both URLs use lowercase http/https, lowercase ASCII host without port,
bracketed IP literal or trailing dot, an absolute path without dot segments, no percent encoding and no
empty query/fragment. Outside this subset, equivalence is unknown rather than
silently excluding a potential conflict. Preserve nonempty fragments; never transfer
an excluded declaration to another family member.

For the current context, compare raw canonical destination literally with the
absolute, fragment-free preference. RFC-valid relative targets can fail this TSEP
criterion; do not infer RFC invalidity or Google behavior. Non-rel/anchor parameters
remain unknown (including title/title*), using the shared modifier registry for lang/hreflang/media/type;
ordinary HTML attributes are not thereby HTTP parameters. Other relations/contexts
cannot satisfy a required HTTP method. Absence fails only after complete reading.

A definite conflict survives independent unknowns; otherwise any unknown prevents
pass. Never recover a guessed separator within an unfinished item. Completed prefix
items and separate fields remain usable. HTML/DOM refusal does not erase attributable
HTTP failure. One successful atomic rule cannot close TS10 or replace human review.

Limits: 100 fields, 65,536 UTF-8 bytes, 1,000 items, 100 parameters/item,
8,192 characters/URI reference, 1 MiB diagnostic. Population/field/byte/diagnostic
limits refuse the whole reader; item/reference limits make that item unknown.
Non-ASCII, control characters other than syntactic HTAB, folded lines, malformed
URI, extensions and unqualified contexts remain unknown. This is not an exhaustive
RFC validator or engine model. Rendering/content/sitemap/link requirements remain.

## Sources / Sources

Consulted 2026-10-11; dated observation and capture fingerprints:
[provenance](../provenance/http-canonical-context-v1.json).

- [RFC 8288, §§3.1–3.3](https://www.rfc-editor.org/rfc/rfc8288.html#section-3.1): target, context, first rel.
- [RFC 3986, §5](https://www.rfc-editor.org/rfc/rfc3986.html#section-5): URI reference resolution.
- [RFC 9110, §6.4.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-6.4.2): GET 200 representation identity; supersedes RFC7231.
- [Google canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls): canonical methods; this profile does not observe engine processing.
