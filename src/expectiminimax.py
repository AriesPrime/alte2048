"""Expectiminimax-haku 2048-tekoälylle.

Tämä moduuli sisältää Expectiminimax-haun toteutuksen.  
Rakenteessa on kolme tasoa:
- MAX-solmut: pelaajan siirrot (best_move, max_value).
- CHANCE-solmut: satunnaisten laattojen lisäys (exp_value).
- LEAF-solmut: arviointifunktio (leaf_value).

Algoritmi hyödyntää heuristiikkaa (evaluate) ja dynaamista hakusyvyyttä.
"""

from __future__ import annotations
from typing import Tuple, List
from .board import GameState, Direction, PROB_FOUR
from .heuristics import evaluate

MOVE_ORDER = ("left", "up", "right", "down")
cache: dict[tuple, float] = {}


def make_key(g: List[List[int]], d: int, node: str) -> tuple:
    """Luo hajautusavaimen välimuistia varten."""
    return (tuple(map(tuple, g)), d, node)


def leaf_value(s: GameState) -> float:
    """Laskee lehtisolmun arvon (pisteet + heuristiikka)."""
    return float(s.score) + evaluate(s.grid)


def dynamic_depth(b: int, e: int) -> int:
    """Säätää hakusyvyyttä tyhjien solujen määrän mukaan."""
    return b+1 if e >= 8 else max(1, b-1) if e <= 2 else b


def best_move(s: GameState, depth: int = 4) -> Tuple[Direction, float]:
    """Palauttaa tekoälyn parhaan siirron ja sen arvioidun arvon.

    Args:
        s: Pelitila.
        depth: Perushaun syvyys.

    Returns:
        (suunta, arvio).
    """
    cache.clear()
    d = dynamic_depth(depth, sum(v == 0 for r in s.grid for v in r))
    best_dir, best_val = "left", float("-inf")
    for m in MOVE_ORDER:
        c = s.copy()
        if not c.move_no_spawn(m):
            continue
        val = exp_value(c, d-1)
        if val > best_val:
            best_val, best_dir = val, m
    return best_dir, best_val


def exp_value(s: GameState, d: int) -> float:
    """CHANCE-solmu: laskee satunnaislaatan lisäämisen odotusarvon."""
    if d == 0:
        return leaf_value(s)
    k = make_key(s.grid, d, "chance")
    if k in cache:
        return cache[k]
    cells = s.empty_cells()
    if not cells:
        v = leaf_value(s)
        cache[k] = v
        return v
    probs = ((2, 1.0-PROB_FOUR), (4, PROB_FOUR))
    total = 0.0
    for r, c in cells:
        for val, p in probs:
            cpy = s.copy()
            cpy.grid[r][c] = val
            total += p * max_value(cpy, d-1)
    res = total / len(cells)
    cache[k] = res
    return res


def max_value(s: GameState, d: int) -> float:
    """MAX-solmu: valitsee parhaan pelaajasiirron."""
    if d == 0:
        return leaf_value(s)
    k = make_key(s.grid, d, "max")
    if k in cache:
        return cache[k]
    best = float("-inf")
    has = False
    for m in MOVE_ORDER:
        c = s.copy()
        if not c.move_no_spawn(m):
            continue
        has = True
        v = exp_value(c, d-1)
        if v > best:
            best = v
    res = leaf_value(s) if not has else best
    cache[k] = res
    return res