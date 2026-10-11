# Migration draft.26 → draft.27 / Migration draft.26 → draft.27

## Français

TS39 ajoute trois règles atomiques et le profil explicite `delivery-evidence-v1` :
matrice/configuration préalable revue, signaux par cellule, attribution des
contextes et du cache. Le [contrat bilingue](delivery-evidence.md) précise les
entrées, dates, revues liées et limites. Interpréteur 26, adaptateur 27, HTML 10 ;
observateur de variantes 1 et rejeu 3 inchangés. Les 44 IDs/titres et leur provenance
sont conservés ; les 1 104 anciens cas gardent exactement leur sens et leur ordre.

Les rapports draft.26 et paquets précédents se rejouent avec leurs outils exacts.
Ne pas remplacer leur version ou leur empreinte. Pour évaluer TS39, préparer un
nouveau plan de collecte, ses revues et les entrées requises ; l’ancien observateur
HTTP/Vary seul ne devient pas un résultat de contrôle. Aucune revue humaine n’est
créée par migration. Les 77 nouveaux cas sont des exercices rédigés, pas des
observations de CDN ou d’Edikka. La remise en forme compacte du corpus maintient
la borne de lecture 8 Mio sans modifier les objets historiques.

L’ancienne mention d’accessibilité Googlebot est explicitée : une politique revue
doit permettre l’accès aux variantes, les tests établissent le traitement de leur
client déclaré. Une visite ou l’accès réel d’un opérateur restent non établis.
Ce point n’autorise pas une dispense d’accessibilité cachée. Les exemptions de
contrôle exigent toujours une preuve positive d’absence de mécanisme de variation ;
le premier lecteur n’émet pas de NA atomique automatique.

Historique de qualification conservé : les 60 premiers scénarios figés avaient une
erreur de date dans les exemptions natives (revue après l’évaluation). Le premier
lecteur a correctement laissé 34 couples attendus à tort positifs inconclusifs.
V2 corrige seulement ces entrées et leurs liaisons, conserve les attendus et
l’original V1. Dix-sept frontières supplémentaires ont ensuite révélé un faux
défaut de présentation : la vue HTTP seule ignorait une meta nosnippet valide.
Elle est désormais limitée aux exclusions additives, avec lecture complète native
toujours exigée. Les échecs de développement restent dans la provenance.

## English

TS39 adds three atomic rules under explicit `delivery-evidence-v1`: prior reviewed
matrix/configuration, per-cell signal consistency, and context/cache attribution.
See the [bilingual contract](delivery-evidence.md). Interpreter26, adapter27,
HTML10; variants observer1 and replay3 unchanged. All44 IDs/titles/provenance remain;
the previous1,104 case objects retain their exact meaning and order.

Keep draft26 reports and old bundles with their exact tools. Never upgrade their
labels/fingerprints in place. A new TS39 assessment requires a prior plan, supplied
reviews and required evidence. The earlier HTTP/Vary observer alone is not a
control verdict; migration creates no human review. The77 new cases are authored
exercises, not CDN or Edikka observations. Compact corpus formatting preserves the
8MiB input limit without changing historical objects.

Googlebot accessibility is clarified: reviewed policy must permit declared variant
access, while test evidence concerns the declared client. Actual operator access
or visits remain unestablished; no hidden accessibility exemption is introduced.
Whole-control NA still needs positive configuration evidence that no variation
mechanism exists; this reader emits no automatic atomic NA.

Qualification history: the first60 prefrozen scenarios dated native exemption
reviews after their native assessment. The reader correctly left34 wrongly expected
positive pairs inconclusive. V2 corrects only those input timestamps/bindings,
preserving expectations and V1. Seventeen additional boundaries exposed a false
preview failure when a valid meta nosnippet was ignored by the header-only view.
That auxiliary view now detects additive exclusions only; full native interpretation
remains required. Development failures are retained in provenance.
