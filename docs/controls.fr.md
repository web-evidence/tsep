# TSEP 0.1.0-draft.1 — Contrôles

Generated from `spec/protocol.json` / Généré depuis `spec/protocol.json`.

Draft / Version de travail. See / Voir [contract](contract.fr.md).

## TS01 — La page finale répond avec un code HTTP exploitable.

**Sévérité**: blocking. **Unité**: page.

**Entrées requises**: http, intent.

**Applicabilité.** Pages publiques désignées comme canoniques.

**Méthode.** Envoyer une requête GET, suivre les redirections et relever le code final.

**Attendus.** Chaque GET atteint une réponse finale 200 pour la ressource attendue ; horodatage et chaîne conservés.

**Preuves.** URL testée, horodatage, code final 200 pour une page canonique publique.

**Conditions de NA.** Aucune page publique canonique dans le périmètre déclaré.

**Limites.** Un test depuis une IP ne prouve pas la réponse reçue par Googlebot.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110)

## TS02 — Les redirections sont intentionnelles, directes et sans boucle.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: http, intent.

**Applicabilité.** Variantes et anciennes URL dont le comportement attendu est déclaré.

**Méthode.** Tester les variantes HTTP/HTTPS, hôte, slash et anciennes URL avec le nombre de redirections.

**Attendus.** Chaque variante testée suit la destination et le nombre de sauts autorisés, sans boucle ; intention validée par le responsable.

**Preuves.** Destination finale unique, chaîne documentée, absence de boucle.

**Conditions de NA.** Aucune redirection ni variante attendue, inventaire à l’appui.

**Limites.** Une redirection valide ne prouve pas la pertinence sémantique de sa destination.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/301-redirects](https://developers.google.com/search/docs/crawling-indexing/301-redirects)

## TS03 — Les erreurs serveur et soft 404 ne remplacent pas une réponse explicite.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: http, content, intent.

**Applicabilité.** Routes existantes, supprimées et inexistantes du périmètre.

**Méthode.** Tester une page existante, une URL supprimée et une URL inexistante ; comparer code et contenu.

**Attendus.** Codes et contenus correspondent aux trois cas déclarés ; les erreurs testées ne livrent pas une page d’erreur en 200.

**Preuves.** Codes 4xx/5xx cohérents et modèle d’erreur qui ne renvoie pas 200 par défaut.

**Conditions de NA.** Périmètre ne contenant aucun routage HTTP, justification fournie.

**Limites.** La classification soft 404 finale reste une décision du moteur.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/http-network-errors](https://developers.google.com/search/docs/crawling-indexing/http-network-errors)

## TS04 — La politique robots effective correspond à l’intention déclarée.

**Sévérité**: blocking. **Unité**: host.

**Entrées requises**: http, robots, intent.

**Applicabilité.** Hôtes et agents pour lesquels une politique d’exploration est évaluée.

**Méthode.** Récupérer robots.txt pour chaque origine ; conserver le statut, les règles effectives du robot ciblé et la politique attendue. Examiner les erreurs selon la documentation du robot, sans assimiler toute absence à un échec.

**Attendus.** Règles effectives et accès aux ressources correspondent à la politique déclarée ; une absence volontaire documentée peut être compatible, sans exiger systématiquement 200.

**Preuves.** Origine, robot, statut, règles ou absence constatée, ressources testées et politique attendue.

**Conditions de NA.** Aucun hôte explorable dans le périmètre.

**Limites.** robots.txt est un protocole d’exploration, pas un contrôle d’accès.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://www.rfc-editor.org/rfc/rfc9309.html](https://www.rfc-editor.org/rfc/rfc9309.html)

## TS05 — Une directive Disallow n’est jamais présentée comme une garantie de désindexation.

**Sévérité**: blocking. **Unité**: policy.

**Entrées requises**: configuration, intent.

**Applicabilité.** Politiques d’exploration ou d’exclusion du périmètre.

**Méthode.** Comparer la politique robots, les besoins d’indexation et les directives meta/X-Robots-Tag.

**Attendus.** Exploration, indexation et protection ont des mécanismes et objectifs distincts ; aucune garantie de désindexation ne repose seulement sur Disallow.

**Preuves.** Décision distincte pour exploration, indexation et protection.

**Conditions de NA.** Aucune politique concernée, périmètre et décision documentés.

**Limites.** Une URL bloquée peut rester connue et apparaître sans extrait.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/robots/intro](https://developers.google.com/search/docs/crawling-indexing/robots/intro)

## TS06 — Les zones sensibles refusent réellement l’accès au serveur.

**Sévérité**: blocking. **Unité**: route-set.

**Entrées requises**: configuration, http, intent.

**Applicabilité.** Routes déclarées privées ou sensibles.

**Méthode.** Tester sans session les routes privées et vérifier authentification, autorisation et cache.

**Attendus.** Sans session et avec les rôles non autorisés testés, aucun contenu sensible n’est livré, y compris par le cache ; contrôles et rôles couverts sont listés.

**Preuves.** Réponse 401/403 ou redirection d’authentification sans contenu sensible livré.

**Conditions de NA.** Absence de routes privées attestée par un inventaire autorisé.

**Limites.** L’absence dans l’index ne constitue pas une preuve de confidentialité.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110)

## TS07 — Les directives meta robots et X-Robots-Tag sont cohérentes avec l’objectif de la page.

**Sévérité**: blocking. **Unité**: page.

**Entrées requises**: http, html, intent.

**Applicabilité.** Documents et ressources dont l’objectif d’indexation est déclaré.

**Méthode.** Inspecter les en-têtes et le DOM source sur les gabarits indexables et exclus.

**Attendus.** Les directives effectives du robot cible, dans les en-têtes finaux et le HTML, correspondent à cet objectif ; directives inconnues et états rendus nécessaires sont examinés.

**Preuves.** Directive unique ou combinaison compatible, sans noindex accidentel.

**Conditions de NA.** Aucune ressource soumise à une politique d’indexation dans le périmètre.

**Limites.** Le moteur doit pouvoir explorer la ressource pour lire la directive.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)

## TS08 — Le statut d’indexation réel est vérifié dans Search Console.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: search-console, intent.

**Applicabilité.** URL dont l’état dans Google doit être établi.

**Méthode.** Utiliser l’inspection d’URL sur un échantillon représentatif et conserver l’export ou la capture.

**Attendus.** L’inspection est datée pour chaque URL retenue ; état réel, exploration et canonique sont consignés et rapprochés de l’objectif, écarts expliqués.

**Preuves.** URL connue, exploration autorisée, indexation et canonique Google documentées.

**Conditions de NA.** Le moteur Google est explicitement hors périmètre ; absence d’accès seule ne suffit pas.

**Limites.** Un audit public ne peut pas établir ce statut sans accès à la propriété.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://support.google.com/webmasters/answer/9012289](https://support.google.com/webmasters/answer/9012289)

## TS09 — Les exclusions volontaires ont un propriétaire et une justification.

**Sévérité**: minor. **Unité**: policy.

**Entrées requises**: configuration, intent.

**Applicabilité.** Familles volontairement exclues.

**Méthode.** Relier chaque famille exclue à une règle, un responsable et une date de revue.

**Attendus.** Chaque exclusion du périmètre possède mécanisme, motif, propriétaire et date de revue.

**Preuves.** Registre des exclusions : type de page, mécanisme, motif, propriétaire, révision.

**Conditions de NA.** Aucune exclusion volontaire, inventaire de politique fourni.

**Limites.** La pertinence métier de l’exclusion ne peut pas être automatisée.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/block-indexing](https://developers.google.com/search/docs/crawling-indexing/block-indexing)

## TS10 — Chaque page canonique publie une URL absolue, stable et cohérente.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: http, html, sitemap, crawl, intent.

**Applicabilité.** Familles déclarant une stratégie de canonicalisation.

**Méthode.** Comparer URL finale, rel=canonical, sitemap et liens internes.

**Attendus.** URL finales, canonicals déclarés, sitemap et liens internes convergent selon cette stratégie ; les exceptions sont justifiées.

**Preuves.** Signaux convergents vers la même URL canonique sans chaîne.

**Conditions de NA.** Aucun document concerné, inventaire et stratégie à l’appui.

**Limites.** rel=canonical est un signal fort, pas une directive garantie.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

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

## TS12 — La canonique choisie par Google est comparée à celle déclarée.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: search-console, html, intent.

**Applicabilité.** URL dont la canonique Google doit être comparée à la déclaration.

**Méthode.** Inspecter les URL prioritaires et consigner canonique utilisateur et canonique Google.

**Attendus.** Les deux valeurs sont datées et comparées ; chaque divergence dispose d’une qualification et d’une décision.

**Preuves.** Accord ou divergence qualifiée et traitée.

**Conditions de NA.** Google explicitement hors périmètre ; manque d’accès classé NT.

**Limites.** La canonique Google peut évoluer après une nouvelle exploration.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://support.google.com/webmasters/answer/9012289](https://support.google.com/webmasters/answer/9012289)

## TS13 — Le sitemap contient uniquement des URL absolues et canoniques utiles.

**Sévérité**: major. **Unité**: sitemap-set.

**Entrées requises**: sitemap, http, html, intent.

**Applicabilité.** Sitemaps utilisés pour les URL du périmètre.

**Méthode.** Parser chaque sitemap, compter les URL et comparer statut, canonique et indexabilité.

**Attendus.** Chaque entrée du périmètre est résolue, canonique selon la stratégie et destinée à l’indexation ; exclusions et limites de l’échantillon sont explicites.

**Preuves.** Inventaire sans redirection, 4xx, noindex ni doublon de canonique.

**Conditions de NA.** Aucun sitemap utilisé, inventaire et décision fournis.

**Limites.** La présence dans un sitemap ne garantit pas l’indexation.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

## TS14 — lastmod reflète une modification significative de la page.

**Sévérité**: minor. **Unité**: sitemap-set.

**Entrées requises**: sitemap, change-history.

**Applicabilité.** Sitemaps comportant lastmod.

**Méthode.** Comparer lastmod à l’historique éditorial ou au déploiement de contenu significatif.

**Attendus.** Chaque date testée correspond à une modification significative traçable ; la génération du fichier ne suffit pas.

**Preuves.** Horodatage ISO 8601 lié à une modification réelle, pas à la génération du fichier.

**Conditions de NA.** Aucun lastmod déclaré ; son absence n’est pas un défaut en soi.

**Limites.** Le moteur peut ignorer un lastmod jugé peu fiable.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping](https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping)

## TS15 — Les limites et découpages de sitemap sont respectés.

**Sévérité**: major. **Unité**: sitemap-set.

**Entrées requises**: sitemap.

**Applicabilité.** Fichiers et index de sitemap déclarés.

**Méthode.** Contrôler taille décompressée, nombre d’URL, index de sitemaps et encodage.

**Attendus.** Encodage et syntaxe sont valides ; limites de taille décompressée et de nombre d’entrées sont respectées pour chaque type de fichier.

**Preuves.** Maximum 50 000 URL et 50 Mo non compressés par sitemap.

**Conditions de NA.** Aucun sitemap utilisé dans le périmètre.

**Limites.** Un fichier valide peut contenir un mauvais périmètre éditorial.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://www.sitemaps.org/protocol.html](https://www.sitemaps.org/protocol.html)

## TS16 — Chaque page importante reçoit au moins un lien interne crawlable.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: crawl, inventory, intent.

**Applicabilité.** Pages identifiées comme importantes dans un inventaire.

**Méthode.** Crawler le site depuis les entrées publiques et lister les pages sans lien entrant HTML.

**Attendus.** Chaque page retenue possède au moins un lien entrant HTML résoluble depuis une page interne ; source et destination archivées.

**Preuves.** Source du lien, destination, ancre et statut de la page.

**Conditions de NA.** Aucune page importante concernée, justification et inventaire fournis.

**Limites.** Un lien présent ne prouve pas sa valeur éditoriale.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

## TS17 — Les liens essentiels utilisent un élément a avec href résoluble.

**Sévérité**: major. **Unité**: page.

**Entrées requises**: html, render, intent.

**Applicabilité.** Destinations de navigation déclarées essentielles.

**Méthode.** Comparer DOM source et rendu ; relever boutons, onclick et ancres sans href.

**Attendus.** Chaque destination essentielle testée possède un lien a avec href résoluble au stade observé ; les stades source et rendu sont distingués.

**Preuves.** Lien HTML crawlable vers chaque destination essentielle.

**Conditions de NA.** Aucune navigation concernée, périmètre justifié.

**Limites.** La crawlabilité ne garantit ni indexation ni classement.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

## TS18 — La profondeur et les pages orphelines sont mesurées sur un périmètre explicite.

**Sévérité**: major. **Unité**: url-set.

**Entrées requises**: crawl, sitemap, inventory, intent.

**Applicabilité.** Inventaire de référence déclaré, avec frontières du crawl.

**Méthode.** Comparer crawl, sitemap et export CMS ; qualifier chaque différence.

**Attendus.** Crawl et inventaire sont rapprochés ; profondeur observée et candidats orphelins sont qualifiés par famille ; aucune exhaustivité n’est inférée d’un seul crawl.

**Preuves.** Inventaire de référence identifié et daté, frontières du crawl, liens entrants, profondeurs observées et différences qualifiées.

**Conditions de NA.** Aucun graphe de navigation concerné, justification fournie ; inventaire manquant signifie NT.

**Limites.** Il n’existe pas de profondeur universelle garantissant un classement.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

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

## TS23 — Les annotations hreflang sont réciproques et incluent la page elle-même.

**Sévérité**: major. **Unité**: locale-cluster.

**Entrées requises**: hreflang, intent.

**Applicabilité.** Groupes hreflang déclarés.

**Méthode.** Construire les groupes de variantes et vérifier retour et auto-référence.

**Attendus.** Toutes les paires du groupe déclaré sont réciproques et chaque variante s’inclut ; frontières du groupe conservées.

**Preuves.** Groupe complet, réciproque et sans URL contradictoire.

**Conditions de NA.** Aucun groupe hreflang dans le périmètre.

**Limites.** Un groupe valide ne prouve pas que le moteur servira toujours la variante attendue.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

## TS24 — x-default représente une destination neutre ou la variante par défaut assumée.

**Sévérité**: minor. **Unité**: locale-cluster.

**Entrées requises**: hreflang, http, intent.

**Applicabilité.** Groupes où x-default est déclaré ou requis par la politique.

**Méthode.** Vérifier sa présence et sa fonction dans chaque groupe multilingue pertinent.

**Attendus.** La destination est accessible et correspond au parcours de sélection ou à la variante par défaut assumée.

**Preuves.** URL x-default documentée, accessible et cohérente avec le parcours.

**Conditions de NA.** Aucun x-default requis ou déclaré ; justification de politique conservée.

**Limites.** x-default n’est pas obligatoire dans tous les cas.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

## TS25 — Le contenu critique existe dans le HTML source ou devient observable après rendu.

**Sévérité**: blocking. **Unité**: page.

**Entrées requises**: html, render, intent.

**Applicabilité.** Gabarits dont les éléments critiques sont listés.

**Méthode.** Lister les éléments critiques puis comparer HTML source et DOM rendu dans les conditions déclarées. Une inspection Google facultative est une observation supplémentaire distincte.

**Attendus.** Chaque élément critique est observé au stade source ou rendu déclaré ; moteur, version et conditions sont conservés ; aucune équivalence avec Google n’est inférée.

**Preuves.** Titre, contenu, liens, canonical et données structurées présents au bon stade.

**Conditions de NA.** Aucun document HTML concerné dans le périmètre.

**Limites.** Un navigateur local ne reproduit pas exactement le rendu Google.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

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

## TS33 — Les erreurs, avertissements et usages non pris en charge sont distingués.

**Sévérité**: minor. **Unité**: page.

**Entrées requises**: structured-data, validator-output, intent.

**Applicabilité.** Balisages dont la validité et l’éligibilité sont évaluées.

**Méthode.** Tester syntaxe Schema.org et éligibilité Google séparément ; consigner les résultats.

**Attendus.** Erreurs de syntaxe, vocabulaire, critères du moteur et avertissements sont séparés ; chaque résultat a outil, version/date et décision.

**Preuves.** Rapport sans erreur bloquante et avertissements qualifiés.

**Conditions de NA.** Aucun balisage structuré dans le périmètre.

**Limites.** Le test de résultats enrichis ne valide pas tout le vocabulaire Schema.org.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)

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

## TS39 — Le CDN, Vary et la géolocalisation ne servent pas des signaux SEO contradictoires.

**Sévérité**: major. **Unité**: delivery-matrix.

**Entrées requises**: http, configuration, intent.

**Applicabilité.** Diffusion variant selon région, cache, appareil ou négociation.

**Méthode.** Comparer code, canonical, robots, langue et contenu depuis plusieurs régions ou clés de cache ; inspecter Vary, redirections géographiques et règles edge.

**Attendus.** La matrice de conditions est déclarée ; les signaux observés suivent la politique et les variantes restent accessibles selon celle-ci ; cases non testées visibles.

**Preuves.** Mêmes signaux SEO pour une même URL, ou variantes explicitement documentées et accessibles à Googlebot.

**Conditions de NA.** Absence de mécanisme de variation attestée par configuration.

**Limites.** Deux points de test ne couvrent pas toutes les routes, tous les POP ni toutes les clés de cache.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** RFC 9110 établit la sémantique de Vary et des réponses HTTP. Le comportement des pages adaptées à la région est documenté séparément par Google.

**Références**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110); [https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)

## TS40 — Les méthodes hreflang utilisées sont complètes et cohérentes.

**Sévérité**: major. **Unité**: locale-cluster.

**Entrées requises**: hreflang, sitemap, http, html, intent.

**Applicabilité.** Groupes utilisant au moins une méthode hreflang.

**Méthode.** Identifier toutes les méthodes publiées, vérifier les groupes et comparer leurs annotations lorsqu’elles coexistent.

**Attendus.** Chaque méthode utilisée couvre le groupe ; si plusieurs sont publiées, leurs annotations sont cohérentes ; aucune obligation d’une méthode unique.

**Preuves.** Groupes équivalents et réciproques ; si le sitemap est choisi, namespace xhtml et entrées par URL valides.

**Conditions de NA.** Aucune annotation hreflang dans le périmètre.

**Limites.** Cumuler HTML, en-têtes et sitemap n’apporte pas de bénéfice de recherche et augmente le risque de divergence.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

## TS41 — Les invariants SEO critiques sont rejoués automatiquement avant et après déploiement.

**Sévérité**: major. **Unité**: release.

**Entrées requises**: configuration, ci-output, change-history, intent.

**Applicabilité.** Déploiements soumis aux invariants SEO définis par le projet.

**Méthode.** Exécuter dans la CI un jeu d’URL représentatif : code final, redirections, robots/noindex, canonical, hreflang, contenu serveur, liens essentiels et JSON-LD.

**Attendus.** Commande et version, jeux d’URL, seuils, sorties avant/après et lien au déploiement sont conservés ; un test contradictoire prouve le comportement d’échec.

**Preuves.** Commande versionnée, sortie horodatée, seuil d’échec explicite et lien vers le déploiement concerné.

**Conditions de NA.** Aucun déploiement ou pipeline concerné dans le périmètre et la période.

**Limites.** Une CI valide des invariants connus ; elle ne remplace ni Search Console, ni les logs, ni une revue éditoriale.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Contrôle de gouvernance et de non-régression proposé par Edikka ; aucune documentation officielle unique ne prescrit ce pipeline complet.

**Références**: TSEP / Edikka method.

## TS42 — Chaque agent automatisé est gouverné selon son usage documenté.

**Sévérité**: major. **Unité**: policy.

**Entrées requises**: configuration, operator-docs, intent.

**Applicabilité.** Agents automatisés visés par la politique du site.

**Méthode.** Relier chaque jeton concerné à son usage documenté (recherche, action utilisateur, entraînement, publicité ou autre), à une décision et à un propriétaire ; conserver la source opérateur datée.

**Attendus.** Chaque jeton est relié à son usage documenté, à une décision, une source opérateur datée et un responsable ; usages publicitaires distingués si concernés.

**Preuves.** Table user-agent / finalité / règle / source opérateur / date de revue, sans confondre recherche en direct et entraînement.

**Conditions de NA.** Aucune politique d’agents dans le périmètre déclaré, raison fournie.

**Limites.** Une directive robots est déclarative ; elle ne prouve ni l’identité réelle du requérant ni le respect par tous les opérateurs.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots); [https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)

## TS43 — L’accès des crawlers autorisés est testé avec leur chaîne complète et rapproché des journaux.

**Sévérité**: major. **Unité**: request-set.

**Entrées requises**: http, logs, operator-docs, intent.

**Applicabilité.** Tests de politique d’accès pour des agents déclarés.

**Méthode.** Envoyer une requête GET avec le user-agent complet documenté, relever code et redirections, puis rechercher la requête dans les logs et vérifier l’identité lorsque l’opérateur publie une méthode.

**Attendus.** Chaîne complète, réponse et trace serveur sont rapprochées ; identité vérifiée ou non vérifiée explicite ; imitation jamais présentée comme visite réelle.

**Preuves.** Commande, chaîne complète, réponse finale, horodatage, trace serveur et statut d’identité vérifiée ou non vérifiée.

**Conditions de NA.** Aucun agent à tester dans la politique déclarée.

**Limites.** Imiter un user-agent ne reproduit pas l’infrastructure du crawler ; le test valide la politique applicative, pas la visite réelle de l’opérateur.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Référence technique ; les attendus TSEP restent une proposition éditoriale.

**Références**: [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots)

## TS44 — Le contenu critique et ses preuves restent accessibles sans dépendre d’une exécution JavaScript non documentée.

**Sévérité**: major. **Unité**: page.

**Entrées requises**: html, render, content, intent.

**Applicabilité.** Contenus destinés à des consommateurs automatisés déclarés.

**Méthode.** Comparer la réponse HTML brute, la version rendue et, lorsqu’elle existe, une ressource machine publique ; vérifier titres, faits, sources, liens et date de mise à jour.

**Attendus.** Les éléments critiques et leurs preuves sont accessibles dans le HTML serveur ou une ressource publique reliée ; cohérence et capacités supposées sont explicites.

**Preuves.** Faits et sources essentiels dans le HTML serveur ou une ressource publique reliée, avec une version cohérente et une URL stable.

**Conditions de NA.** Aucun contenu destiné à ces consommateurs dans le périmètre.

**Limites.** Un fichier llms.txt ou Markdown peut faciliter l’accès, mais aucun de ces fichiers ne garantit une citation ni un classement.

C exige tous les attendus sur le périmètre déclaré. NC exige une contradiction étayée ; sinon NT. NA exige la preuve de non-applicabilité.

**Portée des sources.** Portée partielle : la source Google documente le rendu JavaScript pour Google Search. Le contrôle étend prudemment la vérification à des consommateurs dont les capacités de rendu ne sont pas uniformément documentées.

**Références**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics); [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots); [https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)
