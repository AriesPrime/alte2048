"""Pelilaudan siirto-operaatiot (grid_ops).

Tämä moduuli sisältää pelilaudan suuntaiset siirtofunktiot
(vasemmalle, oikealle, ylös, alas) ilman GameState-olioita.
Funktiot ovat puhtaita: ne eivät muuta alkuperäistä ruudukkoa
vaan palauttavat uuden ruudukon ja saadut pisteet (gain).

Näitä funktioita voidaan käyttää hakualgoritmissa nopeuttamaan 
laskentaa, koska ne eivät tee ylimääräisiä kopioita tai 
pelitilan päivityksiä.
"""

from typing import List, Tuple

Grid = List[List[int]]


# ---------- Apufunktiot ----------

def _compress_line_left(line: List[int]) -> Tuple[List[int], int]:
    """Puristaa ja yhdistää rivin vasemmalle päin.

    Poistaa nollat, yhdistää vierekkäiset samat arvot
    (kuten 2+2=4) ja täyttää loput nollilla.
    Palauttaa sekä uuden rivin että yhdistymisistä saadut pisteet.

    Args:
        line: Lista (yksi rivi) kokonaislukuja.

    Returns:
        Tuple (uusi_rivi, pisteet)
    """
    tiles = [v for v in line if v != 0]
    gained = 0
    i = 0
    while i < len(tiles) - 1:
        if tiles[i] == tiles[i + 1]:
            tiles[i] *= 2
            gained += tiles[i]
            tiles[i + 1] = 0
            i += 2
        else:
            i += 1

    new_tiles = [v for v in tiles if v != 0]
    return new_tiles + [0] * (len(line) - len(new_tiles)), gained


def _move_generic(g: Grid, reverse: bool = False, transpose: bool = False) -> Tuple[Grid, int]:
    """Yleinen siirto-operaatio: käännä/transpose lauta ja käytä samaa puristuslogiikkaa.

    Args:
        g: 2D-lista (pelilauta).
        reverse: jos True, siirto tehdään oikealle tai alas.
        transpose: jos True, siirto tehdään ylös tai alas.

    Returns:
        (uusi_ruudukko, saadut_pisteet)
    """
    n = len(g)
    new_board = [[0] * n for _ in range(n)]
    gained_total = 0

    # Jos siirto on pysty-, vaihdetaan rivit ja sarakkeet (transpose)
    source = list(zip(*g)) if transpose else g

    for i, line in enumerate(source):
        line = list(line)
        if reverse:
            line.reverse()
        new_line, gained = _compress_line_left(line)
        if reverse:
            new_line.reverse()
        gained_total += gained

        # Palautetaan joko suoraan tai transposoituna
        for j, val in enumerate(new_line):
            if transpose:
                new_board[j][i] = val
            else:
                new_board[i][j] = val

    return new_board, gained_total


# ---------- Siirrot ----------

def move_left_grid(g: Grid) -> Tuple[Grid, int]:
    """Simuloi vasemmalle siirron pelilaudalla."""
    return _move_generic(g, reverse=False, transpose=False)


def move_right_grid(g: Grid) -> Tuple[Grid, int]:
    """Simuloi oikealle siirron pelilaudalla."""
    return _move_generic(g, reverse=True, transpose=False)


def move_up_grid(g: Grid) -> Tuple[Grid, int]:
    """Simuloi ylöspäin siirron pelilaudalla."""
    return _move_generic(g, reverse=False, transpose=True)


def move_down_grid(g: Grid) -> Tuple[Grid, int]:
    """Simuloi alaspäin siirron pelilaudalla."""
    return _move_generic(g, reverse=True, transpose=True)


# ---------- Apusanakirja ----------

MOVE_FUN = {
    "left": move_left_grid,
    "right": move_right_grid,
    "up": move_up_grid,
    "down": move_down_grid,
}
"""Sanakirja, joka yhdistää siirtosuunnan vastaavaan funktioon.

Esimerkiksi:
    new_grid, gained = MOVE_FUN["left"](grid)
"""
