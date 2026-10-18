# Rendu, HTML et transport / Render, HTML and transport — v1

0.3.0-draft.4. Treize nouvelles règles / Thirteen new rules. All fixtures and capture examples are SYNTHETIC / SYNTHÉTIQUES. No actual site audit.

## TS26-A01 — Accès des ressources et politiques natives / Resource access and native policies

Entrées / Inputs: `http, robots, html, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS26, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS26 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Sur chaque ressource critique sélectionnée, comparer HTTP direct200, robots du même origin et intersection des CSP HTTP du document HTTPS. Relever la source complète pour exclure une CSP meta non qualifiée.

EN: For each selected critical resource compare direct HTTP200, same-origin robots and intersection of HTTP CSP policies from the HTTPS document. Retain complete source to exclude unqualified meta CSP.

**Attendus / Expectations**

FR : Une erreur HTTP, un refus robots ou un refus CSP qualifié échoue indépendamment des autres lacunes.

EN: A qualified HTTP error, robots denial or CSP denial fails independently of other gaps.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, robots, html, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: http, robots, html, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : Inventaire absent, robots non fourni, directive CSP non prise en charge, nonce, meta CSP, source ambiguë ou revue absente : NT.

EN: Absent inventory, missing robots, unsupported CSP directive, nonce, meta CSP, ambiguous source or absent review: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS26-A02 — Trafic et console attribués au rendu / Traffic and console attributed to rendering

Entrées / Inputs: `render, http, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS26, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS26 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Lire un export HAR borné fourni, relier la réponse du document aux octets HTTP, puis vérifier chaque ressource critique. Conserver la console datée liée au HAR et la revue de criticité.

EN: Read a supplied bounded HAR export, bind its document response to native HTTP bytes, then check every critical resource. Retain dated HAR-bound console and criticality review.

**Attendus / Expectations**

FR : Les ressources sélectionnées ont une réponse2xx sans erreur réseau fournie. Une erreur console sans classification qualifiée reste NT ; un échec réseau natif reste NC.

EN: Selected resources have2xx responses without supplied network error. Unclassified console errors remain NT; native network failure remains NC.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : render, http, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: render, http, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : HAR incomplet, corps absent, contexte/session non attribué, console absente ou erreur non qualifiée : NT.

EN: Incomplete HAR, omitted body, unattributed context/session, missing console or unqualified error: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS27-A01 — Routes et historique attribués / Attributed routes and history

Entrées / Inputs: `http, render, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS27, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS27 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Vérifier quatre états fournis dans l’ordre direct, actualisation, retour, avance : session, séquence, date, URL, liaison à la réponse serveur et statut.

EN: Check four supplied states in direct, refresh, back, forward order: session, sequence, time, URL, server-response binding and status.

**Attendus / Expectations**

FR : Chaque état conserve l’URL de route et sa source200 prévue. Une URL ou un statut contraire qualifié échoue.

EN: Every state retains its route URL and intended200 source. A qualified conflicting URL or status fails.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, render, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: http, render, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : État, action, liaison, session ou ordre absent/ambigu ; surface frame/shadow non collectée : NT.

EN: Missing/ambiguous state, action, binding, session or order; uncollected frame/shadow surface: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS27-A02 — Contenu et canonical par état SPA / Content and canonical in each SPA state

Entrées / Inputs: `http, render, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS27, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS27 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Dans les mêmes états qualifiés, comparer les identifiants littéraux, textes essentiels et destinations de liens au plan, puis une canonical explicite dans head. Exiger la revue de fonctionnement.

EN: Within the same qualified states compare literal IDs, essential text and link destinations with the plan, then one explicit head canonical. Require operation review.

**Attendus / Expectations**

FR : Les états conservent contenus et signaux propres. Absence sur surface complète, contenu divergent ou canonical contraire échoue.

EN: States retain their intended content and signals. Absence on a complete surface, differing content or conflicting canonical fails.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, render, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: http, render, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : État partiel, contexte masqué, ID ambigu, hypothèses HTML divergentes ou revue absente : NT.

EN: Partial state, hidden context, ambiguous ID, differing HTML hypotheses or absent review: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS28-A01 — Structure native et structure DOM fournie / Native source and supplied DOM structure

Entrées / Inputs: `html, render, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS28, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS28 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Comparer dans la source et la sérialisation fournie : titre, langue, main déclaré, liste ordonnée des titres, liens et libellés. Le nombre de H1 est celui du plan.

EN: Compare source and supplied serialization: title, language, declared main landmark, ordered headings, links and labels. H1 count follows the plan.

**Attendus / Expectations**

FR : Les structures correspondent au plan préalable ; divergences structurelles qualifiées échouent.

EN: Structures agree with the prior plan; qualified structural conflicts fail.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, render, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: html, render, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : Source/DOM absent, langue non déclarée, arbre ambigu ou contexte visuel non qualifié : NT.

EN: Absent source/DOM, undeclared language, ambiguous tree or unqualified visual context: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS28-A02 — Revue du sens et de la navigation / Meaning and navigation review

Entrées / Inputs: `html, render, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS28, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS28 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Reprendre les faits structurels attribués et exiger une revue distincte liée : adéquation du titre et de la langue, hiérarchie, sujet principal, navigation et libellés dans l’usage déclaré.

EN: Reuse attributed structural facts and require a distinct bound review of title/language adequacy, hierarchy, main subject, navigation and labels in declared use.

**Attendus / Expectations**

FR : Les faits sont qualifiés et le jugement motivé soutient le sens et l’usage ; contradiction étayée échoue.

EN: Facts are qualified and a reasoned judgment supports meaning and use; evidenced contradiction fails.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, render, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: html, render, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : Le parseur seul, une revue sans liaison ou des originaux insuffisants ne suffisent pas : NT.

EN: Parser output alone, an unbound review or insufficient originals are not enough: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS29-A01 — Scénario scripts bloqués et repli testé / Blocked-script scenario and tested fallback

Entrées / Inputs: `html, render, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS29, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS29 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Lire la source et un état fourni explicitement scripts-blocked ; comparer chaque contenu/lien essentiel, ou le repli prédéclaré dans ce même état. Exiger la revue des actions et du fonctionnement.

EN: Read source and a supplied state explicitly marked scripts-blocked; compare every essential content/link or the prior fallback within that same state. Require action and operation review.

**Attendus / Expectations**

FR : Tous les attendus principaux ou tous ceux du repli testé sont étayés. Un échec principal et du repli qualifiés échoue ; aucune fonction n’est déduite du texte seul.

EN: All main expectations or all tested fallback expectations are supported. Qualified failures of both main and fallback fail; text alone does not establish function.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, render, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: html, render, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : Condition normale, capture partielle, repli seulement décrit, contexte masqué ou revue manquante : NT.

EN: Normal condition, partial capture, merely described fallback, hidden context or missing review: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS29-A02 — Scénario styles dégradés et repli testé / Degraded-style scenario and tested fallback

Entrées / Inputs: `html, render, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS29, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS29 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Appliquer le même examen dans un état explicitement styles-degraded, avec observations d’actions et revue liée. Ne pas assimiler la désactivation des scripts à ce scénario.

EN: Apply the same examination in an explicitly styles-degraded state with action observations and a bound review. Script disabling does not qualify this scenario.

**Attendus / Expectations**

FR : Les fonctions essentielles ou le repli testé restent étayés dans ce scénario distinct.

EN: Essential functions or tested fallback remain supported in this distinct scenario.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, render, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: html, render, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : Absence de scénario styles dégradés, preuve de repli ou jugement attribué : NT.

EN: Missing degraded-style scenario, fallback evidence or attributed judgment: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS30-A01 — Métadonnées et doublons du corpus déclaré / Metadata and duplicates in the declared corpus

Entrées / Inputs: `html, content, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS30, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS30 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Lire title, description, H1, og:title, og:description natifs par page. Comparer aux valeurs prévues puis les doublons entre pages sélectionnées ; exiger une décision préalable pour chaque doublon intentionnel.

EN: Read native title, description, H1, og:title, og:description for each page. Compare prior values and duplicates among selected pages; require a prior decision for each intentional duplicate.

**Attendus / Expectations**

FR : Valeurs et multiplicité concordent ; chaque doublon observé possède une décision motivée unique. Le corpus ne dépasse pas les pages fournies.

EN: Values and multiplicity agree; each observed duplicate has one reasoned decision. The corpus is limited to supplied pages.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, content, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: html, content, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : Source absente, politique de champ omise, parse ambigu ou revue manquante : NT. null autorise seulement un champ facultatif explicitement absent.

EN: Missing source, omitted field policy, ambiguous parse or missing review: NT. null permits only an explicitly absent optional field.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS30-A02 — Cohérence éditoriale et contenu principal / Editorial coherence and main content

Entrées / Inputs: `html, content, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS30, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS30 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Rapprocher les métadonnées natives et le contenu principal identifié ; exiger une revue distincte de la promesse, du sens et de la visibilité pertinente.

EN: Reconcile native metadata and identified main content; require a distinct review of promise, meaning and relevant visibility.

**Attendus / Expectations**

FR : Les faits concordent avec le plan et la revue éditoriale liée les soutient ; une contradiction native ou humaine qualifiée échoue.

EN: Facts agree with the plan and the bound editorial review supports them; qualified native or human contradiction fails.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, content, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: html, content, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : Source/rendu nécessaire non qualifié, contenu masqué, sens sans revue ou jugement non lié : NT.

EN: Unqualified required source/rendering, hidden content, meaning without review or unbound judgment: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS37-A01 — Certificats, hôte, date et confiance fournie / Certificates, host, time and supplied trust

Entrées / Inputs: `tls, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS37, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS37 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Relire les PEM publics fournis avec OpenSSL3 hors réseau : chaîne, usage serveur, hôte DNS, heure fournie et racines explicitement fournies. Désactiver magasins implicites ; conserver version et diagnostic.

EN: Recheck supplied public PEMs with offline OpenSSL3: chain, server purpose, DNS host, supplied time and explicit supplied roots. Disable implicit stores; retain version and diagnostic.

**Attendus / Expectations**

FR : La vérification du profil réussit sous les racines fournies. Une erreur X509 prise en charge, dont expiration ou mauvais hôte, échoue.

EN: Profile verification succeeds under supplied roots. A supported X509 error, including expiry or wrong host, fails.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : tls, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: tls, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : OpenSSL3 absent, PEM inutilisable, capture mal attribuée, racines absentes ou code d’erreur non qualifié : NT.

EN: Missing OpenSSL3, unusable PEM, misattributed capture, absent roots or unqualified error code: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS37-A02 — Redirections HTTPS et décision HSTS / HTTPS redirects and HSTS decision

Entrées / Inputs: `http, configuration, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS37, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS37 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Suivre la chaîne HTTP fournie vers HTTPS sans rétrogradation, vérifier la réponse directe200, comparer configuration HSTS et en-tête au plan : activation, max-age, sous-domaines, portée, propriétaire, motif.

EN: Follow the supplied HTTP chain to HTTPS without downgrade, check direct200 response, compare HSTS configuration and header with planned enablement, max-age, subdomains, scope, owner and rationale.

**Attendus / Expectations**

FR : Chaînes et décision HSTS concordent ; HSTS peut être désactivé explicitement. Aucun preload imposé.

EN: Chains and HSTS decision agree; HSTS may be explicitly disabled. No preload requirement.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, configuration, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: http, configuration, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : Chaîne/configuration manquante, en-tête ambigu, portée ou décision absente : NT.

EN: Missing chain/configuration, ambiguous header, absent scope or decision: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## TS37-A03 — Sous-ressources et trafic mixte du périmètre / Embedded resources and mixed traffic in scope

Entrées / Inputs: `http, render, intent`.

**Périmètre / Scope**

FR : Population finie préalable de TS37, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

EN: Prior finite TS37 population under render-transport-v1; see docs/render-transport-evidence.md.

**Procédure / Procedure**

FR : Relier HAR et console au document HTTPS ; examiner les requêtes observées et les URL intégrées de la source. Le profil strict exige HTTPS pour ces ressources, même si un navigateur peut les mettre à niveau.

EN: Bind HAR and console to the HTTPS document; inspect observed requests and source embedded URLs. The strict profile requires HTTPS for these resources even when a browser might upgrade them.

**Attendus / Expectations**

FR : Aucune URL HTTP observée sur ces surfaces ; revue de la couverture dynamique consignée. Un HTTP natif observé échoue malgré une autre lacune.

EN: No HTTP URL observed on these surfaces; dynamic-coverage review retained. An observed native HTTP URL fails despite another gap.

**Preuves / Evidence**

FR : Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, render, intent.

EN: Exact originals, plan and dates/context, fingerprints, diagnostics and reasoned review bound to the entire dossier. Kinds: http, render, intent.

**Hypothèses / Assumptions**

FR : Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

EN: Supplied unauthenticated provenance, inventory, browser state, conditions and judgment; two static HTML readings are not two navigations. TLS trust depends on supplied roots.

**Indéterminés / Inconclusive**

FR : HAR tronqué, corps absent, CSS/srcset non qualifiés, contexte incomplet ou revue absente : NT.

EN: Truncated HAR, missing body, unqualified CSS/srcset, incomplete context or absent review: NT.

**Non-applicabilité / Non-applicability**

FR : Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

EN: No atomic NA. Empty population or claimed absent domain without evidence remains NT in this profile.

**Limites / Limitations**

FR : Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

EN: No real audit inferred from synthetic cases. No indexing, ranking, global conformity, accessibility certification, exhaustive security or universal browser trust. Reviews may be wrong and captures may omit states.

## Contrat des entrées / Input contract

FR : reprendre le [dossier v1](evidence-dossier-v1.md), avec `reader=render-transport-v1`,1–32 items préalables identifiés, originaux natifs datés et revues liées au dossier entier. Aucun champ `status=C` ou verdict externe n'est lu. Le dossier reste limité à8MiB, chaque original et HTML à1MiB ; listes usuelles1–32, HAR128 requêtes, console128 événements. Les arbres parse5/Node24 conservent les deux hypothèses statiques,20 000 nœuds/profondeur128 et au plus2MiB de texte projeté cumulé. Une ambiguïté ou un dépassement donne NT, sans tronquer.

EN: reuse the [v1 dossier](evidence-dossier-v1.md), with `reader=render-transport-v1`,1–32 identified prior items, dated native originals and whole-dossier-bound reviews. No `status=C` or external verdict field is read. Dossiers remain bounded at8MiB, each original and HTML at1MiB; ordinary lists1–32, HAR128 requests, console128 events. parse5/Node24 trees retain both static hypotheses,20,000 nodes/depth128 and at most2MiB aggregate projected text. Ambiguity or overflow yields NT without truncation.

| Contrôle / Control | Champs du plan / Plan fields | Originaux / Originals |
|---|---|---|
| TS26 | `id,page,resources[{url,type,robots_url,robots_profile}],har,console,page_ref,complete_capture,capture_reason` | HTTP page/resources/robots ; HAR et console / HAR and console. `type` script/style/img/font/connect/media. |
| TS27 | `id,page,states[4],content[{id,text,href}],canonical` | Quatre états browser-state-v1 liés à leurs documents HTTP / Four browser-state-v1 records bound to HTTP documents. |
| TS28 | `id,page,state,structure{title,lang,main_id,headings[{id,tag,text}],links[{id,text,href}]}` | Source HTTP et état DOM fourni / HTTP source and supplied DOM state. |
| TS29 | `id,page,script_state,style_state,essential[{id,text,href}],fallback` | Source et deux états distincts ; fallback=null ou `{reason,content:[...]}` dans le même état testé / Source and two distinct states; fallback=null or `{reason,content:[...]}` within the same tested state. |
| TS30 | `id,pages[{url,metadata,content}],duplicate_decisions` | Sources HTTP sélectionnées / Selected HTTP sources. Five metadata keys: title,description,h1,og:title,og:description. Decisions: `{field,urls,value,reason,decision:'intentional'}`. |
| TS37 | `id,host,page,http_variant,certificates,configuration,hsts,har,console,page_ref,complete_capture,capture_reason` | HTTP, certificats/racines publics, configuration, HAR, console / HTTP, public certificates/roots, configuration, HAR, console. |

FR : `browser-state-v1` est un original JSON fourni sous kind `render`, avec `page_url,source_document,source_http_sha256,html,browser{name,version},session,sequence,action,condition,captured_at,complete,shadow_roots,frames,steps,failures`. `source_document` désigne l'ID unique d'un document natif ; son tableau `http` est lié par le SHA256 JSON canonique du dossier. `steps` décrit les actions effectivement observées et leurs résultats, pas seulement un plan de test ; le réviseur doit juger leur suffisance pour le fonctionnement. `complete=true`, frames=shadow_roots=0 et failures=[] sont requis dans ce profil. Ils restent des déclarations fournies, jamais authentifiées. Les actions de route sont direct/refresh/history-back/history-forward avec séquences0–3 et même session ; conditions normal/scripts-blocked/styles-degraded. Une sérialisation documentaire ne prouve pas une exécution navigateur ni la visibilité CSS. Les contextes hidden/inert/aria-hidden/style/details/dialog/noscript et les ID dupliqués restent indéterminés pour le contenu sélectionné.

EN: `browser-state-v1` is supplied original JSON under kind `render`, with `page_url,source_document,source_http_sha256,html,browser{name,version},session,sequence,action,condition,captured_at,complete,shadow_roots,frames,steps,failures`. `source_document` identifies a unique native document; its `http` array is bound by the dossier's canonical JSON SHA256. `steps` describes actually observed actions and their results, not merely a test plan; the reviewer must judge their adequacy for operation. This profile requires `complete=true`, frames=shadow_roots=0 and failures=[]. These remain supplied unauthenticated declarations. Route actions are direct/refresh/history-back/history-forward with sequence0–3 in one session; conditions are normal/scripts-blocked/styles-degraded. Documentary serialization does not prove browser execution or computed CSS visibility. hidden/inert/aria-hidden/style/details/dialog/noscript contexts and duplicate IDs remain inconclusive for selected content.

FR : le HAR est conservé dans ses octets originaux, sans enveloppe de verdict, sous kind `render`. Sous-ensemble lu : `log.version=1.2`, creator/browser{name,version}, une page avec id/startedDateTime et1–128 entries avec pageref/startedDateTime/request{method,url}/response{status,content{text,encoding}}. GET seulement ; corps principal littéral UTF8 ou base64, identique à la réponse HTTP native et même statut. Les entrées absentes ou répétées pour une ressource critique sont NT. Les champs supplémentaires restent archivés sans devenir des preuves interprétées. `browser-console-v1` contient page_url, har_sha256 (octets originaux), complete et events[{level,text,url,timestamp}]. Une console sans erreur ne prouve ni absence d'autres erreurs hors fenêtre ni rendu réussi ; la revue qualifie la couverture. Une erreur non classifiée donne NT ; ce lecteur ne fabrique aucune classification humaine.

EN: HAR original bytes are retained without a verdict wrapper under kind `render`. Read subset: `log.version=1.2`, creator/browser{name,version}, one page with id/startedDateTime and1–128 entries with pageref/startedDateTime/request{method,url}/response{status,content{text,encoding}}. GET only; literal UTF8 or base64 main body must equal native HTTP body with the same status. Missing/repeated critical-resource entries are NT. Additional fields remain archived without becoming interpreted evidence. `browser-console-v1` contains page_url, har_sha256 (original bytes), complete and events[{level,text,url,timestamp}]. An error-free console proves neither absence of other errors outside its window nor successful rendering; review qualifies coverage. Unclassified errors yield NT; this reader never manufactures a human classification.

FR : CSP est limité aux ressources de documents HTTPS : expressions none/self/*, schémas http:/https: (http: autorise aussi l'évolution vers https:) et origins HTTPS explicites sans chemin. Les directives de récupération sélectionnées suivent script-src-elem/style-src-elem, puis script-src/style-src, puis default-src ; plusieurs politiques s'intersectent. Une extension, un nonce/hash, strict-dynamic, une expression de chemin ou CSP meta nécessite une autre méthode et reste NT. Ce profil n'évalue pas l'exécution inline, l'injection ou la sûreté générale de CSP.

EN: CSP is limited to resources of HTTPS documents: none/self/* expressions, http:/https: schemes (http: also allows upgrading to https:) and explicit HTTPS origins without paths. Selected fetch directives follow script-src-elem/style-src-elem, then script-src/style-src, then default-src; multiple policies intersect. Extensions, nonce/hash, strict-dynamic, path expressions or meta CSP require another method and remain NT. This profile does not assess inline execution, injection or overall CSP security.

FR : `tls-certificates-v1` contient host,captured_at,leaf_pem,intermediates_pem (0–8),trust_store (ID original kind tls),trust_scope. Clés privées interdites. OpenSSL3 est lancé sans shell, sans option de récupération, avec magasin fourni seul, profondeur8, niveau d'authentification2, usage sslserver, hôte DNS et heure fournie. Les codes X509 explicitement reconnus sont2,7,9,10,18,19,20,21,23,24,25,26,27,28,30,32,34,62,66,67,68 ; autre sortie/erreur technique : NT. Ni révocation OCSP/CRL, politique d'entreprise, confiance publique, Certificate Transparency, configuration du serveur ou négociation TLS réelle ne sont établies. TSEP_OPENSSL peut désigner un exécutable local OpenSSL3.

EN: `tls-certificates-v1` contains host,captured_at,leaf_pem,intermediates_pem (0–8),trust_store (original kind tls ID),trust_scope. Private keys are forbidden. OpenSSL3 runs without a shell or fetching option, with supplied trust alone, depth8, authentication level2, sslserver purpose, DNS host and supplied time. Explicitly recognized X509 codes are2,7,9,10,18,19,20,21,23,24,25,26,27,28,30,32,34,62,66,67,68; other output/technical error: NT. OCSP/CRL revocation, enterprise policy, public trust, Certificate Transparency, server configuration and actual TLS negotiation are not established. TSEP_OPENSSL may select a local OpenSSL3 executable.

FR : `transport-policy-v1` contient host et hsts{enabled,max_age,include_subdomains,scope,reason,owner}, identique au plan. max_age est entier0–2³¹−1 ; un seul en-tête, directives max-age/includeSubDomains/preload reconnues, pas de preload requis ni inféré. Le profil contenu mixte strict examine URL observées HAR et src, poster, data, liens stylesheet/preload/modulepreload/icon de la source. CSS, srcset, frames/shadow, schémas spéciaux et surfaces dynamiques absentes sont NT. Les ressources HTTP sont NC pour ce profil explicite même si un navigateur les bloque ou les met à niveau : ce n'est pas une simulation universelle du navigateur.

EN: `transport-policy-v1` contains host and hsts{enabled,max_age,include_subdomains,scope,reason,owner}, identical to the plan. max_age is integer0–2³¹−1; one header, recognized max-age/includeSubDomains/preload directives, no required or inferred preload. The strict mixed-content profile examines observed HAR URLs and source src, poster, data, stylesheet/preload/modulepreload/icon links. CSS, srcset, frames/shadow, special schemes and absent dynamic surfaces are NT. HTTP resources are NC under this explicit profile even if a browser blocks or upgrades them: this is not universal browser simulation.

FR : une contradiction native indépendante demeure NC malgré une revue absente. Une contradiction humaine sur originaux insuffisants demeure NT. C exige tous les items et toutes les règles du contrôle, preuves et revue incluses ; un seul sondage ne qualifie jamais le site entier. Les fixtures, certificats et revues synthétiques ne peuvent être requalifiés en preuves publiques réelles. Voir [migration](migration-0.3.0-draft.4.md) et [références datées](source-captures/render-transport-2026-10-18.md).

EN: an independent native contradiction remains NC despite an absent review. Human contradiction with insufficient originals remains NT. C requires every item and every control rule, including evidence and review; one probe never qualifies an entire site. Synthetic fixtures, certificates and reviews cannot be relabelled as real public evidence. See [migration](migration-0.3.0-draft.4.md) and [dated references](source-captures/render-transport-2026-10-18.md).
