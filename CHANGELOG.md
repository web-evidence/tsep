# Change history / Historique

## 0.1.0-draft.1 — 2026-10-09 — unpublished candidate

Initial independent version sequence derived from Edikka grid 1.1. The 44 IDs and
original FR/EN files are retained, with source hashes. Add bilingual applicability,
acceptance, NA conditions, input requirements, evidence profiles, report schema,
conservative gating, EARL companion, examples and report-interchange tests.
Original software: Apache-2.0; protocol text/data: CC-BY-4.0.

This is a new interpretation contract, not an editorial patch of the 1.1 grid.
Every control gains explicit acceptance and scope rules. Material clarifications:

- TS04: robots.txt 200 is not universally mandatory; evaluate effective policy.
- TS16/TS18: an authoritative inventory is required for claims about a population;
  a crawl cannot establish that inventory's completeness.
- TS19/TS20: policy/configuration inputs prevent a public-only conformance claim.
- TS25: local rendering and Google inspection are separate observations.
- TS32: do not require every example entity type from the legacy grid.
- TS34: field evidence can come from CrUX, Search Console or RUM; C establishes
  correct measurement/reporting, not that measured performance is good.
- TS37: HSTS scope is a documented policy decision; preload is not mandatory.
- TS40: multiple hreflang methods are allowed if complete and consistent.
- TS42: distinguish documented purposes including advertising where applicable.
- All controls: no implied automatic implementation; no global GO from a partial
  probe. NT is split into unstarted and inconclusive for EARL export.
- Gate: any nonblocking NT now prevents GO (INCOMPLETE); all-NA is INCOMPLETE.

The technical references inherited from grid 1.1 have not all been freshly
revalidated. New design observations about robots.txt, hreflang, CrUX, ACT, EARL
and ASVS were checked on 2026-10-09 in the local development recipe. No market
data, independent review, public repository, DOI or adopter is asserted.

### Français

Première version propre à TSEP, dérivée de la grille 1.1 sans réécrire ses fichiers
historiques. Chaque contrôle reçoit des attendus et un périmètre explicites : il
s’agit d’un nouveau contrat, pas d’un renommage. Les précisions ci-dessus modifient
notamment les accès requis pour TS16/18/19/20 et évitent des exigences excessives
sur robots.txt, les entités Schema.org et les méthodes hreflang. TS34 mesure la
qualité de lecture des données, pas une performance nécessairement bonne.

Toute inconnue non bloquante empêche désormais le GO ; tous les résultats NA ne
valent pas une recette réussie. Les références historiques ne sont pas toutes
revérifiées. Aucune publication, adoption, collecte ou revue indépendante nouvelle.
