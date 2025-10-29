# Viikkoraportti - Viikko 6

1. **Mitä olen tehnyt tällä viikolla?**  
   Viimeistelin koko projektin: kirjoitin loput yksikkötestit (`test_grid_ops.py`, `test_expectiminimax.py`, `test_heuristics.py`) ja varmistin, että testikattavuus nousi lähes täydelliseksi (~99 %).  
   Lisäksi viimeistelin kaikki vaaditut dokumentit: **määrittelydokumentti**, **testausdokumentti**, **toteutusdokumentti** ja **README.md**. Päivitin myös `requirements.txt`-tiedoston, tarkistin projektin rakenteen ja siistin koodikommentit yhtenäisiksi.  
   Lopuksi testasin ohjelman toiminnan eri `depth`-arvoilla varmistaakseni, että tekoäly toimii johdonmukaisesti ja että pelilogiikka vastaa odotettua käyttäytymistä kaikissa siirtosuunnissa.

2. **Miten ohjelma on edistynyt?**  
   Projekti on nyt täysin valmis. Kaikki keskeiset moduulit (`board`, `grid_ops`, `heuristics`, `expectiminimax`, `gui`, `autoplay`, `cli`) toimivat saumattomasti yhteen, ja ohjelma pystyy pelaamaan pelin loppuun asti tekoälyn avulla.  
   Testaus kattaa nyt lähes kaikki koodirivit, ja tekoäly tekee johdonmukaisia päätöksiä Expectiminimax-algoritmin pohjalta. Dokumentaatio on viimeistelty ja kuvaa ohjelman rakenteen, toiminnan ja testauksen selkeästi.

3. **Mitä opin tällä viikolla / tänään?**  
   Opin viimeistelemään laajan Python-projektin loppuun dokumentteineen ja testauksineen. Opin myös parantamaan testien laatua lisäämällä testit, jotka kattavat välimuistit, dynaamisen syvyyden ja haun determinismin.  
   Lisäksi opin optimoimaan testejä siten, että ne ovat sekä nopeita että informatiivisia.

4. **Mikä jäi epäselväksi tai tuottanut vaikeuksia?**  
   Joissakin testeissä (erityisesti Expectiminimax-moduulissa) oli haastavaa hallita mockattujen funktioiden käyttäytymistä, koska algoritmi kutsuu samoja funktioita useita kertoja eri tilanteissa.  

5. **Mitä teen seuraavaksi?**  
   Projekti on valmis ja dokumentit ja testit ovat valmiit palautettaviksi.

---

**Tämän viikon työaika:** n. 15 tuntia  