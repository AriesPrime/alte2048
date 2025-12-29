from __future__ import annotations
from typing import List, Iterable, Tuple
import math

Grid = List[List[int]]
N = 4

_BASE_SNAKE: List[List[int]] = [
    [15, 14, 13, 12],
    [8,   9, 10, 11],
    [7,   6,  5,  4],
    [0,   1,  2,  3],
]

def log_value(v: int) -> float:
    return math.log2(v) if v > 0 else 0.0

def _rotate(w: List[List[int]]) -> List[List[int]]:
    return [list(col) for col in zip(*w[::-1])]

_SNAKES: Tuple[List[List[int]], ...] = (
    _BASE_SNAKE,
    _rotate(_BASE_SNAKE),
    _rotate(_rotate(_BASE_SNAKE)),
    _rotate(_rotate(_rotate(_BASE_SNAKE))),
)

def count_empties(g: Grid) -> int:
    return sum(v == 0 for row in g for v in row)

def snake_score(g: Grid) -> float:
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
    return -sum(abs(log_value(a) - log_value(b)) for a, b in _adjacent_pairs(g))

def merge_potential(g: Grid) -> float:
    tot = 0.0
    for a, b in _adjacent_pairs(g):
        if a == b:
            tot += log_value(a)
    return tot

def corner_bonus(g: Grid) -> float:
    m = max(max(row) for row in g)
    corners = (g[0][0], g[0][N-1], g[N-1][0], g[N-1][N-1])
    return log_value(m) if (m > 0 and m in corners) else 0.0

def max_tile(g: Grid) -> int:
    return max(max(row) for row in g)

_W_EMPTY  = 12.0
_W_SNAKE  = 1.0
_W_SMOOTH = 0.4
_W_MERGE  = 2.5
_W_CORNER = 0.8

def evaluate(g: Grid) -> float:
    m = max_tile(g)

    return (
        _W_EMPTY  * count_empties(g) +
        _W_SNAKE  * snake_score(g) +
        _W_SMOOTH * smoothness(g) +
        _W_MERGE  * merge_potential(g) +
        _W_CORNER * corner_bonus(g)
    )
