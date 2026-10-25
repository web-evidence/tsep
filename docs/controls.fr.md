# TSEP 0.3.0-draft.8 — Contrôles

Generated from `spec/protocol.json` / Généré depuis `spec/protocol.json`.

Draft / Version de travail. See / Voir [contract](contract.fr.md).

## TS01 — La page finale répond avec un code HTTP exploitable.

**Sévérité**: blocking. **Unité**: page.

**Entrées requises**: http, intent.

**Applicabilité.** Pages publiques désignées comme canoniques.

**Méthode.** Envoyer une requête GET, suivre les redirections et relever le code final.

**Attendus.** Chaque GET atteint une réponse finale 200 pour la ressource attendue ; horodatage et chaîne conservés.

**Preuves.** Intention, trace GET complète et corps conservé ; justifications par règle A01–A02.

**Conditions de NA.** Aucune page publique canonique dans le périmètre déclaré.

**Limites.** Un test depuis une IP ne prouve pas la réponse reçue par Googlebot.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité. Note TSEP : le critère est un 200 final ; le titre permanent hérité de la grille 1.1 est plus large.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110)

### TS01-A01 — GET final en 200

`TSEP@0.3.0-draft.7:TS01-A01`

**Entrées requises**: http, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Chaque page publique désignée canonique, dans le contexte de requête déclaré.

**Méthode.** Exécuter un GET sans cache conditionnel ; enregistrer chaque saut et la réponse finale. Déclarer agent, en-têtes, cookies/authentification, réseau, heure et bornes de temps, taille et redirections.

**Attendus.** Une réponse finale complète est observée en 200. Un 204, 206, 4xx ou 5xx final observé contredit cet attendu ; HEAD seul ou 304 sans représentation ne suffit pas.

**Preuves.** Intention par URL ; commande et version de l’outil ; trace GET datée, URL et codes de tous les sauts, en-têtes finaux et indicateurs de troncature.

**Hypothèses.** La requête et ses bornes sont déclarées avant l’essai ; le 200 est une exigence TSEP pour cette population.

**Indéterminé.** Délai, DNS/TLS, chaîne interrompue, borne atteinte, capture incomplète, requête HEAD seule ou 304 sans corps conservé : inconclusive, sans défaut SEO déduit.

**Conditions de NA.** Aucune exemption atomique quand le contrôle s’applique.

**Limites.** Ni disponibilité permanente ni réponse réelle de Googlebot. Une chaîne observée ne valide pas TS02.

### TS01-A02 — Ressource finale attendue

`TSEP@0.3.0-draft.7:TS01-A02`

**Entrées requises**: http, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Chaque réponse finale dont le contenu peut être comparé à l’intention.

**Méthode.** Comparer d’abord l’URL finale à expected_final_url, puis le SHA-256 du corps complet à expected_body_sha256. Fixer références, éventuelle stabilité et marqueurs avant la mesure. La branche de variation sans stabilité utilise le lecteur historique, sauf identity_reader: html-tree-markers-v1 déclaré au préalable : deux hypothèses statiques globales, segments parsés attribués aux octets et critères littéraux. L’empreinte porte toujours sur le corps complet inchangé. Édition draft.6 : les espaces ASCII structurels sous html ou traversant uniquement les fermetures body/html sont exclus avec leurs positions et octets conservés ; voir migration-0.3.0-draft.6. Le profil distinct html-tree-markers-v2 exclut les segments sous noscript de toute comparaison de marqueurs, y compris aux recontrôles. Le profil v1 garde sa sémantique historique. Une intention doit nommer explicitement le profil retenu avant la nouvelle capture. Le profil distinct html-tree-markers-v3 porte sur le texte HTML principal : exclusions attribuées noscript/iframe/sous-arbres étrangers ; un interdit dans ces exclusions empêche pass ; seuls les doublons d’attributs sont admis parmi les erreurs parse5, sans interprétation de directives. Espaces ASCII traversant des fermetures ignorées admis seulement avec reconstruction exacte. Voir migration-0.3.0-draft.7 pour les limites et la migration explicite.

**Attendus.** URL finale différente : fail. À URL identique, empreinte identique : pass. Sinon, representation: stable impose fail. Sinon, sous le lecteur historique, des marqueurs valides donnent fail si un requis manque ou si un interdit apparaît. Pass exige au moins un marqueur requis, tous les requis présents et tous les interdits absents. Interdits seuls absents : inconclusive. Sans marqueurs ni stabilité déclarée : inconclusive. Le statut HTTP ne remplace pas cette comparaison. Sous html-tree-markers-v1, chaque lecture complète compare tous les marqueurs ; deux pass donnent pass, deux fail donnent fail, tout autre couple donne inconclusive. Les priorités URL, empreinte et stabilité restent inchangées.

**Preuves.** Trace HTTP, corps complet et intention préalable datée avec URL, empreinte de référence et éventuels marqueurs/politique de stabilité ; extraction, valeurs calculées et outil/version. Empreinte après décodage de transfert et de contenu, avant toute transformation. Marqueurs littéraux sensibles à la casse dans chaque segment de texte source HTML décodé : entités résolues, commentaires, script/style, balises et attributs exclus, segments jamais concaténés à travers le balisage. Pour text/plain, corps décodé intégral. Ni normalisation des espaces ni expression régulière. Le profil parsé distinct normalise CRLF/CR source en LF avant expansion des références, sans modifier les critères ; conserve les deux projections, contextes, positions, erreurs rapportées, résultats et outils. Les contextes identiques sont référencés sans suppression de segments ; arbres reconstructibles à partir du corps et des outils exacts.

**Hypothèses.** Le responsable fixe une représentation de référence avant la collecte ; sa pertinence métier reste sa responsabilité. La comparaison est automatique, la définition de l’intention ne l’est pas. Le profil éventuel et ses critères sont déclarés dans une nouvelle intention avant capture ; aucune sélection ou conversion silencieuse des anciennes intentions.

**Indéterminé.** Capture absente/tronquée, décodage inconnu, référence URL absente/invalide, intention postérieure : inconclusive. À URL identique, empreinte de référence absente/invalide : inconclusive. Si les empreintes diffèrent sans stabilité, marqueurs absents, vides, malformés ou contradictoires, extraction indéterminée, ou interdits seuls tous absents : inconclusive. Une URL différente reste fail même sans empreinte de référence. Pour le profil parsé : divergence des hypothèses, erreur rapportée par parse5, texte étranger non blanc hors exclusions, frames/contextes non qualifiés, intervalles non attribuables, runtime indisponible ou borne dépassée restent inconclusive, sans repli.

**Conditions de NA.** Aucune exemption atomique quand le contrôle s’applique.

**Limites.** Une variation d’empreinte seule ne prouve pas un contenu erroné. L’extraction du texte source ne mesure ni visibilité CSS/DOM, ni similarité sémantique ; titre et texte masqué par CSS peuvent compter. Des marqueurs pertinents et une référence correcte restent la responsabilité du propriétaire. Une mauvaise intention peut valider un mauvais contenu. Ni classification soft 404 du moteur, ni indexation, ni routes non déclarées. Le nouveau profil conserve title/textarea/options/textes masqués, exclut scripts/styles HTML/SVG et templates inactifs ; le contrat précise les refus. Aucun comportement navigateur, validité HTML complète ou nouvelle évaluation Edikka déduit.

## TS02 — Les redirections sont intentionnelles, directes et sans boucle.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: http, intent.

**Applicabilité.** Variantes et anciennes URL dont le comportement attendu est déclaré.

**Méthode.** Tester les variantes HTTP/HTTPS, hôte, slash et anciennes URL avec le nombre de redirections.

**Attendus.** Chaque variante testée suit la destination et le nombre de sauts autorisés, sans boucle ; intention validée par le responsable.

**Preuves.** Destination finale unique, chaîne documentée, absence de boucle.

**Conditions de NA.** Aucune redirection ni variante attendue, inventaire à l’appui.

**Limites.** Une redirection valide ne prouve pas la pertinence sémantique de sa destination. La référence exécutable borne les trajectoires serveur HTTP ; les autres mécanismes restent non établis, sans exemption du contrôle.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/301-redirects](https://developers.google.com/search/docs/crawling-indexing/301-redirects)

### TS02-A01 — Plan de redirection approuvé au préalable

`TSEP@0.3.0-draft.6:TS02-A01`

**Entrées requises**: intent.

**Automation / Automatisation**: `manual`.

**Applicabilité.** Variantes et anciennes URL dont le comportement attendu est déclaré.

**Méthode.** Déclarer source, destination finale, statuts de redirection et terminaux admis, nombres minimal et maximal de redirections et contexte. Vérifier la revue fournie du responsable, motivée, datée entre déclaration et capture et liée par empreinte au plan/contexte.

**Attendus.** Le plan applicable est explicitement approuvé par le responsable avant la capture. Un rejet explicite lié au même plan est fail ; une revue absente ou non attribuable reste inconclusive.

**Preuves.** Plan, contexte, identité déclarée et rôle du responsable, date, décision, motif, assistance et provenance de la revue ; empreinte exacte des critères examinés.

**Hypothèses.** Le responsable fournit ses critères avant la capture ; un auteur de laboratoire peut fournir une revue synthétique explicitement identifiée. Une empreinte lie les pièces, sans authentifier une personne.

**Indéterminé.** Plan absent, invalide ou postérieur ; validation manquante, non liée ou hors période ; mécanisme non couvert. L’outil ne fournit aucune approbation humaine.

**Conditions de NA.** Aucune exemption atomique. La non-applicabilité du contrôle exige un inventaire positif distinct ; elle ne découle pas d’une capture absente.

**Limites.** Une redirection valide ne prouve pas la pertinence sémantique de sa destination. La référence exécutable borne les trajectoires serveur HTTP ; les autres mécanismes restent non établis, sans exemption du contrôle.

### TS02-A02 — Trajectoire HTTP conforme au plan

`TSEP@0.3.0-draft.6:TS02-A02`

**Entrées requises**: http, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Variantes et anciennes URL dont le comportement attendu est déclaré.

**Méthode.** Lire chaque échange GET attribuable dans l’ordre, résoudre Location, conserver codes et URL, compter les redirections et vérifier destination/statut terminaux. Comparer au plan fixé avant la capture, sans reconstruire les réponses manquantes. Le profil préalable http-trajectory-headers-v1 peut conclure sur les en-têtes complets après un arrêt attribué à la borne d’octets du collecteur 2 ; le corps reste incomplet et non évalué.

**Attendus.** La chaîne complète respecte destination, statuts et bornes déclarés, sans boucle. Un type interdit, une borne maximale dépassée, une redirection sans Location ou un retour vers une URL déjà parcourue sont fail dès le préfixe complet qui les prouve. Une destination/statut terminal ou un nombre minimal contradictoires sont fail après réponse terminale attribuable.

**Preuves.** Requêtes et réponses HTTP originales pour chaque saut, URL, complétude, client et contexte ; plan antérieur. Une contradiction prouvée survit aux lacunes ultérieures et à l’absence d’approbation A01.

**Hypothèses.** Le responsable fournit ses critères avant la capture ; un auteur de laboratoire peut fournir une revue synthétique explicitement identifiée. Une empreinte lie les pièces, sans authentifier une personne.

**Indéterminé.** Chaîne inachevée sans contradiction, limite de collecte atteinte, Location ambiguë, fragment ou syntaxe hors portée, requête conditionnelle/authentifiée, capture incomplète ou mal attribuée. Atteindre une borne de collecte ne prouve pas une boucle ; dépasser une borne d’intention est distinct. Exception bornée : préfixe à la limite exactement attestée avec un octet excédentaire, sans ambiguïté d’en-têtes ou contradiction de framing, sous le nouveau profil explicite uniquement.

**Conditions de NA.** Aucune exemption atomique. La non-applicabilité du contrôle exige un inventaire positif distinct ; elle ne découle pas d’une capture absente.

**Limites.** Une redirection valide ne prouve pas la pertinence sémantique de sa destination. La référence exécutable borne les trajectoires serveur HTTP ; les autres mécanismes restent non établis, sans exemption du contrôle.

## TS03 — Les erreurs serveur et soft 404 ne remplacent pas une réponse explicite.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: configuration, http, content, intent.

**Applicabilité.** Routes synthétiques explicitement classées existantes, supprimées et inexistantes dans un plan daté ; la portée réelle n’est pas authentifiée.

**Méthode.** Avant les captures, lier à configuration le plan d’intention des trois états de route et leurs critères de contenu. Comparer une matrice HTTP GET fournie, sans résolution DNS ni collecte réseau.

**Attendus.** Pass qualifie seulement la matrice complète fournie : 200 et marqueurs attendus pour une route existante ; 404/410 et critères de corps déclarés pour les routes supprimées/inexistantes. Un 2xx pour ces dernières, un autre statut complet, ou une contradiction de marqueur est fail. La classification soft 404 reste hors mesure.

**Preuves.** Plan d’intention antérieur, empreinte de liaison, attentes de corps, URL/GET et réponses HTTP brutes complètes pour chaque état requis ; conserver les contre-cas même si d’autres pièces manquent.

**Conditions de NA.** Périmètre ne contenant aucun routage HTTP, justification fournie.

**Limites.** La sonde n’utilise que des captures synthétiques .invalid et des marqueurs littéraux UTF-8. Elle ne confirme ni existence réelle, suppression, disponibilité durable, qualité sémantique, ni classification soft 404 par Google. Une réponse ponctuelle 5xx échoue au statut déclaré sans prouver une panne persistante. Aucun site ni moteur n’est interrogé.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Google Search Central décrit les effets de classes de statuts sur ses systèmes ; cette source ne prescrit pas un standard TSEP. La règle compare des attentes fournies et ne reproduit pas la classification soft 404.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/http-network-errors](https://developers.google.com/search/docs/crawling-indexing/http-network-errors)

### TS03-A01 — Réponses HTTP synthétiques comparées à un plan préalable

`TSEP@0.2.0-rc.1:TS03-A01`

**Entrées requises**: configuration, http, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Un plan de route contient au moins un état existant, supprimé et inexistant dans le périmètre synthétique.

**Méthode.** Vérifier le plan antérieur et son empreinte ; comparer chaque GET/response attribuable, complète et liée à une route .invalid aux statuts permis et marqueurs littéraux UTF-8 fixés dans les attentes content.

**Attendus.** Pass exige exactement une réponse complète par route et tous les états requis : 200 pour existante, 404/410 pour supprimée ou inexistante, marqueurs requis présents et interdits absents. Une contradiction complète reste fail malgré doublon, autre capture incomplète ou lacune. Les 206/304, données absentes, ambiguës ou mal attribuées restent inconclusives.

**Preuves.** Le plan et son empreinte, les attentes content, puis pour chaque route la requête GET, la réponse HTTP brute, le statut, la date et le corps complet. Conserver les observations contradictoires et les lacunes séparément.

**Hypothèses.** Le plan, les classifications et critères sont fournis et non authentifiés. La revue attachée est un exercice synthétique, pas une approbation indépendante.

**Indéterminé.** Plan absent/futur/mal lié, état de route manquant, doublon, HTTP incomplet, URL/client non attribuable, statut 206/304, contenu non UTF-8, marqueurs contradictoires dans le plan ou matrice incomplète ; une contradiction attribuable reste fail.

**Conditions de NA.** Aucune exemption atomique. NA du contrôle entier exige un inventaire positif, complet, motivé et daté prouvant qu’aucun routage HTTP n’entre dans le périmètre.

**Limites.** Une capture .invalid ne teste aucun serveur. Les marqueurs sont recherchés littéralement dans le corps décodé, sans DOM, rendu, jugement sémantique ou classification de moteur. C ne porte que sur la matrice déclarée, pas sur un site entier, une disponibilité dans le temps, une indexation ou un ranking.

## TS04 — La politique robots effective correspond à l’intention déclarée.

**Sévérité**: blocking. **Unité**: host.

**Entrées requises**: http, robots, intent.

**Applicabilité.** Hôtes et agents pour lesquels une politique d’exploration est évaluée.

**Méthode.** Déclarer avant collecte une origine, le robot, le profil d’interprétation et une matrice de ressources avec politique attendue ; confronter règles et accès selon A01–A02.

**Attendus.** Règles effectives et accès aux ressources correspondent à la politique déclarée ; une absence volontaire documentée peut être compatible, sans exiger systématiquement 200.

**Preuves.** Plan préalable, origine, product token et User-Agent, profil, robots brut daté, lignes retenues, réponses des ressources nécessaires et revues fournies.

**Conditions de NA.** Aucun hôte explorable dans le périmètre.

**Limites.** robots.txt est un protocole d’exploration, pas un contrôle d’accès.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Références techniques datées du 10 octobre 2026, captures et empreintes dans docs/source-observations.md. Les attendus restent une proposition TSEP.

**Références**: [https://www.rfc-editor.org/rfc/rfc9309.html](https://www.rfc-editor.org/rfc/rfc9309.html); [https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)

### TS04-A01 — Politique par origine, robot et ressource

`TSEP@0.2.0-rc.1:TS04-A01`

**Entrées requises**: http, robots, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque origine et matrice de chemins dont la politique d’exploration est évaluée.

**Méthode.** Figer le profil et les autorisations/interdictions attendues avant les observations. Interpréter statut, groupes, règles et redirections du robots dans le contexte de l’origine initiale ; conserver les lignes qui déterminent chaque issue.

**Attendus.** Chaque politique observée correspond à l’intention déclarée. Une permission inattendue comme une interdiction inattendue est une contradiction. Une absence volontaire peut convenir selon le profil ; aucun statut 200 universel.

**Preuves.** Matrice complète, intention antérieure, contexte, requête et réponse robots intégrales, profil et résultat motivé par ressource.

**Hypothèses.** Profil choisi avant mesure, identique pour un contexte de campagne ; pas de sélection a posteriori du profil favorable. Distinguer modèle RFC, politique Google documentée et cache réellement inconnu. Le champ facultatif directive_crawler=googlebot, figé avant capture, sélectionne la politique Googlebot sur la seule représentation reçue par crawler, le User-Agent HTTP exact. robots_policy explicite et product_token concordant avec googlebot sans distinction de casse sont requis, comme pour TS07. Sans ce champ, le comportement historique est conservé. Le profil facultatif préalable google-robotstxt-fields-v2 étend la liste fermée des champs hors portée accès, selon le registre google/robotstxt épinglé ; anciens profils inchangés, sans sélection automatique.

**Indéterminé.** Profil absent, capture ou chronologie manquante, syntaxe hors couverture, erreur/cache non résolu : inconclusive. Une contradiction attribuable sur une autre ressource reste fail. Un directive_crawler nul, inconnu ou incohérent rend la politique indéterminée sans repli vers le groupe du client. Une contradiction HTTP indépendante reste limitée au client observé.

**Conditions de NA.** Aucune exemption atomique quand le contrôle s’applique.

**Limites.** semiAuto : matrice et pertinence du profil restent déclarées. La référence est bornée à une origine, des profils documentés et des captures fournies ; aucune visite, ingestion ou indexation du moteur n’est démontrée. En mode explicite, toute conclusion robots concerne le produit déclaré sur les octets reçus par le client, sans prouver la représentation reçue par Googlebot. Un statut HTTP contraire au plan (dont 401/403/429/5xx quand 200 est attendu) reste fail pour ce client, jamais une preuve de refus à Googlebot. Les champs du registre et sitemap sont relevés, sans évaluer leurs préférences d’usage, TS42 ou l’indexation ; ils ne délimitent pas les groupes. Autres champs et tolérances restent hors couverture. Numéros et valeurs intégrales sont conservés ; les aperçus de motifs signalent leur troncature.

### TS04-A02 — Accès aux ressources nécessaires

`TSEP@0.2.0-rc.1:TS04-A02`

**Entrées requises**: http, robots, intent.

**Automation / Automatisation**: `semiAuto`.

**Entrées pour exemption atomique**: intent.

**Applicabilité.** Ressources explicitement nécessaires dans le périmètre déclaré, y compris les ressources de rendu retenues.

**Méthode.** Comparer politique robots et trajectoires HTTP aux destinations/statuts prévus, puis examiner les réponses pour obstacles. Lier chaque revue fournie aux octets, dates, intention et contexte. Conserver séparément les lacunes.

**Attendus.** Toutes les ressources nécessaires et leurs sauts observés sont autorisés sous le profil, atteignent la réponse prévue et ne présentent aucun obstacle selon la revue fournie. Blocage robots, réponse contradictoire ou obstacle étayé donne fail même avec une autre preuve manquante.

**Preuves.** Plan de ressources, robots, traces HTTP complètes, revue motivée par ressource avec identité déclarée, date, provenance, assistance et empreinte de liaison.

**Hypothèses.** Un client de test ne s’authentifie pas comme Googlebot ; un 200 seul ne prouve pas l’absence de challenge. La revue n’est pas produite par le logiciel et son identité n’est pas authentifiée. Le champ facultatif directive_crawler=googlebot, figé avant capture, sélectionne la politique Googlebot sur la seule représentation reçue par crawler, le User-Agent HTTP exact. robots_policy explicite et product_token concordant avec googlebot sans distinction de casse sont requis, comme pour TS07. Sans ce champ, le comportement historique est conservé. Le profil facultatif préalable google-robotstxt-fields-v2 étend la liste fermée des champs hors portée accès, selon le registre google/robotstxt épinglé ; anciens profils inchangés, sans sélection automatique.

**Indéterminé.** Ressource ou revue manquante, revue non liée, réponse incomplète, doute ou portée hors couverture : inconclusive sans effacer une contradiction établie. Un directive_crawler nul, inconnu ou incohérent rend la politique indéterminée sans repli vers le groupe du client. Une contradiction HTTP indépendante reste limitée au client observé.

**Conditions de NA.** Aucune ressource nécessaire dans ce périmètre, établi par une revue d’inventaire motivée et datée avant le plan ; une liste vide sans justification ne suffit pas.

**Limites.** La suffisance de l’inventaire et le jugement humain restent hors automatisation complète. La référence couvre une origine et les trajectoires attribuables ; elle n’exécute pas le rendu et n’établit pas l’accès réel du moteur. En mode explicite, toute conclusion robots concerne le produit déclaré sur les octets reçus par le client, sans prouver la représentation reçue par Googlebot. Un statut HTTP contraire au plan (dont 401/403/429/5xx quand 200 est attendu) reste fail pour ce client, jamais une preuve de refus à Googlebot. Les champs du registre et sitemap sont relevés, sans évaluer leurs préférences d’usage, TS42 ou l’indexation ; ils ne délimitent pas les groupes. Autres champs et tolérances restent hors couverture. Numéros et valeurs intégrales sont conservés ; les aperçus de motifs signalent leur troncature.

## TS05 — Une directive Disallow n’est jamais présentée comme une garantie de désindexation.

**Sévérité**: blocking. **Unité**: policy.

**Entrées requises**: configuration, intent.

**Applicabilité.** Politiques d’exploration ou d’exclusion du périmètre.

**Méthode.** Comparer une carte de décision datée avant l’observation — exploration, objectif et méthode d’indexation, visibilité de noindex, protection et portée des affirmations — au record de configuration fourni.

**Attendus.** Un pass indique uniquement la cohérence interne du plan fourni. Exploration, indexation et protection sont séparées ; Disallow seul ne garantit ni désindexation ni confidentialité. Aucun état réel de l’index ou du serveur n’est établi.

**Preuves.** Records configuration et intent liés à la cible, carte antérieure datée, portée, mécanismes et affirmations avec leurs bases ; revue positive et datée pour une non-applicabilité.

**Conditions de NA.** Aucune politique concernée, périmètre et décision documentés.

**Limites.** Le lecteur compare un plan synthétique fourni ; il ne récupère aucun site, ne teste aucune authentification, ne vérifie pas l’exécution d’un retrait, ni l’état de l’index. Une URL bloquée peut rester connue et apparaître sans extrait. La qualification complète de TS05 et sa réception dans l’application sont distinctes.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité. Le profil policy_version=2 compare aussi authentification, autorisation et suppression HTTP 404/410. Une exclusion empêchée par Disallow est contradictoire, même sans garantie affirmée. Le résultat porte uniquement sur la cohérence du plan déclaré ; il ne prouve ni désindexation ni confidentialité.

**Portée des sources.** Les pages Google Search Central ci-dessous appuient la distinction technique ; les attendus TSEP restent une règle éditoriale. Capture sélective datée et empreintée, pas un audit de site.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/robots/intro](https://developers.google.com/search/docs/crawling-indexing/robots/intro); [https://developers.google.com/search/docs/crawling-indexing/block-indexing](https://developers.google.com/search/docs/crawling-indexing/block-indexing); [https://developers.google.com/search/docs/crawling-indexing/control-what-you-share](https://developers.google.com/search/docs/crawling-indexing/control-what-you-share)

### TS05-A01 — Carte fournie : exploration, indexation et protection sont distinctes.

`TSEP@0.3.0-draft.8:TS05-A01`

**Entrées requises**: configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Une politique d’exploration, un objectif d’indexation ou une déclaration de confidentialité existe dans le périmètre.

**Méthode.** Lire intent.ts05_policy, datée avant observed_at, et le record configuration. Comparer les méthodes/effets d’exploration, l’objectif/méthode de l’indexation et la visibilité de noindex, puis la protection et les bases d’affirmations de désindexation/confidentialité. Le profil policy_version=2 compare aussi authentification, autorisation et suppression HTTP 404/410. Une exclusion empêchée par Disallow est contradictoire, même sans garantie affirmée. Le résultat porte uniquement sur la cohérence du plan déclaré ; il ne prouve ni désindexation ni confidentialité.

**Attendus.** Pass signifie seulement que la carte fournie est cohérente et distingue les trois axes. Une garantie de désindexation fondée seulement sur Disallow échoue ; une directive noindex inaccessible n’établit pas une exclusion. Aucun verdict positif ne prouve l’état de l’index, l’accès réel du robot ou la confidentialité serveur.

**Preuves.** Configuration, carte d’intention préalable, dates, périmètre, méthodes/effets et affirmations avec bases ; les deux records couvrent la cible.

**Hypothèses.** Les records sont fournis et non authentifiés. L’interpréteur teste leur forme et cohérence déclarée, non leur vérité ni leur mise en œuvre.

**Indéterminé.** Plan absent, mal daté, incomplet ou futur ; méthode non prise en charge ; index inconnu ; noindex bloqué ou visibilité inconnue ; retrait non terminé ; bases de protection indéterminées.

**Conditions de NA.** Ce test atomique n’accepte pas d’exemption partielle. NA du contrôle entier exige une revue d’inventaire complète, motivée et datée avant observed_at, prouvant l’absence de politique concernée sur chaque cible.

**Limites.** Mécanisme semi-automatisé sur un modèle synthétique. N’interprète pas robots.txt, meta, X-Robots-Tag ou HTTP en direct ; ne mesure pas la visite, l’indexation, le retrait ou les contrôles d’accès. Pass qualifie uniquement la cohérence de la carte fournie.

## TS06 — Les zones sensibles refusent réellement l’accès au serveur.

**Sévérité**: blocking. **Unité**: route-set.

**Entrées requises**: configuration, http, intent.

**Applicabilité.** Routes privées ou sensibles explicitement inventoriées dans un périmètre déclaré ; cette règle candidate ne qualifie que les traces HTTP synthétiques fournies.

**Méthode.** Avant les observations, fournir intent.ts06_access et son empreinte liée à configuration.ts06_access. Déclarer routes, marqueurs synthétiques, rôles fictifs, tests exacts par route/rôle et triplets froid anonyme → amorçage autorisé synthétique → rejeu anonyme, avec même étiquette de cache. Examiner les GET fournis sans résolution DNS ni requête réseau. Les redirections d’authentification doivent rester sur la même origine (schéma, hôte, port effectif) et suivre une liste de chemins explicitement déclarée. Une réponse 404 ne compte comme refus que si le plan la déclare pour cette route.

**Attendus.** Pass signifie seulement que toutes les cellules route/rôle non autorisées déclarées sont complètes, refusées sans marqueur sensible et que chaque triplet fourni suit l’ordre déclaré sans fuite au rejeu ; le contrôle ne mesure ni une identité réelle ni un cache réel. Toute réponse attribuable à un rôle non autorisé contenant un canari échoue, y compris un corps encodé détecté ou un en-tête de réponse. Une représentation 2xx livrée à un rôle non autorisé échoue aussi.

**Preuves.** Records configuration, intent et HTTP fournis, empreinte exacte du plan, dates, identifiants route/rôle, chaque échange GET brut et ordre, liste complète des cellules non autorisées et chaque étiquette/phase de triplet. Conserver aussi les réponses contradictoires attribuables avant de signaler toute lacune de matrice.

**Conditions de NA.** Le contrôle entier peut être NA seulement avec une revue d’inventaire synthétique complète, datée et motivée qui déclare aucune route sensible dans le périmètre ; aucun test ni triplet contradictoire ne peut alors être présent.

**Limites.** Interpréteur de fixture borné aux URL-étiquettes .invalid, sans DNS, socket, crawl ni domaine réel. Un rôle HTTP est une étiquette synthétique, pas une authentification. Une étiquette de cache commune ne prouve aucun cache partagé ; Age/X-Cache seuls ne prouvent pas l’attribution. La règle n’exécute pas cookies, Authorization, JavaScript, TLS, variantes d’URL ou méthode HEAD. 206, 304 sans corps complet, codage non pris en charge, cellule manquante/ambiguë et état de cache incomplet donnent inconclusive. Le résultat ne qualifie pas toutes les pages d’un site.

C exige les cellules et triplets complets du périmètre synthétique déclaré. Une fuite de canari ou une réponse 2xx non autorisée est une contradiction étayée ; les données partielles ou ambiguës restent NT. NA est uniquement une déclaration d’inventaire complète et positive.

**Portée des sources.** Les RFC 9110, 9111, 6454 et 6761 appuient respectivement la sémantique HTTP, quelques conditions de cache, la notion d’origine et l’usage réservé de .invalid. Elles n’établissent pas une règle de certification TSEP ; l’attendu reste éditorial et les observations sont des fixtures synthétiques.

**Références**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110); [https://www.rfc-editor.org/rfc/rfc9111](https://www.rfc-editor.org/rfc/rfc9111); [https://www.rfc-editor.org/rfc/rfc6454](https://www.rfc-editor.org/rfc/rfc6454); [https://www.rfc-editor.org/rfc/rfc6761](https://www.rfc-editor.org/rfc/rfc6761)

### TS06-A01 — Accès refusé dans la matrice HTTP synthétique fournie

`TSEP@0.2.0-rc.1:TS06-A01`

**Entrées requises**: configuration, http, intent.

**Automation / Automatisation**: `semiAuto`.

**Entrées pour exemption atomique**: intent.

**Applicabilité.** Au moins une route sensible est explicitement déclarée dans le périmètre synthétique.

**Méthode.** Comparer le plan préalable lié à la configuration à une matrice complète de GET synthétiques par route et rôle. Détecter les marqueurs dans les en-têtes et corps, préserver les contradictions avant validation des doublons/lacunes, vérifier les redirections de même origine et les séquences froid/autorisé/rejeu.

**Attendus.** Pass couvre uniquement la matrice synthétique complète fournie : aucune réponse non autorisée ne contient de canari, les refus sont établis selon le plan, et chaque triplet froid → amorçage autorisé → rejeu anonyme est complet et ordonné. Une fuite attribuable ou une représentation 2xx non autorisée donne fail.

**Preuves.** Records configuration/intent/http liés à la cible, empreinte du plan, routes/rôles/tests, échanges GET bruts avec horodatages, canaris et triplets de cache étiquetés.

**Hypothèses.** Les fixtures sont fournies, synthétiques et non authentifiées. L’étiquette de rôle et l’identifiant de cache ne prouvent ni identité ni cache partagé.

**Indéterminé.** Plan absent/futur/incohérent, cellule manquante ou dupliquée, en-tête d’identification absent/ambigu, redirection externe, 206, 304 sans représentation conservée, codage non pris en charge ou triplet/attribution incomplets.

**Conditions de NA.** Aucune exemption atomique. Le NA du contrôle entier exige une revue d’inventaire complète, datée et motivée ; elle doit être liée à intent.

**Limites.** Pas de DNS, socket, collecte live, identité réelle, authentification, cookie, cache réel, TLS, JavaScript, alias de chemin, HEAD ni évaluation de site entier. La détection de canaris couvre uniquement les codages implémentés ; le reste est inconclusif.

## TS07 — Les directives meta robots et X-Robots-Tag sont cohérentes avec l’objectif de la page.

**Sévérité**: blocking. **Unité**: page.

**Entrées requises**: http, html, intent, robots.

**Applicabilité.** Documents et ressources dont l’objectif d’indexation est déclaré.

**Méthode.** Examiner les en-têtes finaux, le HTML source, l’accès et les états rendus nécessaires selon A01–A03.

**Attendus.** Les directives effectives du robot cible, dans les en-têtes finaux et le HTML, correspondent à cet objectif ; directives inconnues et états rendus nécessaires sont examinés.

**Preuves.** Directive unique ou combinaison compatible, sans noindex accidentel.

**Conditions de NA.** Aucune ressource soumise à une politique d’indexation dans le périmètre.

**Limites.** Le moteur doit pouvoir explorer la ressource pour lire la directive.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité. Le profil google-indexing-2026-10-v1 interprète les directives Googlebot de la page autonome. Une exclusion certaine demeure probante avec des jetons inconnus. Les restrictions datées sont comparées à la capture ; les consignes ignorées et inconnues sont conservées. Un noindex HTTP certain reste interprétable même si le corps ne peut être lu. Accès et rendu restent séparés.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale. Sources consultées le 2026-10-09 ; captures datées et empreintes consignées dans docs/source-observations.md.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag); [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics); [https://developers.google.com/search/docs/crawling-indexing/block-indexing](https://developers.google.com/search/docs/crawling-indexing/block-indexing); [https://www.rfc-editor.org/rfc/rfc9309](https://www.rfc-editor.org/rfc/rfc9309)

### TS07-A01 — Directives effectives et objectif

`TSEP@0.3.0-draft.8:TS07-A01`

**Entrées requises**: http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque document avec objectif d’indexation déclaré, pour un robot et un contexte explicitement nommés.

**Méthode.** Inventorier tous les X-Robots-Tag finaux et meta robots/robot cible dans le HTML source, sans les confondre avec les sauts. Appliquer la sémantique documentée du robot, y compris doublons, portée, casse, paramètres et directives ignorées. Le profil facultatif source_reader=html-tree-directives-v1, déclaré avant capture, construit deux hypothèses statiques complètes sans exécuter de script ; les meta HTML robots/googlebot de head/body sans ancêtre étranger sont combinés séparément avec les en-têtes finaux. Les contenus des templates ordinaires sont conservés mais exclus des directives actives. Le choix préalable facultatif presentation_reader=google-preview-intent-v1 compare les intervalles minimum/maximum de permission texte, image et vidéo selon le contrat preview-intent ; extraction et états restent distincts. Le profil google-indexing-2026-10-v1 interprète les directives Googlebot de la page autonome. Une exclusion certaine demeure probante avec des jetons inconnus. Les restrictions datées sont comparées à la capture ; les consignes ignorées et inconnues sont conservées. Un noindex HTTP certain reste interprétable même si le corps ne peut être lu. Accès et rendu restent séparés.

**Attendus.** L’effet combiné correspond à l’objectif déclaré d’indexation et aux restrictions de présentation/liens déclarées. Pour Google : une restriction applicable prime une permission, none inclut noindex/nofollow ; nofollow ou une limite d’aperçu seuls ne signifient pas noindex. L’absence de directive n’est pas un échec si l’objectif autorise l’indexation. Pour ce profil, deux pass donnent pass, deux fail donnent fail, toute autre paire reste inconclusive ; ne jamais fusionner les directives des hypothèses alternatives ni les confondre avec des états rendus observés. Pour ce nouveau profil, toutes les valeurs possibles dans l’intervalle voulu donnent pass ; toutes hors intervalle du même côté donnent fail ; sinon inconclusive. Une contradiction indépendante prévaut dans une lecture ; les règles de consensus source et de priorité rendue restent inchangées.

**Preuves.** En-têtes répétés bruts, HTML source, tableau token/robot/effet et référence technique datée. Pour un non-HTML, le fichier de type html décrit la non-applicabilité de cette surface avec le Content-Type, sans inventer de HTML. Ce profil conserve aussi les deux inventaires meta complets, contextes/namespaces, tags et positions dans les octets d’origine, templates, décodage, erreurs signalées, versions et empreintes dans les observations calculées liées au rapport et comparées au rejeu. Le nouveau profil conserve aussi les valeurs HTTP/meta ordonnées, portées, inconnues, décisions et intervalles par dimension dans les observations liées et rejouées.

**Hypothèses.** Intention et robot figés avant revue ; ne pas extrapoler les règles Google à un autre moteur. En cas d’indexifembedded ou unavailable_after, inclure contexte d’intégration et date nécessaires. L’intention conserve crawler comme User-Agent HTTP exact. Le champ facultatif directive_crawler, figé avant capture et limité ici à googlebot, choisit la sémantique des directives sur cette seule représentation cliente ; il ne décrit pas une réponse reçue par Googlebot. Sans ce champ, le comportement historique exige crawler=googlebot. Sans source_reader, garder le lecteur historique ; nul/inconnu ou Node 24 absent ne se replie pas. Le profil exige HTML HTTP UTF-8 explicite, consomme un BOM initial, conserve les réparations non signalées du parseur épinglé. Les règles et bornes du contrat bilingue source-directives précisent les hypothèses, sans assertion de validité HTML. Les bornes portent sur un plafond de permission, pas sur l’affichage réel. Le choix et les bornes sont préalables ; absence du lecteur conserve le comportement historique et aucun scalaire n’est migré automatiquement.

**Indéterminé.** Objectif absent, syntaxe/portée inconnue, capture partielle ou contexte manquant : inconclusive. Une directive documentée comme ignorée est consignée, pas transformée automatiquement en erreur. directive_crawler présent mais non pris en charge, nul ou incohérent : inconclusive ; aucun repli favorable. Pour ce profil : lecture incomplète, erreur signalée, encodage non couvert, shadow déclaratif open/closed, template for, metadata robots de contexte étranger, contenu absent/rôle mixte ou forme approchante définie au contrat, directive inconnue et dépassement de borne restent indéterminés. Un HTML illisible ne devient pas un accord fondé sur les seuls en-têtes. Le profil de présentation garde les défauts d’image non qualifiés, l’interaction vidéo de max-snippet:0, les syntaxes non couvertes et les dépassements comme inconnues selon les intervalles conservateurs du contrat. Noindex ne donne pas un pass de présentation.

**Conditions de NA.** Aucune exemption atomique quand le contrôle s’applique.

**Limites.** Évalue les déclarations observées, pas leur ingestion ni l’indexation réelle. A01 seul ne couvre pas l’accès ou le rendu. Automatisation semiAuto : l’interpréteur borné ne couvre pas toutes les syntaxes, tous les robots ou tous les contextes ; les entrées non prises en charge restent inconclusive et exigent une revue. Ce choix méthodologique ne simule pas Google. Aucun rendu, accès, revue ou résultat TS10 n’est déduit. Le profil de présentation ne vérifie ni affichage Google, ni disponibilité d’image, ni data-nosnippet, ni usages sous licence, données structurées ou IA ; aucune revue n’est produite.

### TS07-A02 — Accès à la directive

`TSEP@0.3.0-draft.8:TS07-A02`

**Entrées requises**: http, robots, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Toute ressource pour laquelle l’effet des directives est évalué.

**Méthode.** Confronter politique robots effective et conditions d’accès au robot cible ; distinguer réponse au client de test, blocage explicite et accès du robot non observé. Avec directive_crawler explicite, exiger un robots_policy explicite dont product_token concorde avec googlebot sans distinction de casse ; sélectionner ce groupe et jamais le groupe de l’agent du navigateur par repli.

**Attendus.** Aucun obstacle observé n’empêche de lire la directive dans le contexte déclaré. Une interdiction robots contredit une stratégie reposant sur la lecture de noindex. Un refus HTTP 401/403 attribuable reste fail même si la capture robots manque.

**Preuves.** Capture et interprétation robots pour URL/robot, trace HTTP et hypothèses d’accès documentées dans l’intention.

**Hypothèses.** La politique est interprétée par le lecteur partagé TS04. Un nouveau profil est déclaré dans l’intention avant capture. Sans champ robots_policy, les anciennes entrées restent sous le profil fixe legacy-exact-v1, sans extension implicite de sa couverture. Le client ne s’authentifie pas comme Googlebot. L’intention conserve crawler comme User-Agent HTTP exact. Le champ facultatif directive_crawler, figé avant capture et limité ici à googlebot, choisit la sémantique des directives sur cette seule représentation cliente ; il ne décrit pas une réponse reçue par Googlebot. Sans ce champ, les profils robots historiques conservent leur comportement. Le profil facultatif préalable google-robotstxt-fields-v2 étend la liste fermée des champs hors portée accès, selon le registre google/robotstxt épinglé ; anciens profils inchangés, sans sélection automatique.

**Indéterminé.** Politique inaccessible ou ambiguë, challenge non résolu, capture manquante : inconclusive, jamais NA pour manque d’accès. Le nouveau chemin sans profil concordant reste indéterminé. Le refus HTTP 401/403 attribuable conserve sa priorité.

**Conditions de NA.** Aucune exemption atomique quand le contrôle s’applique.

**Limites.** Aucune preuve de visite réelle du moteur ; TS04 et les autres contrôles d’accès ne sont pas globalement validés. Automatisation semiAuto : l’interpréteur borné ne couvre pas toutes les syntaxes, tous les robots ou tous les contextes ; les entrées non prises en charge restent inconclusive et exigent une revue. Les champs du registre et sitemap sont relevés, sans évaluer leurs préférences d’usage, TS42 ou l’indexation ; ils ne délimitent pas les groupes. Autres champs et tolérances restent hors couverture. Numéros et valeurs intégrales sont conservés ; les aperçus de motifs signalent leur troncature.

### TS07-A03 — États rendus nécessaires

`TSEP@0.3.0-draft.8:TS07-A03`

**Entrées requises**: http, html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Entrées pour exemption atomique**: intent, http, html.

**Applicabilité.** Pages dont scripts ou états peuvent affecter les directives, ou dont la stabilité n’est pas établie.

**Méthode.** Fixer avant la capture les états requis, interactions et conditions d’attente. Comparer les en-têtes finaux et le HTML source avec chaque DOM, en déclarant navigateur/version, scripts activés, heure, erreurs et contexte. Relier chaque capture à la réponse source et à la cible. Ne pas supposer que le moteur rend un HTML initial noindex. Le lecteur DOM est choisi avant capture : structured-inventory-v2 ou le lecteur sérialisé historique fixe en l’absence de champ. Aucun repli après un refus. L’inventaire structuré complet conserve namespaces, positions, doublons, sérialisation et pièces de rattachement à la navigation ; aucune suppression de nœud selon son origine supposée. Le nouveau source_reader facultatif affecte seulement le préalable source A01, jamais le lecteur de chaque DOM ; la priorité d’une contradiction rendue attribuable reste inchangée. Le choix préalable facultatif presentation_reader=google-preview-intent-v1 compare les intervalles minimum/maximum de permission texte, image et vidéo selon le contrat preview-intent ; extraction et états restent distincts.

**Attendus.** Tous les états requis sont documentés et compatibles avec l’objectif, dans le contexte déclaré. Une contradiction dans un état complet et attribuable est fail, même si d’autres états manquent. Un retrait de noindex initial par JavaScript ne donne pas pass : A03 reste inconclusive si aucun état requis ne fournit une autre contradiction ; A01 conserve son propre verdict source. Pour ce nouveau profil, toutes les valeurs possibles dans l’intervalle voulu donnent pass ; toutes hors intervalle du même côté donnent fail ; sinon inconclusive. Une contradiction indépendante prévaut dans une lecture ; les règles de consensus source et de priorité rendue restent inchangées.

**Preuves.** En-têtes et HTML source conservés, plan préalable, DOM bruts datés avec empreinte de liaison à la trace HTTP, URL finale, contexte, navigateur/version, état des scripts, interactions, attente et erreurs. Comparaison motivée et limites ; aucune capture du moteur simulée. Le nouveau profil conserve aussi les valeurs HTTP/meta ordonnées, portées, inconnues, décisions et intervalles par dimension dans les observations liées et rejouées.

**Hypothèses.** Les états nécessaires sont listés avant le test ; rendu local et rendu du moteur restent distincts. Le lecteur structuré interprète les meta HTML enfants directs du head réel ; position ou shadow ambigu reste indéterminé. Il conserve la combinaison avec les en-têtes de la navigation déclarée. L’intention conserve crawler comme User-Agent HTTP exact. Le champ facultatif directive_crawler, figé avant capture et limité ici à googlebot, choisit la sémantique des directives sur cette seule représentation cliente ; il ne décrit pas une réponse reçue par Googlebot. Sans ce champ, le comportement historique exige crawler=googlebot. Les bornes portent sur un plafond de permission, pas sur l’affichage réel. Le choix et les bornes sont préalables ; absence du lecteur conserve le comportement historique et aucun scalaire n’est migré automatiquement.

**Indéterminé.** Plan ou capture requis absent, état tronqué, erreur de script, liaison source/cible/contexte incohérente, chronologie invalide, directive non interprétable ou retrait tardif du noindex initial : inconclusive sans réussite déduite. Une contradiction établie dans un autre état attribuable reste fail. Pour le lecteur structuré : arbre/transport incomplet, chargement en cours, API connue comme altérée, histoire d’intégrité absente, capture source/DOM séparée sans rattachement à une même navigation ou agent différent : inconclusive. Une empreinte seule ne prouve pas la navigation. directive_crawler présent mais non pris en charge, nul ou incohérent : inconclusive ; aucun repli favorable. Le profil de présentation garde les défauts d’image non qualifiés, l’interaction vidéo de max-snippet:0, les syntaxes non couvertes et les dépassements comme inconnues selon les intervalles conservateurs du contrat. Noindex ne donne pas un pass de présentation.

**Conditions de NA.** Non-HTML ou stabilité des directives démontrée par revue documentée ; la preuve intent référence cette justification et ses pièces. Aucune simple affirmation « pas de JS ».

**Limites.** semiAuto : le plan et la suffisance des observations nécessitent une revue. L’interpréteur compare des captures fournies ; il n’exécute pas JavaScript et ne démontre ni exhaustivité des états, ni TS25, ni rendu ou indexation du moteur. Rattachement et API fournis non authentifiés ; relevé synthétique explicitement signalé, jamais une visite réelle. Frames, fragments template et shadow fermés hors périmètre. Bornes et migration dans docs/structured-rendering.md. Le profil de présentation ne vérifie ni affichage Google, ni disponibilité d’image, ni data-nosnippet, ni usages sous licence, données structurées ou IA ; aucune revue n’est produite.

## TS08 — Le statut d’indexation réel est vérifié dans Search Console.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: search-console, intent.

**Applicabilité.** URL dont l’état dans Google doit être établi.

**Méthode.** Déclarer sélection, objectifs, sources et connaissances antérieures avant acquisition ; conserver les JSON API, leurs limites et les revues fournies selon google-inspection-evidence-v1.

**Attendus.** Les trois règles réussissent pour tout l’ensemble sélectionné. C qualifie le dossier du statut rapporté par Google, jamais une promesse d’indexation ni l’état actuel du site.

**Preuves.** URL connue, exploration autorisée, indexation et canonique Google documentées.

**Conditions de NA.** Le moteur Google est explicitement hors périmètre ; absence d’accès seule ne suffit pas.

**Limites.** API non live, attribution et dates fournies non authentifiées ; champs manquants/réservés, fraîcheur insuffisante et revues absentes restent inconclusifs selon le profil borné. Aucune extrapolation au site.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://support.google.com/webmasters/answer/9012289](https://support.google.com/webmasters/answer/9012289); [https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect); [https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult](https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult)

### TS08-A01 — Périmètre et objectifs préalables qualifiés.

`TSEP@0.2.0-rc.1:TS08-A01`

**Entrées requises**: intent, search-console.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Ensemble explicite d’URL dont l’état rapporté par Google doit être documenté.

**Méthode.** Déclarer les membres, leur objectif/source, motif de sélection, connaissances antérieures et politique de fraîcheur ; conserver la revue préalable liée au plan.

**Attendus.** Sélection et objectifs qualifiés supported, plan et revue avant acquisition, aucun membre omis. Une contradiction fournie ou une acquisition antérieure au plan donne fail ; absence seule reste indéterminée.

**Preuves.** Plan daté et sourcé, JSON requête/réponse natifs et empreintes, métadonnées réelles, revues fournies liées aux pièces ; contrat inspection-evidence-v1.

**Hypothèses.** Dates, auteur, provenance, accès et attribution sont déclarés, jamais authentifiés par leurs seules empreintes.

**Indéterminé.** Pièce, revue ou liaison manquante, invalide ou ambiguë ; limites, inconnues et erreurs API conservées.

**Conditions de NA.** Aucune exemption atomique ; absence d’accès ne vaut pas NA.

**Limites.** Dossier de la sélection seulement ; API non live et dernier crawl distinct de la date des champs. Ni état actuel, ni causalité, ni TS12, ni résultats SEO déduits.

### TS08-A02 — Inspections natives attribuées et lisibles.

`TSEP@0.2.0-rc.1:TS08-A02`

**Entrées requises**: search-console, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Ensemble explicite d’URL dont l’état rapporté par Google doit être documenté.

**Méthode.** Lire les octets natifs avec le diagnostic 1, comparer l’attribution URL/propriété, conserver les champs et contrôler les dates selon la politique préalable.

**Attendus.** Chaque membre possède une réponse exploitable avec champs requis connus et dates dans la politique. Les absences API expressément admises restent visibles ; erreur API et valeurs inconnues ne deviennent pas C.

**Preuves.** Plan daté et sourcé, JSON requête/réponse natifs et empreintes, métadonnées réelles, revues fournies liées aux pièces ; contrat inspection-evidence-v1.

**Hypothèses.** Dates, auteur, provenance, accès et attribution sont déclarés, jamais authentifiés par leurs seules empreintes.

**Indéterminé.** Pièce, revue ou liaison manquante, invalide ou ambiguë ; limites, inconnues et erreurs API conservées.

**Conditions de NA.** Aucune exemption atomique ; absence d’accès ne vaut pas NA.

**Limites.** Dossier de la sélection seulement ; API non live et dernier crawl distinct de la date des champs. Ni état actuel, ni causalité, ni TS12, ni résultats SEO déduits.

### TS08-A03 — Interprétation et décision liées aux preuves.

`TSEP@0.2.0-rc.1:TS08-A03`

**Entrées requises**: search-console, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Ensemble explicite d’URL dont l’état rapporté par Google doit être documenté.

**Méthode.** Lire la revue fournie : verdict API repris exactement, interprétation, relation à l’objectif préalable, portée temporelle, explication typée et décision opérationnelle.

**Attendus.** Toutes les facettes sont qualifiées ; un écart documenté peut passer. Contradiction explicite de verdict/portée ou qualification contradiction donne fail et survit aux inconnues indépendantes. Revue absente ou cause non étayée reste inconclusive.

**Preuves.** Plan daté et sourcé, JSON requête/réponse natifs et empreintes, métadonnées réelles, revues fournies liées aux pièces ; contrat inspection-evidence-v1.

**Hypothèses.** Dates, auteur, provenance, accès et attribution sont déclarés, jamais authentifiés par leurs seules empreintes.

**Indéterminé.** Pièce, revue ou liaison manquante, invalide ou ambiguë ; limites, inconnues et erreurs API conservées.

**Conditions de NA.** Aucune exemption atomique ; absence d’accès ne vaut pas NA.

**Limites.** Dossier de la sélection seulement ; API non live et dernier crawl distinct de la date des champs. Ni état actuel, ni causalité, ni TS12, ni résultats SEO déduits.

## TS09 — Les exclusions volontaires ont un propriétaire et une justification.

**Sévérité**: minor. **Unité**: policy.

**Entrées requises**: configuration, intent.

**Applicabilité.** Familles volontairement exclues.

**Méthode.** Relier chaque famille exclue à une règle, un responsable et une date de revue.

**Attendus.** Chaque exclusion du périmètre possède mécanisme, motif, propriétaire et date de revue.

**Preuves.** Registre des exclusions : type de page, mécanisme, motif, propriétaire, révision.

**Conditions de NA.** Aucune exclusion volontaire, inventaire de politique fourni.

**Limites.** La pertinence métier de l’exclusion ne peut pas être automatisée.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité. Le profil url-exclusion-observed-v2 exige un registre, une réponse HTTP représentative et robots.txt par famille, puis une revue explicitement liée aux preuves affichées. Une contradiction native reste NC en l’absence de revue ; une correspondance sans revue reste NT. Une famille entière, l’index Google et la confidentialité ne sont pas établis par cet échantillon.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/block-indexing](https://developers.google.com/search/docs/crawling-indexing/block-indexing)

### TS09-A01 — Registre des exclusions et responsabilités

`TSEP@0.3.0-draft.8:TS09-A01`

**Entrées requises**: configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments explicitement sélectionnés du contrôle TS09 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Méthode.** Lire le registre natif JSON exclusion-register-v1 ; rapprocher chaque famille sélectionnée du mécanisme préalable, puis vérifier propriétaire, motif et date de revue. Exiger une revue liée au dossier. Le profil url-exclusion-observed-v2 exige un registre, une réponse HTTP représentative et robots.txt par famille, puis une revue explicitement liée aux preuves affichées. Une contradiction native reste NC en l’absence de revue ; une correspondance sans revue reste NT. Une famille entière, l’index Google et la confidentialité ne sont pas établis par cet échantillon.

**Attendus.** Les mécanismes concordent et chaque famille a ses informations de gouvernance ; la revue fournie confirme le périmètre. Une divergence de mécanisme échoue.

**Preuves.** Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : configuration, intent.

**Hypothèses.** Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminé.** Un champ absent ou ambigu, un registre manquant ou une revue non liée donne indéterminé. La date de revue est une date de calendrier déclarée, pas une preuve de réalisation.

**Conditions de NA.** Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites.** Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

## TS10 — Chaque page canonique publie une URL absolue, stable et cohérente.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: http, html, sitemap, crawl, intent.

**Applicabilité.** Familles déclarant une stratégie de canonicalisation.

**Méthode.** Comparer URL finale, rel=canonical, sitemap et liens internes.

**Attendus.** Les quatre règles A01–A04 établissent une préférence cohérente selon la stratégie déclarée ; exceptions et absences sont justifiées, pas déduites d’un défaut de collecte.

**Preuves.** Signaux convergents vers la même URL canonique sans chaîne.

**Conditions de NA.** Aucun document concerné, inventaire et stratégie à l’appui.

**Limites.** rel=canonical est un signal fort, pas une directive garantie.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls); [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics); [https://www.sitemaps.org/protocol.html](https://www.sitemaps.org/protocol.html); [https://www.rfc-editor.org/rfc/rfc8288](https://www.rfc-editor.org/rfc/rfc8288)

### TS10-A01 — Déclaration canonique

`TSEP@0.2.0-rc.1:TS10-A01`

**Entrées requises**: http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque membre d’une famille et sa stratégie de canonicalisation déclarée.

**Méthode.** Lister membres, URL préférée et méthode attendue ; comparer URL finales, Link HTTP, rel=canonical HTML et états rendus nécessaires. Conserver les déclarations multiples, même identiques. Le lecteur DOM est choisi avant capture : structured-inventory-v2 ou le lecteur sérialisé historique fixe en l’absence de champ. Aucun repli après un refus. L’inventaire structuré complet conserve namespaces, positions, doublons, sérialisation et pièces de rattachement à la navigation ; aucune suppression de nœud selon son origine supposée. Le profil source facultatif intent.canonical.source_reader=html-tree-canonical-v1 est choisi avant capture ; il compare deux hypothèses statiques complètes, avec positions source/arbre attribuées aux octets. Le contrat source-canonical.md fixe ses frontières. Le choix préalable facultatif intent.canonical.http_reader=http-link-context-v1 applique le contrat docs/http-canonical-context.md aux Link de la réponse finale GET 200 ; absence de champ conserve le lecteur historique.

**Attendus.** Les signaux présents et ceux exigés par la stratégie désignent la même URL HTTP(S) absolue, sans fragment. HTML dans head ou en-tête Link sont acceptés ; pas d’obligation universelle d’une balise HTML. Une canonical relative est fail pour cette règle TSEP, sans affirmer son invalidité pour Google. Les déclarations répétées identiques sont conservées et peuvent converger ; un conflit attribuable demeure fail malgré une autre capture manquante. Deux lectures source pass donnent pass, deux fail donnent fail ; sinon inconclusive. Une canonical ordinaire dans body reste une contradiction, même de valeur égale. Les valeurs relatives ne sont jamais résolues via base. Les contradictions HTTP Link, redirections ou DOM attribuables restent indépendantes des inconnues source. La nouvelle lecture distingue contexte et destination littérale, conserve le premier rel et les déclarations répétées ; aucune inconnue ne permet pass, une contradiction HTTP attribuable indépendante demeure fail.

**Preuves.** Inventaire de famille dans intent ; en-têtes et source (ou record html non applicable pour non-HTML) ; extraction avec emplacement et méthode, DOM requis joint si nécessaire. Relier chaque capture à la famille, au contexte et à la date. Déclarer les méthodes et les états DOM requis avant examen ; lier les DOM à la trace HTTP par empreinte. Une exemption de rendu exige une revue liée à la source et ses pièces, pas une simple affirmation « pas de JS ». Conserver aussi les observations du profil : document, corps, canonical/base, templates, tokens du préfixe, contexte, erreurs, décodage, sources/runtime et décisions séparées. Le rejeu les compare. Diagnostic HTTP ordonné, champs et paramètres bruts, contextes exclus/inconnus, URL finale/demandée, date et empreinte de la chaîne conservés.

**Hypothèses.** La stratégie distingue canonical préférée et doublons ; aucune suppression implicite de paramètres, casse ou slash lors des comparaisons. Dans le DOM structuré, une différence entre href absolu brut et propriété résolue empêche la conclusion de cette surface, sans substituer l’une des valeurs ni affirmer un défaut SEO. La canonical relative ou hors head dans le DOM ordinaire reste une contradiction TSEP ; le shadow ouvert reste indéterminé. Champ absent : lecteur historique. Nul/inconnu ou Node 24 absent : pas de repli. Ce profil ne valide pas HTML et ne remplace ni rendu ni jugement humain.

**Indéterminé.** Famille/intention incomplète, Link ambigu, document tronqué ou état rendu requis absent : inconclusive. Pour le lecteur structuré : arbre/transport incomplet, chargement en cours, API connue comme altérée, histoire d’intégrité absente, capture source/DOM séparée sans rattachement à une même navigation ou agent différent : inconclusive. Une empreinte seule ne prouve pas la navigation. Réinsertion après fermeture explicite du head, descendant indirect, contexte étranger, modificateur/attribut inconnu, shadow déclaré, lecture ou diagnostic borné incomplet empêchent une réussite selon le contrat ; une contradiction distincte qualifiée reste conservée. Sélection HTTP inconnue, contexte non qualifié/équivalence incertaine, extension ou syntaxe hors couverture : inconclusive sans repli favorable ; les bornes et leur portée sont fixées dans le contrat HTTP.

**Conditions de NA.** Aucune exemption atomique quand le contrôle s’applique.

**Limites.** Relatif, placement et convergence sont des critères TSEP ; la sélection canonique du moteur n’est pas observée ici. Rattachement et API fournis non authentifiés ; relevé synthétique explicitement signalé, jamais une visite réelle. Frames, fragments template et shadow fermés hors périmètre. Bornes et migration dans docs/structured-rendering.md. Portée source uniquement ; A04 et les lecteurs DOM ne sont pas étendus. Les deux hypothèses ne sont pas deux états rendus observés. Aucun choix canonique Google n’est déduit. Aucune exécution du moteur ni normalisation de la destination ; un relatif valide RFC peut échouer au critère TSEP absolu. Migration draft.19 et ancien lecteur préservé.

### TS10-A02 — Destination canonique directe

`TSEP@0.2.0-rc.1:TS10-A02`

**Entrées requises**: http, html, intent.

**Automation / Automatisation**: `manual`.

**Applicabilité.** Toute destination préférée dans les familles déclarées.

**Méthode.** Tester la destination, conserver GET et contenu ; vérifier que son éventuelle canonical ne repart pas ailleurs. Comparer le contenu à la famille déclarée. Le lecteur DOM est choisi avant capture : structured-inventory-v2 ou le lecteur sérialisé historique fixe en l’absence de champ. Aucun repli après un refus. L’inventaire structuré complet conserve namespaces, positions, doublons, sérialisation et pièces de rattachement à la navigation ; aucune suppression de nœud selon son origine supposée. Le profil source facultatif intent.canonical.source_reader=html-tree-canonical-v1 est choisi avant capture ; il compare deux hypothèses statiques complètes, avec positions source/arbre attribuées aux octets. Le contrat source-canonical.md fixe ses frontières. Le choix préalable facultatif intent.canonical.http_reader=http-link-context-v1 applique le contrat docs/http-canonical-context.md aux Link de la réponse finale GET 200 ; absence de champ conserve le lecteur historique.

**Attendus.** La destination attendue est accessible directement en 200, sans chaîne ni cycle canonique, avec contenu compatible. Un doublon peut rester en 200 et pointer vers la préférée ; l’URL finale de chaque doublon n’a pas à lui être identique. Deux lectures source pass donnent pass, deux fail donnent fail ; sinon inconclusive. Une canonical ordinaire dans body reste une contradiction, même de valeur égale. Les valeurs relatives ne sont jamais résolues via base. Les contradictions HTTP Link, redirections ou DOM attribuables restent indépendantes des inconnues source. La nouvelle lecture distingue contexte et destination littérale, conserve le premier rel et les déclarations répétées ; aucune inconnue ne permet pass, une contradiction HTTP attribuable indépendante demeure fail.

**Preuves.** Trace et corps de la destination reliés à la famille ; graphe des déclarations et comparaison de contenu motivée. La revue humaine de compatibilité identifie son auteur, sa date, chaque membre comparé à la préférence, le jugement motivé et les captures exactes examinées, par empreinte. Une référence manquante, périmée ou une comparaison non établie empêche pass. Conserver aussi les observations du profil : document, corps, canonical/base, templates, tokens du préfixe, contexte, erreurs, décodage, sources/runtime et décisions séparées. Le rejeu les compare. Diagnostic HTTP ordonné, champs et paramètres bruts, contextes exclus/inconnus, URL finale/demandée, date et empreinte de la chaîne conservés.

**Hypothèses.** La proximité du contenu est évaluée dans le contexte métier, sans seuil universel de similarité. Dans le DOM structuré, une différence entre href absolu brut et propriété résolue empêche la conclusion de cette surface, sans substituer l’une des valeurs ni affirmer un défaut SEO. La canonical relative ou hors head dans le DOM ordinaire reste une contradiction TSEP ; le shadow ouvert reste indéterminé. Champ absent : lecteur historique. Nul/inconnu ou Node 24 absent : pas de repli. Ce profil ne valide pas HTML et ne remplace ni rendu ni jugement humain.

**Indéterminé.** Destination non collectée, délai ou contenu non comparable : inconclusive. Un 404/5xx, cycle ou saut observé est une contradiction. Pour le lecteur structuré : arbre/transport incomplet, chargement en cours, API connue comme altérée, histoire d’intégrité absente, capture source/DOM séparée sans rattachement à une même navigation ou agent différent : inconclusive. Une empreinte seule ne prouve pas la navigation. Réinsertion après fermeture explicite du head, descendant indirect, contexte étranger, modificateur/attribut inconnu, shadow déclaré, lecture ou diagnostic borné incomplet empêchent une réussite selon le contrat ; une contradiction distincte qualifiée reste conservée. Sélection HTTP inconnue, contexte non qualifié/équivalence incertaine, extension ou syntaxe hors couverture : inconclusive sans repli favorable ; les bornes et leur portée sont fixées dans le contrat HTTP.

**Conditions de NA.** Aucune exemption atomique quand le contrôle s’applique.

**Limites.** Un GET réussi ne prouve pas que Google retiendra cette URL ; aucune stabilité dans le temps déduite d’un instant. Un comparateur peut vérifier les liens et la couverture de la revue fournie ; il ne transforme pas ce jugement en comparaison automatique du contenu. Rattachement et API fournis non authentifiés ; relevé synthétique explicitement signalé, jamais une visite réelle. Frames, fragments template et shadow fermés hors périmètre. Bornes et migration dans docs/structured-rendering.md. Portée source uniquement ; A04 et les lecteurs DOM ne sont pas étendus. Les deux hypothèses ne sont pas deux états rendus observés. Aucun choix canonique Google n’est déduit. Aucune exécution du moteur ni normalisation de la destination ; un relatif valide RFC peut échouer au critère TSEP absolu. Migration draft.19 et ancien lecteur préservé.

### TS10-A03 — Convergence du sitemap

`TSEP@0.2.0-rc.1:TS10-A03`

**Entrées requises**: sitemap, intent.

**Automation / Automatisation**: `semiAuto`.

**Entrées pour exemption atomique**: intent, sitemap.

**Applicabilité.** Familles associées à un sitemap selon la stratégie déclarée.

**Méthode.** Comparer les entrées de tous les sitemaps/index nécessaires à la famille et à l’URL préférée ; conserver les exclusions justifiées par la stratégie. Rapprocher les captures de chaque index et de tous ses enfants attendus. Un échec observé reste fail si une autre branche manque ; une omission ne devient fail qu’après examen complet de la population annoncée. Le lecteur facultatif sitemap-locations-v1 doit être déclaré avant capture ; champ absent : lecteur historique fixe, valeur inconnue : aucun repli. Seuls les loc directs du namespace Sitemaps 0.9 sous url comptent comme URL de pages ; sous sitemap, ils désignent les enfants. Décoder XML et retirer les seuls espaces XML périphériques, puis comparer littéralement sans normalisation d’URL. Relever séparément les annotations XHTML alternate, image et champs ordinaires reconnus, sans les comparer comme URL de pages.

**Attendus.** Les entrées observées et exigées concordent avec la préférence déclarée ; un doublon publié comme canonique concurrent sans justification est fail.

**Preuves.** Sitemaps bruts et couverture des index, correspondance famille/entrées et justification des omissions. Conserver les octets XML et valeurs intégrales des annotations ; aperçu borné dans le motif, troncatures explicites.

**Hypothèses.** Le périmètre des sitemaps est déclaré ; leur absence ne se déduit pas du 404 d’un seul chemin supposé. Le nouveau lecteur exige les namespaces et structures explicitement couverts ; préfixes libres, valeurs des annotations non validées. La préférence reste une intention fournie, pas un choix observé du moteur.

**Indéterminé.** Index incomplet, sitemap attendu indisponible ou stratégie inconnue : inconclusive. Lecteur inconnu, namespace absent ou erroné, extension/attribut non couvert, doublon de feuille, structure ambiguë, texte mixte, DTD/entités, XML mal formé ou borne dépassée : document entier indéterminé.

**Conditions de NA.** Aucun sitemap utilisé pour cette famille, établi par stratégie et inventaire documentés. Conserver un record sitemap expliquant cette absence ; pas de NA de tout TS10.

**Limites.** Sitemap = préférence publiée, pas sélection du moteur ni inventaire exhaustif du site. Aucun verdict hreflang, image ou validité des valeurs. Le lecteur borné n’est pas un validateur XML Schema complet. Profil, registre de structures, bornes et migration : docs/sitemap-locations.md et docs/migration-draft.14.md.

### TS10-A04 — Convergence des liens internes

`TSEP@0.2.0-rc.1:TS10-A04`

**Entrées requises**: crawl, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque famille et population de pages sources déclarée.

**Méthode.** Extraire les liens de la population annoncée ; comparer leurs destinations et les exceptions documentées à la préférence canonique. Le lecteur DOM est choisi avant capture : structured-inventory-v2 ou le lecteur sérialisé historique fixe en l’absence de champ. Aucun repli après un refus. L’inventaire structuré complet conserve namespaces, positions, doublons, sérialisation et pièces de rattachement à la navigation ; aucune suppression de nœud selon son origine supposée. Le profil source facultatif préalable intent.canonical.links.source_reader=html-tree-links-v1 qualifie les href HTML a/area attribués, leur base et leur résolution WHATWG dans deux hypothèses statiques. Le contrat source-link-policy.md fixe cette méthode ; les lecteurs rendus antérieurs restent inchangés. Draft.18 ajoute html-tree-links-v2 : seule une première base dont le href échoue à l’analyse WHATWG ajoute une incertitude de base ; v1 reste inchangé. Le calcul avec l’URL finale est alors conditionnel, sans destination déduite pour un href dépendant. Le complément source-link-policy-v2.md définit cette différence.

**Attendus.** Tous les liens évalués suivent la stratégie ; aucune destination concurrente inexpliquée. Zéro lien peut satisfaire la règle uniquement si la population annoncée est intégralement examinée. Un lien concurrent attribuable reste fail même si une autre page source ou un état requis manque. Deux lectures source pass donnent pass, deux fail donnent fail, sinon inconclusive. Une base incertaine ne permet pas un fail sur un href dépendant ; une contradiction absolue qualifiée indépendante demeure exploitable. Les comptes zéro et la portée de convergence restent visibles jusque contrôle et gate, sans exigence de présence de lien.

**Preuves.** Export de crawl avec URL source, href, destination, pages réellement parcourues, échecs et exclusions ; rapprochement avec la population déclarée. Conserver le HTML source et les DOM nécessaires à l’extraction, liés à leurs traces, contextes et dates ; une exemption de rendu est revue et étayée. Les exceptions identifient source, destination et motif. Le nouveau profil conserve inventaire, namespaces, templates, balises/octets, URL calculées, bases et limites, versions, décisions et comptes par hypothèse dans les observations rejouables.

**Hypothèses.** Le crawl vérifie une population déclarée ; il n’en prouve pas à lui seul l’exhaustivité. Le lecteur structuré v2 conserve les href bruts ; résolution bornée seulement sans base déclarée et avec baseURI égale à l’URL finale. Un lien shadow ou une syntaxe non couverte reste indéterminé. Famille déjà identique à sa sérialisation WHATWG ou source indéterminée, sans normalisation implicite. URL hors famille conservées, pas de doublons devinés. href sans namespace, annotations nofollow/download non filtrantes ; destination statique seulement. href de base vide ou composé d’espaces, schémas data/javascript et CSP restent distincts de cet échec de parsing ; ne pas sélectionner une seconde base.

**Indéterminé.** Pages sources manquantes, liens non examinés ou crawl absent : inconclusive, jamais réussite par zéro résultat. Pour le lecteur structuré : arbre/transport incomplet, chargement en cours, API connue comme altérée, histoire d’intégrité absente, capture source/DOM séparée sans rattachement à une même navigation ou agent différent : inconclusive. Une empreinte seule ne prouve pas la navigation. Sélection source nulle/inconnue, runtime Node24 absent, parcours ou diagnostic incomplet : inconclusive sans repli. SVG/ancêtres étrangers, shadow déclaré et attributs dupliqués du lien restent inconnus ; CSP/base non modélisée empêche la résolution concluante des href dépendants.

**Conditions de NA.** Aucune exemption atomique quand le contrôle s’applique.

**Limites.** Aucun résultat étendu aux liens externes, pages hors population ou dates futures. Rattachement et API fournis non authentifiés ; relevé synthétique explicitement signalé, jamais une visite réelle. Frames, fragments template et shadow fermés hors périmètre. Bornes et migration dans docs/structured-rendering.md. Le profil source ne mesure ni activation, ni présence/suffisance du maillage, ni formulaires/événements ou comportement Google. Bornes, portée des autres éléments conservés et migration : source-link-policy.md et migration-draft.17.md. Correction v2 et conservation des anciens résultats : migration-draft.18.md. Aucun bug général de navigateur ni état Google n’est établi par le diagnostic.

## TS11 — Les variantes réellement dupliquées convergent sans masquer des pages distinctes.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: content, html, intent.

**Applicabilité.** Familles de variantes ou doublons identifiés.

**Méthode.** Échantillonner paramètres, pagination, filtres et versions imprimables ; comparer contenu et canonique.

**Attendus.** Chaque rapprochement est justifié par comparaison du contenu ; aucune page distincte testée n’est absorbée involontairement.

**Preuves.** Correspondance documentée entre doublon et canonique pertinent.

**Conditions de NA.** Aucune variante ni duplication connue après inventaire documenté.

**Limites.** Une similarité calculée ne remplace pas la décision éditoriale.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### TS11-A01 — Comparaison éditoriale des variantes

`TSEP@0.3.0-draft.2:TS11-A01`

**Entrées requises**: http, html, content, intent.

**Automation / Automatisation**: `manual`.

**Applicabilité.** Éléments explicitement sélectionnés du contrôle TS11 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Méthode.** Pour chaque paire déclarée duplicate ou distinct, lire les deux réponses HTML UTF-8 complètes et conserver leurs empreintes. Exiger la revue comparative liée, y compris la suffisance du périmètre source.

**Attendus.** Les deux contenus sont disponibles et la revue éditoriale étaye la relation déclarée. Une revue contradictoire échoue ; égalité ou similarité textuelle ne crée pas cette revue.

**Preuves.** Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : http, html, content, intent.

**Hypothèses.** Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminé.** Contenu absent, format HTML non pris en charge, comparaison dépendante du rendu ou jugement manquant : indéterminé.

**Conditions de NA.** Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites.** Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### TS11-A02 — Convergence sans absorption de pages distinctes

`TSEP@0.3.0-draft.2:TS11-A02`

**Entrées requises**: http, html, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments explicitement sélectionnés du contrôle TS11 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Méthode.** Lire séparément canonical HTTP et HTML des deux membres. Un doublon désigne la préférence ; une page distincte se désigne elle-même. Exiger la revue de la décision et du périmètre source.

**Attendus.** Toutes les déclarations qualifiées concordent avec la relation éditoriale préalable ; une déclaration contraire échoue, même si une autre surface manque.

**Preuves.** Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : http, html, content, intent.

**Hypothèses.** Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminé.** Aucune canonical explicite, source non interprétable ou rendu nécessaire non fourni : indéterminé, sans choix du moteur inféré.

**Conditions de NA.** Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites.** Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

## TS12 — La canonique choisie par Google est comparée à celle déclarée.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: search-console, http, html, render, intent.

**Applicabilité.** URL dont la canonique Google doit être comparée à la déclaration.

**Méthode.** Déclarer préférence sourcée, lecteurs et états rendus ; attribuer JSON API et captures, comparer les chaînes et conserver revues/décisions selon google-canonical-comparison-v1.

**Attendus.** Plan préalable et toutes les surfaces prévues qualifiés ; valeurs conservées avec dates séparées et décisions liées. C documentaire, jamais égalité canonique ; divergences documentées admises.

**Preuves.** Accord ou divergence qualifiée et traitée.

**Conditions de NA.** Google explicitement hors périmètre ; manque d’accès classé NT.

**Limites.** Rendu requis manquant ou canonical Google absente : indéterminé. Comparaison littérale sans équivalence d’URL, état live, causalité, TS10 ou indexation déduits.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://support.google.com/webmasters/answer/9012289](https://support.google.com/webmasters/answer/9012289)

### TS12-A01 — Plan de comparaison préalable qualifié.

`TSEP@0.2.0-rc.1:TS12-A01`

**Entrées requises**: intent, search-console, http.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Ensemble sélectionné dont les canonical rapportées et capturées doivent être comparées.

**Méthode.** Déclarer sélection/objectifs, connaissances antérieures, préférence sourcée, lecteurs et états rendus ; qualifier le plan lié avant chaque acquisition.

**Attendus.** Jugements selection/objectives/preferences/surfaces/temporal_policy supported, ordre préalable et ensemble complet. Contradiction fournie ou acquisition avant plan : fail ; lacune : inconclusive.

**Preuves.** Plan/revue préalables, JSON API natifs, traces HTTP, états DOM structurés fournis et revues liées aux pièces exactes ; contrat canonical-comparison-v1.

**Hypothèses.** Données, dates, provenance et jugements fournis ; empreintes sans authentification de personne, navigation ou histoire.

**Indéterminé.** Pièce, état requis, valeur, politique, revue ou liaison absente/inconnue/invalide ; limites et erreurs conservées.

**Conditions de NA.** Aucune exemption atomique ; manque d’accès ou de rendu ne vaut pas NA.

**Limites.** Rendu requis manquant ou canonical Google absente : indéterminé. Comparaison littérale sans équivalence d’URL, état live, causalité, TS10 ou indexation déduits.

### TS12-A02 — Lectures et comparaisons attribuées complètes.

`TSEP@0.2.0-rc.1:TS12-A02`

**Entrées requises**: search-console, http, html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Ensemble sélectionné dont les canonical rapportées et capturées doivent être comparées.

**Méthode.** Lire les pièces natives et les deux hypothèses HTML statiques ; conserver les candidats HTTP/HTML/DOM, les dates et les comparaisons littérales distinctes.

**Attendus.** API qualifiée, Google canonical présente, HTTP/HTML et tous les états DOM prévus lisibles ; seuils préalables respectés, aucun doublon fusionné. Différence de valeurs admise ; source seule/absence Google = inconclusive.

**Preuves.** Plan/revue préalables, JSON API natifs, traces HTTP, états DOM structurés fournis et revues liées aux pièces exactes ; contrat canonical-comparison-v1.

**Hypothèses.** Données, dates, provenance et jugements fournis ; empreintes sans authentification de personne, navigation ou histoire.

**Indéterminé.** Pièce, état requis, valeur, politique, revue ou liaison absente/inconnue/invalide ; limites et erreurs conservées.

**Conditions de NA.** Aucune exemption atomique ; manque d’accès ou de rendu ne vaut pas NA.

**Limites.** Rendu requis manquant ou canonical Google absente : indéterminé. Comparaison littérale sans équivalence d’URL, état live, causalité, TS10 ou indexation déduits.

### TS12-A03 — Qualification et décision liées aux comparaisons.

`TSEP@0.2.0-rc.1:TS12-A03`

**Entrées requises**: search-console, http, html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Ensemble sélectionné dont les canonical rapportées et capturées doivent être comparées.

**Méthode.** Examiner les revendications de valeurs de chaque surface dans une revue fournie liée aux pièces, avec interprétation, temporalité, changements, objectif, explication et décision.

**Attendus.** Revendications fidèles aux listes connues, qualification supported, relation et décision motivées. Une revendication contredite conserve fail malgré une autre inconnue ; revue absente ou cause non établie hors profil : inconclusive.

**Preuves.** Plan/revue préalables, JSON API natifs, traces HTTP, états DOM structurés fournis et revues liées aux pièces exactes ; contrat canonical-comparison-v1.

**Hypothèses.** Données, dates, provenance et jugements fournis ; empreintes sans authentification de personne, navigation ou histoire.

**Indéterminé.** Pièce, état requis, valeur, politique, revue ou liaison absente/inconnue/invalide ; limites et erreurs conservées.

**Conditions de NA.** Aucune exemption atomique ; manque d’accès ou de rendu ne vaut pas NA.

**Limites.** Rendu requis manquant ou canonical Google absente : indéterminé. Comparaison littérale sans équivalence d’URL, état live, causalité, TS10 ou indexation déduits.

## TS13 — Le sitemap contient uniquement des URL absolues et canoniques utiles.

**Sévérité**: major. **Unité**: sitemap-set.

**Entrées requises**: sitemap, http, html, intent.

**Applicabilité.** Sitemaps utilisés pour les URL du périmètre.

**Méthode.** Appliquer TS13-A01/A02 aux originaux déclarés et aux pages fournies selon le contrat sitemap-quality-v1.

**Attendus.** Chaque entrée du périmètre est résolue, canonique selon la stratégie et destinée à l’indexation ; exclusions et limites de l’échantillon sont explicites.

**Preuves.** Inventaire sans redirection, 4xx, noindex ni doublon de canonique.

**Conditions de NA.** Aucun sitemap utilisé, inventaire et décision fournis.

**Limites.** Population déclarée de fichiers et pages fournis ; sources HTML bornées et revues non authentifiées. Aucun audit réel, exhaustivité du site, TS15 global, canonical choisie par Google, indexation ou classement déduit.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

### TS13-A01 — Population native et URL absolues qualifiées.

`TSEP@0.3.0-draft.1:TS13-A01`

**Entrées requises**: sitemap, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Entrées de pages dans les fichiers sitemap déclarés au préalable, profil borné supplied-sitemap-quality-v1.

**Méthode.** Rapprocher les racines et enfants déclarés avec les originaux complets ; lire chaque loc de page, conserver occurrences et vérifier son caractère absolu HTTP(S).

**Attendus.** Pass exige la couverture de tous les fichiers déclarés et tous les loc qualifiés. Un loc relatif, avec fragment, identifiants ou port invalide donne fail ; couverture manquante : inconclusive.

**Preuves.** Plan, originaux XML/gzip datés et SHA-256, index/position/loc de chaque entrée. Les répétitions littérales restent visibles sans défaut automatique.

**Hypothèses.** Plan antérieur, URL littérales, fenêtre fournie de24h maximum et intégrité des originaux. Dates, contexte et jugements déclarés, sans authentification.

**Indéterminé.** Plan, document, enfant, liaison, capture ou revue absent, ambigu ou hors profil ; borne dépassée. Conserver tout fail indépendant et les autres inconnues.

**Conditions de NA.** Aucune exemption atomique ; manque de preuve ne vaut pas NA.

**Limites.** Population déclarée de fichiers et pages fournis ; sources HTML bornées et revues non authentifiées. Aucun audit réel, exhaustivité du site, TS15 global, canonical choisie par Google, indexation ou classement déduit.

### TS13-A02 — Pages référencées cohérentes avec la stratégie fournie.

`TSEP@0.3.0-draft.1:TS13-A02`

**Entrées requises**: sitemap, http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Entrées de pages dans les fichiers sitemap déclarés au préalable, profil borné supplied-sitemap-quality-v1.

**Méthode.** Pour chaque URL native distincte, vérifier GET direct200, directives Googlebot HTTP/HTML et canonical littérale ; rapprocher stratégie préalable et revue liée à la page et aux fichiers.

**Attendus.** Pass exige source qualifiée, canonical explicite identique, intention utile/indexable/self-canonical et revue supported, rendering source-only. Redirection, statut complet hors200, noindex, canonical divergente ou jugement contradicted donne fail. Rendu requis, absence de canonical/revue ou format hors profil : inconclusive.

**Preuves.** Originaux des fichiers et requêtes/réponses HTTP, contexte/date par page, plan et revue avec SHA-256 de l’ensemble examiné. Aucune revue manquante produite par l’outil.

**Hypothèses.** Plan antérieur, URL littérales, fenêtre fournie de24h maximum et intégrité des originaux. Dates, contexte et jugements déclarés, sans authentification.

**Indéterminé.** Plan, document, enfant, liaison, capture ou revue absent, ambigu ou hors profil ; borne dépassée. Conserver tout fail indépendant et les autres inconnues.

**Conditions de NA.** Aucune exemption atomique ; manque de preuve ne vaut pas NA.

**Limites.** Population déclarée de fichiers et pages fournis ; sources HTML bornées et revues non authentifiées. Aucun audit réel, exhaustivité du site, TS15 global, canonical choisie par Google, indexation ou classement déduit.

## TS14 — lastmod reflète une modification significative de la page.

**Sévérité**: minor. **Unité**: sitemap-set.

**Entrées requises**: sitemap, change-history, intent.

**Applicabilité.** Sitemaps comportant lastmod.

**Méthode.** Lire le lastmod natif de chaque entrée de page ; comparer sa date UTC ou son instant zoné à un événement JSON original attribué, puis vérifier la revue de signification liée.

**Attendus.** Chaque date testée correspond à une modification significative traçable ; la génération du fichier ne suffit pas.

**Preuves.** Horodatage ISO 8601 lié à une modification réelle, pas à la génération du fichier.

**Conditions de NA.** Aucun lastmod déclaré ; son absence n’est pas un défaut en soi.

**Limites.** Une date égale et une revue fournie ne prouvent pas une modification réelle ni sa signification. Précision au jour UTC ou à l’instant zoné ; aucun historique CMS complet, fraîcheur idéale ou traitement moteur déduit.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping](https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping)

### TS14-A01 — lastmod relié à une modification significative documentée.

`TSEP@0.3.0-draft.1:TS14-A01`

**Entrées requises**: sitemap, change-history, intent.

**Automation / Automatisation**: `semiAuto`.

**Entrées pour exemption atomique**: sitemap, intent.

**Applicabilité.** Entrées de pages portant lastmod dans la population préalable ; profil supplied-sitemap-lastmod-v1. lastmod des index hors périmètre.

**Méthode.** Lire le lastmod natif de chaque entrée de page ; comparer sa date UTC ou son instant zoné à un événement JSON original attribué, puis vérifier la revue de signification liée.

**Attendus.** Pass exige dates concordantes non futures, événement content attribué et revue supported. Date invalide/future, écart traçable, génération du fichier seule ou revue contradicted : fail. Historique/revue insuffisant : inconclusive. Absence native complète de lastmod : exemption atomique, jamais défaut.

**Preuves.** XML original daté/empreinté, URL du fichier et position de l’entrée, événement JSON UTF8 original avec SHA-256, change_id, URL, changed_at, kind et description ; revue attribuée et liée.

**Hypothèses.** Plan antérieur, URL littérales, fenêtre fournie de24h maximum et intégrité des originaux. Dates, contexte et jugements déclarés, sans authentification.

**Indéterminé.** Plan, document, enfant, liaison, capture ou revue absent, ambigu ou hors profil ; borne dépassée. Conserver tout fail indépendant et les autres inconnues. Fuseau absent ou précision de lastmod hors profil : inconclusive, jamais défaut inventé.

**Conditions de NA.** not-applicable atomique uniquement si absence lue dans une entrée native complète. Toutes les entrées exemptées ne produisent pas un C ni un NA de contrôle automatique.

**Limites.** Une date égale et une revue fournie ne prouvent pas une modification réelle ni sa signification. Précision au jour UTC ou à l’instant zoné ; aucun historique CMS complet, fraîcheur idéale ou traitement moteur déduit.

## TS15 — Les limites et découpages de sitemap sont respectés.

**Sévérité**: major. **Unité**: sitemap-set.

**Entrées requises**: sitemap, intent.

**Applicabilité.** Population déclarée de fichiers sitemap natifs fournis ; racines non découvertes automatiquement.

**Méthode.** Lire les octets originaux, la structure XML de base, la taille décompressée, les éléments directs et les enfants d’index du jeu déclaré.

**Attendus.** Dans le profil borné : UTF-8 et structure minimale qualifiés, au plus52 428 800 octets et50 000 éléments directs par fichier, couverture du jeu déclaré.

**Preuves.** Originaux base64/SHA-256, URL et dates déclarées, plan du jeu ; limites du profil native-sitemap-files-v1.

**Conditions de NA.** Aucun sitemap utilisé dans le périmètre.

**Limites.** Fichiers fournis seulement, pas serveur observé ni exhaustivité du site. Ni validation XSD complète, ni valeurs lastmod/changefreq/priority, portée hôte/chemin/longueur URL, canonical ou indexation.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://www.sitemaps.org/protocol.html](https://www.sitemaps.org/protocol.html)

### TS15-A01 — Encodage et structure minimale des fichiers fournis.

`TSEP@0.2.0-rc.1:TS15-A01`

**Entrées requises**: sitemap, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Population déclarée de fichiers sitemap natifs fournis ; racines non découvertes automatiquement.

**Méthode.** Vérifier UTF-8 strict, racine0.9, loc unique non vide et feuilles uniques ordonnées ; DTD/extension non qualifiée restent inconnus.

**Attendus.** Tous les fichiers complets passent la structure bornée ; contradiction structurelle établie fail.

**Preuves.** Originaux base64/SHA-256, URL et dates déclarées, plan du jeu ; limites du profil native-sitemap-files-v1.

**Hypothèses.** URL, date, origine et complétude fournies, non authentifiées. Aucune observation du serveur.

**Indéterminé.** Fichier absent/ambigu, flux incomplet, profil inconnu, borne interne, index imbriqué ou extension non qualifiée ; violation indépendante conservée.

**Conditions de NA.** Pas de NA dans ce profil.

**Limites.** Fichiers fournis seulement, pas serveur observé ni exhaustivité du site. Ni validation XSD complète, ni valeurs lastmod/changefreq/priority, portée hôte/chemin/longueur URL, canonical ou indexation.

### TS15-A02 — Limites réelles de taille et de population.

`TSEP@0.2.0-rc.1:TS15-A02`

**Entrées requises**: sitemap, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Population déclarée de fichiers sitemap natifs fournis ; racines non découvertes automatiquement.

**Méthode.** Compter les octets réellement décompressés et les éléments url/sitemap directs, doublons et loc absents compris.

**Attendus.** Chaque fichier reste à52 428 800 octets et50 000 éléments au plus ; dépassement lu fail, lecture partielle sans dépassement inconclusive.

**Preuves.** Originaux base64/SHA-256, URL et dates déclarées, plan du jeu ; limites du profil native-sitemap-files-v1.

**Hypothèses.** URL, date, origine et complétude fournies, non authentifiées. Aucune observation du serveur.

**Indéterminé.** Fichier absent/ambigu, flux incomplet, profil inconnu, borne interne, index imbriqué ou extension non qualifiée ; violation indépendante conservée.

**Conditions de NA.** Pas de NA dans ce profil.

**Limites.** Fichiers fournis seulement, pas serveur observé ni exhaustivité du site. Ni validation XSD complète, ni valeurs lastmod/changefreq/priority, portée hôte/chemin/longueur URL, canonical ou indexation.

### TS15-A03 — Couverture de la population déclarée et enfants liés.

`TSEP@0.2.0-rc.1:TS15-A03`

**Entrées requises**: sitemap, intent.

**Automation / Automatisation**: `automatic`.

**Issues autorisées**: pass, inconclusive.

**Applicabilité.** Population déclarée de fichiers sitemap natifs fournis ; racines non découvertes automatiquement.

**Méthode.** Relier chaque document à une URL déclarée exacte et chaque enfant d’index à une feuille complète ; racines et périmètre restent déclarés.

**Attendus.** Tous les documents déclarés et branches sont qualifiés ; absence/ambiguïté/hors profil inconclusive, jamais preuve négative de sitemap utilisé sur le site.

**Preuves.** Originaux base64/SHA-256, URL et dates déclarées, plan du jeu ; limites du profil native-sitemap-files-v1.

**Hypothèses.** URL, date, origine et complétude fournies, non authentifiées. Aucune observation du serveur.

**Indéterminé.** Fichier absent/ambigu, flux incomplet, profil inconnu, borne interne, index imbriqué ou extension non qualifiée ; violation indépendante conservée.

**Conditions de NA.** Pas de NA dans ce profil.

**Limites.** Fichiers fournis seulement, pas serveur observé ni exhaustivité du site. Ni validation XSD complète, ni valeurs lastmod/changefreq/priority, portée hôte/chemin/longueur URL, canonical ou indexation.

## TS16 — Chaque page importante reçoit au moins un lien interne crawlable.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: http, html, inventory, intent.

**Applicabilité.** Population importante et sources internes choisies avant les captures, avec inventaire original daté et plan lié ; profil incoming-document-links-v1.

**Méthode.** Pour chaque destination, chercher un témoin a/href depuis un autre document interne qualifié : source HTML sous deux hypothèses statiques ou DOM déclaré sans interaction. Qualifier séparément chaque source, destination et surface.

**Attendus.** Chaque destination déclarée possède un témoin entrant qualifié et son original HTTP. Une absence n’est établie que sur toutes les surfaces éligibles qualifiées de l’inventaire préalable ; elle reste limitée à cette population.

**Preuves.** Inventaire original, plan, originaux HTTP/DOM, URL demandées/finales, dates, statut de destination, href brut, référence d’ancre et diagnostics par destination. Les DOM sont requis pour les surfaces qui en dépendent ; un témoin source indépendant suffit sans DOM, sans en inventer un.

**Conditions de NA.** Aucune page importante concernée seulement avec justification et inventaire ; aucune NA automatique dans le lecteur borné.

**Limites.** Population et importance déclarées, non authentifiées. Aucune exhaustivité du site, acquisition ou interaction observée, valeur éditoriale, visite Google, indexation ou classement. Une absence bornée ne prouve pas une page orpheline du site. Le contenu attendu de la source et les soft404 ne sont pas évalués.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

### TS16-A01 — Témoin entrant dans la population interne préalable.

`TSEP@0.2.0-rc.1:TS16-A01`

**Entrées requises**: http, html, inventory, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Population importante et sources internes choisies avant les captures, avec inventaire original daté et plan lié ; profil incoming-document-links-v1.

**Méthode.** Pour chaque destination, chercher un témoin a/href depuis un autre document interne qualifié : source HTML sous deux hypothèses statiques ou DOM déclaré sans interaction. Qualifier séparément chaque source, destination et surface.

**Attendus.** Pass si toutes les destinations possèdent un témoin indépendant qualifié et un original de destination. Fail si une destination n’a aucun témoin dans toute la population éligible qualifiée. Sinon inconclusive ; un fail indépendant survit aux autres inconnues.

**Preuves.** Inventaire original, plan, originaux HTTP/DOM, URL demandées/finales, dates, statut de destination, href brut, référence d’ancre et diagnostics par destination. Les DOM sont requis pour les surfaces qui en dépendent ; un témoin source indépendant suffit sans DOM, sans en inventer un.

**Hypothèses.** Inventaire observé avant le plan qui lie son empreinte, captures dans la fenêtre préalable ; origines exactes et états sans interaction déclarés. L’intégrité ne prouve pas l’authenticité ni la simultanéité.

**Indéterminé.** Plan/inventaire ou original insuffisant, population ambiguë, surface non qualifiée, dates incohérentes ou runtime absent. Une paire dont la destination retourne par redirection à la source reste indéterminée ; un autre témoin peut suffire.

**Conditions de NA.** Aucune NA automatique dans ce profil.

**Limites.** Population et importance déclarées, non authentifiées. Aucune exhaustivité du site, acquisition ou interaction observée, valeur éditoriale, visite Google, indexation ou classement. Une absence bornée ne prouve pas une page orpheline du site. Le contenu attendu de la source et les soft404 ne sont pas évalués.

## TS17 — Les liens essentiels utilisent un élément a avec href résoluble.

**Sévérité**: major. **Unité**: page.

**Entrées requises**: http, html, render, intent.

**Applicabilité.** Destinations essentielles déclarées dans la stratégie préalable source-and-rendered, sur les captures fournies.

**Méthode.** Comparer les liens HTML a/href de la source et de chaque état DOM déclaré ; deux stades distincts, URL de document exactes.

**Attendus.** Chaque destination déclarée possède un lien a/href résoluble dans les deux stades requis, dans le profil borné essential-document-links-v1.

**Preuves.** Octets HTTP originaux, arbre DOM v2 lié, plan et diagnostics source/rendu séparés ; états déclarés par le fournisseur.

**Conditions de NA.** Aucune navigation concernée, périmètre justifié.

**Limites.** C dans la stratégie déclarée seulement. Aucune visibilité, interaction, importance éditoriale, authenticité, visite Google, indexation ou classement établi. Pas d’exigence Google universelle de présence source.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

### TS17-A01 — Liens essentiels présents dans la source fournie.

`TSEP@0.2.0-rc.1:TS17-A01`

**Entrées requises**: http, html, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Destinations essentielles déclarées dans la stratégie préalable source-and-rendered, sur les captures fournies.

**Méthode.** Lire la source native sous les deux hypothèses statiques de scripts ; exiger leur accord.

**Attendus.** Toutes les destinations au stade qualifié : pass ; absence établie sur inventaire complet : fail ; sinon inconclusive.

**Preuves.** Octets HTTP originaux, arbre DOM v2 lié, plan et diagnostics source/rendu séparés ; états déclarés par le fournisseur.

**Hypothèses.** Plan préalable, population, scénarios et complétude déclarés ; liaison HTTP/DOM vérifiée mais acquisition non authentifiée.

**Indéterminé.** Plan/stade absent, incomplet, hors profil, base active, lecture ambiguë ou runtime absent. Une contradiction indépendante reste conservée.

**Conditions de NA.** Aucune NA automatique dans ce profil.

**Limites.** C dans la stratégie déclarée seulement. Aucune visibilité, interaction, importance éditoriale, authenticité, visite Google, indexation ou classement établi. Pas d’exigence Google universelle de présence source.

### TS17-A02 — Liens essentiels présents dans les états rendus déclarés.

`TSEP@0.2.0-rc.1:TS17-A02`

**Entrées requises**: http, render, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Destinations essentielles déclarées dans la stratégie préalable source-and-rendered, sur les captures fournies.

**Méthode.** Vérifier chaque arbre complet lié au HTTP et signaler les snapshots répétés ; scénarios non authentifiés.

**Attendus.** Toutes les destinations au stade qualifié : pass ; absence établie sur inventaire complet : fail ; sinon inconclusive.

**Preuves.** Octets HTTP originaux, arbre DOM v2 lié, plan et diagnostics source/rendu séparés ; états déclarés par le fournisseur.

**Hypothèses.** Plan préalable, population, scénarios et complétude déclarés ; liaison HTTP/DOM vérifiée mais acquisition non authentifiée.

**Indéterminé.** Plan/stade absent, incomplet, hors profil, base active, lecture ambiguë ou runtime absent. Une contradiction indépendante reste conservée.

**Conditions de NA.** Aucune NA automatique dans ce profil.

**Limites.** C dans la stratégie déclarée seulement. Aucune visibilité, interaction, importance éditoriale, authenticité, visite Google, indexation ou classement établi. Pas d’exigence Google universelle de présence source.

## TS18 — La profondeur et les pages orphelines sont mesurées sur un périmètre explicite.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: crawl, sitemap, inventory, intent, http, html.

**Applicabilité.** Population, racines, familles et frontières déclarées avant les captures ; profil borné supplied-graph-reconciliation-v1.

**Méthode.** Rapprocher les originaux de référence, crawl, CMS et sitemap ; calculer liens et distances du graphe natif borné ; vérifier les revues fournies et liées aux mesures par famille et différence.

**Attendus.** Trois couches complètes dans le périmètre fourni : rapprochement qualifié, mesures natives qualifiées et revues documentaires liées. Une contradiction revue et étayée reste NC malgré une autre inconnue.

**Preuves.** Inventaires originaux datés et empreintés, production et dépendances déclarées, plan, HTTP/source/DOM originaux, paires et bornes, dates par inventaire et revues fournies liées aux dossiers exacts.

**Conditions de NA.** Aucun graphe de navigation concerné, justification fournie ; inventaire manquant signifie NT.

**Limites.** Graphe déclaré uniquement : aucune exhaustivité, page orpheline globale, profondeur SEO universelle, authenticité des captures ou des revues, interaction observée, indexation ou classement. HTTP200 ne vérifie pas le contenu attendu ni les soft404. Le motif fourni n’est pas jugé par le lecteur.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

### TS18-A01 — Périmètre préalable et inventaires originaux rapprochés.

`TSEP@0.2.0-rc.1:TS18-A01`

**Entrées requises**: crawl, sitemap, inventory, intent.

**Automation / Automatisation**: `automatic`.

**Issues autorisées**: pass, inconclusive.

**Applicabilité.** Population, racines, familles et frontières déclarées avant les captures ; profil borné supplied-graph-reconciliation-v1.

**Méthode.** Lire les formats et lignées explicitement déclarés ; référence ordonnée liée au plan, crawl suivant les liens depuis les seules racines, CMS natif et sitemap avec dépendance éventuelle explicite.

**Attendus.** Pass si toutes les pièces, dates, familles et déclarations sont qualifiées ; sinon inconclusive. L’accord entre listes ne prouve pas leur exhaustivité. Amorçage mixte ou mode liste : inconclusive dans ce profil.

**Preuves.** Inventaires originaux datés et empreintés, production et dépendances déclarées, plan, HTTP/source/DOM originaux, paires et bornes, dates par inventaire et revues fournies liées aux dossiers exacts.

**Hypothèses.** Origines et documents exacts, plan antérieur, captures dans une fenêtre maximale de24h ; déclarations de production et états sans interaction non authentifiés.

**Indéterminé.** Plan, original, surface ou revue absent, ambigu, hors profil, mal lié ou hors fenêtre ; runtime requis absent. Les inconnues restent explicites et un défaut indépendant ne disparaît pas.

**Conditions de NA.** Aucune NA automatique ; absence de preuve signifie indéterminé.

**Limites.** Graphe déclaré uniquement : aucune exhaustivité, page orpheline globale, profondeur SEO universelle, authenticité des captures ou des revues, interaction observée, indexation ou classement. HTTP200 ne vérifie pas le contenu attendu ni les soft404. Le motif fourni n’est pas jugé par le lecteur.

### TS18-A02 — Profondeurs et degrés entrants dans le graphe borné.

`TSEP@0.2.0-rc.1:TS18-A02`

**Entrées requises**: http, html, intent.

**Automation / Automatisation**: `automatic`.

**Issues autorisées**: pass, inconclusive.

**Applicabilité.** Population, racines, familles et frontières déclarées avant les captures ; profil borné supplied-graph-reconciliation-v1.

**Méthode.** Lire chaque paire depuis la source sous deux hypothèses ou un DOM qualifié sans interaction ; calculer distances minimale/majorante et nombres minimal/maximal de sources distinctes, sans auto-liens.

**Attendus.** Pass si les racines et toutes les paires sont qualifiées ; sinon inconclusive, même si une profondeur particulière est exacte. Candidat sans lien entrant seulement si son maximum vaut0. Aucun seuil universel de profondeur.

**Preuves.** Inventaires originaux datés et empreintés, production et dépendances déclarées, plan, HTTP/source/DOM originaux, paires et bornes, dates par inventaire et revues fournies liées aux dossiers exacts.

**Hypothèses.** Origines et documents exacts, plan antérieur, captures dans une fenêtre maximale de24h ; déclarations de production et états sans interaction non authentifiés.

**Indéterminé.** Plan, original, surface ou revue absent, ambigu, hors profil, mal lié ou hors fenêtre ; runtime requis absent. Les inconnues restent explicites et un défaut indépendant ne disparaît pas.

**Conditions de NA.** Aucune NA automatique ; absence de preuve signifie indéterminé.

**Limites.** Graphe déclaré uniquement : aucune exhaustivité, page orpheline globale, profondeur SEO universelle, authenticité des captures ou des revues, interaction observée, indexation ou classement. HTTP200 ne vérifie pas le contenu attendu ni les soft404. Le motif fourni n’est pas jugé par le lecteur.

### TS18-A03 — Qualification documentaire fournie des familles et différences.

`TSEP@0.2.0-rc.1:TS18-A03`

**Entrées requises**: intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population, racines, familles et frontières déclarées avant les captures ; profil borné supplied-graph-reconciliation-v1.

**Méthode.** Déduire les sujets des seules mesures natives ; vérifier une revue pour chaque famille, différence connue, candidat sans entrant et document inaccessible, liée au plan, originaux, dates et mesures.

**Attendus.** Pass si tous les sujets qualifiés ont une explication fournie correctement liée ; fail si un défaut fourni est lié à un sujet étayé ; sinon inconclusive. Une revue ne qualifie pas une mesure inconnue et ne devient jamais une approbation humaine créée par le logiciel.

**Preuves.** Inventaires originaux datés et empreintés, production et dépendances déclarées, plan, HTTP/source/DOM originaux, paires et bornes, dates par inventaire et revues fournies liées aux dossiers exacts.

**Hypothèses.** Origines et documents exacts, plan antérieur, captures dans une fenêtre maximale de24h ; déclarations de production et états sans interaction non authentifiés.

**Indéterminé.** Plan, original, surface ou revue absent, ambigu, hors profil, mal lié ou hors fenêtre ; runtime requis absent. Les inconnues restent explicites et un défaut indépendant ne disparaît pas.

**Conditions de NA.** Aucune NA automatique ; absence de preuve signifie indéterminé.

**Limites.** Graphe déclaré uniquement : aucune exhaustivité, page orpheline globale, profondeur SEO universelle, authenticité des captures ou des revues, interaction observée, indexation ou classement. HTTP200 ne vérifie pas le contenu attendu ni les soft404. Le motif fourni n’est pas jugé par le lecteur.

## TS19 — Les paramètres, filtres et calendriers ne créent pas un espace infini.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: crawl, configuration, intent.

**Applicabilité.** Paramètres, filtres, calendriers et autres espaces combinatoires.

**Méthode.** Regrouper les URL par motif, compter les combinaisons et rechercher les pièges de crawl.

**Attendus.** Chaque motif testé a une politique de navigation/indexation ; limites et pièges observés sont expliqués sans inférer le volume exploré réel.

**Preuves.** Règle d’indexation et de navigation pour chaque motif de paramètre.

**Conditions de NA.** Inventaire attestant l’absence de tels motifs.

**Limites.** Le volume réellement exploré exige les logs ou Search Console.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/url-structure](https://developers.google.com/search/docs/crawling-indexing/url-structure)

### TS19-A01 — Politique bornée par motif combinatoire

`TSEP@0.3.0-draft.2:TS19-A01`

**Entrées requises**: configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments explicitement sélectionnés du contrôle TS19 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Méthode.** Comparer les axes max_combinations, navigation et indexing du fichier natif url-pattern-config-v1 à chaque motif préalable ; exiger la revue du choix de bornes.

**Attendus.** Chaque axe fourni correspond au plan fini sélectionné. Une valeur contradictoire, notamment une limite nulle contraire au plan positif, échoue.

**Preuves.** Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : configuration, intent.

**Hypothèses.** Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminé.** Axe ou configuration manquant, borne non entière ou hors 1–128, revue absente : indéterminé.

**Conditions de NA.** Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites.** Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### TS19-A02 — Population observée et décision sur les pièges

`TSEP@0.3.0-draft.2:TS19-A02`

**Entrées requises**: crawl, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments explicitement sélectionnés du contrôle TS19 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Méthode.** Lire url-crawl-v1, compter les URL distinctes et les comparer à la liste finie et à sa borne ; conserver la décision motivée sur les pièges/cycles et sa revue.

**Attendus.** Les URL observées appartiennent à la population prévue, leur nombre respecte la borne et les pièges sont expliqués. Une URL extérieure ou un dépassement échoue.

**Preuves.** Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : crawl, intent.

**Hypothèses.** Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminé.** Crawl fourni incomplet, identités ambiguës, liste ou décision absente : indéterminé. Un échantillon fini ne prouve jamais la finitude de tout le site.

**Conditions de NA.** Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites.** Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

## TS20 — La structure d’URL est lisible, stable et encodée correctement.

**Sévérité**: minor. **Unité**: url-set.

**Entrées requises**: crawl, configuration, intent.

**Applicabilité.** Motifs d’URL publiés.

**Méthode.** Relever espaces, fragments, caractères encodés, casse et identifiants volatils.

**Attendus.** Encodage, casse, stabilité et variations correspondent aux règles déclarées ; aucune variante involontaire observée n’est laissée sans décision.

**Preuves.** Motifs d’URL documentés et absence de variantes involontaires.

**Conditions de NA.** Aucune URL publique dans le périmètre.

**Limites.** Une URL lisible n’est pas un facteur suffisant de performance SEO.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/url-structure](https://developers.google.com/search/docs/crawling-indexing/url-structure)

### TS20-A01 — Forme des URL selon la politique fournie

`TSEP@0.3.0-draft.2:TS20-A01`

**Entrées requises**: crawl, configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments explicitement sélectionnés du contrôle TS20 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Méthode.** Lire la capture après et url-shape-config-v1. Vérifier espaces/contrôles, antislash, échappements percent, fragments et casse de chemin selon les choix préalables ; revue humaine de lisibilité.

**Attendus.** La configuration correspond au plan et chaque URL respecte ses axes lexicaux. Une divergence qualifiée échoue. Aucun changement implicite de casse ou de décodage.

**Preuves.** Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : crawl, configuration, intent.

**Hypothèses.** Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminé.** URL/autorité non prise en charge, politique inconnue, capture ou revue manquante : indéterminé.

**Conditions de NA.** Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites.** Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### TS20-A02 — Stabilité temporelle et décisions de variation

`TSEP@0.3.0-draft.2:TS20-A02`

**Entrées requises**: crawl, configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments explicitement sélectionnés du contrôle TS20 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Méthode.** Comparer deux captures ordonnées url-crawl-v1 ayant les mêmes identités ; toute URL changée doit avoir une décision unique avant/après avec motif, dans le plan lié à la revue.

**Attendus.** Les URL sont égales aux deux dates, ou leur variation est explicitement décidée et revue. Un changement observé sans décision échoue.

**Preuves.** Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : crawl, configuration, intent.

**Hypothèses.** Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminé.** Une seule date, dates inversées/égales, identité manquante ou revue absente : indéterminé. La stabilité future reste inconnue.

**Conditions de NA.** Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites.** Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

## TS21 — Les URL découvertes mais non indexées sont investiguées par famille.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: search-console, logs, sitemap, intent.

**Applicabilité.** Familles signalées découvertes ou explorées mais non indexées.

**Méthode.** Segmenter le rapport Pages par gabarit et comparer aux sitemaps et logs.

**Attendus.** Chaque famille retenue possède un diagnostic documenté, une hypothèse testable et une décision ; causalité non démontrée signalée.

**Preuves.** Hypothèse par famille, échantillon d’URL et résultat après correction.

**Conditions de NA.** Rapport daté ne contenant aucune famille concernée, ou Google explicitement exclu.

**Limites.** Le libellé de Search Console décrit un état, pas toujours sa cause.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://support.google.com/webmasters/answer/7440203](https://support.google.com/webmasters/answer/7440203)

### TS21-A01 — Attribution des familles non indexées

`TSEP@0.3.0-draft.3:TS21-A01`

**Entrées requises**: search-console, logs, sitemap, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Familles ou groupes explicitement sélectionnés pour TS21 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Méthode.** Lire les requêtes/réponses Google URL Inspection fournies pour chaque URL retenue, comparer propriété, URL et libellé de famille ; rapprocher le urlset natif et l’export TSV de logs dans leur fenêtre. Exiger la revue de segmentation et d’attribution.

**Attendus.** Les pièces natives sont disponibles et attribuées à la famille choisie ; l’appartenance sitemap concorde avec le plan. Un désaccord de requête, de famille ou de sitemap échoue. Les logs décrivent seulement leur fenêtre et leur client fourni.

**Preuves.** Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : search-console, logs, sitemap, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses.** Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminé.** Pièce manquante, résultat API absent/erroné, libellé non pris en charge, logs non interprétables ou revue absente : indéterminé.

**Conditions de NA.** Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites.** Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

### TS21-A02 — Hypothèse testable et décision sans causalité inventée

`TSEP@0.3.0-draft.3:TS21-A02`

**Entrées requises**: content, intent.

**Automation / Automatisation**: `manual`.

**Applicabilité.** Familles ou groupes explicitement sélectionnés pour TS21 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Méthode.** Lire family-diagnosis-v1 : diagnostic, hypothèse, prédiction, réfutation, mesure, décision, propriétaire et échéance pour la même liste d’URL. Vérifier la distinction entre suivi prévu et résultat observé puis la revue liée.

**Attendus.** Les axes de diagnostic sont renseignés et revus ; causality=unproven et follow_up=planned-not-observed. Une causalité proclamée à partir du libellé ou de la corrélation échoue dans ce profil.

**Preuves.** Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : content, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses.** Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminé.** Hypothèse sans critère de réfutation, famille mal attribuée, suivi prétendu observé hors méthode séparée, jugement manquant : indéterminé.

**Conditions de NA.** Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites.** Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

## TS22 — Chaque variante hreflang pointe vers une URL indexable et canonique.

**Sévérité**: major. **Unité**: locale-cluster.

**Entrées requises**: hreflang, http, html, intent.

**Applicabilité.** Groupes de variantes localisées utilisant hreflang.

**Méthode.** Parser les annotations HTML, HTTP ou sitemap et résoudre chaque URL.

**Attendus.** Chaque cible du groupe est accessible, destinée à l’indexation et cohérente avec sa canonique ; codes langue/région contrôlés.

**Preuves.** Langue/région valide, URL 200, canonique cohérente.

**Conditions de NA.** Aucun groupe hreflang dans le périmètre, inventaire fourni.

**Limites.** hreflang aide au ciblage ; il ne remplace pas un contenu réellement localisé.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

### TS22-A01 — Annotations natives et codes enregistrés

`TSEP@0.3.0-draft.3:TS22-A01`

**Entrées requises**: hreflang, http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Familles ou groupes explicitement sélectionnés pour TS22 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Méthode.** Lire séparément HTML, en-têtes Link et urlset XHTML déclarés ; conserver les accords des deux hypothèses HTML statiques. Vérifier chaque code observé dans le sous-ensemble figé du registre IANA et l’attribution à la destination prévue.

**Attendus.** Les codes observés appartiennent au profil langue/script/région documenté et les destinations concordent. Un code explicitement invalide ou une destination contraire échoue ; x-default qualifie seulement le jeton réservé.

**Preuves.** Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : hreflang, http, html, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses.** Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminé.** Code obsolète, région exceptionnelle hors sous-ensemble, méthode ou page manquante, contexte HTML ambigu, annotation relative ou revue manquante : indéterminé.

**Conditions de NA.** Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites.** Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

### TS22-A02 — Destinations hreflang et signaux d’indexabilité

`TSEP@0.3.0-draft.3:TS22-A02`

**Entrées requises**: hreflang, http, html, robots, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Familles ou groupes explicitement sélectionnés pour TS22 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Méthode.** Pour chaque destination sélectionnée : comparer intention d’indexation, HTTP direct 200, directives HTTP/HTML, canonical explicite vers elle-même et robots.txt du même origin avec le profil Google préalable. Exiger la revue du périmètre source.

**Attendus.** Les signaux qualifiés autorisent la destination prévue et concordent avec elle. Une réponse contraire, un noindex, une canonical divergente ou un refus robots étayé échoue malgré d’autres inconnues.

**Preuves.** Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : hreflang, http, html, robots, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses.** Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminé.** Robots absent/non qualifié, canonical absente, trace partielle, rendu nécessaire ou revue absente : indéterminé. Permission d’indexation n’est pas indexation.

**Conditions de NA.** Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites.** Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

## TS23 — Les annotations hreflang sont réciproques et incluent la page elle-même.

**Sévérité**: major. **Unité**: locale-cluster.

**Entrées requises**: http, hreflang, intent.

**Applicabilité.** Groupe et canaux principaux déclarés avant les captures ; profil borné hreflang-reciprocity-v1.

**Méthode.** Lire les annotations natives HTML ou HTTP Link depuis les originaux, conserver deux hypothèses HTML et les canaux secondaires, comparer chaque code–URL au groupe préalable sans union de canaux.

**Attendus.** Chaque page du groupe conserve dans son canal principal tout le jeu attendu, auto-référence comprise ; aucune contradiction qualifiée entre cibles. Plusieurs codes peuvent partager une URL et les groupes entre domaines sont admis.

**Preuves.** Plan et associations attendues, canaux choisis, requêtes/réponses HTTP originales et empreintes, dates, positions des éléments et fermetures du head, hypothèses, jeux principaux/secondaires, exclusions et inconnues.

**Conditions de NA.** Aucun groupe hreflang dans le périmètre.

**Limites.** Groupe fourni et mode principal déclarés : aucune authenticité de capture, exhaustivité du site, validité linguistique TS22, indexabilité/canonical, pertinence x-default TS24, traduction, rendu JavaScript ou traitement Google. Les sitemaps/DOM pertinents fournis restent hors profil.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

### TS23-A01 — Réciprocité et auto-référence natives dans le groupe préalable.

`TSEP@0.2.0-rc.1:TS23-A01`

**Entrées requises**: http, hreflang, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Groupe et canaux principaux déclarés avant les captures ; profil borné hreflang-reciprocity-v1.

**Méthode.** Lire les annotations natives HTML ou HTTP Link depuis les originaux, conserver deux hypothèses HTML et les canaux secondaires, comparer chaque code–URL au groupe préalable sans union de canaux.

**Attendus.** Pass si toutes les pages sont qualifiées et incluent tout le jeu attendu dans leur canal principal. Fail si un manque qualifié, placement invalide du primaire HTML ou conflit de cible est établi. Sinon inconclusive ; une contradiction indépendante survit aux inconnues.

**Preuves.** Plan et associations attendues, canaux choisis, requêtes/réponses HTTP originales et empreintes, dates, positions des éléments et fermetures du head, hypothèses, jeux principaux/secondaires, exclusions et inconnues.

**Hypothèses.** Plan antérieur, fenêtre maximale24h, HTTP200 demandé=final sans redirection, URL absolues HTTP(S) exactes. Deux hypothèses HTML statiques, aucune exécution de scripts.

**Indéterminé.** Plan/original absent ou ambigu, dates ou canal non qualifiés, source récupérée hors frontière admise, langue/URL hors admission fermée, annotation extérieure non prévue, runtime requis absent.

**Conditions de NA.** Aucune NA automatique ; un plan vide n’établit pas la non-applicabilité.

**Limites.** Groupe fourni et mode principal déclarés : aucune authenticité de capture, exhaustivité du site, validité linguistique TS22, indexabilité/canonical, pertinence x-default TS24, traduction, rendu JavaScript ou traitement Google. Les sitemaps/DOM pertinents fournis restent hors profil.

## TS24 — x-default représente une destination neutre ou la variante par défaut assumée.

**Sévérité**: minor. **Unité**: locale-cluster.

**Entrées requises**: http, hreflang, intent.

**Applicabilité.** Groupe et politique x-default fournis avant les captures ; profil borné xdefault-role-v1.

**Méthode.** Relire les observations natives HTML/HTTP Link, vérifier cible, contexte motivé, disponibilité capturée et revue de rôle fournie liée ; conserver inconnues et contestations.

**Attendus.** Présence et contexte qualifiés, cible conforme à la politique, original200 et revue fournie cohérente. Un défaut indépendant documenté est NC ; aucune approbation ni validité sémantique inférée.

**Preuves.** Politique et contexte préalables, originaux HTTP et empreintes, observations principales/secondaires, revues originales liées, dates et inconnues.

**Conditions de NA.** Aucune NA native ni override manuel ; dossiers manuels historiques séparés, absence optionnelle indéterminée.

**Limites.** Périmètre fourni, aucun public représentatif ou rôle sémantique authentifié ; HTTP200 ne détecte pas une page d’erreur/soft404. Pas de traduction, visite Google, indexation, exhaustivité ou conformité globale.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

### TS24-A01 — Rôle x-default documenté dans le contexte préalable.

`TSEP@0.2.0-rc.1:TS24-A01`

**Entrées requises**: http, hreflang, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Groupe et politique x-default fournis avant les captures ; profil borné xdefault-role-v1.

**Méthode.** Relire les observations natives HTML/HTTP Link, vérifier cible, contexte motivé, disponibilité capturée et revue de rôle fournie liée ; conserver inconnues et contestations.

**Attendus.** Pass exige toutes les surfaces qualifiées, une cible prévue non ambiguë, son original200 et une revue consistent liée. Fail pour absence primaire requise qualifiée, toute cible qualifiée contraire à la destination unique du plan, même parmi plusieurs déclarations,404/410 attribuable, distinction URL contredite ou revue defect unique liée. Sinon inconclusive.

**Preuves.** Politique et contexte préalables, originaux HTTP et empreintes, observations principales/secondaires, revues originales liées, dates et inconnues.

**Hypothèses.** Plan antérieur et contexte unique motivé ; un GET sans redirection par original, fenêtre<=24h, deux hypothèses HTML statiques. Revue fournie, auteur non authentifié.

**Indéterminé.** Plan, contexte, original ou revue absent/non qualifié ; déclarations non qualifiées ou hypothèses divergentes sans contradiction indépendante, revues contestées, statut hors200/404/410, canal pertinent non examiné ou runtime requis absent.

**Conditions de NA.** Aucune NA native ni override manuel ; dossiers manuels historiques séparés, absence optionnelle indéterminée.

**Limites.** Périmètre fourni, aucun public représentatif ou rôle sémantique authentifié ; HTTP200 ne détecte pas une page d’erreur/soft404. Pas de traduction, visite Google, indexation, exhaustivité ou conformité globale.

## TS25 — Le contenu critique existe dans le HTML source ou devient observable après rendu.

**Sévérité**: blocking. **Unité**: page.

**Entrées requises**: http, intent.

**Applicabilité.** Éléments critiques et politiques de stade déclarés avant les captures, profil critical-stage-presence-v1.

**Méthode.** Vérifier les cinq décisions de rôle puis les éléments dans les hypothèses source et états rendus prévus ; conserver originaux, exclusions et revues fournies liées.

**Attendus.** Deux règles pass dans le périmètre fourni : couverture motivée et présence selon les politiques préalables. Tout défaut indépendant qualifié donne NC ; sinon les inconnues donnent NT.

**Preuves.** Plan antérieur, originaux HTTP/DOM, empreintes, conditions, valeurs par élément/stade, revues réellement fournies et dates.

**Conditions de NA.** Aucune NA native ; rôle hors périmètre motivé conservé, jamais équivalent à un contrôle NA.

**Limites.** Périmètre déclaré uniquement, hypothèses statiques sans exécution ; revues et attribution non authentifiées. Ni rendu Google, visibilité CSS déduite, vérité, validité structurée, indexation ou conformité globale.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

### TS25-A01 — Périmètre critique préalable et décisions des cinq rôles.

`TSEP@0.2.0-rc.1:TS25-A01`

**Entrées requises**: intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments critiques et politiques de stade déclarés avant les captures, profil critical-stage-presence-v1.

**Méthode.** Vérifier les cinq décisions de rôle puis les éléments dans les hypothèses source et états rendus prévus ; conserver originaux, exclusions et revues fournies liées.

**Attendus.** Pass exige population motivée, cinq décisions exactes et revue supported liée antérieure. Revue contradiction liée : fail. Revue absente, non liée ou inconnue : inconclusive.

**Preuves.** Plan antérieur, originaux HTTP/DOM, empreintes, conditions, valeurs par élément/stade, revues réellement fournies et dates.

**Hypothèses.** 1–32 éléments,0–16 états préalables, fenêtre<=24h, HTTP<=30s ; cinq rôles explicites. Deux hypothèses HTML doivent concorder ; états requis combinés avec priorité au défaut qualifié. Revue fournie, aucune authentification.

**Indéterminé.** Plan/capture/revue absent ou invalide, rôle non pris en charge, lectures contradictoires, contexte rendu non qualifié, états supplémentaires/doublons, limites dépassées. Un défaut indépendant reste fail. Draft.44 / reader3 : les champs reviewer, assistance et reason des revues TS25 fournies sont limités à8192octets UTF8 bruts chacun, avant strip ou normalisation ; chaque objet revue, champs supplémentaires inclus, à32768octets de JSON compact UTF8. Toute revue fournie est vérifiée à l’admission, même inutilisée. Un dépassement donne un refus technique avant publication, jamais C ou NT public ; les originaux sont conservés sans réécriture. Le diagnostic natif de chaque règle est borné à4MiB de JSON compact UTF8 trié, y compris A01 et les sorties d’erreur. Au dépassement, un diagnostic compact explicitement incomplet conserve un fail indépendant établi, sinon inconclusive ; aucun pass. Le transport refuse ce marqueur et borne aussi à4MiB par cible la somme des artefacts TS25 réellement sérialisés (JSON UTF8 indent2, saut de ligne final), pour les règles demandées. Les maxima individuels ne garantissent pas que toutes leurs combinaisons respectent les bornes cumulées. Aucun changement des autres contrôles ni du validateur partagé.

**Conditions de NA.** Aucune NA native ; rôle hors périmètre motivé conservé, jamais équivalent à un contrôle NA.

**Limites.** Périmètre déclaré uniquement, hypothèses statiques sans exécution ; revues et attribution non authentifiées. Ni rendu Google, visibilité CSS déduite, vérité, validité structurée, indexation ou conformité globale.

### TS25-A02 — Présence critique selon la politique source/rendu de chaque élément.

`TSEP@0.2.0-rc.1:TS25-A02`

**Entrées requises**: http, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments critiques et politiques de stade déclarés avant les captures, profil critical-stage-presence-v1.

**Méthode.** Vérifier les cinq décisions de rôle puis les éléments dans les hypothèses source et états rendus prévus ; conserver originaux, exclusions et revues fournies liées.

**Attendus.** Pass exige tous les éléments présents selon leur politique et couverture des états qualifiée. Absence indépendante qualifiée : fail malgré une autre inconnue. Sinon inconclusive.

**Preuves.** Plan antérieur, originaux HTTP/DOM, empreintes, conditions, valeurs par élément/stade, revues réellement fournies et dates.

**Hypothèses.** 1–32 éléments,0–16 états préalables, fenêtre<=24h, HTTP<=30s ; cinq rôles explicites. Deux hypothèses HTML doivent concorder ; états requis combinés avec priorité au défaut qualifié. Revue fournie, aucune authentification.

**Indéterminé.** Plan/capture/revue absent ou invalide, rôle non pris en charge, lectures contradictoires, contexte rendu non qualifié, états supplémentaires/doublons, limites dépassées. Un défaut indépendant reste fail. Un conteneur render non objet reste inconnu ; il ne supprime pas une absence source indépendante requise. Draft.44 / reader3 : les champs reviewer, assistance et reason des revues TS25 fournies sont limités à8192octets UTF8 bruts chacun, avant strip ou normalisation ; chaque objet revue, champs supplémentaires inclus, à32768octets de JSON compact UTF8. Toute revue fournie est vérifiée à l’admission, même inutilisée. Un dépassement donne un refus technique avant publication, jamais C ou NT public ; les originaux sont conservés sans réécriture. Le diagnostic natif de chaque règle est borné à4MiB de JSON compact UTF8 trié, y compris A01 et les sorties d’erreur. Au dépassement, un diagnostic compact explicitement incomplet conserve un fail indépendant établi, sinon inconclusive ; aucun pass. Le transport refuse ce marqueur et borne aussi à4MiB par cible la somme des artefacts TS25 réellement sérialisés (JSON UTF8 indent2, saut de ligne final), pour les règles demandées. Les maxima individuels ne garantissent pas que toutes leurs combinaisons respectent les bornes cumulées. Aucun changement des autres contrôles ni du validateur partagé.

**Conditions de NA.** Aucune NA native ; rôle hors périmètre motivé conservé, jamais équivalent à un contrôle NA.

**Limites.** Périmètre déclaré uniquement, hypothèses statiques sans exécution ; revues et attribution non authentifiées. Ni rendu Google, visibilité CSS déduite, vérité, validité structurée, indexation ou conformité globale.

## TS26 — Les ressources nécessaires au rendu ne sont pas bloquées ni en erreur.

**Sévérité**: major. **Unité**: page.

**Entrées requises**: http, render, robots, intent.

**Applicabilité.** Ressources nécessaires au rendu des gabarits testés.

**Méthode.** Inspecter réseau, robots, CSP et erreurs console sur les gabarits prioritaires.

**Attendus.** Aucune ressource critique testée n’est empêchée par erreur réseau, politique robots ou CSP ; console et réseau sont conservés.

**Preuves.** Ressources critiques accessibles et absence d’erreur qui retire le contenu.

**Conditions de NA.** Aucune ressource de rendu dépendante, inventaire fourni.

**Limites.** Une console sans erreur ne prouve pas l’indexation.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

### TS26-A01 — Accès des ressources et politiques natives

`TSEP@0.3.0-draft.4:TS26-A01`

**Entrées requises**: http, robots, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS26, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Sur chaque ressource critique sélectionnée, comparer HTTP direct200, robots du même origin et intersection des CSP HTTP du document HTTPS. Relever la source complète pour exclure une CSP meta non qualifiée.

**Attendus.** Une erreur HTTP, un refus robots ou un refus CSP qualifié échoue indépendamment des autres lacunes.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, robots, html, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** Inventaire absent, robots non fourni, directive CSP non prise en charge, nonce, meta CSP, source ambiguë ou revue absente : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

### TS26-A02 — Trafic et console attribués au rendu

`TSEP@0.3.0-draft.4:TS26-A02`

**Entrées requises**: render, http, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS26, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Lire un export HAR borné fourni, relier la réponse du document aux octets HTTP, puis vérifier chaque ressource critique. Conserver la console datée liée au HAR et la revue de criticité.

**Attendus.** Les ressources sélectionnées ont une réponse2xx sans erreur réseau fournie. Une erreur console sans classification qualifiée reste NT ; un échec réseau natif reste NC.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : render, http, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** HAR incomplet, corps absent, contexte/session non attribué, console absente ou erreur non qualifiée : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

## TS27 — Les états et routes SPA produisent des URL partageables et des réponses serveur cohérentes.

**Sévérité**: major. **Unité**: route-set.

**Entrées requises**: http, render, intent.

**Applicabilité.** Routes applicatives ou états SPA destinés à l’indexation.

**Méthode.** Ouvrir directement les routes, tester actualisation, historique, canonical et statut HTTP.

**Attendus.** Ouverture directe, actualisation et historique conservent URL, contenu, statut et signaux attendus pour chaque route retenue.

**Preuves.** Chaque vue indexable possède URL, 200, contenu et signaux propres.

**Conditions de NA.** Aucune route applicative ou SPA concernée.

**Limites.** Le choix SSR, CSR ou SSG n’est pas en soi une garantie SEO.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/javascript/fix-search-javascript](https://developers.google.com/search/docs/crawling-indexing/javascript/fix-search-javascript)

### TS27-A01 — Routes et historique attribués

`TSEP@0.3.0-draft.4:TS27-A01`

**Entrées requises**: http, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS27, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Vérifier quatre états fournis dans l’ordre direct, actualisation, retour, avance : session, séquence, date, URL, liaison à la réponse serveur et statut.

**Attendus.** Chaque état conserve l’URL de route et sa source200 prévue. Une URL ou un statut contraire qualifié échoue.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, render, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** État, action, liaison, session ou ordre absent/ambigu ; surface frame/shadow non collectée : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

### TS27-A02 — Contenu et canonical par état SPA

`TSEP@0.3.0-draft.4:TS27-A02`

**Entrées requises**: http, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS27, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Dans les mêmes états qualifiés, comparer les identifiants littéraux, textes essentiels et destinations de liens au plan, puis une canonical explicite dans head. Exiger la revue de fonctionnement.

**Attendus.** Les états conservent contenus et signaux propres. Absence sur surface complète, contenu divergent ou canonical contraire échoue.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, render, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** État partiel, contexte masqué, ID ambigu, hypothèses HTML divergentes ou revue absente : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

## TS28 — Le document expose une structure HTML compréhensible sans dépendre de son apparence.

**Sévérité**: major. **Unité**: page.

**Entrées requises**: html, render, intent.

**Applicabilité.** Documents HTML du périmètre.

**Méthode.** Inspecter titre, langue, main, niveaux de titres, liens et libellés sur un échantillon.

**Attendus.** Titre, langue, structure, navigation et libellés correspondent au contenu et à son usage ; revue humaine consignée, sans certification d’accessibilité.

**Preuves.** Structure logique, un sujet principal identifiable, composants accessibles.

**Conditions de NA.** Aucun document HTML concerné.

**Limites.** La validité syntaxique seule ne prouve ni qualité ni pertinence.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://html.spec.whatwg.org/](https://html.spec.whatwg.org/)

### TS28-A01 — Structure native et structure DOM fournie

`TSEP@0.3.0-draft.4:TS28-A01`

**Entrées requises**: html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS28, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Comparer dans la source et la sérialisation fournie : titre, langue, main déclaré, liste ordonnée des titres, liens et libellés. Le nombre de H1 est celui du plan.

**Attendus.** Les structures correspondent au plan préalable ; divergences structurelles qualifiées échouent.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, render, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** Source/DOM absent, langue non déclarée, arbre ambigu ou contexte visuel non qualifié : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

### TS28-A02 — Revue du sens et de la navigation

`TSEP@0.3.0-draft.4:TS28-A02`

**Entrées requises**: html, render, intent.

**Automation / Automatisation**: `manual`.

**Applicabilité.** Population finie préalable de TS28, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Reprendre les faits structurels attribués et exiger une revue distincte liée : adéquation du titre et de la langue, hiérarchie, sujet principal, navigation et libellés dans l’usage déclaré.

**Attendus.** Les faits sont qualifiés et le jugement motivé soutient le sens et l’usage ; contradiction étayée échoue.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, render, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** Le parseur seul, une revue sans liaison ou des originaux insuffisants ne suffisent pas : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

## TS29 — Les contenus essentiels restent disponibles lorsque scripts ou styles échouent.

**Sévérité**: major. **Unité**: page.

**Entrées requises**: html, render, intent.

**Applicabilité.** Parcours dont le contenu et la navigation essentiels sont définis.

**Méthode.** Tester HTML source, désactivation JavaScript et mode réseau dégradé.

**Attendus.** Les scénarios scripts bloqués et styles dégradés conservent les fonctions déclarées ou un repli effectivement testé.

**Preuves.** Information et navigation principales toujours accessibles ou solution de repli documentée.

**Conditions de NA.** Aucun parcours web concerné, justification fournie.

**Limites.** La dégradation acceptable dépend de la fonction du composant.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

### TS29-A01 — Scénario scripts bloqués et repli testé

`TSEP@0.3.0-draft.4:TS29-A01`

**Entrées requises**: html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS29, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Lire la source et un état fourni explicitement scripts-blocked ; comparer chaque contenu/lien essentiel, ou le repli prédéclaré dans ce même état. Exiger la revue des actions et du fonctionnement.

**Attendus.** Tous les attendus principaux ou tous ceux du repli testé sont étayés. Un échec principal et du repli qualifiés échoue ; aucune fonction n’est déduite du texte seul.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, render, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** Condition normale, capture partielle, repli seulement décrit, contexte masqué ou revue manquante : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

### TS29-A02 — Scénario styles dégradés et repli testé

`TSEP@0.3.0-draft.4:TS29-A02`

**Entrées requises**: html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS29, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Appliquer le même examen dans un état explicitement styles-degraded, avec observations d’actions et revue liée. Ne pas assimiler la désactivation des scripts à ce scénario.

**Attendus.** Les fonctions essentielles ou le repli testé restent étayés dans ce scénario distinct.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, render, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** Absence de scénario styles dégradés, preuve de repli ou jugement attribué : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

## TS30 — Les métadonnées essentielles sont uniques, visibles et cohérentes avec la page.

**Sévérité**: major. **Unité**: page.

**Entrées requises**: html, content, intent.

**Applicabilité.** Pages dont les métadonnées éditoriales sont évaluées.

**Méthode.** Comparer title, description, H1, Open Graph et contenu principal par gabarit.

**Attendus.** Les métadonnées présentes décrivent le contenu sans contradiction ; unicité et duplication évaluées dans le corpus déclaré, avec revue humaine.

**Preuves.** Sujet et promesse cohérents sans duplication mécanique.

**Conditions de NA.** Aucun document comportant de métadonnées éditoriales pertinentes.

**Limites.** Google peut réécrire le title ou l’extrait dans ses résultats.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/appearance/title-link](https://developers.google.com/search/docs/appearance/title-link)

### TS30-A01 — Métadonnées et doublons du corpus déclaré

`TSEP@0.3.0-draft.5:TS30-A01`

**Entrées requises**: html, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS30, profil render-transport-v1 ; voir docs/render-transport-evidence.md. Amendement: docs/render-transport-prerequisites-v2.md.

**Méthode.** Lire title, description, H1, og:title, og:description natifs par page. Comparer aux valeurs prévues puis les doublons entre pages sélectionnées ; exiger une décision préalable pour chaque doublon intentionnel. Qualifier séparément les drapeaux du H1 et de ses textes descendants ; préserver les contradictions natives des autres champs.

**Attendus.** Valeurs et multiplicité concordent ; chaque doublon observé possède une décision motivée unique. Le corpus ne dépasse pas les pages fournies.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, content, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** Source absente, politique de champ omise, parse ambigu ou revue manquante : NT. null autorise seulement un champ facultatif explicitement absent. H1 ou texte descendant masqué/non qualifié : NT, sans fabriquer une absence.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

### TS30-A02 — Cohérence éditoriale et contenu principal

`TSEP@0.3.0-draft.5:TS30-A02`

**Entrées requises**: html, content, intent.

**Automation / Automatisation**: `manual`.

**Applicabilité.** Population finie préalable de TS30, profil render-transport-v1 ; voir docs/render-transport-evidence.md. Amendement: docs/render-transport-prerequisites-v2.md.

**Méthode.** Rapprocher les métadonnées natives et le contenu principal identifié ; exiger une revue distincte de la promesse, du sens et de la visibilité pertinente. Qualifier séparément les drapeaux du H1 et de ses textes descendants ; préserver les contradictions natives des autres champs.

**Attendus.** Les faits concordent avec le plan et la revue éditoriale liée les soutient ; une contradiction native ou humaine qualifiée échoue.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : html, content, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** Source/rendu nécessaire non qualifié, contenu masqué, sens sans revue ou jugement non lié : NT. H1 ou texte descendant masqué/non qualifié : NT, sans fabriquer une absence.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

## TS31 — Le JSON-LD décrit des entités visibles et appropriées au contenu.

**Sévérité**: major. **Unité**: page.

**Entrées requises**: structured-data, content, intent.

**Applicabilité.** Documents publiant des données structurées.

**Méthode.** Comparer chaque propriété importante au contenu visible et aux recommandations du type.

**Attendus.** Syntaxe et propriétés examinées sont cohérentes avec les faits visibles et le type choisi ; aucune donnée inventée observée.

**Preuves.** Graphe valide, cohérent, sans entité ni note inventée.

**Conditions de NA.** Aucune donnée structurée publiée dans le périmètre.

**Limites.** Un balisage valide ne garantit pas un résultat enrichi ni un meilleur classement.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/appearance/structured-data/sd-policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)

### TS31-A01 — Périmètre et hypothèses préalables revus.

`TSEP@0.2.0-rc.1:TS31-A01`

**Entrées requises**: structured-data, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Page sélectionnée avec JSON-LD ; profil source et états DOM prévus.

**Méthode.** Qualifier le plan, ses références datées et la revue préalable liée du périmètre, de la base source et des recommandations.

**Attendus.** Trois jugements supported ; contradiction liée fail, revue manquante ou inconnue inconclusive.

**Preuves.** HTTP natif, arbres attribués, contextes et références fournis, graphes recalculés et revues liées ; contrat jsonld-visible-content-v1.

**Hypothèses.** Périmètre, bases, dates, contenu visible et jugements fournis ; empreintes sans authentification.

**Indéterminé.** Manque, limite, contexte/runtime absent, lecture ambiguë, graphe vide, notice ou revue inconnue ; contradictions indépendantes conservées.

**Conditions de NA.** Aucune exemption atomique ; absence dans un profil limité ne vaut pas NA.

**Limites.** JSON-LD et revue documentaire de la page sélectionnée ; ni vocabulaire Schema.org, vérité/visibilité authentifiée, résultat enrichi, indexation ou classement.

### TS31-A02 — Lecture attribuée du JSON-LD source et rendu.

`TSEP@0.2.0-rc.1:TS31-A02`

**Entrées requises**: structured-data, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Page sélectionnée avec JSON-LD ; profil source et états DOM prévus.

**Méthode.** Recalculer les scripts exacts sous les deux hypothèses source et tous les états DOM prévus, avec contextes fournis.

**Attendus.** Lectures complètes et au moins un graphe non vide sans notice ; JSON invalide attribué fail, autres limites inconclusive.

**Preuves.** HTTP natif, arbres attribués, contextes et références fournis, graphes recalculés et revues liées ; contrat jsonld-visible-content-v1.

**Hypothèses.** Périmètre, bases, dates, contenu visible et jugements fournis ; empreintes sans authentification.

**Indéterminé.** Manque, limite, contexte/runtime absent, lecture ambiguë, graphe vide, notice ou revue inconnue ; contradictions indépendantes conservées.

**Conditions de NA.** Aucune exemption atomique ; absence dans un profil limité ne vaut pas NA.

**Limites.** JSON-LD et revue documentaire de la page sélectionnée ; ni vocabulaire Schema.org, vérité/visibilité authentifiée, résultat enrichi, indexation ou classement.

### TS31-A03 — Cohérence du contenu et des types revue par entité.

`TSEP@0.2.0-rc.1:TS31-A03`

**Entrées requises**: structured-data, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Page sélectionnée avec JSON-LD ; profil source et états DOM prévus.

**Méthode.** Lier le contenu fourni et chaque nœud aplati aux revues complètes couvrant visibilité, type, toutes les propriétés et absence de fabrication.

**Attendus.** Population exacte et qualifications supported ; contradiction fournie liée fail, manque ou inconnue inconclusive.

**Preuves.** HTTP natif, arbres attribués, contextes et références fournis, graphes recalculés et revues liées ; contrat jsonld-visible-content-v1.

**Hypothèses.** Périmètre, bases, dates, contenu visible et jugements fournis ; empreintes sans authentification.

**Indéterminé.** Manque, limite, contexte/runtime absent, lecture ambiguë, graphe vide, notice ou revue inconnue ; contradictions indépendantes conservées.

**Conditions de NA.** Aucune exemption atomique ; absence dans un profil limité ne vaut pas NA.

**Limites.** JSON-LD et revue documentaire de la page sélectionnée ; ni vocabulaire Schema.org, vérité/visibilité authentifiée, résultat enrichi, indexation ou classement.

## TS32 — Les identifiants @id relient les mêmes entités sans créer de doublons.

**Sévérité**: minor. **Unité**: graph.

**Entrées requises**: structured-data, intent.

**Applicabilité.** Graphes utilisant des identifiants d’entité.

**Méthode.** Construire le graphe, repérer les nœuds sans nom, les identifiants variables et les doublons.

**Attendus.** Les mêmes entités conservent leurs identifiants dans le corpus ; références résolubles dans le graphe et doublons qualifiés, sans imposer tous les types cités dans la grille historique.

**Preuves.** Graphe archivé, liste des entités et identifiants présents, références et doublons qualifiés.

**Conditions de NA.** Aucun graphe avec identifiants concerné.

**Limites.** Schema.org décrit un vocabulaire ; l’interprétation dépend du consommateur.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://schema.org/docs/datamodel.html](https://schema.org/docs/datamodel.html)

### TS32-A01 — Registre et corpus préalables qualifiés.

`TSEP@0.2.0-rc.1:TS32-A01`

**Entrées requises**: structured-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Corpus déclaré de 2–16 exports JSON-LD utilisant des identifiants.

**Méthode.** Vérifier les entités distinctes, le plan et la revue préalable liée des populations/correspondances/références.

**Attendus.** Registre sans collision et trois qualifications supported ; collision distincte fail même si revue absente.

**Preuves.** Registre préalable, exports natifs, contextes locaux, graphes recalculés et revues liées ; contrat jsonld-identity-corpus-v1.

**Hypothèses.** Origine, complétude, bases, dates et correspondances déclarées puis revues ; non authentifiées.

**Indéterminé.** Pièce, revue, runtime ou contexte manquant ; graphe vide/nommé, notice, référence ou identifiant non qualifiés. Contradictions indépendantes conservées.

**Conditions de NA.** Pas de NA dans ce profil borné.

**Limites.** Cohérence du corpus fourni, sans stabilité temporelle, identité réelle, collecte de pages, fusion inter-documents ni garantie Google.

### TS32-A02 — Identifiants requis et références du corpus.

`TSEP@0.2.0-rc.1:TS32-A02`

**Entrées requises**: structured-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Corpus déclaré de 2–16 exports JSON-LD utilisant des identifiants.

**Méthode.** Recalculer indépendamment les exports natifs et comparer les IRI définies au registre ; inventorier les références et leur portée.

**Attendus.** IRI requises définies et périmètre/références qualifiés ; absence requise dans graphe complet non vide fail, manque ou ambiguïté inconclusive.

**Preuves.** Registre préalable, exports natifs, contextes locaux, graphes recalculés et revues liées ; contrat jsonld-identity-corpus-v1.

**Hypothèses.** Origine, complétude, bases, dates et correspondances déclarées puis revues ; non authentifiées.

**Indéterminé.** Pièce, revue, runtime ou contexte manquant ; graphe vide/nommé, notice, référence ou identifiant non qualifiés. Contradictions indépendantes conservées.

**Conditions de NA.** Pas de NA dans ce profil borné.

**Limites.** Cohérence du corpus fourni, sans stabilité temporelle, identité réelle, collecte de pages, fusion inter-documents ni garantie Google.

### TS32-A03 — Correspondances et doublons revus sur pièces.

`TSEP@0.2.0-rc.1:TS32-A03`

**Entrées requises**: structured-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Corpus déclaré de 2–16 exports JSON-LD utilisant des identifiants.

**Méthode.** Lier chaque export et nœud recalculé aux revues des correspondances, répétitions/doublons et sens des références.

**Attendus.** Couverture exacte et qualifications supported ; contradiction liée fail, revue incomplète ou inconnue inconclusive.

**Preuves.** Registre préalable, exports natifs, contextes locaux, graphes recalculés et revues liées ; contrat jsonld-identity-corpus-v1.

**Hypothèses.** Origine, complétude, bases, dates et correspondances déclarées puis revues ; non authentifiées.

**Indéterminé.** Pièce, revue, runtime ou contexte manquant ; graphe vide/nommé, notice, référence ou identifiant non qualifiés. Contradictions indépendantes conservées.

**Conditions de NA.** Pas de NA dans ce profil borné.

**Limites.** Cohérence du corpus fourni, sans stabilité temporelle, identité réelle, collecte de pages, fusion inter-documents ni garantie Google.

## TS33 — Les erreurs, avertissements et usages non pris en charge sont distingués.

**Sévérité**: minor. **Unité**: page.

**Entrées requises**: structured-data, validator-output, intent.

**Applicabilité.** Page sélectionnée avec captures JSON-LD HTTP/DOM liées et résultat natif Google indexé séparé.

**Méthode.** Qualifier le plan ; recalculer syntaxe et noms Schema.org des captures ; classer séparément les messages natifs de la version indexée et leurs décisions.

**Attendus.** Les trois règles passent sur le périmètre déclaré : plan qualifié, syntaxe et noms attribués, messages indexés sans erreur bloquante avec revue exacte. La correspondance entre instantanés reste non établie.

**Preuves.** Rapport sans erreur bloquante et avertissements qualifiés.

**Conditions de NA.** Pas de NA dans ce profil ; absence de balisage ou de preuve reste NT.

**Limites.** Noms et rôles de vocabulaire seulement ; pas de validité sémantique complète, correspondance entre instantanés, éligibilité actuelle ni affichage déduit. Origines et dates fournies, non authentifiées.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)

### TS33-A01 — Périmètre, fonctions et couches préalables qualifiés.

`TSEP@0.2.0-rc.1:TS33-A01`

**Entrées requises**: structured-data, validator-output, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Page sélectionnée, captures HTTP/DOM JSON-LD liées et instantané indexé APIv1 séparé.

**Méthode.** Vérifier le plan préalable, les documents datés des fonctions et la revue liée scope/support/separation.

**Attendus.** Trois qualifications supported ; contradiction motivée fail, absence ou inconnue inconclusive.

**Preuves.** Plan, captures natives, vocabulaire30.1 épinglé, sorties API originales et revues liées ; contrat jsonld-validation-layers-v1.

**Hypothèses.** Origine, dates et complétude fournies/revues, non authentifiées ; version serveur Google non exposée.

**Indéterminé.** Preuve/revue/runtime absent, couche non attribuée, format/criticité inconnu ou fonction non détectée ; erreurs indépendantes conservées.

**Conditions de NA.** Pas de NA dans ce profil.

**Limites.** Noms Schema.org seulement ; instantanés distincts, aucun test live, éligibilité actuelle, affichage ou indexation déduits.

### TS33-A02 — Syntaxe et noms de vocabulaire sur les captures liées.

`TSEP@0.2.0-rc.1:TS33-A02`

**Entrées requises**: structured-data, validator-output, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Page sélectionnée, captures HTTP/DOM JSON-LD liées et instantané indexé APIv1 séparé.

**Méthode.** Recalculer source/DOM avec les lecteurs TS31 ; comparer classes/propriétés à Schema.org30.1 complet, espaces HTTP/HTTPS équivalents.

**Attendus.** Graphes typés attribués sans erreur de syntaxe ni terme absent/rôle contradictoire ; inconnues restent distinctes.

**Preuves.** Plan, captures natives, vocabulaire30.1 épinglé, sorties API originales et revues liées ; contrat jsonld-validation-layers-v1.

**Hypothèses.** Origine, dates et complétude fournies/revues, non authentifiées ; version serveur Google non exposée.

**Indéterminé.** Preuve/revue/runtime absent, couche non attribuée, format/criticité inconnu ou fonction non détectée ; erreurs indépendantes conservées.

**Conditions de NA.** Pas de NA dans ce profil.

**Limites.** Noms Schema.org seulement ; instantanés distincts, aucun test live, éligibilité actuelle, affichage ou indexation déduits.

### TS33-A03 — Messages natifs Google et décisions conservés sans rétrogradation.

`TSEP@0.2.0-rc.1:TS33-A03`

**Entrées requises**: structured-data, validator-output, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Page sélectionnée, captures HTTP/DOM JSON-LD liées et instantané indexé APIv1 séparé.

**Méthode.** Lire tous les messages APIv1, sévérités et fonctions ; lier une revue exacte à la réponse indexée, séparée des captures actuelles.

**Attendus.** Aucun ERROR/FAIL ; couverture et qualifications exactes. Erreur, omission ou rétrogradation fail même documentée ; panne technique inconclusive.

**Preuves.** Plan, captures natives, vocabulaire30.1 épinglé, sorties API originales et revues liées ; contrat jsonld-validation-layers-v1.

**Hypothèses.** Origine, dates et complétude fournies/revues, non authentifiées ; version serveur Google non exposée.

**Indéterminé.** Preuve/revue/runtime absent, couche non attribuée, format/criticité inconnu ou fonction non détectée ; erreurs indépendantes conservées.

**Conditions de NA.** Pas de NA dans ce profil.

**Limites.** Noms Schema.org seulement ; instantanés distincts, aucun test live, éligibilité actuelle, affichage ou indexation déduits.

## TS34 — Les Core Web Vitals terrain sont documentés et classés au 75e percentile.

**Sévérité**: major. **Unité**: field-cohort.

**Entrées requises**: field-data, intent.

**Applicabilité.** Cohortes disposant de données terrain pertinentes.

**Méthode.** Utiliser une source terrain identifiée : CrUX, Search Console ou RUM. Consigner période, appareil, granularité et population ; ne pas fusionner URL et origine.

**Attendus.** Source, période, granularité, appareil et p75 de LCP/INP/CLS sont consignés et classés selon les seuils cités ; les mauvaises valeurs restent visibles et motivent une décision.

**Preuves.** LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 au 75e percentile pour l’état Bon.

**Conditions de NA.** Parcours explicitement hors périmètre CWV ; absence de données seule signifie NT.

**Limites.** L’absence de données CrUX ne signifie pas que la page est rapide.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://web.dev/articles/defining-core-web-vitals-thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds)

### TS34-A01 — Cohorte terrain attribuable

`TSEP@0.2.0-rc.1:TS34-A01`

**Entrées requises**: field-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Périmètre de performance déclaré pour ce contrôle et profil de lecture qualifié.

**Méthode.** Identifier source, requête et clé retournée, URL/origine, appareil, période et population selon performance-evidence-v1. Aucun repli de portée implicite.

**Attendus.** La cohorte correspond au plan et conserve ses dates et sa provenance. Une substitution explicite laboratoire/terrain échoue ; une cohorte différente ou ancienne reste indéterminée.

**Preuves.** Originaux JSON conservés avec source, date, empreinte ; plan et revue fournie quand exigée, diagnostics et limites selon docs/performance-evidence.md.

**Hypothèses.** Les données et revues fournies ne sont pas authentifiées. Le plan précède l’évaluation et les exécutions laboratoire ; une cohorte historique n’est pas un préenregistrement.

**Indéterminé.** Source, plan, dates ou mesures insuffisants ; format/profil non qualifié, incohérence de portée, borne dépassée ou revue manquante selon le contrat. Aucune absence ne devient C ou NA.

**Conditions de NA.** Aucune exemption atomique automatique ; la non-applicabilité du contrôle exige sa preuve propre.

**Limites.** C qualifie la documentation, pas de bonnes performances. Aucun affichage, classement, cause démontrée, revue humaine automatique ou conformité globale. Rejeu sans nouvelle mesure.

### TS34-A02 — Mesures p75 et classes conservées

`TSEP@0.2.0-rc.1:TS34-A02`

**Entrées requises**: field-data, intent.

**Automation / Automatisation**: `automatic`.

**Applicabilité.** Périmètre de performance déclaré pour ce contrôle et profil de lecture qualifié.

**Méthode.** Lire LCP, INP et CLS p75 dans les unités natives ; comparer exactement aux seuils cités, sans renommer FID ou TBT. Conserver les valeurs mauvaises et les inconnues.

**Attendus.** Les trois mesures sont classées correctement. Une classification liée contraire à un p75 est fail ; une performance mauvaise correctement documentée donne pass.

**Preuves.** Originaux JSON conservés avec source, date, empreinte ; plan et revue fournie quand exigée, diagnostics et limites selon docs/performance-evidence.md.

**Hypothèses.** Les données et revues fournies ne sont pas authentifiées. Le plan précède l’évaluation et les exécutions laboratoire ; une cohorte historique n’est pas un préenregistrement.

**Indéterminé.** Source, plan, dates ou mesures insuffisants ; format/profil non qualifié, incohérence de portée, borne dépassée ou revue manquante selon le contrat. Aucune absence ne devient C ou NA.

**Conditions de NA.** Aucune exemption atomique automatique ; la non-applicabilité du contrôle exige sa preuve propre.

**Limites.** C qualifie la documentation, pas de bonnes performances. Aucun affichage, classement, cause démontrée, revue humaine automatique ou conformité globale. Rejeu sans nouvelle mesure.

### TS34-A03 — Décision motivée liée aux mesures

`TSEP@0.2.0-rc.1:TS34-A03`

**Entrées requises**: field-data, intent.

**Automation / Automatisation**: `manual`.

**Applicabilité.** Périmètre de performance déclaré pour ce contrôle et profil de lecture qualifié.

**Méthode.** Conserver la revue fournie, auteur, provenance, date, empreinte et décision pour chacune des trois métriques ; vérifier la liaison sans fabriquer un jugement.

**Attendus.** Chaque métrique garde sa classe, un motif et une action. Une classe contradictoire échoue. Revue absente/incomplète/non liée : indéterminé.

**Preuves.** Originaux JSON conservés avec source, date, empreinte ; plan et revue fournie quand exigée, diagnostics et limites selon docs/performance-evidence.md.

**Hypothèses.** Les données et revues fournies ne sont pas authentifiées. Le plan précède l’évaluation et les exécutions laboratoire ; une cohorte historique n’est pas un préenregistrement.

**Indéterminé.** Source, plan, dates ou mesures insuffisants ; format/profil non qualifié, incohérence de portée, borne dépassée ou revue manquante selon le contrat. Aucune absence ne devient C ou NA.

**Conditions de NA.** Aucune exemption atomique automatique ; la non-applicabilité du contrôle exige sa preuve propre.

**Limites.** C qualifie la documentation, pas de bonnes performances. Aucun affichage, classement, cause démontrée, revue humaine automatique ou conformité globale. Rejeu sans nouvelle mesure.

## TS35 — Les tests de laboratoire servent au diagnostic, pas à simuler le terrain.

**Sévérité**: minor. **Unité**: page.

**Entrées requises**: lab-data, intent.

**Applicabilité.** Diagnostics de performance en laboratoire.

**Méthode.** Conserver URL, appareil, profil réseau, version de l’outil et mesures détaillées.

**Attendus.** URL, outil/version, appareil, réseau et mesures sont conservés ; les conclusions restent limitées au laboratoire et reliées à une hypothèse.

**Preuves.** Rapport Lighthouse/WebPageTest reproductible et relié à une hypothèse de correction.

**Conditions de NA.** Aucun diagnostic laboratoire prévu dans ce périmètre.

**Limites.** Un score Lighthouse de 100 n’est ni une garantie de CWV terrain ni de classement.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://web.dev/articles/lab-and-field-data-differences](https://web.dev/articles/lab-and-field-data-differences)

### TS35-A01 — Contexte et mesures de laboratoire reproductibles

`TSEP@0.2.0-rc.1:TS35-A01`

**Entrées requises**: lab-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Périmètre de performance déclaré pour ce contrôle et profil de lecture qualifié.

**Méthode.** Conserver une série prévue de 2 à 10 rapports Lighthouse distincts, dates, URL, outil/version, client, appareil, bridage, mesures natives et dispersion.

**Attendus.** La série respecte le contexte et le nombre prévus. URL contraire au plan : fail ; autre contexte, mesure manquante ou erreur runtime : indéterminé.

**Preuves.** Originaux JSON conservés avec source, date, empreinte ; plan et revue fournie quand exigée, diagnostics et limites selon docs/performance-evidence.md.

**Hypothèses.** Les données et revues fournies ne sont pas authentifiées. Le plan précède l’évaluation et les exécutions laboratoire ; une cohorte historique n’est pas un préenregistrement.

**Indéterminé.** Source, plan, dates ou mesures insuffisants ; format/profil non qualifié, incohérence de portée, borne dépassée ou revue manquante selon le contrat. Aucune absence ne devient C ou NA.

**Conditions de NA.** Aucune exemption atomique automatique ; la non-applicabilité du contrôle exige sa preuve propre.

**Limites.** C qualifie la documentation, pas de bonnes performances. Aucun affichage, classement, cause démontrée, revue humaine automatique ou conformité globale. Rejeu sans nouvelle mesure.

### TS35-A02 — Hypothèse de diagnostic et prochaine vérification

`TSEP@0.2.0-rc.1:TS35-A02`

**Entrées requises**: lab-data, intent.

**Automation / Automatisation**: `manual`.

**Applicabilité.** Périmètre de performance déclaré pour ce contrôle et profil de lecture qualifié.

**Méthode.** Relier une revue fournie aux rapports ordonnés, aux métriques, à une hypothèse et à une prochaine mesure. Séparer laboratoire, INP et terrain.

**Attendus.** La revue liée expose hypothèse, métriques et action sans assimilation au terrain. Une assimilation explicite laboratoire/CWV ou TBT/INP échoue ; revue absente : indéterminé.

**Preuves.** Originaux JSON conservés avec source, date, empreinte ; plan et revue fournie quand exigée, diagnostics et limites selon docs/performance-evidence.md.

**Hypothèses.** Les données et revues fournies ne sont pas authentifiées. Le plan précède l’évaluation et les exécutions laboratoire ; une cohorte historique n’est pas un préenregistrement.

**Indéterminé.** Source, plan, dates ou mesures insuffisants ; format/profil non qualifié, incohérence de portée, borne dépassée ou revue manquante selon le contrat. Aucune absence ne devient C ou NA.

**Conditions de NA.** Aucune exemption atomique automatique ; la non-applicabilité du contrôle exige sa preuve propre.

**Limites.** C qualifie la documentation, pas de bonnes performances. Aucun affichage, classement, cause démontrée, revue humaine automatique ou conformité globale. Rejeu sans nouvelle mesure.

## TS36 — Le suivi relie Search Console, logs et déploiements à des dates de décision.

**Sévérité**: major. **Unité**: release.

**Entrées requises**: logs, search-console, change-history, intent.

**Applicabilité.** Changements dont le suivi crawl/indexation est évalué.

**Méthode.** Créer une baseline avant changement puis vérifier J+1, J+7 et J+30 selon le risque.

**Attendus.** Baseline, déploiement et observations de suivi prévues par le risque sont datés ; anomalies et décisions reliées, sans causalité automatique.

**Preuves.** Journal des déploiements, anomalies crawl/indexation et décisions signées.

**Conditions de NA.** Aucun changement soumis au suivi dans la période déclarée.

**Limites.** Une corrélation temporelle ne suffit pas à attribuer une variation de trafic.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/crawling/docs/crawl-budget](https://developers.google.com/crawling/docs/crawl-budget)

### TS36-A01 — Plan préalable et chronologie du changement.

`TSEP@0.2.0-rc.1:TS36-A01`

**Entrées requises**: intent, change-history.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Changement sélectionné dont le suivi daté est évalué.

**Méthode.** Qualifier le plan lié avant baseline, les identités du reçu et l’ordre baseline/déploiement.

**Attendus.** Plan supported, identité conforme et baseline enregistrée avant déploiement ; contradiction explicite fail, manque inconclusive.

**Preuves.** Plan et revues liés, reçu de déploiement, API natives et journaux normalisés fournis ; contrat release-monitoring-v1.

**Hypothèses.** Périmètre, dates, couche et jugements fournis ; aucune authentification par empreinte seule.

**Indéterminé.** Échéance future, pièce manquante, erreur, valeur inconnue, journal incomplet ou liaison invalide ; conserver les contradictions indépendantes.

**Conditions de NA.** Aucune exemption atomique ; aucun manque ou délai ne vaut NA.

**Limites.** C documentaire sur baseline/J+1/J+7/J+30 sélectionnés ; aucune causalité, visite Google authentifiée, indexation ou couverture globale.

### TS36-A02 — Observations attribuées aux échéances du suivi.

`TSEP@0.2.0-rc.1:TS36-A02`

**Entrées requises**: intent, search-console, logs, change-history.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Changement sélectionné dont le suivi daté est évalué.

**Méthode.** Lire baseline/d1/d7/d30, qualifier API TS08-A02 et inventaires de journaux par fenêtre exacte.

**Attendus.** Quatre échéances atteintes, pièces attribuées complètes, limites respectées ; futur/absence/erreur reste inconclusive.

**Preuves.** Plan et revues liés, reçu de déploiement, API natives et journaux normalisés fournis ; contrat release-monitoring-v1.

**Hypothèses.** Périmètre, dates, couche et jugements fournis ; aucune authentification par empreinte seule.

**Indéterminé.** Échéance future, pièce manquante, erreur, valeur inconnue, journal incomplet ou liaison invalide ; conserver les contradictions indépendantes.

**Conditions de NA.** Aucune exemption atomique ; aucun manque ou délai ne vaut NA.

**Limites.** C documentaire sur baseline/J+1/J+7/J+30 sélectionnés ; aucune causalité, visite Google authentifiée, indexation ou couverture globale.

### TS36-A03 — Interprétation, décisions et clôture liées aux pièces.

`TSEP@0.2.0-rc.1:TS36-A03`

**Entrées requises**: intent, search-console, logs, change-history.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Changement sélectionné dont le suivi daté est évalué.

**Méthode.** Comparer revendications et valeurs connues, conserver les changements sans causalité et qualifier les revues/décisions fournies.

**Attendus.** Revendications fidèles, revues supported et cycle complet ; fausse revendication connue ou clôture avant échéance future fail ; autre manque inconclusive.

**Preuves.** Plan et revues liés, reçu de déploiement, API natives et journaux normalisés fournis ; contrat release-monitoring-v1.

**Hypothèses.** Périmètre, dates, couche et jugements fournis ; aucune authentification par empreinte seule.

**Indéterminé.** Échéance future, pièce manquante, erreur, valeur inconnue, journal incomplet ou liaison invalide ; conserver les contradictions indépendantes.

**Conditions de NA.** Aucune exemption atomique ; aucun manque ou délai ne vaut NA.

**Limites.** C documentaire sur baseline/J+1/J+7/J+30 sélectionnés ; aucune causalité, visite Google authentifiée, indexation ou couverture globale.

## TS37 — HTTPS, HSTS et les ressources intégrées ne créent ni erreur de certificat ni contenu mixte.

**Sévérité**: major. **Unité**: host.

**Entrées requises**: http, tls, render, configuration, intent.

**Applicabilité.** Hôtes et ressources d’un service web public.

**Méthode.** Tester le certificat sur les hôtes publics, suivre les variantes HTTP/HTTPS, relever Strict-Transport-Security et rechercher les sous-ressources en HTTP.

**Attendus.** Certificats et redirections sont valides pour les hôtes testés ; contenu mixte examiné ; décision HSTS et sa portée documentées, sans imposer le preload.

**Preuves.** Certificats et chaînes HTTP archivés, ressources mixtes examinées, décision HSTS explicite et portée documentée.

**Conditions de NA.** Aucun service HTTP public concerné.

**Limites.** HSTS renforce le transport après réception de la politique ; il ne corrige ni un certificat invalide ni une mauvaise architecture d’URL.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://www.rfc-editor.org/rfc/rfc6797](https://www.rfc-editor.org/rfc/rfc6797)

### TS37-A01 — Certificats, hôte, date et confiance fournie

`TSEP@0.3.0-draft.5:TS37-A01`

**Entrées requises**: tls, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS37, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Relire les PEM publics fournis avec OpenSSL3 hors réseau : chaîne, usage serveur, hôte DNS, heure fournie et racines explicitement fournies. Désactiver magasins implicites ; conserver version et diagnostic.

**Attendus.** La vérification du profil réussit sous les racines fournies. Une erreur X509 prise en charge, dont expiration ou mauvais hôte, échoue.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : tls, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** OpenSSL3 absent, PEM inutilisable, capture mal attribuée, racines absentes ou code d’erreur non qualifié : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

### TS37-A02 — Redirections HTTPS et décision HSTS

`TSEP@0.3.0-draft.5:TS37-A02`

**Entrées requises**: http, configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS37, profil render-transport-v1 ; voir docs/render-transport-evidence.md.

**Méthode.** Suivre la chaîne HTTP fournie vers HTTPS sans rétrogradation, vérifier la réponse directe200, comparer configuration HSTS et en-tête au plan : activation, max-age, sous-domaines, portée, propriétaire, motif.

**Attendus.** Chaînes et décision HSTS concordent ; HSTS peut être désactivé explicitement. Aucun preload imposé.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, configuration, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** Chaîne/configuration manquante, en-tête ambigu, portée ou décision absente : NT.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

### TS37-A03 — Sous-ressources et trafic mixte du périmètre

`TSEP@0.3.0-draft.5:TS37-A03`

**Entrées requises**: http, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Population finie préalable de TS37, profil render-transport-v1 ; voir docs/render-transport-evidence.md. Amendement: docs/render-transport-prerequisites-v2.md.

**Méthode.** Relier HAR et console au document HTTPS ; examiner les requêtes observées et les URL intégrées de la source. Le profil strict exige HTTPS pour ces ressources, même si un navigateur peut les mettre à niveau. Avec base href non qualifiée, une URL relative reste NT ; examiner indépendamment les URL absolues malgré CSS/srcset ou un autre schéma inconnu.

**Attendus.** Aucune URL HTTP observée sur ces surfaces ; revue de la couverture dynamique consignée. Un HTTP natif observé échoue malgré une autre lacune.

**Preuves.** Originaux exacts, plan et dates/contexte, empreintes, diagnostics et revue motivée liée au dossier entier. Types : http, render, intent.

**Hypothèses.** Provenance, inventaire, état navigateur, conditions et jugement fournis, non authentifiés ; deux lectures HTML statiques ne sont pas deux navigations. La confiance TLS dépend des racines fournies.

**Indéterminé.** HAR tronqué, corps absent, CSS/srcset non qualifiés, contexte incomplet ou revue absente : NT. Résolution relative avec base href non qualifiée : NT ; une contradiction HTTP indépendante reste NC.

**Conditions de NA.** Pas de NA atomique. Population vide ou domaine prétendu absent sans preuve reste NT dans ce profil.

**Limites.** Aucun audit réel déduit des cas synthétiques. Ni indexation, classement, conformité globale, certification d’accessibilité, sécurité exhaustive ou confiance universelle des navigateurs. La revue peut être erronée ; les captures peuvent omettre des états.

## TS38 — Les variantes d’hôte, de casse et de slash convergent vers une règle unique.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: http, html, sitemap, crawl, intent.

**Applicabilité.** Variantes hôte, casse et slash de ressources déclarées équivalentes.

**Méthode.** Rejouer www/sans www, HTTP/HTTPS, casse pertinente et slash final sur un échantillon de routes ; comparer redirection, canonical, sitemap et liens internes.

**Attendus.** Chaque variante testée suit la règle déclarée ; redirections, canonicals, sitemap et liens concordent, sans fusion de ressources distinctes.

**Preuves.** Une URL finale stable par ressource, sans chaîne, avec des signaux internes concordants.

**Conditions de NA.** Aucune variante concernée après inventaire explicite.

**Limites.** La casse peut être significative selon le serveur et l’application ; la règle doit être testée, pas supposée.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### TS38-A01 — Trajectoires et canonical des variantes équivalentes

`TSEP@0.3.0-draft.2:TS38-A01`

**Entrées requises**: http, html, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments explicitement sélectionnés du contrôle TS38 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Méthode.** Exiger l’équivalence revue puis lire chaque trajectoire native : un seul saut depuis chaque variante, réponse directe 200 pour la préférence, canonical HTTP/HTML vers elle.

**Attendus.** Chaque variante converge en un saut et chaque canonical qualifiée concorde. La fusion déclarée de ressources distinctes ou une divergence native échoue.

**Preuves.** Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : http, html, content, intent.

**Hypothèses.** Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminé.** Trace manquante, canonical absente, équivalence non décidée ou rendu nécessaire : indéterminé.

**Conditions de NA.** Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites.** Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### TS38-A02 — Signaux internes des variantes

`TSEP@0.3.0-draft.2:TS38-A02`

**Entrées requises**: sitemap, html, crawl, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Éléments explicitement sélectionnés du contrôle TS38 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Méthode.** Lire le urlset natif complet sélectionné et toutes les sources de liens prévues. Exiger la présence de la préférence dans ce sitemap, aucune variante non préférée dans sitemap/liens et la revue d’équivalence/périmètre.

**Attendus.** Sitemap et liens du périmètre concordent avec la préférence ; une divergence ou fusion de pages distinctes échoue. Zéro lien reste une observation du corpus complet fourni.

**Preuves.** Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : sitemap, html, crawl, content, intent.

**Hypothèses.** Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminé.** Index XML, fichier tronqué, source de liens manquante, population ou revue ambiguë : indéterminé ; aucune absence globale inférée.

**Conditions de NA.** Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites.** Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

## TS39 — Le CDN, Vary et la géolocalisation ne servent pas des signaux SEO contradictoires.

**Sévérité**: major. **Unité**: delivery-matrix.

**Entrées requises**: http, configuration, intent.

**Applicabilité.** Diffusion variant selon région, cache, appareil ou négociation.

**Méthode.** Déclarer et faire revoir matrice, configuration et politique avant collecte ; comparer signaux natifs, contenu et accès par cellule ; qualifier contextes et réutilisations du cache avec pièces liées selon delivery-evidence-v1.

**Attendus.** Les trois règles réussissent sur les cellules déclarées : politique revue, signaux cohérents et mécanismes attribués ; variations légitimes, défauts indépendants et cellules non qualifiées restent distincts.

**Preuves.** Configuration, matrice préalable, HTTP natifs, rendus ou exemptions positives, revues liées et journaux du cache lorsqu’il est testé. Politique d’accès Googlebot qualifiée séparément des requêtes du client de test ; aucune visite réelle déduite.

**Conditions de NA.** Absence de mécanisme de variation attestée par configuration.

**Limites.** Premier profil borné avec un membre canonical par cellule et réutilisation sans transformation. Revues, sources, régions, horloges et journaux fournis sans authentification ; pas de simulation générale du cache. Deux points ne couvrent pas tous les POP/routes, et C n’établit pas l’accès réel de Googlebot.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** RFC 9110 établit la sémantique de Vary et des réponses HTTP. Le comportement des pages adaptées à la région est documenté séparément par Google.

**Références**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110); [https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)

### TS39-A01 — Matrice préalable et configuration revues

`TSEP@0.2.0-rc.1:TS39-A01`

**Entrées requises**: configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Diffusion variant selon région, cache, appareil ou négociation.

**Méthode.** Vérifier fenêtre, cellules, mécanismes, configuration conservée et revue liée avant collecte, incluant représentativité et politique d’accès Googlebot.

**Attendus.** Configuration et matrice qualifiées par une revue favorable ; rejet documenté = fail.

**Preuves.** Configuration, matrice préalable, HTTP natifs, rendus ou exemptions positives, revues liées et journaux du cache lorsqu’il est testé. Politique d’accès Googlebot qualifiée séparément des requêtes du client de test ; aucune visite réelle déduite.

**Hypothèses.** Intention, contexte et qualifications des sources/revues fournis ; leur vérité reste à vérifier.

**Indéterminé.** Configuration/revue absente, tardive, non liée ; minimum de matrice ou mécanisme non qualifié.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil borné avec un membre canonical par cellule et réutilisation sans transformation. Revues, sources, régions, horloges et journaux fournis sans authentification ; pas de simulation générale du cache. Deux points ne couvrent pas tous les POP/routes, et C n’établit pas l’accès réel de Googlebot.

### TS39-A02 — Cohérence des signaux dans chaque contexte

`TSEP@0.2.0-rc.1:TS39-A02`

**Entrées requises**: http, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Diffusion variant selon région, cache, appareil ou négociation.

**Méthode.** Comparer statut/URL finale, recalculer TS07-A01/A02/A03 et TS10-A01, puis confronter langue/contenu/accessibilité aux revues liées ; conserver chaque inconnue.

**Attendus.** Toutes les cellules suivent la politique ; exemption de rendu positive conservée. Toute contradiction attribuable donne fail malgré les autres inconnues.

**Preuves.** Configuration, matrice préalable, HTTP natifs, rendus ou exemptions positives, revues liées et journaux du cache lorsqu’il est testé. Politique d’accès Googlebot qualifiée séparément des requêtes du client de test ; aucune visite réelle déduite.

**Hypothèses.** Intention, contexte et qualifications des sources/revues fournis ; leur vérité reste à vérifier.

**Indéterminé.** Cellule, source, rendu, revue ou profil manquant ; corps incomplet, contexte non lié ou sémantique inconnue.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil borné avec un membre canonical par cellule et réutilisation sans transformation. Revues, sources, régions, horloges et journaux fournis sans authentification ; pas de simulation générale du cache. Deux points ne couvrent pas tous les POP/routes, et C n’établit pas l’accès réel de Googlebot.

### TS39-A03 — Attribution des contextes et du cache

`TSEP@0.2.0-rc.1:TS39-A03`

**Entrées requises**: configuration, http, logs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Diffusion variant selon région, cache, appareil ou négociation.

**Méthode.** Qualifier contextes/mécanismes sur sources liées ; pour le cache, rapprocher entrée stockée, requête servie, couche, horloge, Vary et revue de fraîcheur.

**Attendus.** Attribution et politique cohérentes sur toutes les cellules/checks ; réutilisation attribuée incompatible avec Vary ou politique = fail. Un test n’est pas une visite opérateur.

**Preuves.** Configuration, matrice préalable, HTTP natifs, rendus ou exemptions positives, revues liées et journaux du cache lorsqu’il est testé. Politique d’accès Googlebot qualifiée séparément des requêtes du client de test ; aucune visite réelle déduite.

**Hypothèses.** Intention, contexte et qualifications des sources/revues fournis ; leur vérité reste à vérifier.

**Indéterminé.** Région, source, journal, lien ou fraîcheur non qualifié ; Age/HIT, User-Agent, séquence ou ETag seuls insuffisants.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil borné avec un membre canonical par cellule et réutilisation sans transformation. Revues, sources, régions, horloges et journaux fournis sans authentification ; pas de simulation générale du cache. Deux points ne couvrent pas tous les POP/routes, et C n’établit pas l’accès réel de Googlebot.

## TS40 — Les méthodes hreflang utilisées sont complètes et cohérentes.

**Sévérité**: major. **Unité**: locale-cluster.

**Entrées requises**: hreflang, intent.

**Applicabilité.** Groupes utilisant au moins une méthode hreflang.

**Méthode.** Identifier toutes les méthodes publiées, vérifier les groupes et comparer leurs annotations lorsqu’elles coexistent.

**Attendus.** Chaque méthode utilisée couvre le groupe ; si plusieurs sont publiées, leurs annotations sont cohérentes ; aucune obligation d’une méthode unique.

**Preuves.** Groupes équivalents et réciproques ; si le sitemap est choisi, namespace xhtml et entrées par URL valides.

**Conditions de NA.** Aucune annotation hreflang dans le périmètre.

**Limites.** Cumuler HTML, en-têtes et sitemap n’apporte pas de bénéfice de recherche et augmente le risque de divergence.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

### TS40-A01 — Complétude indépendante des méthodes publiées

`TSEP@0.3.0-draft.3:TS40-A01`

**Entrées requises**: hreflang, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Familles ou groupes explicitement sélectionnés pour TS40 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Méthode.** Inventorier les méthodes avant capture ; lire chaque méthode/page séparément et vérifier tout le groupe attendu, auto-référence comprise. Une méthode secondaire ne complète pas une primaire partielle.

**Attendus.** Chaque méthode complète contient les associations prévues. Une omission démontrée dans une surface complète ou une destination contraire échoue ; un jeu unique de méthodes est autorisé.

**Preuves.** Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : hreflang, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses.** Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminé.** Capture/méthode absente, XML tronqué/index, méthode publiée omise du plan, association hors groupe ou revue absente : indéterminé.

**Conditions de NA.** Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites.** Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

### TS40-A02 — Cohérence des méthodes et des pages du groupe

`TSEP@0.3.0-draft.3:TS40-A02`

**Entrées requises**: hreflang, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Familles ou groupes explicitement sélectionnés pour TS40 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Méthode.** Comparer les associations qualifiées entre méthodes/pages sans fusionner leurs jeux. Conserver un conflit de destination indépendant même si une troisième méthode manque ; comparer l’égalité des jeux quand les deux sont complets.

**Attendus.** Les méthodes complètes et les pages concordent. Une seule méthode complète est admise. Un conflit natif ou une différence de jeux complets échoue.

**Preuves.** Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : hreflang, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses.** Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminé.** Comparaison sans surface qualifiée, capture partielle, méthode manquante ou revue absente : indéterminé, sauf contradiction indépendante établie.

**Conditions de NA.** Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites.** Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

## TS41 — Les invariants SEO critiques sont rejoués automatiquement avant et après déploiement.

**Sévérité**: major. **Unité**: release.

**Entrées requises**: configuration, ci-output, change-history, intent.

**Applicabilité.** Déploiements soumis aux invariants SEO définis par le projet.

**Méthode.** Fixer population, matrice et politique avant les tentatives ; relire les entrées/sorties natives, événements liés et exercice négatif selon release-invariants-v1.

**Attendus.** Plan représentatif revu, exécutions couvertes et réaction correcte aux échecs/inconnues ; les trois règles réussissent. Un défaut SEO correctement bloqué reste visible et ne condamne pas le dispositif.

**Preuves.** Plan et revues liées, commande/environnement identifiés, reçus avec entrées/sorties natives, codes processus, journal JSONL et artefacts avant/après application.

**Conditions de NA.** Aucun déploiement ou pipeline concerné dans le périmètre et la période.

**Limites.** Premier profil natif TSEP strict sans dérogation ; commandes jamais exécutées. Revues, complétude, horloges et runner fournis, non authentifiés. C qualifie le dispositif déclaré, sans santé SEO globale, effet causal ni CI distante déduite.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Contrôle de gouvernance et de non-régression proposé par Edikka ; aucune documentation officielle unique ne prescrit ce pipeline complet.

**Références**: TSEP / Edikka method.

### TS41-A01 — Plan préalable et représentativité

`TSEP@0.2.0-rc.1:TS41-A01`

**Entrées requises**: configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Déploiements soumis aux invariants SEO définis par le projet.

**Méthode.** Vérifier fenêtre, tentatives, matrice, politique stricte et revue de représentativité liée avant la fenêtre.

**Attendus.** Plan complet et revue favorable ; rejet explicite lié = fail.

**Preuves.** Plan et revues liées, commande/environnement identifiés, reçus avec entrées/sorties natives, codes processus, journal JSONL et artefacts avant/après application.

**Hypothèses.** Population, contexte comparable, identité des artefacts et revues fournis ; leur véracité reste à qualifier.

**Indéterminé.** Plan ou revue absent, non lié, tardif, incomplet ; profil, seuil ou portée non qualifiés.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil natif TSEP strict sans dérogation ; commandes jamais exécutées. Revues, complétude, horloges et runner fournis, non authentifiés. C qualifie le dispositif déclaré, sans santé SEO globale, effet causal ni CI distante déduite.

### TS41-A02 — Couverture et fidélité des exécutions

`TSEP@0.2.0-rc.1:TS41-A02`

**Entrées requises**: configuration, ci-output, change-history, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Déploiements soumis aux invariants SEO définis par le projet.

**Méthode.** Recalculer les entrées conservées ; vérifier matrice, artefacts, commande, déclencheurs et chronologie, sans exécuter argv.

**Attendus.** Population exacte et sorties fidèles, y compris inconnues conservées ; contradiction conclusive de rattachement ou sortie = fail.

**Preuves.** Plan et revues liées, commande/environnement identifiés, reçus avec entrées/sorties natives, codes processus, journal JSONL et artefacts avant/après application.

**Hypothèses.** Population, contexte comparable, identité des artefacts et revues fournis ; leur véracité reste à qualifier.

**Indéterminé.** Reçu, cellule, revue, événement ou runtime manquant ; journal ambigu, exécution supplémentaire ou recalcul indéterminé différent.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil natif TSEP strict sans dérogation ; commandes jamais exécutées. Revues, complétude, horloges et runner fournis, non authentifiés. C qualifie le dispositif déclaré, sans santé SEO globale, effet causal ni CI distante déduite.

### TS41-A03 — Exercice négatif et réaction du dispositif

`TSEP@0.2.0-rc.1:TS41-A03`

**Entrées requises**: configuration, ci-output, change-history, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Déploiements soumis aux invariants SEO définis par le projet.

**Méthode.** Vérifier échec négatif préalable, codes distincts pass/fail/inconclusive et événement explicite de blocage/application ou acceptation/suspension.

**Attendus.** Exercice négatif effectif et réactions conformes à la phase ; échec/inconnu masqué, mauvaise action ou dérogation observée = fail.

**Preuves.** Plan et revues liées, commande/environnement identifiés, reçus avec entrées/sorties natives, codes processus, journal JSONL et artefacts avant/après application.

**Hypothèses.** Population, contexte comparable, identité des artefacts et revues fournis ; leur véracité reste à qualifier.

**Indéterminé.** Exercice, code processus, lien ou action absent/non qualifié ; absence dans un journal insuffisante pour prouver un blocage.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil natif TSEP strict sans dérogation ; commandes jamais exécutées. Revues, complétude, horloges et runner fournis, non authentifiés. C qualifie le dispositif déclaré, sans santé SEO globale, effet causal ni CI distante déduite.

## TS42 — Chaque agent automatisé est gouverné selon son usage documenté.

**Sévérité**: major. **Unité**: policy.

**Entrées requises**: configuration, operator-docs, intent.

**Applicabilité.** Agents automatisés visés par la politique du site.

**Méthode.** Documenter les correspondances et leur revue, retenir la décision du responsable, puis comparer sa traduction selon agent-governance-v1 ; conserver les finalités couplées et les inconnues.

**Attendus.** Les trois règles réussissent pour chaque cible et mécanisme déclaré ; la politique qualifiée correspond au choix accepté, avec revue et responsabilité fournies.

**Preuves.** Inventaire mécanisme/finalité, sources opérateurs datées et liées aux revues, décision du responsable et arbitrages, politique robots capturée.

**Conditions de NA.** Aucune politique d’agents dans le périmètre déclaré, raison fournie.

**Limites.** Périmètre fourni et profil robots borné ; aucun registre automatique. Sources, revues et décisions non authentifiées ; aucune visite, identité réelle, conformité opérateur, indexation ou citation déduite.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots); [https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)

### TS42-A01 — Usages et mécanismes documentés

`TSEP@0.2.0-rc.1:TS42-A01`

**Entrées requises**: operator-docs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque cible URL et mécanisme de la politique préalablement déclarée.

**Méthode.** Lier opérateur, acteur, jeton, mécanisme et finalités aux sources UTF-8 datées ; vérifier empreintes et revue fournie liée.

**Attendus.** Chaque correspondance a une revue supported, complète, datée et liée aux sources, avec applicabilité robots explicite. Une contradiction liée échoue.

**Preuves.** Entrées, dates, empreintes et résultats détaillés selon docs/agent-usage-policy.md.

**Hypothèses.** Inventaire fourni ; interprétation des sources et autorité des personnes déclarées, sans authentification automatique.

**Indéterminé.** Source absente, trop ancienne ou ambiguë ; empreinte, liaison, complétude ou revue manquante.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Périmètre fourni et profil robots borné ; aucun registre automatique. Sources, revues et décisions non authentifiées ; aucune visite, identité réelle, conformité opérateur, indexation ou citation déduite.

### TS42-A02 — Décisions du responsable et arbitrages

`TSEP@0.2.0-rc.1:TS42-A02`

**Entrées requises**: intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque cible URL et mécanisme de la politique préalablement déclarée.

**Méthode.** Vérifier chaque décision motivée, la décision séparée du responsable ou délégué déclaré et sa liaison au plan ; conserver tout arbitrage des finalités couplées.

**Attendus.** Chaque couple mécanisme/finalité porte un choix et un motif ; le responsable accepte le plan et ses arbitrages exacts. Son refus lié échoue.

**Preuves.** Entrées, dates, empreintes et résultats détaillés selon docs/agent-usage-policy.md.

**Hypothèses.** Inventaire fourni ; interprétation des sources et autorité des personnes déclarées, sans authentification automatique.

**Indéterminé.** Auteur absent ou non déclaré, décision non liée, dates incohérentes, choix ou arbitrage incomplet.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Périmètre fourni et profil robots borné ; aucun registre automatique. Sources, revues et décisions non authentifiées ; aucune visite, identité réelle, conformité opérateur, indexation ou citation déduite.

### TS42-A03 — Politique capturée et choix effectif

`TSEP@0.2.0-rc.1:TS42-A03`

**Entrées requises**: configuration, operator-docs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque cible URL et mécanisme de la politique préalablement déclarée.

**Méthode.** Regrouper les jetons identiques sans casse, qualifier les correspondances et comparer Allow/Disallow à la décision effective ; conserver lecture, arbitrages, contradictions et inconnues.

**Attendus.** Dans chaque groupe qualifié, la réponse robots 200 attribuée au client suit le choix accepté. Toute contradiction indépendante échoue.

**Preuves.** Entrées, dates, empreintes et résultats détaillés selon docs/agent-usage-policy.md.

**Hypothèses.** Inventaire fourni ; interprétation des sources et autorité des personnes déclarées, sans authentification automatique.

**Indéterminé.** Finalités opposées sans arbitrage, mécanisme non qualifié, champ ignoré ou preuve HTTP/source/décision absente ; autres profils robots non qualifiés.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Périmètre fourni et profil robots borné ; aucun registre automatique. Sources, revues et décisions non authentifiées ; aucune visite, identité réelle, conformité opérateur, indexation ou citation déduite.

## TS43 — L’accès des crawlers autorisés est testé avec leur chaîne complète et rapproché des journaux.

**Sévérité**: major. **Unité**: request-set.

**Entrées requises**: http, logs, operator-docs, intent.

**Applicabilité.** Tests de politique d’accès pour des agents déclarés.

**Méthode.** Déclarer séparément l’accès de l’opérateur et le traitement du client de test ; comparer sa chaîne complète, rapprocher les journaux et qualifier honnêtement son origine selon agent-access-v1.

**Attendus.** Les trois règles réussissent sur le périmètre de tests déclaré, avec réponse prévue, rapprochement qualifié et identité opérateur explicitement non vérifiée ; un refus prévu peut être conforme.

**Preuves.** Plan préalable, chaîne User-Agent revue, HTTP brut, journal JSONL natif, revues liées, commande/reçu fourni et qualification d’identité.

**Conditions de NA.** Aucun agent à tester dans la politique déclarée.

**Limites.** Premier profil : client de test initié par l’évaluateur ; aucune visite, identité réelle, sécurité ou accessibilité de l’opérateur déduite. Sources, journaux, revues et reçu non authentifiés.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots)

### TS43-A01 — Client complet et traitement attendu

`TSEP@0.2.0-rc.1:TS43-A01`

**Entrées requises**: http, operator-docs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque URL et client HTTP du périmètre de tests préalablement déclaré.

**Méthode.** Relire les sources et leur revue liée ; vérifier la chaîne HTTP datée puis la réponse et le corps prévus pour le client de test.

**Attendus.** Documentation revue et réponse conformes au plan du test ; contradiction indépendante conservée même si une autre preuve manque.

**Preuves.** Pièces, dates, liaisons et observations selon docs/agent-access-evidence.md.

**Hypothèses.** Sources, contexte, qualité du journal et revues fournis ; portée du test limitée à son client.

**Indéterminé.** Client/source/revue absent, trace incomplète, traitement attendu ou référence de corps manquant.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil : client de test initié par l’évaluateur ; aucune visite, identité réelle, sécurité ou accessibilité de l’opérateur déduite. Sources, journaux, revues et reçu non authentifiés.

### TS43-A02 — Chaîne rapprochée des journaux

`TSEP@0.2.0-rc.1:TS43-A02`

**Entrées requises**: http, logs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque URL et client HTTP du périmètre de tests préalablement déclaré.

**Méthode.** Vérifier export, revue de couche/identifiant/cache/horloge, puis identifier chaque ligne unique dans sa fenêtre avant comparaison littérale.

**Attendus.** Chaque saut a une ligne attribuée dont méthode, URL, chaîne client et statut concordent ; tout écart qualifié échoue malgré un autre saut absent.

**Preuves.** Pièces, dates, liaisons et observations selon docs/agent-access-evidence.md.

**Hypothèses.** Sources, contexte, qualité du journal et revues fournis ; portée du test limitée à son client.

**Indéterminé.** Logs absents, ID client ou rejoué, doublon, mauvaise couche, format inconnu, fenêtre/revue insuffisante.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil : client de test initié par l’évaluateur ; aucune visite, identité réelle, sécurité ou accessibilité de l’opérateur déduite. Sources, journaux, revues et reçu non authentifiés.

### TS43-A03 — Origine du test et identité non inventée

`TSEP@0.2.0-rc.1:TS43-A03`

**Entrées requises**: http, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Chaque URL et client HTTP du périmètre de tests préalablement déclaré.

**Méthode.** Vérifier reçu d’exécution et qualification fournie liés ; distinguer test initié par l’évaluateur et visite de l’opérateur.

**Attendus.** Origine assessor-test, identité opérateur not-verified et aucune revendication de visite réelle ; toute revendication liée contraire échoue.

**Preuves.** Pièces, dates, liaisons et observations selon docs/agent-access-evidence.md.

**Hypothèses.** Sources, contexte, qualité du journal et revues fournis ; portée du test limitée à son client.

**Indéterminé.** Reçu/commande/qualification manquant, dates incohérentes, liaison absente ou statut d’identité ambigu.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil : client de test initié par l’évaluateur ; aucune visite, identité réelle, sécurité ou accessibilité de l’opérateur déduite. Sources, journaux, revues et reçu non authentifiés.

## TS44 — Le contenu critique et ses preuves restent accessibles sans dépendre d’une exécution JavaScript non documentée.

**Sévérité**: major. **Unité**: page.

**Entrées requises**: http, html, render, content, intent.

**Applicabilité.** Contenus destinés à des consommateurs automatisés déclarés.

**Méthode.** Déclarer les faits critiques et leurs chemins avant collecte ; vérifier accès sans JS, valeurs et revues exactes des représentations selon critical-content-nojs-v1.

**Attendus.** Les trois règles réussissent pour le client de référence sans JavaScript, avec livraison qualifiée, valeurs cohérentes et revues liées ; aucune consommation réelle déduite.

**Preuves.** Plan et revue préalables, chaînes HTTP complètes, HTML/JSON brut, arbre rendu attribué et revues de contexte liées.

**Conditions de NA.** Aucun contenu destiné à ces consommateurs dans le périmètre.

**Limites.** Premier profil HTML/JSON borné, Node facultatif et rendu fourni ; pas de visibilité CSS, vérité, identité du relecteur, ingestion ou citation authentifiées. DOM rédigé explicitement synthétique.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Portée partielle : la source Google documente le rendu JavaScript pour Google Search. Le contrôle étend prudemment la vérification à des consommateurs dont les capacités de rendu ne sont pas uniformément documentées.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics); [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots); [https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)

### TS44-A01 — Périmètre critique préalable

`TSEP@0.2.0-rc.1:TS44-A01`

**Entrées requises**: content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Contenus destinés à des consommateurs automatisés déclarés.

**Méthode.** Vérifier inventaire, client sans JS, états et ressources prévus, puis revue liée antérieure aux captures.

**Attendus.** Périmètre complet soutenu par la revue ; rejet lié = fail.

**Preuves.** Plan et revue préalables, chaînes HTTP complètes, HTML/JSON brut, arbre rendu attribué et revues de contexte liées.

**Hypothèses.** Inventaire, références attendues, contexte et revues fournis ; portée fixée avant capture, pièces non authentifiées.

**Indéterminé.** Plan/revue absent, tardif, non lié, incomplet ou capacité de référence différente.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil HTML/JSON borné, Node facultatif et rendu fourni ; pas de visibilité CSS, vérité, identité du relecteur, ingestion ou citation authentifiées. DOM rédigé explicitement synthétique.

### TS44-A02 — Chemin de livraison sans JavaScript

`TSEP@0.2.0-rc.1:TS44-A02`

**Entrées requises**: http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Contenus destinés à des consommateurs automatisés déclarés.

**Méthode.** Vérifier le chemin préalable, le lien explicite si ressource, HTTP anonyme et présence de tous les éléments critiques.

**Attendus.** Destination/réponse attendues et éléments présents ; tout refus, chemin contraire ou absence qualifiée échoue.

**Preuves.** Plan et revue préalables, chaînes HTTP complètes, HTML/JSON brut, arbre rendu attribué et revues de contexte liées.

**Hypothèses.** Inventaire, références attendues, contexte et revues fournis ; portée fixée avant capture, pièces non authentifiées.

**Indéterminé.** Capture, format, runtime, lien/contexte ou lecture incomplète et non qualifiée.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil HTML/JSON borné, Node facultatif et rendu fourni ; pas de visibilité CSS, vérité, identité du relecteur, ingestion ou citation authentifiées. DOM rédigé explicitement synthétique.

### TS44-A03 — Cohérence des valeurs et du contexte

`TSEP@0.2.0-rc.1:TS44-A03`

**Entrées requises**: http, html, render, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicabilité.** Contenus destinés à des consommateurs automatisés déclarés.

**Méthode.** Comparer les valeurs qualifiées de chaque représentation et état rendu au plan ; relire le contexte critique entier avec des revues propres à chaque pièce.

**Attendus.** Valeurs et revues cohérentes ; contradiction qualifiée conservée malgré une autre pièce manquante.

**Preuves.** Plan et revue préalables, chaînes HTTP complètes, HTML/JSON brut, arbre rendu attribué et revues de contexte liées.

**Hypothèses.** Inventaire, références attendues, contexte et revues fournis ; portée fixée avant capture, pièces non authentifiées.

**Indéterminé.** Revue, rendu, valeur ou attribution absent/inconnu ; état fourni hors du plan ou contexte non pris en charge.

**Conditions de NA.** Aucune exemption atomique automatique.

**Limites.** Premier profil HTML/JSON borné, Node facultatif et rendu fourni ; pas de visibilité CSS, vérité, identité du relecteur, ingestion ou citation authentifiées. DOM rédigé explicitement synthétique.
