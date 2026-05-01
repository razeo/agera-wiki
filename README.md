# AGERA Wiki — Baza znanja za knjigovodstvo i registraciju

Ovo je centralizovana baza znanja za **AGERA d.o.o.**, knjigovodstvenu agenciju koja pruža usluge registracije i vodjenja knjigovodstva u Crnoj Gori.

## Struktura

```
wiki/
├── README.md                 # Ovaj fajl
├── SCHEMA.md                 # Schema graph za Wiki 2
├── concepts/                 # Zakoni, propisi, pravila (Markdown)
├── documents/                # Originalni dokumenti (PDF, DOCX, DOC)
├── converted/                # Tekstualne verzija dokumenata (.txt)
├── templates/                # Šabloni za generisanje dokumenata
├── tools/                    # Generator dokumenta i alati
│   └── doo-registracija/     # DOO registracija workflow
├── scripts/                  # Wiki-management skriptovi
└── graph/                    # Entiteti i relacije za Wiki 2
```

## Kategorije

### `concepts/`
 Zakoni, podzakonski akti, statuti, odluke i drugi pravni koncepti u Markdown formatu. Svi sadrže metapodatke (kategorija, datum, izvor).

### `documents/`
 Originalni zvanični dokumenti u PDF i Word formatu (zakoni, odluke, statuti, forme). Ovo su izvorni fajlovi koji se koriste za referencu.

### `converted/`
 Čisti tekstualni ekvivalenti dokumenata iz `documents/` (prevedeni/ekstrahovani za brzu pretragu).

### `templates/`
Tekstualni šabloni za automatsko generisanje dokumenata (statut, odluka o osnivanju, itd.) koji se koriste u `tools/doo-registracija/`.

### `tools/doo-registracija/`
Python skripte i YAML konfiguracije za generisanje complete paketa dokumenata za registraciju d.o.o. u Crnoj Gori.

### `scripts/`
Skriptovi za održavanje wiki: lint, search, graph build, hooks.

## Korišćenje

- Brza pretraga: koristi `scripts/search.py` za pretragu po konceptima
-vizualizacija: `scripts/graph.py` generiše knowledge graph
- Generisanje dokumenata: pokreni `tools/doo-registracija/generator.py`

## Zašto ova struktura?

- **concepts/** su lako čitljivi i verzionisani (Markdown)
- **documents/** čuvaju izvorne zvanične dokumente
- **converted/** omogućavaju tekstualnu pretragu bez OCR-a
- **templates/** i **tools/** automatizuju repetitivne zadatke
- **scripts/** održavaju čistoću i konzistentnost

---

*Poslednja organizacija: May 2026*
