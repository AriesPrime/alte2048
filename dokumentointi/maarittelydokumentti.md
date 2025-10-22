# Määrittelydokumentti

## Ohjelmointikieli
Projektissa käytän **Pythonia**. Käyttöliittymä on yksinkertainen tekstipohjainen ratkaisu, jossa pelilauta tulostetaan terminaaliin ja tekoäly pelaa automaattisesti ilman graafista rajapintaa.  

Hallitsen myös muita kieliä kuten **Java**, **JavaScript**, **SQL** ja jonkin verran **C**.

---

## Algoritmit ja tietorakenteet
Projektin keskiössä on **Expectiminimax-algoritmi**, joka sopii 2048-peliin, koska siinä on yksi pelaaja ja satunnaiselementti (uuden laatan ilmestyminen).  
Algoritmi arvioi sekä pelaajan mahdolliset siirrot että todennäköisyyksiin perustuvat satunnaistapahtumat (2 tai 4 -laatan syntyminen).  

Tietorakenteena käytän kiinteää **4×4-kokoista kaksidimensionaalista listaa (`list[list[int]`)**, jossa pidetään kirjaa laudan tilasta.  
Siirtojen simulointi on erotettu omaan moduuliin **`grid_ops.py`**, jossa laudan liikkeitä käsitellään puhtailla funktioilla ilman olioiden kopiointia. Tämä tekee algoritmista merkittävästi nopeamman ja vähentää muistinkulutusta.

---

## Ratkaistava ongelma
Tavoitteena on toteuttaa tehokas ja älykäs tekoäly, joka pelaa 2048-peliä mahdollisimman pitkälle ja saavuttaa korkeita pistemääriä.  
Haasteena on yhdistää **hakualgoritmin tehokkuus** ja **heuristiikkojen laatu**, jotta tekoäly osaa tasapainottaa riskin ja hyötyä satunnaisissa tilanteissa.

---

## Syötteet ja niiden käyttö
- **Pelaajan syötteet:** Peliä voi ajaa automaattisesti tekoälyn ohjaamana (komentoriviltä `autoplay.py`).  
- **Satunnaissyöte:** Uudet laatat ilmestyvät laudalle arvoilla 2 (90 %) tai 4 (10 %).  
- **Tekoälyn syöte:** Expectiminimax-haku arvioi eri siirtovaihtoehdot ja valitsee parhaan.

---

## Aika- ja tilavaativuus
- **Aikavaativuus:** Expectiminimaxin aikavaativuus kasvaa eksponentiaalisesti hakusyvyyden myötä. Käytännössä syvyys on rajattu noin 4–6 kerrokseen, mikä tuottaa hyviä tuloksia ilman hidastumista.  
  Dynaaminen hakusyvyys mukautuu tilanteen mukaan (enemmän tyhjiä tai iso laatta kulmassa → syvempää hakua).  
- **Tilavaativuus:** Laudan koko on vakio (4×4), joten muistinkulutus pysyy rajattuna. Eniten muistia kuluu välimuisteihin ja heuristiikka-arvojen tallennukseen.  

Optimointien ansiosta (välimuisti, heuristiikkojen uudelleenkäyttö ja tehokkaat siirtofunktiot `grid_ops.py`:ssa) tekoäly pystyy arvioimaan tuhansia pelitiloja sekunnissa.

---

## Heuristiikat
Arviointifunktio yhdistää useita tekijöitä:
1. **Tyhjien ruutujen määrä** – enemmän tyhjää tilaa mahdollistaa liikkumisen ja yhdistämisen.  
2. **Käärmemäinen painotus (monotonicity)** – suosii suurten laattojen sijoittamista kulmiin ja arvojen pientä vaihtelua riveittäin.  
3. **Tasaisuus (smoothness)** – palkitsee vierekkäisiä laattoja, joiden log2-arvojen erot ovat pieniä.  
4. **Yhdistymispotentiaali** – rohkaisee samanarvoisia laattoja vierekkäin.  
5. **Kulmabonus** – antaa lisäpisteitä, jos suurin laatta on kulmassa.  

Painotettu yhdistelmä näistä tekijöistä ohjaa tekoälyä tehokkaasti pitkissä peleissä.

---

## Mahdolliset puutteet ja kehitysehdotukset
Tekoälyn suorituskykyä voisi edelleen parantaa:
- **Iteratiivisella syvyyshaulla (iterative deepening)** tai **aikarajoitetulla haulla**, jolloin tekoäly pelaa reaaliajassa ilman kiinteää syvyysrajaa.  
- **Monisäikeisyydellä** (parallelisointi), jolloin eri siirrot voidaan arvioida samanaikaisesti.  
- **Painokertoimien automaattisella optimoinnilla**, esimerkiksi koneoppimisen avulla.

---

## Lähteet
- Yun Nie, Wenqi Hou & Yicheng An: *AI Plays 2048* (kurssin ohjeissa)  
- [2048 Using Expectimax (University of Massachusetts Lowell)](https://www.cs.uml.edu/ecg/uploads/AIfall14/vignesh_gayas_2048_project.pdf)  
- [Wikipedia: Expectiminimax](https://en.wikipedia.org/wiki/Expectiminimax)

---

## Harjoitustyön ydin
Harjoitustyön ydin on **Expectiminimax-tekniikkaan perustuvan 2048-tekoälyn toteutus ja optimointi**.  
Tärkeimmät osa-alueet ovat hakualgoritmin tehokkuus, heuristiikkojen laatu ja puhtaan rakenteen ylläpito (`grid_ops`, `heuristics`, `expectiminimax`).

---

## Suurten kielimallien käyttö (ChatGPT)
Hyödynsin **ChatGPT:tä (GPT-5)**:
- Koodin optimointiin (erityisesti välimuistit, siirtofunktiot ja heuristiikat).  
- Dokumentaation rakenteen ja kielen yhtenäistämiseen.  
- Erilaisten heuristiikkavaihtoehtojen vertailuun.  

Kaikki koodi, algoritmit ja testit on kuitenkin toteutettu ja validoitu itsenäisesti.

---

## Opinto-ohjelma
Tietojenkäsittelytieteen kandidaatti (TKT).
