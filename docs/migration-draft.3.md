# Migration 0.1.0-draft.2 → 0.1.0-draft.3

## Français

Nouvelle interprétation normative, toujours non publiée ; format de rapport `2`
conservé. Les identifiants TS01–TS44, titres hérités, sévérités, populations des
profils et empreintes des sources 1.1 restent inchangés. Ne pas remplacer une
ancienne archive ou un tag ni changer seulement l’empreinte d’un ancien rapport.

1. Réévaluer TS01-A02 avec URL finale et SHA-256 du corps décodé attendus, déclarés
   avant la mesure. L’ancien jugement de compatibilité ne suffit plus. Sans
   référence exacte, consigner inconclusive et NT, sauf contradiction établissant NC.
2. Chaque règle porte `automation`. TS01-A01/A02 sont automatic ; TS07-A01/A02/A03
   et TS10-A01/A03/A04 semiAuto ; TS10-A02 manual. Un C automatique exige toutes
   les règles automatic, leur couverture complète et `assessor.tool.name/version`.
3. TSEP-2 désigne un type de preuve : outils webmaster du moteur visé. Google est
   la première série normative. `webmaster-tools` impose `engine`. Le type historique
   `search-console` reste Google ; une preuve Bing ne satisfait pas cette entrée.
4. Regénérer le compagnon EARL : il ajoute une assertion par observation atomique,
   reliée au contrôle, portant sur sa propre cible. Conserver le rapport complet.
5. Figer version/empreinte draft.3 et les nouveaux résultats dans un nouveau paquet.
   Exécuter `python3 scripts/verify.py` et, pour un adaptateur, la suite de conformance.

Les 43 cas de jugement historiques vérifient toujours les rapports. Les cas bruts
exécutables distincts couvrent quatre règles, pas TS07-A03, TS10 ou les 44 contrôles.
Les sorties inconnues, manquantes ou contradictoires sont testées explicitement.
Le parcours CLI, les refus de C automatique et les correspondances EARL sont testés.
Le minimum Python 3.9 est conservé ; la matrice CI ajoute 3.9/3.11/3.12/3.13.

## English

New normative interpretation, still unpublished; report format remains `2`.
TS01–TS44 identities, inherited titles, severities, profile populations and grid
1.1 source hashes are unchanged. Do not replace an old archive/tag or merely
change the fingerprint of an old report.

1. Reassess TS01-A02 against the expected final URL and decoded body SHA-256 fixed
   before measurement. The old compatibility judgment is insufficient. Without
   an exact reference, record inconclusive and NT, unless a contradiction establishes NC.
2. Every rule declares `automation`. TS01-A01/A02 are automatic; TS07-A01/A02/A03
   and TS10-A01/A03/A04 semiAuto; TS10-A02 manual. Automatic C requires every rule
   automatic, complete coverage and `assessor.tool.name/version`.
3. TSEP-2 defines an evidence type: the target engine’s webmaster tools. Google is
   the first normative series. `webmaster-tools` requires `engine`. Legacy
   `search-console` remains Google-specific; Bing evidence cannot satisfy it.
4. Regenerate the EARL companion: each atomic observation gains an assertion linked
   to its control and concerning its own target. Retain the complete report.
5. Pin the draft.3 version/hash and reassessed results in a new bundle. Run
   `python3 scripts/verify.py` and the conformance suite for an adapter.

The 43 historical judgment cases still test reports. Separate executable raw
cases cover four rules, not TS07-A03, TS10 or all 44 controls. Unknown, missing and
contradictory outputs are tested explicitly, alongside the CLI workflow, automatic
C rejection and EARL mappings. Python 3.9 remains the minimum; CI adds 3.9/3.11/3.12/3.13.
