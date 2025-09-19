"""Minimax-haku 2048-tekoälylle.

Tämä moduuli sisältää Minimax-haun toteutuksen alpha-beta -karsinnalla.
Rakenteessa on kaksi tasoa:
- MAX-solmut: pelaajan siirrot (best_move_minimax, max_value).
- MIN-solmut: vastustajan sijoitus 2/4 laatalla (min_value).

Algoritmi hyödyntää heuristiikkaa (evaluate) ja dynaamista hakusyvyyttä.
"""

from __future__ import annotations
from typing import Tuple, List
from .board import GameState, Direction
from .heuristics import evaluate

MOVE_ORDER = ("left", "up", "right", "down")
tt: dict[tuple, float] = {}


def make_key(g: List[List[int]], d: int, node: str) -> tuple:
    """Luo hajautusavaimen välimuistia varten."""
    return (tuple(map(tuple, g)), d, node)


def leaf_value(s: GameState) -> float:
    """Laskee lehtisolmun arvon (pisteet + heuristiikka)."""
    return float(s.score) + evaluate(s.grid)


def dynamic_depth(b: int, e: int) -> int:
    """Säätää hakusyvyyttä tyhjien solujen määrän mukaan."""
    return b+1 if e >= 8 else max(1, b-1) if e <= 2 else b


def best_move_minimax(s: GameState, depth: int = 4) -> Tuple[Direction, float]:
    """Palauttaa tekoälyn parhaan siirron ja sen arvioidun arvon.

    Args:
        s: Pelitila.
        depth: Perushaun syvyys.

    Returns:
        (suunta, arvio).
    """
    tt.clear()
    d = dynamic_depth(depth, sum(v == 0 for r in s.grid for v in r))
    alpha, beta = float("-inf"), float("inf")
    best_dir, best_val = "left", float("-inf")
    for m in MOVE_ORDER:
        c = s.copy()
        if not c.move_no_spawn(m):
            continue
        v = min_value(c, d-1, alpha, beta)
        if v > best_val:
            best_val, best_dir = v, m
        if v > alpha:
            alpha = v
    return best_dir, best_val


def max_value(s: GameState, d: int, alpha: float, beta: float) -> float:
    """MAX-solmu: valitsee parhaan pelaajasiirron."""
    if d == 0:
        return leaf_value(s)
    k = make_key(s.grid, d, "max")
    if k in tt:
        return tt[k]

    v = float("-inf")
    has = False
    for m in MOVE_ORDER:
        c = s.copy()
        if not c.move_no_spawn(m):
            continue
        has = True
        v = max(v, min_value(c, d-1, alpha, beta))
        alpha = max(alpha, v)
        if alpha >= beta:
            # katkaisu - ei talletusta (ei exact)
            return v
    if not has:
        v = leaf_value(s)
    tt[k] = v
    return v


def min_value(s: GameState, d: int, alpha: float, beta: float) -> float:
    """MIN-solmu: vastustaja lisää 2/4 siihen ruutuun, joka minimoi MAX:n arvon."""
    if d == 0:
        return leaf_value(s)
    k = make_key(s.grid, d, "min")
    if k in tt:
        return tt[k]

    cells = s.empty_cells()
    if not cells:
        v = leaf_value(s)
        tt[k] = v
        return v

    v = float("inf")
    for (r, c) in cells:
        # kokeile 2 ja 4 - vastustaja valitsee pahimman
        for val in (2, 4):
            child = s.copy()
            child.grid[r][c] = val
            v = min(v, max_value(child, d-1, alpha, beta))
            beta = min(beta, v)
            if alpha >= beta:
                # katkaisu - ei talletusta (ei exact)
                return v
    tt[k] = v
    return v
