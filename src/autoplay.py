"""Automaattinen pelinsimulaattori 2048-tekoälylle.

Tämä moduuli ajaa yhden täyden 2048-pelin Expectiminimax-tekniikalla ja
tulostaa tilanteen jokaisen siirron jälkeen.

Käyttö komentoriviltä:
    python -m src.autoplay --depth 5

Argumentit:
- --depth: Haun syvyys (suurempi = vahvempi, mutta hitaampi).
"""

from __future__ import annotations
import argparse
from .board import new_game
from .expectiminimax import best_move_expecti
from .gui import render, print_ai_move, print_final


def run(depth: int = 4) -> None:
    """Suorittaa yhden pelin Expectiminimaxilla.

    Args:
        depth: Haun perussyvyys.
    """
    s = new_game()
    render(s)
    i = 0
    while not s.over:
        d, _ = best_move_expecti(s, depth=depth)
        s.move(d)
        i += 1
        print_ai_move(i, d)
        render(s)
    print_final(s)


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Suorita yksi tekoälyn pelaama 2048-peli Expectiminimaxilla.")
    ap.add_argument(
        "--depth",
        type=int,
        default=4,
        help="haun syvyys (suurempi = hitaampi, mutta vahvempi)",
    )
    return ap.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    run(depth=args.depth)


if __name__ == "__main__":  # pragma: no cover
    main()
