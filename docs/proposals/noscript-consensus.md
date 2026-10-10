# Noscript : concordance des lectures / Agreement between readings

**PROPOSITION NON APPLIQUÉE — décision non enregistrée.** Option pour une future
évolution normative, éventuellement draft.8. Ce fichier ne crée aucune version,
n’altère aucune règle, n’autorise aucun verdict et ne certifie aucune conformité.
Le protocole actif reste `0.1.0-draft.7`. / **UNAPPLIED PROPOSAL — no decision
recorded.** A possible future normative change, not an issued version or rule.

**État du développement, 2026-10-10 :** l’[expérience isolée 4](../noscript-experiment.md)
couvre 68 cas initiaux, six cas de listes, 96 cas de formulaires et 103 cas de tableaux, figés avant
leurs implémentations. Leurs fichiers restent intacts ; les écarts d'attente sont
explicites pour select en v3 et le tableau vide après select en v4. Une comparaison avec html5lib 1.1 apporte une référence
externe historique limitée, avec des désaccords conservés sur les fins de ligne.
**Elle ne prouve pas deux lectures navigateur : cette limite reste un verrou avant
promotion normative.** / **Development status:** isolated experiment 4 has
68 initial, six list, 96 form and 103 table cases, each frozen before its implementation.
A historical external parser comparison retains differences, including exact-marker
outcomes across CRLF preprocessing. It does not establish browser equivalence or
justify normative promotion. All existing protocol reports remain unchanged.

## Français

### Problème précis

Un `noscript` contenant `<img alt="Forbidden">` peut être du texte brut lorsque
le scripting est activé, ou une balise dont l’attribut est exclu lorsqu’il est
désactivé. Le contrat actuel ne choisit pas le mode. Ignorer systématiquement le
contenu ou adopter le mode qui donne pass serait injustifié. L’interpréteur actuel
conserve donc toute extraction non résolue comme indéterminée.

### Règle proposée, à discuter

Applicabilité : branche des marqueurs de TS01-A02, HTML UTF-8 complet contenant
un noscript non vide. Les priorités URL finale, empreinte complète identique et
stabilité explicitement exigée restent antérieures et inchangées. Cette proposition
ne corrige donc pas, à elle seule, une référence erronée acceptée par égalité de digest.

Entrées : corps original intégral et son empreinte, type de média, critères
préalables inchangés, interpréteur/version et preuves des deux lectures. Aucune
exécution JavaScript ni requête de ressources. Les modes activé et désactivé sont
**deux hypothèses globales appliquées au document entier**, pas un choix par
élément ni une extraction isolée du texte entre deux balises noscript.

Attente proposée : produire les segments puis appliquer les mêmes marqueurs dans
chacune des deux lectures, sans concaténer les segments à travers du balisage,
sans normaliser les espaces, CRLF, la casse ou Unicode. Si les deux lectures
complètes donnent pass, résultat pass ; si elles donnent toutes deux fail,
résultat fail, avec les raisons propres à chacune ; sinon inconclusive.
**Toute lecture incomplète, non prise en charge ou ambiguë garde inconclusive**,
même si l’autre lecture échoue. Aucun verdict majoritaire, aucun vote par marqueur,
aucun choix du mode favorable.

Preuves exigées : empreinte du corps complet, identité de l’outil, limites de
chaque lecture, état de complétude, segments attribuables à leur position source,
marqueurs manquants/présents et raisons, plus une matrice de concordance. Une
fermeture dans un attribut peut changer l’interprétation de la suite du document :
le préfixe déjà extrait ne suffit jamais.

Hypothèses et limites : le comportement du navigateur, le DOM réel, l’exécution
JavaScript, les valeurs de formulaire et la visibilité ne sont pas évalués.
Les modes n’autorisent ni réparation silencieuse du document ni normalisation
HTML5 contraire au contrat. Il reste à spécifier précisément leurs frontières
lexicales et les situations de construction d’arbre nécessitant inconclusive.
Les références de caractères dans RAWTEXT ne se traitent pas comme dans DATA.
La proposition n’affirme pas qu’un interpréteur normatif sait réaliser ces lectures
dans tous les contextes ; l’expérience séparée en éprouve un sous-ensemble explicite.

### Contre-exemples proposés, non exécutés comme règle TSEP

Requis `Expected`, interdit `Forbidden`, corps changé, URL inchangée. Chaque
fragment est à placer dans un document complet ; `Expected` placé avant noscript
est du texte ordinaire. Les résultats ci-dessous sont des attentes de conception,
pas des mesures ni le corpus normatif courant.

| Fragment | Scripting activé | Désactivé | Proposition |
| --- | --- | --- | --- |
| `Expected<noscript><img src="x"></noscript>` | pass | pass | pass |
| `Expected<noscript><img alt="Forbidden"></noscript>` | fail | pass | inconclusive |
| `<noscript><img alt="Expected"></noscript>` | pass | fail | inconclusive |
| `<noscript>Expected</noscript>` | pass | pass | pass |
| `Expected<noscript>Forbidden</noscript>` | fail | fail | fail |
| `<noscript>&#69;xpected</noscript>` | fail | pass | inconclusive |
| Une des lectures exige une réparation ou dépasse une borne | quelconque | inconnue | inconclusive |

Avant implémentation : figer les documents entiers, y compris fermetures piégées,
noscript dans head/body, plusieurs noscript, commentaires, iframe, états bruts et
marqueurs découpés ; définir l’oracle de chaque lecture. Les 73 cas select préparés
localement sont une autre proposition, non figée et non implémentée.

### Impact et décision

Impact potentiel : certains NT pourraient devenir pass ou fail ; les anciens
paquets ne changent jamais. Aucune page Edikka n’est annoncée comme débloquée par
ce document. La campagne réelle séparée indique les constructions observées et
la disponibilité actuelle de l’extraction ; elle n’est pas une simulation de
cette proposition. L’inventaire est non exhaustif, donc lever noscript ne garantit
pas qu’il soit le dernier obstacle.

Si cette option est retenue : créer une version normative distincte, mettre à jour
la source bilingue, contrats, schéma si nécessaire, migration et cas contradictoires ;
conserver tags, anciennes archives et captures ; produire de nouvelles évaluations
avec version et hypothèses explicites. Si elle est refusée : maintenir NT ou
proposer une autre définition explicite du texte source. **Décision : en attente.**

## English

The active draft.7 contract does not choose the scripting mode for noscript.
Markup such as an image with a forbidden-marker attribute can be raw text in one
mode and an excluded attribute in the other. Silently dropping it or choosing the
favorable reading is unjustified. Current unresolved extraction stays inconclusive.

Proposed applicability is only TS01-A02's changed-body HTML UTF-8 marker branch.
Final URL, equal complete-body digest and explicitly stable representation keep
their existing precedence. Inputs are the complete retained body/hash, media type,
prior criteria and identified tools. No JavaScript execution or resource requests.
Apply enabled and disabled scripting as **global hypotheses over the entire
document**, never separately per noscript or only to a sliced fragment.

Each supported complete reading supplies exact source segments and runs the same
literal marker criteria. Both pass gives pass; both fail gives fail, with each
reading's reasons; any disagreement, incomplete reading or unsupported context
gives inconclusive, even when the other reading fails. No majority vote, favorable
mode choice, joining across markup or whitespace/case/Unicode/CRLF normalization.
The table above is a set of proposed expectations, not executed TSEP observations.
RAWTEXT and DATA character references differ. A closing delimiter in an attribute
can change the rest of the document; a resolved prefix never establishes a result.

Evidence must retain the full body hash, tool identity, per-reading boundaries,
completeness, source-attributable segments, missing/present markers and agreement
matrix. Lexical boundaries and cases requiring tree repair still need specification.
The proposal does not assert that the normative tool implements both readings;
the separate experiment tests an explicitly bounded lexical subset.
It does not assess actual DOM, rendering, form values, JavaScript behavior or visibility.

Potential impact is NT becoming pass or fail; no old evidence changes. No real
Edikka page is claimed resolved. The separate campaign measures present behavior,
not this proposed rule; its construction inventory is non-exhaustive. Before code,
freeze whole-document counterexamples, including head/body, multiple noscript,
trapped closings, comments, iframe and raw states, with per-reading expectations.

If accepted, issue a distinct normative version, update bilingual source/contracts,
schema if needed, migration and contradictory cases; preserve old tags, tools and
captures and make new assessments. If declined, retain NT or define another
explicit source-text interpretation. **Decision remains pending; nothing is applied.**

## Sources

[WHATWG noscript](https://html.spec.whatwg.org/multipage/scripting.html#the-noscript-element)
and [parsing](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inbody).
Dated full captures retained in the lot 6 evidence (2026-10-10 06:00:57–58 UTC),
SHA-256 respectively `7629c8213a7f5175d444f5a0eda1fcfb8c61f1eb2a21525ec174d79b0eb69529`
and `34e193906e6898ae7faf576a8d4c0f8de619a86ec99d85a3baeb2713171f1dbf`.
Scope: parsing modes only; the consensus rule is a TSEP proposal, not a WHATWG rule.
