# Testausdokumentti

## Yksikkötestauksen kattavuusraportti

Projektin testaus on toteutettu Pythonin `pytest`-kirjastolla.  
Koodin testikattavuus on mitattu `coverage`-työkalulla.  
Alla oleva kuva (`test_coverage.png`) näyttää yksityiskohtaisen kattavuusraportin:

![Testikattavuusraportti](test_coverage.png)

**Kattavuus:**
- Kokonaiskattavuus: **~99 %**
- Moduulit `autoplay`, `heuristics`, `gui` ja `grid_ops` saavuttivat lähes **100 % kattavuuden**.  
- Pieni osa riveistä jäi testaamatta `board.py`- ja `expectiminimax.py`-moduuleissa.  
  Nämä rivit liittyvät lähinnä erittäin harvinaisiin pelitilanteisiin tai välimuistin sisäisiin haaroihin, joita ei esiinny normaalissa pelissä.

---

## Mitä on testattu ja miten?

### **Pelilauta (`board.py`)**
- Testattiin pelin alustus (`new_game`), siirrot eri suunnissa ja pisteiden laskenta.  
- Varmistettiin, että siirtojen jälkeen laudan tila päivittyy oikein ja pisteet kasvavat.  
- Tarkistettiin myös, että uudet laatat syntyvät oikeilla todennäköisyyksillä (0.9 = 2, 0.1 = 4).

### **Ruudukko-operaatiot (`grid_ops.py`)**
- Testattiin kaikki siirtosuunnat (`left`, `right`, `up`, `down`).  
- Varmistettiin, että funktiot eivät muuta alkuperäistä ruudukkoa (puhtaus).  
- Yhdistämislogiikka (`_compress_line_left`) testattiin kattavasti useilla syötteillä.  
- Näiden funktioiden avulla varmistettiin myös, että tekoäly pystyy arvioimaan siirtoja ilman raskaita `GameState`-kopioita.

### **Heuristiikat (`heuristics.py`)**
- Testattiin kaikki heuristiikkakomponentit:
  - `count_empties`: tyhjien ruutujen määrä.  
  - `snake_score`: neljän suunnan käärmemäinen monotonia, joka suosii kulmissa olevia suuria laattoja.  
  - `smoothness`: vierekkäisten laattojen log-arvojen ero.  
  - `merge_potential`: samanarvoisten vierekkäisten laattojen määrä.  
  - `corner_bonus`: lisäpiste, jos suurin laatta on kulmassa.  
- Testit varmistavat oikean suuntaisen vaikutuksen (esim. enemmän tyhjiä → parempi, kulma → parempi, yhdistymispotentiaali → parempi).  
- Uusittu testaus ei perustu enää kiinteisiin numeerisiin arvoihin, vaan vertailee tilanteiden välisiä suhteita, mikä tekee testeistä robustimpia.

### **Tekoälyalgoritmi (`expectiminimax.py`)**
- Testattiin keskeiset osat:
  - Hajautusavaimen (`make_key`) deterministisyys.  
  - Välimuistin (`cache` ja `_eval_cache`) käyttö ja osumat.  
  - Lehtisolmun arvonlaskenta (`leaf_value`).  
  - Dynaamisen hakusyvyyden sääntö (`dynamic_depth`), joka mukautuu tyhjien ruutujen ja suurimman laatan mukaan.  
  - CHANCE-solmun (`exp_value`) odotusarvon laskenta eri todennäköisyyksillä.  
  - MAX-solmun (`max_value`) valintalogiikka ja järjestetty siirtojen käsittely.  
  - Parhaan siirron valinta (`best_move_expecti`), joka hyödyntää heuristiikkapohjaista esijärjestystä.  
- Kaikki funktiot testattiin erikseen sekä välimuistilla että ilman sitä.

### **Automaattipeli (`autoplay.py`)**
- Testattiin automaattisesti pelaavan tekoälyn pelisilmukka:  
  - Pelin käynnistyminen ja silmukan kulku ilman virheitä.  
  - `render`, `print_ai_move` ja `print_final` kutsutaan oikeassa järjestyksessä.  
  - Pelin eteneminen päättyy oikea-aikaisesti, kun peli on ohi.  
- Testattiin myös komentorivikäyttö (`--depth`), joka määrittää haun syvyyden.

### **Päästä päähän -testit (E2E)**
- Käytetään todellista `GameState`-logiikkaa, ei mockattua pelitilaa.  
- Satunnaisuus (`random.choice`, `random.random`) on kontrolloitu `unittest.mock.patch`illa, jotta tulokset ovat täysin toistettavia.  
- Tekoäly tekee useita siirtoja peräkkäin, ja testit varmistavat, että peli etenee loogisesti ja pisteet kasvavat.  
- Koska projekti ei enää sisällä `minimax`-moduulia, E2E-testit kohdistuvat vain `expectiminimax`-algoritmiin.

---

## Millaisilla syötteillä testaus tehtiin?

- **Pienet, käsin määritellyt pelitilat:**  
  - Tyhjä lauta  
  - Yksi laatta  
  - Täysi lauta ilman mahdollisia siirtoja  
  - Laudat, joissa yhdistyminen tapahtuu vain tietyssä suunnassa  

- **Satunnaisuuden kontrollointi:**  
  `random.choice` ja `random.random` patchattiin, jotta laatat syntyvät aina samoihin paikkoihin ja arvoilla (2 tai 4).  

- **Heuristiikkatestit:**  
  Käytettiin esimerkkilautoja, joissa heuristiikan eri tekijät (tyhjyys, kulmat, tasaisuus) voidaan arvioida selkeästi.  

- **Tekoälytestit:**  
  - Pienet pelitilat, joissa tekoälyn optimaalinen siirto on yksiselitteinen.  
  - Laudat, joissa välimuistin pitäisi osua (cache hit).  
  - E2E-testit, joissa tekoäly suorittaa useita siirtoja kontrolloidussa ympäristössä.

---

## Miten testit voidaan toistaa?

Projektin testit voidaan suorittaa komentoriviltä projektin juurihakemistossa:

```bash
coverage run --branch -m pytest src
coverage report -m
