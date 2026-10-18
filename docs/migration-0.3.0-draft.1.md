# Migration RC1 → 0.3.0-draft.1

## Français

Base exacte : `7b60c20e7ac572574f756ad92531e0c46f7b83e7` (0.2.0-rc.1).
Cette branche de préparation ne conditionne ni ne remplace la finalisation RC1.
Seuls TS13-A01/A02 et TS14-A01 sont ajoutés : 30 contrôles à règles, 70 règles.
TS01–TS44, les profils et la provenance historique sont conservés. Les 67 règles
RC1 gardent leur contenu et leur rule_version `0.2.0-rc.1`, notamment TS12-A01–A03,
TS15-A01–A03, TS16-A01, TS17-A01–A02 et TS18-A01–A03. Seuls les contrôles TS13/TS14
portent rule_version `0.3.0-draft.1`. Le validateur de maintenance accepte ces deux
identités explicites ; les empreintes de préservation sont distribuées dans
`provenance/v030-rc1-preservation.json` et vérifiées par les tests.

Les tests propres aux règles héritées restent inchangés. Deux adaptations des
tests génériques d’intégration sont explicites : ajout de cinq cas TS13/TS14 au
sous-ensemble du transport externe et attente HTML27 au lieu de26. Leurs assertions
historiques restent présentes ; une transformation inverse vérifiée retrouve leurs
octets RC1. Les 524 autres fichiers historiques répertoriés sont identiques.

Nouveaux dossiers uniquement : déclarer le nouveau protocole et son empreinte,
les lecteurs, les originaux et revues selon le [contrat TS13/TS14](sitemap-quality-evidence.md).
Ne pas changer les versions/empreintes des anciens rapports, archives ou reçus.
Un résultat TS15, TS10 ou une liste d’URL ne suffit pas à créer une preuve TS13/TS14.
Conserver le moteur exact de RC1 pour son rejeu ; aucun ancien verdict n’est converti.
Les rapports de cette édition ont une nouvelle empreinte de protocole même si leurs
règles sélectionnées sont inchangées. Le format de rapport reste 2.

TS13 demande ses deux règles pour C ; preuves incomplètes donnent NT, contradiction
étayée donne NC même avec d’autres inconnues. TS14 sans lastmod complet autorise
seulement une exemption atomique ; absence d’historique n’est jamais C ou NA.
Les nouvelles règles utilisent Python standard et les lecteurs historiques bornés ;
la vérification de toutes les règles héritées conserve Node24 explicite.
Interpréteur47 /adaptateur46 /HTML27 ; rejeu3 inchangé. Aucun outil d’application,
site Edikka/TSEP, tag ni publication n’est modifié.

Les exemples régénérés sont des dérivés courants explicitement synthétiques.
Aucun audit réel, navigateur, revue humaine, modification de contenu réelle,
indexation, classement ou adoption ne peut être déduit de leur réussite.
La vérification locale, ses échecs éventuels et l’archive reconstruite sont consignés
séparément avec leurs empreintes ; ce texte ne prouve aucune exécution CI distante.

## English

Exact base: `7b60c20e7ac572574f756ad92531e0c46f7b83e7` (0.2.0-rc.1).
This preparation branch neither blocks nor replaces RC1 finalization. Only
TS13-A01/A02 and TS14-A01 are added: 30 rule-bearing controls, 70 rules.
TS01–TS44, profiles and historical provenance are retained. The 67 RC1 rules retain
their content and rule_version 0.2.0-rc.1, including TS12-A01–A03, TS15-A01–A03,
TS16-A01, TS17-A01–A02 and TS18-A01–A03. Only TS13/TS14 receive rule_version
0.3.0-draft.1. Maintenance admits these two explicit identities; distributed
preservation fingerprints are verified in tests.

Inherited rule-specific tests remain unchanged. Two generic integration updates
are explicit: append five TS13/TS14 external-transport cases and expect HTML27
instead of26. Historical assertions remain; a checked inverse transformation
recovers the exact RC1 test bytes. The other 524 listed historical files are identical.

Create new dossiers with the new protocol/fingerprint, selected readers, originals
and supplied reviews under the linked contract. Never relabel historical reports,
archives or receipts. A TS15/TS10 result or URL list is insufficient TS13/TS14 evidence.
Replay RC1 with its exact historical engine; no verdict conversion. New reports have
the new protocol fingerprint even when selecting unchanged rules. Report format 2
is unchanged. TS13 C needs both rules; gaps are NT and evidenced contradiction NC
with other unknowns retained. Complete lastmod absence permits only atomic exemption;
missing history is never C/NA. New rules use standard Python and bounded historical
readers; full inherited verification still uses explicit Node24.
Interpreter47 /adapter46 /HTML27, replay3 unchanged. No application, Edikka/TSEP
website, tag or publication change.

Current generated examples remain explicitly synthetic. They establish no real audit,
browser observation, human review, actual change, indexing, ranking or adoption.
Local results/failures and the reconstructed archive are recorded separately with
fingerprints; preparing this text is not evidence of remote CI execution.
