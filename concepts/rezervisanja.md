---
title: Rezervisanja u Crnoj Gori
created: 2026-04-13
updated: 2026-04-13
type: concept
tags: ['rezervisanje', 'rezerve', 'provizije', 'crna-gora', 'knjigovodstvo', 'propis', 'msfi']
sources: ['Zakon o računovodstvu', 'MSFI - MRS 37']
confidence: 0.8
last_confirmed: 2026-04-13
sources_count: 1
access_count: 0
last_accessed: null
supersedes: []
entity_type: concept
---

# Rezervisanja

## Pravni osnov

- Zakon o računovodstvu ("Službeni list CG" br. 052/16)
- MSFI - MRS 37 Rezervisanja, uslovne obaveze i uslovna imovina

## Šta su rezervisanja

Rezervisanja su obaveze za koje:
- Postoji sadašnja obaveza
- Vjerovatno je odliv resursa
- Može se pouzdano procijeniti iznos

### Rezervisanja ≠ Rezerve
- **Rezervisanja**: Obaveze (dugovi)
- **Rezerve**: Dio kapitala (vlasništvo)

## Vrste rezervisanja

### 1. Rezervisanja za sudske sporove
- Očekivani gubici od sporova
- Na osnovu procjene advokata

### 2. Rezervisanja za garancije
- Garancije kupljene robe
- Očekivani povrat robe

### 3. Rezervisanja za restrukturiranje
- Troškovi restrukturiranja
- Otpremnine, preraspored

### 4. Rezervisanja za otpremnine
- Otpremnine pri penzionisanju
- Naknade za neiskorištene godišnje odmore

### 5. Rezervisanja za poreske obaveze
- Neizvjesne poreske obaveze
- Poreski rizici

## Kada se priznaju

### Kriteriji:
1. Postoji sadašnja obaveza (pravna ili implicitna)
2. Vjerovatno je odliv ekonomskih koristi
3. Iznos se može pouzdano procijeniti

### NE priznaju se:
- Budući gubici (nisu sadašnja obaveza)
- Potencijalne obaveze (nisu obaveze)
- Obaveze koje se ne mogu procijeniti

## Knjigovodstveni tretman

### Nastanak rezervisanja:
```
Duguje     |     Potražuje
-----------------------
Trošak rezervisanja |   Rezervisanja
(63x)               |   (28x)
```

### Korištenje (isplata):
```
Duguje     |     Potražuje
-----------------------
Rezervisanja |   Novčani račun
(28x)       |
```

### Oslobađanje (višak rezervisanja):
```
Duguje     |     Potražuje
-----------------------
Rezervisanja |   Prihodi od rezervisanja
(28x)       |   (64x)
```

## Primjer: Rezervisanje za godišnje odmore

### Situacija:
- 10 zaposlenih
- Prosječna dnevna plata: 50 EUR
- Nepravdani dani: 3 dana po zaposlenom

### Izračun:
```
Rezervisanje = 10 × 3 × 50 = 1.500 EUR
```

### Knjiženje:
```
Duguje     |     Potražuje
-----------------------
Troškovi rezervisanj. 1.500 |   Rezervisanja za godišnje odmore 1.500
```

### Korištenje (u januaru):
```
Duguje     |     Potražuje
-----------------------
Rezervisanja za GO 500 |   Novčani račun / Zarade 500
```

### Oslobađanje (kraj godine):
```
Duguje     |     Potražuje
-----------------------
Rezervisanja za GO 1.000 |   Prihodi od rezervisanja 1.000
```

## Uslovne obaveze

### Šta su:
- Moguće obaveze koje nastaju ili ne nastaju
- Ne priznaju se u finansijskim izvještajima
- Objavljuju se u napomenama

### Primjeri:
- Sudski spor u toku (ishod neizvjestan)
- Garancija data za treće lice

## Poreski tretman

### Ograničenja:
- Rezervisanja moraju biti priznata po MSFI/MRS
- Poreska uprava može ne priznati neka rezervisanja
- Nastaju trajne ili privremene razlike

### Trajne razlike:
- Rezervisanja koja poreska uprava ne priznaje
- Dodaju se osnovici poreza

## Napomene u finansijskim izvještajima

### Obavezno objavljivanje:
- Iznos rezervisanja na početku i kraju
- Dodatna rezervisanja
- Korištena rezervisanja
- Oslobođena rezervisanja
- Opis prirode obaveze
