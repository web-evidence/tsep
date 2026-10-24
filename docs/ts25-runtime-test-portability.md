# TS25 runtime boundary fixtures / Frontières de test TS25

Version 1, 2026-10-18. Non-normative test extension on 0.3.0-draft.1.

## Français

Les 19 recettes `critical-presence-budget-v3.json`, leurs empreintes et leurs
attentes natives restent intactes. Deux tailles publiques exactes de cette fixture
sont propres au runtime d'origine : Python 3.9.6 et Node 24.19.0. Sur RC1 exact,
Python 3.12.14 ajoute quatre octets, car son identité apparaît deux fois. Le refus
au-delà de 4 194 304 octets est correct ; le moteur n'est pas modifié.

L'extension `critical-presence-runtime-boundaries-v1.json` conserve les empreintes
des observations historiques après normalisation **en copie** des six chaînes
Python/Node/V8/Ada/ICU/Unicode aux deux emplacements explicitement vérifiés. Toute
autre variation échoue. La classification publique historique dépend alors de la
taille réelle, comparée à la constante littérale. Les preuves exportées gardent
les identités réelles ; aucune version n'est maquillée.

Deux nouveaux cas synthétiques attendent littéralement C à 4 194 304 octets et un
refus technique à 4 194 305 octets. Leur recette est calculée une fois à partir de
la taille sans remplissage, avec deux occurrences de l'espace de portée et une
occurrence du complément de revue. Aucun verdict, garde de production, recherche
itérative ou relance jusqu'au succès n'intervient dans ce calcul. Le test exige
ensuite la taille exacte, les résultats natifs pass/pass, la décision attendue,
l'intégrité de l'entrée, le rejeu hors ligne et la conservation du runtime.

Migration de test uniquement : conserver les fixtures v3 ; ajouter l'extension
v1 et son SHA-256. L'overlay de provenance décrit les remplacements inversibles
du test historique. Les lecteurs, règles, seuils et documents normatifs restent
inchangés. Ces tests sont des exercices synthétiques, sans audit réel ni preuve
de fonctionnement sur les autres environnements. Les résultats observés et
échecs antérieurs figurent dans le dossier local de livraison.

## English

The 19 `critical-presence-budget-v3.json` recipes, fingerprints and native expected
outcomes remain intact. Two exact public sizes belong to the original runtime,
Python 3.9.6 with Node 24.19.0. On exact RC1, Python 3.12.14 adds four bytes because
its identity occurs twice. Refusal above 4,194,304 bytes is correct; no engine change.

The v1 extension fingerprints historical observations after normalizing a **copy**
of the six Python/Node/V8/Ada/ICU/Unicode strings at exactly two checked locations.
Any other change fails. Historical public classification then compares actual
size with the literal bound. Exported evidence retains actual runtime identities.

Two new synthetic cases literally expect C at 4,194,304 bytes and technical refusal
at 4,194,305 bytes. One linear calculation uses the unpadded serialized size, two
scope-padding occurrences and one review-padding occurrence. It never consults
verdicts or the production guard, searches or retries until success. Tests then
require exact size, native pass/pass, expected public outcome, input integrity,
offline replay and actual runtime provenance.

Test-only migration: keep v3 fixtures and add the fingerprinted v1 extension.
The provenance overlay records reversible historical test edits. Readers, rules,
thresholds and normative documents remain unchanged. These are synthetic exercises,
not a real audit or evidence about untested environments. Observed results and
prior failures belong in the local delivery record.
