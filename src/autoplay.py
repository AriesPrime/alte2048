"""Automaattinen pelinsimulaattori 2048-tekoälylle.

Tämä moduuli ajaa yhden täyden 2048-pelin tekoälyn (Expectiminimax)
ohjaamana ja tulostaa tilanteen jokaisen siirron jälkeen.

Käyttö komentoriviltä:
    python -m src.autoplay --depth 5

Argumentit:
- --depth: Haun syvyys (suurempi = vahvempi, mutta hitaampi).
"""

from __future__ import annotations
import argparse
from .board import new_game
from .expectiminimax import best_move
from .gui import render, print_ai_move, print_final


def run(depth: int = 4) -> None:
    """Suorittaa yhden pelin tekoälyllä.

    Luo uuden pelin, tekee siirtoja kunnes peli on ohi ja tulostaa
    jokaisen siirron sekä lopputuloksen.

    Args:
        depth: Expectiminimaxin hakusyvyys.
    """
    s = new_game()
    render(s)
    i = 0
    while not s.over:
        d, _ = best_move(s, depth=depth)
        s.move(d)
        i += 1
        print_ai_move(i, d)
        render(s)
    print_final(s)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Suorita yksi tekoälyn pelaama 2048-peli.")
    ap.add_argument("--depth", type=int, default=4,
                    help="haun syvyys (suurempi = hitaampi mutta vahvempi)")
    run(depth=ap.parse_args().depth)
