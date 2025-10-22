"""Expectiminimax-haku 2048-tekoälylle – optimoitu.

- Dynaaminen syvyys huomioi sekä tyhjät että suurimman laatan.
- Evaluoinnin välimuisti (eval_cache) vähentää heuristiikkakutsuja.
- Siirtojen järjestys: käytä nopeaa proxy-arviota (score+evaluate) ennen exp_valuea.
- CHANCE-solmun ohennus: kun tyhjiä on paljon, arvioi deterministisesti
  vain parhaat 6 syntypaikkaa (kulmat/ reunat ensin) – säilyy determinismi.
"""

from __future__ import annotations
from typing import Tuple, List
from .board import GameState, Direction, PROB_FOUR
from .heuristics import evaluate
from .grid_ops import MOVE_FUN

MOVE_ORDER = ("left", "up", "right", "down")

# Välimuistit
cache: dict[tuple, float] = {}          # (grid, depth, node) -> value
_eval_cache: dict[tuple, float] = {}    # grid -> evaluate(grid)

# ---------- Apufunktiot ----------

def _grid_key(g: List[List[int]]) -> tuple:
    """Yhtenäinen avain ruudukolle (käytetään sekä eval- että haku-välimuisteissa)."""
    return tuple(map(tuple, g))

def make_key(g: List[List[int]], d: int, node: str) -> tuple:
    """Luo hajautusavaimen välimuistia varten."""
    return (_grid_key(g), d, node)

def eval_cached(g: List[List[int]]) -> float:
    """Heuristiikka välimuistista (tai laske ja talleta)."""
    k = _grid_key(g)
    v = _eval_cache.get(k)
    if v is None:
        v = evaluate(g)
        _eval_cache[k] = v
    return v

def leaf_value(s: GameState) -> float:
    """Laskee lehtisolmun arvon (pisteet + heuristiikka)."""
    return float(s.score) + eval_cached(s.grid)

def _largest_tile(g: List[List[int]]) -> int:
    return max(max(row) for row in g)

def dynamic_depth(b: int, empties: int, largest: int) -> int:
    """Säädä hakusyvyyttä sekä tyhjien että suurimman laatan mukaan."""
    d = b
    if empties >= 12:
        d += 2
    elif empties >= 8:
        d += 1
    elif empties <= 2:
        d = max(1, d - 1)
    if largest >= 2048 and empties <= 4:
        d += 1
    return max(1, d)

def _order_cells(g: List[List[int]], cells: List[tuple[int, int]]) -> List[tuple[int, int]]:
    """Deterministinen järjestys: kulmat > reunat > keskusta."""
    n = len(g)
    corners = {(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)}
    def score(cell):
        r, c = cell
        return 0 if cell in corners else 1 if (r in (0, n - 1) or c in (0, n - 1)) else 2
    return sorted(cells, key=score)

def _proxy_child_score(new_grid: List[List[int]], gained: int, base_score: float) -> float:
    """Nopea ennakkoarvio siirtojärjestystä varten (ei käy CHANCE-haaraa)."""
    empties = sum(v == 0 for r in new_grid for v in r)
    return base_score + gained + eval_cached(new_grid) + 0.05 * empties

def _ordered_moves(s: GameState) -> List[tuple[str, List[List[int]], int, float]]:
    """Palauta kaikki toteutettavat siirrot järjestettynä proxy-arvolla."""
    base = float(s.score)
    moves = []
    for m in MOVE_ORDER:
        new_grid, gained = MOVE_FUN[m](s.grid)
        if new_grid != s.grid:
            moves.append((m, new_grid, gained, _proxy_child_score(new_grid, gained, base)))
    moves.sort(key=lambda t: t[3], reverse=True)
    return moves

# ---------- Pääfunktiot ----------

def best_move_expecti(s: GameState, depth: int = 4) -> Tuple[Direction, float]:
    cache.clear()
    _eval_cache.clear()

    empties = sum(v == 0 for r in s.grid for v in r)
    d = dynamic_depth(depth, empties, _largest_tile(s.grid))

    moves = _ordered_moves(s)
    if not moves:
        return "left", leaf_value(s)  # ei laillista siirtoa

    best_dir, best_val = moves[0][0], float("-inf")
    for m, new_grid, gained, _proxy in moves:
        child = s.copy()
        child.grid = new_grid
        child.score = s.score + gained
        val = exp_value(child, d - 1)
        if val > best_val:
            best_val, best_dir = val, m
    return best_dir, best_val

def exp_value(s: GameState, d: int) -> float:
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

    # Kun tyhjiä on paljon, ohennetaan deterministisesti 6 soluun (kulmat/reunat ensin)
    if len(cells) > 6 and d >= 3:
        cells = _order_cells(s.grid, cells)[:6]

    probs = ((2, 1.0 - PROB_FOUR), (4, PROB_FOUR))
    total = 0.0
    for r, c in cells:
        child = s.copy()
        for val, p in probs:
            child.grid[r][c] = val
            total += p * max_value(child, d - 1)
        child.grid[r][c] = 0  # palautus

    res = total / len(cells)
    cache[k] = res
    return res

def max_value(s: GameState, d: int) -> float:
    if d == 0:
        return leaf_value(s)

    k = make_key(s.grid, d, "max")
    if k in cache:
        return cache[k]

    moves = _ordered_moves(s)
    if not moves:
        res = leaf_value(s)
        cache[k] = res
        return res

    best = float("-inf")
    for _m, new_grid, gained, _proxy in moves:
        child = s.copy()
        child.grid = new_grid
        child.score = s.score + gained
        v = exp_value(child, d - 1)
        if v > best:
            best = v

    cache[k] = best
    return best
