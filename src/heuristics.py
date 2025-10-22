"""2048-pelin heuristiikat – parannettu versio.

Heuristiikat:
- Tyhjien ruutujen määrä (enemmän tyhjiä -> parempi).
- "Käärme/monotonicity": pisteytä neljään suuntaan ja valitse paras
  (automaattisesti suosii kulmaa, jossa isot laatat pysyvät).
- Tasaisuus: pienemmät log-arvoerot vierekkäin -> parempi (negatiivinen summa).
- Yhdistymispotentiaali: saman arvoiset vierekkäin -> parempi.
- Kulmabonus: jos maksimiarvo on kulmassa, pieni lisä.

Painot on valittu niin, että tyhjät + monotonicity ohjaavat strategiaa,
merge ja smoothness hienosäätävät, kulmabonus on kevyt tuki.
"""

from __future__ import annotations
from typing import List, Iterable, Tuple
import math

Grid = List[List[int]]
N = 4  # ruudukon koko

# Perus "käärme" -painotus (max-kulma = vasen ylä). Muut suunnat saadaan rotaatioilla.
_BASE_SNAKE: List[List[int]] = [
    [15, 14, 13, 12],
    [8,   9, 10, 11],
    [7,   6,  5,  4],
    [0,   1,  2,  3],
]

# ---------- apurit ----------

def log_value(v: int) -> float:
    """Palauttaa log2(v) jos v > 0, muuten 0.0."""
    return math.log2(v) if v > 0 else 0.0

def _rotate(w: List[List[int]]) -> List[List[int]]:
    """90° kierto myötäpäivään."""
    return [list(col) for col in zip(*w[::-1])]

# Luodaan kaikki neljä käärmevarianttia kerran.
_SNAKES: Tuple[List[List[int]], ...] = (
    _BASE_SNAKE,
    _rotate(_BASE_SNAKE),
    _rotate(_rotate(_BASE_SNAKE)),
    _rotate(_rotate(_rotate(_BASE_SNAKE))),
)

def count_empties(g: Grid) -> int:
    """Laskee tyhjien ruutujen määrän laudalla."""
    return sum(v == 0 for row in g for v in row)

def snake_score(g: Grid) -> float:
    """Pisteytä neljään suuntaan ja palauta maksimi."""
    best = float("-inf")
    for W in _SNAKES:
        s = 0.0
        for r in range(N):
            for c in range(N):
                v = g[r][c]
                if v:
                    s += log_value(v) * W[r][c]
        if s > best:
            best = s
    return 0.0 if best == float("-inf") else best

def _adjacent_pairs(g: Grid) -> Iterable[Tuple[int, int]]:
    """Tuottaa vierekkäiset laatat (vain kun molemmat != 0), vaaka ja pysty."""
    for r in range(N):
        for c in range(N - 1):
            a, b = g[r][c], g[r][c + 1]
            if a and b:
                yield a, b
    for c in range(N):
        for r in range(N - 1):
            a, b = g[r][c], g[r + 1][c]
            if a and b:
                yield a, b

def smoothness(g: Grid) -> float:
    """Negatiivinen erotusten summa (vain kun molemmat solut != 0)."""
    return -sum(abs(log_value(a) - log_value(b)) for a, b in _adjacent_pairs(g))

def merge_potential(g: Grid) -> float:
    """Laske vierekkäiset samat arvot (log-painotettuna)."""
    tot = 0.0
    for a, b in _adjacent_pairs(g):
        if a == b:
            tot += log_value(a)
    return tot

def corner_bonus(g: Grid) -> float:
    """Pieni bonus, jos maksimi on kulmassa (log-painotettuna)."""
    m = max(max(row) for row in g)
    corners = (g[0][0], g[0][N-1], g[N-1][0], g[N-1][N-1])
    return log_value(m) if (m > 0 and m in corners) else 0.0

# ---------- pääarvio ----------

# Painokertoimet – maltilliset ja käytännössä toimivat
_W_EMPTY   = 9.0
_W_SNAKE   = 1.2
_W_SMOOTH  = 0.4
_W_MERGE   = 2.5
_W_CORNER  = 0.8

def evaluate(g: Grid) -> float:
    """Yhdistetty arvio laudan laadusta."""
    return (
        _W_EMPTY  * count_empties(g) +
        _W_SNAKE  * snake_score(g)   +
        _W_SMOOTH * smoothness(g)    +
        _W_MERGE  * merge_potential(g) +
        _W_CORNER * corner_bonus(g)
    )
