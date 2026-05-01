---
title: Plata i doprinosi u Crnoj Gori
created: 2026-04-13
updated: 2026-04-13
type: concept
tags: ['plata', 'doprinosi', 'pio', 'zdravstvo', 'nezaposlenost', 'porez', 'crna-gora']
sources: ['Zakon o doprinosima', 'Zakon o porezu na dohodak']
confidence: 0.8
last_confirmed: 2026-04-13
sources_count: 1
access_count: 0
last_accessed: null
supersedes: []
entity_type: concept
---

# Plata i doprinosi u Crnoj Gori

## Struktura bruto plate

```
BRUTO PLATA
|
+-- Porez na zarade
+-- Doprinos za PIO (zaposleni)
+-- Doprinos za zdravstvo (zaposleni)
+-- Doprinos za nezaposlenost (zaposleni)
|
= NETO PLATA (što zaposleni dobija na račun)
```

## Stopa doprinosa

### Na teret zaposlenog:

| Doprinos | Stopa | Osnovica |
|----------|-------|----------|
| PIO | 15.0% | Bruto plata |
| Zdravstvo | 8.5% | Bruto plata |
| Nezaposlenost | 1.0% | Bruto plata |
| **UKUPNO** | **24.5%** | |

### Na teret poslodavca:

| Doprinos | Stopa | Osnovica |
|----------|-------|----------|
| PIO | 6.0% | Bruto plata |
| Zdravstvo | 4.5% | Bruto plata |
| Nezaposlenost | 0.5% | Bruto plata |
| Fond rada | 0.2% | Bruto plata |
| **UKUPNO** | **11.2%** | |

### UKUPNI TROŠAK POSLODAVCA:
Bruto plata + 11.2% = Ukupni trošak

## Primjer obračuna

### Podaci:
- Bruto plata: 1.000 EUR

### Na teret zaposlenog:
- PIO (15%): 150 EUR
- Zdravstvo (8.5%): 85 EUR  
- Nezaposlenost (1%): 10 EUR
- **Ukupno doprinosi**: 245 EUR

### Porez na zarade:
- Osnovica: 1.000 - 245 = 755 EUR
- Stopa: 9-15-21% (zavisno od ukupnog godišnjeg dohotka)
- Za ovaj primjer: 9% × 755 = 68 EUR

### NETO:
- 1.000 - 245 - 68 = **687 EUR**

### Na teret poslodavca:
- PIO: 60 EUR
- Zdravstvo: 45 EUR
- Nezaposlenost: 5 EUR
- Fond rada: 2 EUR
- **Ukupno**: 112 EUR

### UKUPNI TROŠAK:
1.000 + 112 = **1.112 EUR**

## Porez na zarade

### Progresivna stopa (2026):

| Godišnji dohodak | Stopa |
|------------------|-------|
| Do 7.200 EUR | 9% |
| 7.200 - 14.400 EUR | 15% |
| Preko 14.400 EUR | 21% |

### Olakšice:
- Minimalna plata (75% od prosječne) - ne oporezuje se
- Za svako dijete: dodatno 70 EUR neoporezivo

### Obrazac za poreski izračun:
- PO-1: Podaci o zaposlenom
- GOD-1: Godišnja prijava

## Minimalna plata

- Trenutna minimalna plata u CG: ~450 EUR
- Ne oporezuje se do iznosa minimalne plate

## Knjigovodstveni tretman

### Trošak plate:
```
Duguje     |     Potražuje
-----------------------
Trošak zarade (611) |   Zarade (461)
Zaposleni - PIO (241) |  
Zaposleni - Zdravstvo (242) |
Zaposleni - Nezaposlenost (243) |
Porez na zarade (244) |
```

### Doprinosi poslodavca:
```
Duguje     |     Potražuje
-----------------------
Doprinosi za PIO (632) |   Obaveze za doprinose (281)
Doprinosi za Zdravstvo (633)|
Doprinosi za Nezaposlenost (634)|
Fond rada (635)          |
```

## Prijave i rokovi

| Prijava | Rok | Sadržaj |
|---------|-----|---------|
| PRIJAVA PPE | Mjesečno, do 15. | Plata, porez, doprinosi |
| GOD-1 | Mart | Godišnji poreski obračun |
| ZIR-1 | Mart | Godišnji izvještaj o doprinosima |

## Ugovori o djelu

### Doprinosi:
- PIO: 15.0% (kao za zaposlene)
- Zdravstvo: 8.5%
- Nezaposlenost: 1.0%
- Porez: 20% na iznos preko 150 EUR mjesečno

### Ograničenje:
- Maksimum 50% radnog vremena
- Ne može biti isti poslodavac kao za zaposlenje

## Bolovanje

### Naknada plate:
- Prvi mjesec: 60% od plate
- Drugi mjesec: 80% od plate
- Od trećeg: 100% od plate (iz Fonda)

### Doprinosi:
- Tokom bolovanja: poslodavac plaća doprinose
