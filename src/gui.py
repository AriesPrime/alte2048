"""2048-pelin tekstipohjainen käyttöliittymä.

Tämä moduuli tarjoaa tulostuksen, komentojen lukemisen sekä AI-askeleen
ajamiseen liittyvät apufunktiot. Käytetään sekä tekstikäyttöliittymässä
että automaattisessa pelissä.
"""

from __future__ import annotations
from typing import Optional
from .board import GameState, Direction
from .expectiminimax import best_move


def render(s: GameState) -> None:
    """Tulostaa pelilaudan nykyisen tilan."""
    print("\nPisteet:", s.score, "| Voitto:", s.won, "| Loppu:", s.over)
    print("+----+----+----+----+")
    for r in s.grid:
        print("|" + "|".join(f"{v:>4}" if v else "    " for v in r) + "|")
        print("+----+----+----+----+")


def read_command() -> Optional[Direction | str]:
    """Lukee yhden käyttäjän komennon syötteestä.

    Palauttaa:
        "q"  -> lopetus
        "ai" -> tekoälyn siirto
        "up"/"down"/"left"/"right" jos WASD painettu
        None jos tuntematon komento
    """
    raw = input("> ").strip().lower()
    if raw in ("q", "quit", "exit"):
        return "q"
    if raw == "ai":
        return "ai"
    return {"w": "up", "a": "left", "s": "down", "d": "right"}.get(raw)


def ai_step(s: GameState, depth: int) -> tuple[bool, Direction]:
    """Suorittaa yhden tekoälyn siirron annetulla syvyydellä.

    Returns:
        (onnistuiko siirto, suunta).
    """
    d, _ = best_move(s, depth=depth)
    return s.move(d), d


def print_ai_move(i: int, d: Direction) -> None:
    """Tulostaa tekoälyn tekemän siirron numeron ja suunnan."""
    print(f"\nAI:n siirto {i}: {d}")


def print_final(s: GameState) -> None:
    """Tulostaa lopputuloksen (pisteet ja suurin laatta)."""
    print("\nLOPPU - Pisteet:", s.score, "Suurin laatta:",
          max(v for r in s.grid for v in r))
