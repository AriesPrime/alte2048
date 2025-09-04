# Määrittelydokumentti

## Ohjelmointikieli
Projektissa käytän **Pythonia**. Käyttöliittymä on yksinkertainen tekstipohjainen ratkaisu, jossa pelilauta tulostetaan terminaaliin ja pelaaja voi antaa siirtoja näppäimistön kautta.  

Hallitsen myös muita kieliä kuten **Java**, **JavaScript**, **SQL** ja jonkun verran **C**.

## Algoritmit ja tietorakenteet
Projektin keskiössä on **Expectiminimax-algoritmi**, joka sopii 2048-peliin, koska siinä on yksi pelaaja ja satunnaiselementti (uuden laatan ilmestyminen). Algoritmi arvioi sekä pelaajan mahdolliset siirrot että satunnaistapahtumien todennäköisyydet.  

Tietorakenteena käytän 4×4-kokoista kaksidimensionaalista listaa (Python `list`), jossa pidetään kirjaa laudan tilasta. Lisäksi käytän yksinkertaisia apufunktioita siirtojen ja yhdistämisten toteuttamiseen.

## Ratkaistava ongelma
Tavoitteena on toteuttaa toimiva 2048-peli, jossa tekoäly osaa tehdä hyviä siirtoja Expectiminimax-algoritmin avulla. Ydinongelma on algoritmin suunnittelu ja heuristiikkojen rakentaminen siten, että peliä voidaan pelata pitkälle ja korkeilla pistemäärillä.

## Syötteet ja niiden käyttö
- **Pelaajan syötteet:** näppäimistön nuolinäppäimet tai WASD.  
- **Satunnaissyöte:** laudalle ilmestyvät uudet laatat (2 todennäköisyydellä 0.9 tai 4 todennäköisyydellä 0.1).  
- **Tekoälyn syöte:** Expectiminimax valitsee seuraavan siirron, kun AI:ta pyydetään.

## Tavoitteena olevat aika- ja tilavaativuudet
- **Aikavaativuus:** Expectiminimaxin aikavaativuus kasvaa eksponentiaalisesti syvyyden mukaan, koska jokaisesta tilasta haarautuu pelaajan siirrot ja satunnaiset tapahtumat. Käytännössä rajoitan hakusyvyyden 4–6 kerrokseen.  
- **Tilavaativuus:** Laudan koko on vakio (4×4), joten muistinkulutus on vähäinen. Suurin osa muistista kuluu hakupuun rakenteeseen.  
- Käytän heuristiikkafunktiota estimoimaan tilanteen hyvyyttä, jotta peliä ei tarvitse laskea loppuun asti.

## Heuristiikat
Pelitilanteen arviointi tehdään seuraavilla heuristiikoilla:
1. Tyhjien ruutujen määrä  
2. Suurimman laatikon sijainti kulmassa  
3. Monotonia riveissä ja sarakkeissa (arvot suurenevat tai pienenevät johdonmukaisesti)  
4. Yhdistämismahdollisuudet (kuinka monta siirtoa johtaa yhdistämiseen)  

Näitä voidaan yhdistää painotetuksi summaksi arviointifunktiossa.

## Lähteet
- Yun Nie, Wenqi Hou & Yicheng An: *AI Plays 2048* (artikkeli kurssin ohjeissa)  

---

## Harjoitustyön ydin
Harjoitustyön ydin on **tekoälyalgoritmin (Expectiminimax) toteutus 2048-pelissä**. Käyttöliittymä on yksinkertainen tekstipohjainen, mutta se riittää, koska suurin osa ajasta menee tekoälyn ja heuristiikkojen suunnitteluun ja optimointiin.

---

## Opinto-ohjelma
Tietojenkäsittelytieteen kandidaatti (TKT).
