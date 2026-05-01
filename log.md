# Wiki Log

> Hronološki zapis svih wiki akcija. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`

## [2026-04-09] create | Wiki inicijalizovan
- Domena: Knjigovodstvo i poslovanje u Crnoj Gori
- Struktura kreirana sa SCHEMA.md, index.md, log.md
- Vlasnik: Željko Rajković, AGERA d.o.o.


## [2026-04-09] ingest | Početna dokumentacija iz raw foldera
- Ekstrahovano tekst iz 6 PDF dokumenata
- Kreirano 6 concept strana u concepts/
- Kreirano 3 entity strane u entities/
- Kreirana glavna strana: knjigovodstvo
- Ažuriran index.md

Fajlovi kreirani:
- concepts/knjigovodstvo.md
- concepts/registar-privrednih-subjekata.md
- concepts/naknade-centralni-registar.md
- concepts/registraciona-prijava.md
- concepts/spranje-novca.md
- concepts/registracioni-broj.md
- concepts/registar-stvarnih-vlasnika.md
- entities/centralni-registar.md
- entities/poreska-uprava.md
- entities/crna-gora.md


## [2026-04-09] ingest | DOCX/DOC dokumentacija
- Konvertovano 15 DOCX/DOC fajlova u TXT pomoću LibreOffice
- Kreirano 14 novih concept strana
- Svi fajlovi uspešno obrađeni

Fajlovi obrađeni:
- Odluka o osnivanju preduzetnika
- Odluka o osnivanju ustanove
- Statut DOO jednočlano
- Statut AD
- Ugovor o osnivanju DOO višečlano
- Ugovor o osnivanju OD
- Ugovor o osnivanju KD
- Pravila o osnivanju privrednih društava
- Pravila o diskvalifikaciji direktora
- Uslovi za imenovanje direktora
- Odluka o izmjeni statuta
- IRMS evidencija ovlašćenih lica
- PU Saopštenje 13.03.2026
- GPPFL rok predaje
- (još 2 duplikata preskočena)


## [2026-04-10] ingest | Novi fajlovi
- Novi PDF: IRMS autentifikacija i elektronski potpis → kreirana wiki strana
- Link cdm.me: NEUSPJEŠNO (Cloudflare zaštita - sajt blokira automated pristup)


## [2026-04-12] upgrade | LLM Wiki v2 - Faza 1: Frontmatter proširenje
- Proširen SCHEMA.md sa novim poljima: confidence, last_confirmed, sources_count,
  access_count, last_accessed, supersedes, entity_type
- Dodana entity_type taksonomija: institution, company, regulation, concept, person, document, procedure
- Dodana retention pravila i promotion pipeline
- Ažurirano svih 25 strana sa novim frontmatter poljima:
  - confidence: 0.7 (concept), 0.8 (regulation), 0.9 (institution)
  - entity_type: mapiran po sadržaju
  - access_count: 0, last_accessed: null
  - updated: 2026-04-12
- Svi fajlovi uspješno ažurirani, 0 grešaka


## [2026-04-12] upgrade | LLM Wiki v2 - Faza 3: Lint Engine
- Kreiran ~/wiki/scripts/lint.py
- Provjere: frontmatter, missing fields, broken links, orphans, stale confidence,
  low confidence, contradictions, entity_type
- Auto-fix mode: --fix flag za automatsko ažuriranje confidence decay-a
- Prvi run: 17 orphan strana (očekivano), 0 critical/high problema
- Tag 'crna-gora' na 24 strane - domain tag, normalno


## [2026-04-12] upgrade | LLM Wiki v2 - Faza 2: Knowledge Graph
- Kreiran ~/wiki/graph/entities.json (25 entiteta)
- Kreiran ~/wiki/graph/relations.json (81 outbound + 81 inbound = 162 veza)
- Kreiran ~/wiki/scripts/graph.py (graph traversal, stats, rebuild)
- Tipovi entiteta: concept(4), document(13), institution(3), regulation(5)
- Tipovi veza: vezan_za(59), zavisi_od(12), regulise(10)
- Najpovezaniji: knjigovodstvo(30), centralni-registar(29), registar-privrednih-subjekata(27)
- 17 orphan entiteta (dokumenti koji nemaju inbound linkove)


## [2026-04-12] upgrade | LLM Wiki v2 - Faza 5: Search Engine + CLI
- Kreiran ~/wiki/scripts/search.py - BM25 search sa confidence weighting
- Kreiran ~/wiki/scripts/wiki.py - jedinstveni CLI (wiki search/graph/lint/rebuild/top)
- Symlink ~/.local/bin/wiki za globalni pristup
- Search podržava: BM25 keyword + tag + entity name matching
- Pristup se auto-bilježi (access_count, last_accessed)
- Komande: wiki search, wiki graph, wiki lint, wiki rebuild, wiki top


## [2026-04-12] upgrade | LLM Wiki v2 - Faza 4: Automation Hooks
- Kreiran ~/wiki/scripts/auto_ingest.py - auto-obrada raw/ foldera (PDF/DOCX/TXT → wiki strane)
- Kreiran ~/wiki/scripts/decay.py - confidence retention decay (po tipu entiteta)
- Kreiran ~/wiki/scripts/hooks.py - session hooks (on_query, on_session_end, on_new_fact, on_contradiction, weekly_maintenance)
- Ažuriran ~/wiki/scripts/wiki.py sa novim komandama: ingest, decay, maintenance
- Auto-ingest: konvertuje PDF/DOCX → TXT, ekstrahuje PIB/firme/datume, kreira wiki strane
- Decay rate-ovi po tipu: institution(0.002/mj), procedure(0.003), regulation(0.004), company(0.006), concept(0.008)
- Cisceni duplikata nakon prvog ingest-a

## [2026-04-13] ingest | Zakon o privrednim društvima 2025
- Novi PDF: Zakon o privrednim društvima 2025 (926KB)
- Kreirana wiki strana: concepts/zakon-o-privrednim-drustvima-2025.md
- Confidence: 0.9 (visoka pouzdanost - službeni list)
- Tip: regulation (zakon)
- Ažuriran knowledge graph: 30 entiteta, 81 veza


## [2026-04-13] upgrade | Zakon o privrednim društvima 2025 - proširena dokumentacija
- Dodana detaljna dokumentacija za knjigovodstvo:
  - Tabela oblika društava (OD, KD, AD, DOO) sa oznakama i odgovornošću
  - Minimalni osnovni kapital: AD=25.000 EUR, DOO=1 EUR, OD/KD=nema minimuma
  - Osnivački akt i statut - obavezni za AD i DOO
  - Registracija u CRPS - postupak i dejstva
  - Elektronsko osnivanje (Član 10) - potpuno online
  - Članovi društva - uslovi i registracija
  - Prestanak društva - obaveze kod gubitka
- Tagovi: osnivanje, registracija
- Novi search rezultat: score=13.943 (najviši)


## [2026-04-13] create | Novi wiki dokumenti za osnivanje i upravljanje DOO
Kreirane 4 nove wiki stranice:

1. concepts/odluka-o-osnivanju-doo-jednoclano.md
   - Odluka za jednočlano DOO
   - Sadržaj, primjer strukture, potrebna dokumentacija
   - Notarska ovjera, CRPS registracija, poreski tretman

2. concepts/ugovor-o-osnivanju-doo-viseclano.md
   - Ugovor za višečlano DOO
   - Sadržaj, primjer strukture, prava i obaveze članova
   - Knjigovodstveni tretman osnivanja

3. concepts/statut-doo.md
   - Statut društva sa ograničenom odgovornošću
   - Obavezni elementi, primjer strukture
   - Prava članova, organi, raspodjela dobiti

4. concepts/odluka-o-promjeni-kapitala.md
   - Odluka o povećanju/smanjenju kapitala
   - Načini povećanja: novčani, nenovčani, konverzija, rezerve
   - Načini smanjenja: povlačenje, otpis, pokriće gubitka
   - Knjigovodstveni i poreski tretman


## [2026-04-13] create | Nova dokumentacija za knjigovodstvo i poslovanje

Kreirane nove wiki stranice:

OPERATIVNA DOCUMENTACIJA (odluke):
1. odluka-o-promjeni-sjedista.md - Promjena adrese društva
2. odluka-o-promjeni-djelatnosti.md - Promjena/ proširenje djelatnosti
3. odluka-o-promjeni-direktora.md - Imenovanje i razrješenje direktora
4. odluka-o-likvidaciji.md - Postupak likvidacije i brisanja

KNJIGOVODSTVO:
5. godisnji-izvjestaji.md - Godišnji finansijski izvještaji, rokovi, sastav
6. poreska-prijava.md - Pregled poreskih prijava (dobit, PDV, dohodak, zarade)
7. pdv-porez.md - Detaljno o PDV: stope, fakture, knjiženje, izvoz
8. plata-doprinosi.md - Plata, doprinosi, poreske stope, primjeri

REGISTRI I SISTEMI:
9. irms-sistem.md - Integralni registar ovlaštenja i elektronski potpis
10. crps-registar.md - Centralni registar: registracija, promjene, podaci

UKUPNO: +10 novih stranica u wiki


## [2026-04-13] create | Dodatna dokumentacija za knjigovodstvo

Kreirane nove wiki stranice:

STATUSNE PROMJENE I PRESTANAK:
11. spajanje-preoblikovanje.md - Spajanje, podjela, preoblikovanje društava
12. stecaj.md - Stečajni postupak, prijava, namirenje povjerilaca

CARINA I POTPORE:
13. carinski-postupci.md - Uvoz, izvoz, carinske deklaracije, PDV na uvoz
14. grantovi-dotacije.md - Državne potpore, EU fondovi, apliciranje

KNJIGOVODSTVENI KONCEPTI:
15. amortizacija.md - Metode, stope, knjiženje, poreski tretman
16. rezervisanja.md - Vrste, knjiženje, uslovne obaveze

   195|UKUPNO: +6 novih stranica
   196|
   197|
   205|