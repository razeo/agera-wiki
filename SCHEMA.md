---
title: Wiki Schema
created: 2026-04-09
updated: 2026-04-12
type: schema
tags: [meta, setup]
---

# Wiki Schema — Knjigovodstvo Crna Gora

## Domena
Knjigovodstvo, porezi, računovodstvo i poslovanje u Crnoj Gori. Pravni okvir, propisi, poreska administracija, d.o.o., d.o.o. sa jednim osnivačem, preduzetnici, fizička lica.

## Konvencije
- Imena fajlova: mala slova, crtice, bez razmaka (npr. `porez-na-dohodak.md`)
- Svaki wiki članak počinje YAML frontmatter (vidi ispod)
- Koristi [[wikilinks]] za linkove između strana (minimum 2 outbound linka po strani)
- Prilikom ažuriranja strane, uvijek bumpaj `updated` datum
- Svaka nova strana mora biti dodata u `index.md` pod odgovarajućom sekcijom
- Svaka akcija se dodaje u `log.md`

## Frontmatter
```yaml
---
title: Naslov Strane
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [iz taxonomy ispod]
sources: [raw/articles/izvor.md]
# --- LLM Wiki v2 polja ---
confidence: 0.7          # 0.0-1.0, koliko je činjenica pouzdana
last_confirmed: YYYY-MM-DD # zadnji put potvrđeno iz izvora
sources_count: 1          # koliko izvora podržava ovu stranu
access_count: 0           # koliko puta pristupljeno/query-ano
last_accessed: YYYY-MM-DD # zadnji put pristupljeno
supersedes: []            # liste strana koje ova strana zamjenjuje
entity_type: concept      # tip u knowledge graph-u
---
```

## Polja za Confidence i Retention

### confidence (0.0 - 1.0)
- **0.9-1.0**: Potvrđeno iz više izvora, zakonski propis, trenutno važeće
- **0.7-0.9**: Iz jednog pouzdanog izvora, vjerovatno tačno
- **0.5-0.7**: Nepotpuno, iz sekundarnog izvora, treba verifikaciju
- **0.3-0.5**: Zastarjelo, sumnjivo, potrebno ažuriranje
- **< 0.3**: Fading — treba arhivirati ili obrisati

### Retention pravila
- Svaki pristup (access) → bump access_count, update last_accessed
- Confidence decay: -0.05 svakih 6 mjeseci bez pristupa
- Novi izvor koji potvrđuje → confidence + 0.1 (max 1.0)
- Kontradikcija detektovana → confidence - 0.2
- confidence < 0.3 AND last_accessed > 12 mjeseci → status "archive"
- Procedural memory (workflow/pattern) → decay sporije: -0.02/6mj

### Promotion (konsolidacija)
- Working memory (recent raw) → Episodic: nakon 1 session
- Episodic → Semantic: nakon 3+ potvrda iz različitih sesija
- Semantic → Procedural: ponavljanje istog workflow-a 5+ puta

## Entity Types (za Knowledge Graph)
- **institution**: Institucija (Poreska uprava, Centralni registar...)
- **company**: Firma/preduzeće (AGERA d.o.o., klijenti...)
- **regulation**: Zakon/propis/pravilnik
- **concept**: Koncept/tema (PDV, amortizacija...)
- **person**: Osoba (direktor, osnivač...)
- **document**: Dokument (faktura, bilans, statut...)
- **procedure**: Procedura/workflow

## Tag Taxonomy
- **Poreski sistem**: pdv, porez-na-dohodak, porez-na-dobit, lokalni-porezi
- **Pravni oblici**: doo, preduzetnik, ad, zadruga
- **Institucije**: poreska-uprava, crna-gora, ziro-racun
- **Dokumentacija**: faktura, bilans, poreska-prijava, finansijski-izvestaj
- **Uslovi**: paušalno-oporezivanje, kapital, dividende
- **Veze**: konta, knjigovodstvo, računovodstvo, amortizacija

## Pravila za Strane
- **Kreiraj stranu** kada entitet/koncept pominje u 2+ izvora ILI je centralan za jedan izvor
- **Dodaj na postojeću** kada izvor pominje nešto što već postoji
- **NE kreiraj stranu** za prolazne pominjanja, manje detalje
- **Podijeli stranu** kada pređe ~200 linija

## Entitet Strane
Jedna strana po notable entitetu. Uključuje:
- Pregled / šta jeste
- Ključne činjenice i datumi
- Veze sa drugim entitetima ([[wikilinks]])
- Reference izvora

## Koncept Strane
Jedna strana po konceptu ili temi. Uključuje:
- Definicija / objašnjenje
- Trenutno stanje znanja
- Otvorena pitanja ili debate
- Srodni koncepti ([[wikilinks]])

## Knowledge Graph Pravila
- Svaka strana MORA imati `entity_type`
- Relacije se kreiraju na osnovu [[wikilinks]] i semantike
- Tipovi relacija: regulise, zavisi_od, koristi, supersedes, vezan_za, clan, vlasnik
- Graph se ažurira pri svakom ingest-u
