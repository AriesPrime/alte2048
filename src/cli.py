"""2048-pelin komentorivikäyttöliittymä.

Tämä moduuli käynnistää tekstipohjaisen pelin, jossa käyttäjä voi:
- tehdä siirtoja WASD-näppäimillä,
- pyytää tekoälyä tekemään siirron ("ai"),
- lopettaa pelin ("q").

Moduuli huolehtii pelin alustuksesta, syötteiden lukemisesta ja
pelilaudan tulostamisesta jokaisen siirron jälkeen.
"""

from __future__ import annotations
from .board import new_game
from .gui import render, read_command, ai_step


def main() -> None:
    """Käynnistää tekstikäyttöliittymän ja hallitsee pelin kulkua.

    - Luo uuden pelin.
    - Tulostaa laudan jokaisen siirron jälkeen.
    - Lukee käyttäjän komennot (WASD, ai, q).
    - Tukee keskeytystä Ctrl+C:llä.
    """
    print("2048 - tekstikäyttöliittymä")
    print("Ohje: WASD liikkumiseen, 'ai' tekoälyn siirtoon, 'q' lopetukseen.")
    s = new_game()
    render(s)
    try:
        while not s.over:
            cmd = read_command()
            if cmd is None:
                print("Tuntematon komento. Käytä WASD tai 'ai' tai 'q'.")
                continue
            if cmd == "q":
                break
            if cmd == "ai":
                ch, d = ai_step(s, depth=4)
                print("Tekoälysiirto ei muuttanut lautaa." if not ch else f"AI-siirto: {d}")
            else:
                if not s.move(cmd):
                    print("Ei vaikutusta. Kokeile toista suuntaa.")
            render(s)
    except KeyboardInterrupt:
        print("\nKeskeytetty. Kiitos pelaamisesta!")
    if s.over:
        print("Peli ohi.", "Onnittelut voitosta!" if s.won else "")


if __name__ == "__main__":
    main()
