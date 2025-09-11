"""2048-pelin heuristiikat tekoälylle.

Tämä moduuli sisältää heuristiikkafunktiot, joilla arvioidaan pelilaudan
tilaa Expectiminimax-haussa.

Heuristiikat:
- Tyhjien ruutujen määrä (enemmän tyhjiä -> parempi).
- Käärmemäinen painotus (suuret luvut kulmissa).
- Tasaisuus (pienten log-arvoerojen suosiminen vierekkäin).
"""

from __future__ import annotations
from typing import List
import math

Grid = List[List[int]]

SNAKE_WEIGHTS: List[List[int]] = [
    [15, 14, 13, 12],
    [8, 9, 10, 11],
    [7, 6, 5, 4],
    [0, 1, 2, 3],
]


def log_value(v: int) -> float:
    """Palauttaa log2(v) jos v > 0, muuten 0.0."""
    return math.log2(v) if v > 0 else 0.0


def count_empties(g: Grid) -> int:
    """Laskee tyhjien ruutujen määrän laudalla."""
    return sum(v == 0 for r in g for v in r)


def snake_score(g: Grid) -> float:
    """Laskee laudan käärmesijoittelun pisteet.

    Suuret laatat -> sijoitetaan nurkkiin ja reunoille.
    """
    return sum(log_value(v) * SNAKE_WEIGHTS[r][c]
               for r in range(4) for c in range(4) if (v := g[r][c]))


def smoothness(g: Grid) -> float:
    """Laskee laudan tasaisuuden log-arvojen erojen avulla.

    Pienemmät erot vierekkäisten laattojen välillä -> parempi.
    """
    h = sum(abs(log_value(a) - log_value(b))
            for r in range(4) for c in range(3)
            if (a := g[r][c]) and (b := g[r][c+1]))
    v = sum(abs(log_value(a) - log_value(b))
            for c in range(4) for r in range(3)
            if (a := g[r][c]) and (b := g[r+1][c]))
    return -(h + v)


def evaluate(g: Grid) -> float:
    """Arvioi laudan yhdistämällä heuristiikat painokertoimilla."""
    return 7.0 * count_empties(g) + 1.5 * snake_score(g) + 0.2 * smoothness(g)
