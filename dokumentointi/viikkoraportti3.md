# Viikkoraportti - Viikko 3

1. **Mitä olen tehnyt tällä viikolla?**  
   Toteutin projektiin uuden tekoälyalgoritmin: Minimaxin, joka toimii Expectiminimaxin rinnalla vaihtoehtoisena hakumenetelmänä. Kirjoitin myös kaikki tarvittavat yksikkötestit kaikille moduuleille (`board`, `heuristics`, `expectiminimax`, `minimax`, `gui`, `autoplay`) ja varmistin, että testit kattavat keskeiset toiminnallisuudet. Suoritin kattavuusmittauksen `coverage`-työkalulla ja sain lähes täydellisen kattavuuden. Lisäksi kirjoitin **testausdokumentin**, jossa kuvasin mitä on testattu, miten ja millä syötteillä.  

2. **Miten ohjelma on edistynyt?**  
   Ohjelma on nyt huomattavasti valmiimpi: sekä Expectiminimax että Minimax -algoritmit toimivat ja niitä voidaan käyttää pelin pelaamiseen. Yksikkötestit kattavat käytännössä koko projektin logiikan, mikä tekee ohjelmasta luotettavamman ja helpommin ylläpidettävän. Dokumentaatiota on myös parannettu, ja projekti alkaa olla rakenteellisesti valmis.  

3. **Mitä opin tällä viikolla / tänään?**  
   Opin paljon testauksen kattavuudesta ja siitä, miten `pytest` ja `coverage` toimivat yhdessä. Lisäksi opin alpha-beta -karsinnan toiminnasta Minimax-haussa ja sen käytännön toteutuksesta. Harjoittelin myös testien kirjoittamista niin, että ne kattavat sekä tavalliset tapaukset että harvinaisemmat reunaehdot.  

4. **Mikä jäi epäselväksi tai tuottanut vaikeuksia?**  
   Joidenkin pelilaudan ja hakualgoritmien erikoistilanteiden testaaminen oli aluksi haastavaa, koska niihin piti rakentaa tarkkaan määritellyt pelitilat. Lisäksi kattavuusraportin viimeisten rivien saavuttaminen oli hieman hankalaa, koska ne liittyvät harvinaisempiin tilanteisiin (esim. alpha-beta -katkaisuihin).  

5. **Mitä teen seuraavaksi?**  
   Seuraavaksi voisin keskittyä harjoitustyön valmisteluun vertaisarviointia varten. Tarkoituksena on puhdistaa koodi ja varmistaa, että kaikki komennot ovat helposti luettavia ja selkeitä. Huolehdin myös siitä, että dokumentaatiossa ja kommenteissa ei ole puutteita. En valitettavasti ehtinyt aloittaa graafisen käyttöliittymän toteutusta, joten täytyy katsoa, sallivatko aikataulut sen tekemisen.

---

**Tämän viikon työaika:** n. 14 tuntia  
