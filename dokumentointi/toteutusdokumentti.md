# Toteutusdokumentti

## Ohjelman yleinen rakenne
Ohjelma koostuu selkeästi rajatuista moduuleista:
- **`board.py`** – hallinnoi pelilautaa, pisteitä ja siirtojen logiikkaa.  
- **`grid_ops.py`** – sisältää laudan siirrot (`left`, `right`, `up`, `down`) puhtaina funktioina, joita tekoäly käyttää nopeassa simulaatiossa.  
- **`heuristics.py`** – sisältää arviointifunktion, joka yhdistää useita heuristiikkoja (tyhjät, käärme, smoothness, merge, kulmabonus).  
- **`expectiminimax.py`** – toteuttaa Expectiminimax-algoritmin välimuisteineen ja dynaamisella syvyyssäädöllä.  
- **`autoplay.py`** – suorittaa automaattisesti tekoälyn pelaaman pelin komentoriviltä.  
- **`gui.py`** – vastaa yksinkertaisesta tekstipohjaisesta pelinäkymästä.

Rakenteen ansiosta jokainen osa voidaan testata, optimoida ja kehittää erikseen.

---

## Aika- ja tilavaativuudet
- **Aikavaativuus:** Expectiminimaxin aikavaativuus on eksponentiaalinen suhteessa hakusyvyyteen (*O(b^d × c)*, missä *b* = siirtojen määrä, *c* = satunnaisten syntypaikkojen määrä).  
  Hakua on optimoitu dynaamisella syvyyssäädöllä, välimuisteilla ja deterministisellä solujen valinnalla, joten käytännössä tekoäly toimii nopeasti 4–6 tason haulla.  
- **Tilavaativuus:** 4×4-ruudukko on kiinteä, joten muistinkulutus pysyy vakaana. Välimuistit (`cache`, `eval_cache`) käyttävät eniten muistia, mutta parantavat suorituskykyä merkittävästi.

---

## Suorituskyky ja optimoinnit
- **Grid-operaatiot:** Kaikki neljä siirtosuuntaa toteutetaan nyt yhdellä yleisellä funktiolla `_move_generic`, joka vähentää koodin toistoa ja parantaa nopeutta.  
- **Välimuistit:** Expectiminimax käyttää kahta välimuistia (hakutulokset ja heuristiikka-arvot), jotka estävät toistuvan laskennan.  
- **Heuristiikat:** Parannettu `evaluate`-funktio yhdistää useita mittareita painotetusti ja hyödyntää log2-arvoja, mikä tekee arviosta realistisen ja tehokkaan.  
- **Dynaaminen hakusyvyys:** Syvyys kasvaa, kun laudalla on paljon tyhjiä tai suuria laattoja, ja pienenee loppuvaiheessa, jolloin nopeus pysyy hyvänä.

---

## Suorituskyky ja Big-O-analyysi
- **Expectiminimax:**  
  - Aikavaativuus: *O(b^d × c)*  
  - Tilavaativuus: *O(b^d)*  
  - Käytännössä: kiinteällä 4×4-laudalla ja dynaamisella syvyydellä peli toimii sujuvasti.  
  - Alfa-beeta -karsintaa ei tarvita, sillä todennäköisyydet tekevät hakuavaruudesta jo valmiiksi tasapainoisemman.  

---

## Mahdolliset puutteet ja kehitysehdotukset
- Välimuisti voitaisiin laajentaa käyttämään **Zobrist-hashia**, jolloin avaimet olisivat nopeampia ja pienempiä.  
- **Iteratiivinen syvyyshaku** voisi parantaa reagointiaikojen tasaisuutta.  
- **Heuristiikkojen painot** voisi säätää automaattisesti datan perusteella (esim. koneoppimisella).  

---

## Suuret kielimallit (ChatGPT)
Tässä projektissa käytin **ChatGPT (GPT-5)** -mallia:
- auttamaan dokumentaation kirjoittamisessa ja rakenteen selkeyttämisessä  
- optimoimaan `expectiminimax.py`- ja `grid_ops.py`-moduulien rakennetta  
- ehdottamaan tehokkaampia heuristiikkayhdistelmiä  

Koodi ja lopullinen algoritmi on kuitenkin suunniteltu, toteutettu ja testattu itsenäisesti.

---

## Lähteet
- Yun Nie, Wenqi Hou & Yicheng An: *AI Plays 2048* (kurssin ohjeissa)  
- [2048 Using Expectimax (University of Massachusetts Lowell)](https://www.cs.uml.edu/ecg/uploads/AIfall14/vignesh_gayas_2048_project.pdf)  
- [Wikipedia: Expectiminimax](https://en.wikipedia.org/wiki/Expectiminimax)
