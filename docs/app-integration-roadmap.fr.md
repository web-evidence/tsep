# Dossier d’intégration — application TSEP et moteur 0.2.0-rc.1

## Portée et versionnement

Ce dossier fixe l’ordre souhaité pour étendre les parcours applicatifs existants au-delà de TS02. Il ne modifie pas le dépôt applicatif, ne prétend pas que les nouveaux parcours sont disponibles et ne lance aucun contrôle. Les priorités sont TS01 et TS04, puis TS07 et TS10. Réutiliser les règles et les contrats moteur présents ; ne dupliquer ni le moteur ni ses verdicts dans l’application.

L’application garde son propre numéro de version. Son verrou moteur doit enregistrer séparément la version TSEP 0.2.0-rc.1, l’empreinte de l’archive importée et les outils employés. Chaque reçu porte les versions app et moteur, les octets importés, le périmètre, la procédure, les preuves/sorties et les limites. Une réception de l’archive draft.47 n’est pas un reçu RC1.

## Ordre et prérequis

| Priorité | Contrôle et règles existantes | Prérequis du parcours | Sortie et limites |
| --- | --- | --- | --- |
| 1 | TS01-A01/A02 | Plan daté des URL canoniques et conditions de collecte ; GET final attribuable, horodatage, statut, chaîne de redirections et corps brut dont l’identité peut être comparée aux critères. Toute acquisition doit suivre le plan approuvé. | Évaluer uniquement la page et la réponse reçues. Une IP ou une capture ne représente pas le Googlebot ; l’absence/ambiguïté reste NT. |
| 2 | TS04-A01/A02 | Déclarer avant collecte l’origine, le client/crawler et le profil d’interprétation, la matrice routes/ressources et l’accès attendu. Importer robots.txt brut avec URL/date/chaîne et les réponses des ressources reliées. Conserver séparément politique, accès et revue du propriétaire. | Comparer la politique et l’accès aux seules cellules déclarées. robots.txt est un protocole de crawl, pas une protection d’accès. Aucun accès Google ni identité d’agent n’est déduit des fixtures. |
| 3 | TS07-A01/A02/A03 | Fixer objectif et client visé ; capter en contexte HTTP les en-têtes finaux, HTML source, robots requis et, lorsque nécessaire, états DOM planifiés liés à la même navigation, avec date, URL finale, version navigateur et erreurs. | Distinguer directives source, directives HTTP et états rendus. Les états absents ou non attribuables restent inconclusifs ; il faut pouvoir crawler la ressource pour lire ses directives. Aucun passage Google n’est prouvé. |
| 4 | TS10-A01–A04 | Déclarer stratégie et population/famille ; relier URL finale, canonical HTTP/HTML, sitemap, liens de crawl et contexte. Fournir les captures DOM si le rendu modifie les déclarations et une revue humaine liée pour A02. | Évaluer la cohérence de la famille déclarée seulement. canonical est un signal, pas une directive garantie ; un échantillon ne prouve ni l’exhaustivité du site ni l’indexation. |

## Import, export et rejeu

Avant activation du moteur, comparer version, empreinte, inventaire de fichiers et schéma à l’archive RC1 publiée. Vérifier que l’import refuse un paquet incomplet ou dont les empreintes divergent. Garder les originaux immuables et tracer leurs dates et provenances. L’export doit inclure tous les éléments référencés et un manifeste vérifiable ; le rejeu hors application doit restituer les mêmes résultats, sans réseau et sans lire les sources privées de l’app.

Les statuts de contrôle C/NC/NA/NT restent distincts des résultats atomiques pass/fail/not-applicable/inconclusive. Les preuves manquantes ne deviennent pas C ou NA. Un échec d’outil, une revue absente et une contradiction SEO sont des faits différents.

## État au RC1

La réception app TS03 r2 documentée concerne l’archive 0.1.0-draft.47, des entrées entièrement synthétiques et un rejeu hors application. RC1 exige son propre import/export/rejeu, consignés à l’empreinte RC1. TS01, TS04, TS07 et TS10 sont ici un plan de raccordement futur, pas des parcours reçus. Aucun nouveau contrôle ni audit de site réel n’est engagé dans ce dossier.
