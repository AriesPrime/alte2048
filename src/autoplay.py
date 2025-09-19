"""Automaattinen pelinsimulaattori 2048-tekoälylle.

Tämä moduuli ajaa yhden täyden 2048-pelin valitulla tekoälymoottorilla ja
tulostaa tilanteen jokaisen siirron jälkeen.

Käyttö komentoriviltä:
    python -m src.autoplay --depth 5 --engine minimax

Argumentit:
- --depth: Haun syvyys (suurempi = vahvempi, mutta hitaampi).
- --engine: 'expecti' (Expectiminimax, oletus) tai 'minimax' (Minimax + alpha-beta).
"""

from __future__ import annotations
import argparse
from .board import new_game
from .expectiminimax import best_move_expecti
from .minimax import best_move_minimax
from .gui import render, print_ai_move, print_final




def run(depth: int = 4, engine: str = "expecti") -> None:
    """Suorittaa yhden pelin valitulla tekoälymoottorilla.

    Args:
        depth: Haun perussyvyys.
        engine: 'expecti' tai 'minimax'.
    """
    choose = best_move_expecti if engine == "expecti" else best_move_minimax
    s = new_game()
    render(s)
    i = 0
    while not s.over:
        d, _ = choose(s, depth=depth)
        s.move(d)
        i += 1
        print_ai_move(i, d)
        render(s)
    print_final(s)


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Suorita yksi tekoälyn pelaama 2048-peli.")
    ap.add_argument("--depth", type=int, default=4,
                    help="haun syvyys (suurempi = hitaampi, mutta vahvempi)")
    ap.add_argument("--engine", choices=["expecti", "minimax"], default="expecti",
                    help="valitse algoritmi tekoälylle: 'expecti' (oletus) tai 'minimax'")
    return ap.parse_args(argv)

def main(argv=None) -> None:
    args = parse_args(argv)
    run(depth=args.depth, engine=args.engine)

if __name__ == "__main__":  # pragma: no cover
    main()