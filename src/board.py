"""2048-pelin peruslogiikka (lauta, siirrot, pisteet).

Tämä moduuli sisältää:
- Pelilaudan ja pistelaskennan (GameState).
- Siirtotoiminnot:
  - move: tekee normaalin siirron ja lisää satunnaislaatan.
  - move_no_spawn: tekee siirron ilman satunnaislaattaa (käytetään AI:ssa).
- Aputoiminnot: tyhjien solujen haku, game over -tarkistus, kopiointi.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Literal
import random

SIZE = 4
PROB_FOUR = 0.1

Grid = List[List[int]]
Direction = Literal["up", "down", "left", "right"]


def transpose(g: Grid) -> Grid:
    """Transponoi ruudukon (rivit → sarakkeet)."""
    return [list(c) for c in zip(*g)]


def reverse_rows(g: Grid) -> Grid:
    """Kääntää kaikki rivit ympäri (vasen-oikea)."""
    return [r[::-1] for r in g]


def compress_row_left(row: List[int]) -> Tuple[List[int], int]:
    """Siirtää ja yhdistää rivin vasemmalle 2048-sääntöjen mukaan.

    Args:
        row: Neljän kokonaisluvun lista (0 = tyhjä).

    Returns:
        (uusi rivi, kierroksella saadut pisteet).
    """
    t = [v for v in row if v]
    out: List[int] = []
    gain = i = 0
    while i < len(t):
        if i+1 < len(t) and t[i] == t[i+1]:
            v = t[i]*2
            gain += v
            out.append(v)
            i += 2
        else:
            out.append(t[i])
            i += 1
    out += [0]*(SIZE - len(out))
    return out, gain


@dataclass
class GameState:
    """Pelilaudan tila ja perustoiminnot.

    Attributes:
        grid: 4x4-ruudukko (0 = tyhjä).
        score: Pisteet yhteensä.
        won: Onko 2048 saavutettu.
        over: Onko peli ohi.
    """
    grid: Grid = field(default_factory=lambda: [[0]*SIZE for _ in range(SIZE)])
    score: int = 0
    won: bool = False
    over: bool = False

    def copy(self) -> "GameState":
        """Palauttaa kopion nykyisestä tilasta."""
        return GameState([r[:] for r in self.grid], self.score, self.won, self.over)

    def empty_cells(self) -> List[Tuple[int, int]]:
        """Palauttaa listan tyhjistä soluista (koordinaatit)."""
        g = self.grid
        return [(r, c) for r in range(SIZE) for c in range(SIZE) if not g[r][c]]

    def spawn_tile(self) -> None:
        """Lisää satunnaisen laatan (2 tai 4) tyhjään ruutuun."""
        cells = self.empty_cells()
        if not cells:
            return
        r, c = random.choice(cells)
        self.grid[r][c] = 4 if random.random() < PROB_FOUR else 2

    def slide_left(self) -> int:
        """Tekee vasemmalle siirron kaikille riveille.

        Returns:
            Siirrosta saadut pisteet (0 jos ei muutosta).
        """
        pairs = [compress_row_left(r) for r in self.grid]
        new_grid = [nr for nr, _ in pairs]
        gain = sum(g for _, g in pairs)
        if new_grid != self.grid:
            self.grid = new_grid
            self.score += gain
        return gain

    def apply_move(self, d: Direction) -> bool:
        """Suorittaa siirron annetussa suunnassa.

        Args:
            d: "up", "down", "left" tai "right".

        Returns:
            True jos lauta muuttui, muuten False.
        """
        original = [r[:] for r in self.grid]
        if d == "left":
            self.slide_left()
        elif d == "right":
            self.grid = reverse_rows(self.grid)
            self.slide_left()
            self.grid = reverse_rows(self.grid)
        elif d == "up":
            self.grid = transpose(self.grid)
            self.slide_left()
            self.grid = transpose(self.grid)
        else:  # down
            self.grid = transpose(self.grid)
            self.grid = reverse_rows(self.grid)
            self.slide_left()
            self.grid = reverse_rows(self.grid)
            self.grid = transpose(self.grid)
        return self.grid != original

    def move(self, d: Direction, spawn: bool = True, check_over: bool = True) -> bool:
        """Tekee pelaajan siirron ja lisää satunnaislaatan jos tarvitaan.

        Args:
            d: Suunta.
            spawn: Lisätäänkö satunnaislaatta.
            check_over: Päivitetäänkö over-lippu.

        Returns:
            True jos lauta muuttui, muuten False.
        """
        if not self.apply_move(d):
            return False
        if spawn:
            self.spawn_tile()
        self.won = max(max(r) for r in self.grid) >= 2048
        if check_over:
            self.over = self.is_game_over()
        return True

    def move_no_spawn(self, d: Direction) -> bool:
        """Siirto ilman satunnaislaattaa (AI:n käyttöön)."""
        return self.move(d, spawn=False, check_over=False)

    def is_game_over(self) -> bool:
        """Tarkistaa onko peli ohi (ei tyhjiä eikä yhdistettäviä)."""
        g = self.grid
        for r in range(SIZE):
            for c in range(SIZE):
                if not g[r][c]:
                    return False
                if c < SIZE-1 and g[r][c] == g[r][c+1]:
                    return False
                if r < SIZE-1 and g[r][c] == g[r+1][c]:
                    return False
        return True


def new_game() -> GameState:
    """Luo uuden pelin ja lisää kaksi satunnaislaattaa."""
    gs = GameState()
    for _ in range(2):
        gs.spawn_tile()
    return gs
