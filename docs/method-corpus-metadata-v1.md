# Métadonnée du corpus de méthode / Method corpus metadata — v1

FR : la première qualification complète de draft.5, commit
`4a09f0d0316e39eab25a71ad89baae00ab27f510`, a exécuté 1254 tests et observé un
échec dans `AtomicRules.test_method_case_reports`. La métadonnée
`tests/fixtures/control-cases.json.protocol_version` indiquait encore draft.4,
alors que le protocole était draft.5. Les 1253 autres méthodes n'ont signalé
aucun échec ; les étapes suivantes du vérificateur n'ont pas été exécutées.
Le même échec a été reproduit séparément avant correction. Ce passage n'est
pas une qualification complète réussie.

EN: the first complete draft.5 verification, commit above, ran1254 tests and
observed one failure in `AtomicRules.test_method_case_reports`. The
`tests/fixtures/control-cases.json.protocol_version` metadata still said
draft.4 although the protocol was draft.5. The other1253 test methods reported
no failure; subsequent verifier steps did not run. The same failure was
reproduced separately before correction. This run was not successful complete
qualification.

FR : seule cette métadonnée du corpus est alignée sur draft.5. Chaque cas rédigé,
preuve, résultat attendu et étiquette synthétique demeure identique. Il s'agit
de rapports de méthode contenant des jugements fournis ; ils ne remplacent pas
les contre-cas natifs figés `render-prerequisites-v2.json`, qui éprouvent les
corrections du lecteur. Aucun test, règle, lecteur, contrat ou exemple généré
n'est modifié par cette correction de distribution.

EN: only that corpus metadata is aligned with draft.5. Every authored case,
piece of evidence, expected result and synthetic label remains identical.
These method reports contain supplied judgments; they do not replace the
frozen native `render-prerequisites-v2.json` countercases exercising the reader
corrections. No test, rule, reader, contract or generated example is changed by
this distribution correction.

FR : migration de distribution uniquement. Conserver l'archive de l'essai
échoué (SHA256 `f75c941fc6b7e35220ad5441c7052aa9800fa0d3105facd9e581fd96df69765e`)
et ses journaux. Créer l'artefact distinct
`tsep-0.3.0-draft.5-method-corpus-v1.zip`. La version normative reste draft.5,
empreinte `27fabb482d04a5604e694e7cbf155dcd674a9d7a6d05360fc45b2282145fca1d`.
Relancer les tests atomiques et de préservation, puis toutes les étapes de
`scripts/verify.py`, sans contournement, avec reconstruction et inspection.
Les résultats observés appartiennent au reçu daté séparé. Aucun audit réel,
import applicatif ou publication.

EN: distribution-only migration. Retain the failed-attempt archive (SHA256
above) and its logs. Create the distinct `tsep-0.3.0-draft.5-method-corpus-v1.zip`
artifact. Normative version remains draft.5, with the unchanged fingerprint
above. Rerun atomic and preservation tests, then every `scripts/verify.py` step
without bypass, including reconstruction and inspection. Observed results
belong to the separate dated receipt. No real audit, application import or
publication.
