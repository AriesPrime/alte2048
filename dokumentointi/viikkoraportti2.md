# Viikkoraportti - Viikko 2

1. **Mitä olen tehnyt tällä viikolla?**  
   Toteutin projektin päämoduulit: `autoplay.py`, `board.py`, `cli.py`, `expectiminimax.py`, `gui.py` ja `heuristics.py`. Näiden avulla peli toimii kokonaisuudessaan tekstikäyttöliittymällä (käytän itse Windowsin PowerShelliä) ja tekoäly osaa pelata peliä Expectiminimax-algoritmilla. Aloitin myös ensimmäisten yksikkötestien kirjoittamisen (`test_autoplay.py`) ja varmistin, että testit toimivat.  

2. **Miten ohjelma on edistynyt?**  
   Ohjelma on edennyt selvästi: peruslogiikka on valmis ja tekoäly pystyy pelaamaan pelin loppuun asti. Riippuen siitä, mitä arvoa käytetään depth-parametrina, tekoäly pääsee suhteellisen helposti ja nopeasti korkeisiin lukuihin ja saavuttaa 2048-laatan. Lisäksi testausympäristö on alustettu ja ensimmäiset toimivat testit kirjoitettu. Projektin rakenne on nyt melko selkeä ja sitä on helppo laajentaa lisäämällä testejä ja parantamalla heuristiikoita.  

3. **Mitä opin tällä viikolla / tänään?**  
   Opin kirjoittamaan kommentteja docstring-tyylillä sekä unittestin perusteet Pythonissa.  

4. **Mikä jäi epäselväksi tai tuottanut vaikeuksia?**  
   Aluksi testien ajaminen ei onnistunut, koska hakemistojen rakenne ei ollut oikein ja `src`-moduuli ei löytynyt. Siirtelin tiedostoja vähäsen niin alkoi toimimaan.

5. **Mitä teen seuraavaksi?**  
   Jatkan yksikkötestien kirjoittamista muille moduuleille (`board`, `heuristics`, `expectiminimax`, `gui`). Lisäksi voin alkaa miettiä heuristiikkafunktioiden parantamista ja pelin suorituskyvyn optimointia. Koska projekti on edennyt hyvässä tempossa, voisin myös alkaa suunnitella graafista käyttöliittymää joko pygame-kirjaston avulla tai tekemällä yksinkertaisen HTML-sivun. Työstän myös projektin testikattavuutta.

---

**Tämän viikon työaika:** n. 17 tuntia  
