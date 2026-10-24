# Migration 0.3.0-draft.4 → 0.3.0-draft.5

FR : correction distincte des préalables TS30-A01/A02 et TS37-A03. Les identités
TS01–TS44 et les 98 règles restent présentes ; 95 objets de règles sont inchangés.
Les versions de contrôle TS30/TS37 deviennent draft.5 ; TS37-A01/A02 gardent leurs
définitions exactes. Toutes les 67 règles RC1 et leurs versions sont conservées.
Le manifeste `provenance/v030-draft4-rule-baseline.json` fige les 98 définitions
antérieures ; les autres baselines demeurent intactes. Aucun tag ni archive
antérieurs n'est remplacé, aucune publication ou intégration applicative.

EN: distinct prerequisite correction for TS30-A01/A02 and TS37-A03. TS01–TS44
identities and all98 rules remain;95 rule objects are unchanged. TS30/TS37 control
versions become draft.5; TS37-A01/A02 definitions remain exact. All67 RC1 rules
and their versions are preserved. `provenance/v030-draft4-rule-baseline.json`
freezes all98 prior definitions; earlier baselines remain intact. No old tag or
archive is replaced; no publication or application integration.

FR : le candidat précédent, commit43e5e06, a réussi sa suite complète locale.
Les contre-cas ajoutés ensuite ont néanmoins reproduit des pass incorrects pour
H1 masqué et URL relative avec base, ainsi que des contradictions HTTP masquées
par CSS/srcset ou un schéma non pris en charge. Les tests existants ne couvraient
pas ces combinaisons. Les21 nouveaux cas/28 paires sont rédigés et figés avant
la correction, SHA256 `66d08540d0c6041d463307bb5b7f3e1c1dbcc80fa10b3be32f23143ae59a0fb8`.
Leur premier passage montre10 cas en désaccord ; les archives et reçus antérieurs
restent des résultats historiques, pas une garantie pour ces nouveaux cas.

EN: the preceding candidate, commit43e5e06, passed its complete local suite.
Later countercases nevertheless reproduced incorrect passes for hidden H1 and
relative URLs with a base, and HTTP contradictions hidden by CSS/srcset or an
unsupported scheme. Existing tests did not cover these combinations. The21 new
cases/28 pairs were authored and frozen before correction, SHA256 as above.
Their initial run shows10 mismatching cases; earlier archives and receipts
remain historical results, not guarantees for these added cases.

FR : conserver les anciens rapports et leurs empreintes. Pour un nouveau rapport,
reprendre les originaux et le plan, puis relire avec interpréteur51/lecteur2 sous
le nouveau protocole. Adaptateur49, HTML27, rejeu3 et format `render-transport-v1`
conservés. Un ancien C peut devenir NT ; une contradiction désormais préservée
peut produire NC. Ne pas réétiqueter le paquet ancien pour masquer ces écarts.
Depuis RC1, appliquer les migrations draft.1 à draft.4, puis celle-ci. Les données
insuffisantes restent NT ; aucune nouvelle revue humaine n'est inventée.

EN: retain old reports and fingerprints. For a new report, reuse originals and
plan, then interpret with interpreter51/reader2 under the new protocol. Adapter49,
HTML27, replay3 and `render-transport-v1` input format remain. An old C may become
NT; a now-preserved contradiction may produce NC. Do not relabel an old bundle to
hide differences. From RC1 apply draft.1 through draft.4 migrations, then this one.
Insufficient evidence remains NT; no new human review is manufactured.

FR/EN : [préalables détaillés / detailed prerequisites](render-transport-prerequisites-v2.md).
TS29's independently qualified alternative is preserved; the suggested change
to reject it solely because the main branch is unknown is not adopted.
Le repli TS29 indépendamment qualifié est conservé ; l'indétermination du principal
seul ne suffit pas à rejeter cette alternative prévue par le contrat.

Run / exécuter `TSEP_SOURCE_NODE=/path/node24 TSEP_VERIFY_STEP_TIMEOUT=7200 python3 scripts/verify.py`.
All standard steps, loopback cases, source-immutability guard, archive inspection
and identical reconstruction remain required. Observed qualification is recorded
separately in the dated delivery receipt; preparation is not success.
Tous les contrôles du dépôt et la reconstruction restent obligatoires ; les
résultats observés figurent séparément dans le reçu daté. Tous les cas sont
synthétiques ; aucun audit réel, conformité globale ou certification n'en découle.
