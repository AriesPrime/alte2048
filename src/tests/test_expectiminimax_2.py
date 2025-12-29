import random
import pytest
import src.expectiminimax as ex
from src.board import GameState


def _max_tile(grid):
    """
    Palauttaa laudan suurimman laatan arvon.
    """
    return max(max(row) for row in grid)


def _spawn_random_tile(state, rng):
    """
    Lisää satunnaisen laatan (2 tai 4) johonkin tyhjään ruutuun.

    Laatan arvo valitaan samalla todennäköisyysjaolla kuin varsinaisessa pelissä.
    """
    empties = state.empty_cells()
    if not empties:
        return
    r, c = rng.choice(empties)
    state.grid[r][c] = 4 if rng.random() < ex.PROB_FOUR else 2


def play_until_2048(start_grid, seed, max_moves=10, depth=2, trace=False):
    """
    Pelaa 2048-peliä expectiminimax-algoritmilla.

    Parametrit:
    - start_grid: aloituslauta
    - seed: satunnaislukugeneraattorin siemen
    - max_moves: enimmäissiirtojen määrä
    - depth: expectiminimax-haun perussyvyys
    - trace: jos True, tulostaa laudan jokaisen vuoron jälkeen

    Palauttaa:
    - siirtojen lukumäärän, jossa 2048 saavutetaan
    - None, jos 2048 ei saavuteta sallituissa siirroissa
    """
    rng = random.Random(seed)

    s = GameState()
    s.grid = [row[:] for row in start_grid]
    s.score = 0

    if trace:
        print("\n=== PELI ALKAA ===")
        for row in s.grid:
            print(row)

    if _max_tile(s.grid) >= 2048:
        return 0

    for turn in range(1, max_moves + 1):
        direction, _ = ex.best_move_expecti(s, depth=depth)
        new_grid, gained = ex.MOVE_FUN[direction](s.grid)

        if new_grid == s.grid:
            if trace:
                print(f"\nVuoro {turn} ({direction}) -> ei vaikutusta")
            return None

        s.grid = new_grid
        s.score += gained

        _spawn_random_tile(s, rng)

        if trace:
            print(f"\nVuoro {turn} ({direction})")
            for row in s.grid:
                print(row)

        if _max_tile(s.grid) >= 2048:
            return turn

    return None


FORCED_CASES = [
    (
        "forced-left",
        [
            [0, 64, 128, 256],
            [16, 1024, 512, 512],
            [0, 0, 256, 128],
            [4, 0, 256, 32],
        ],
    ),
    (
        "forced-right",
        [
            [256, 128, 64, 0],
            [512, 512, 1024, 16],
            [128, 64, 32, 8],
            [32, 16, 8, 4],
        ],
    ),
    (
        "forced-center",
        [
            [256, 16, 1024, 64],
            [256, 0, 512, 124],
            [256, 0, 256, 2],
            [4, 0, 4, 2],
        ],
    ),
    (
        "three-moves",
        [
            [128, 16, 128, 1024],
            [0, 0, 0, 512],
            [0, 0, 256, 256],
            [4, 0, 0, 0],
        ],
    ),
]


SEEDS = list(range(20))


@pytest.mark.parametrize("name, grid", FORCED_CASES)
@pytest.mark.parametrize("seed", SEEDS)
def test_forced_positions_reach_2048(name, grid, seed):
    """
    Testaa, että selvästi pakotetut voittotilanteet
    johtavat aina 2048-laattaan satunnaisuudesta huolimatta.
    """
    moves = play_until_2048(grid, seed, max_moves=10, depth=2)
    assert moves is not None


def test_probabilistic_win():
    """
    Testaa lähes-voittotilanne, jossa kaikkien satunnaissyntyjen
    ei tarvitse johtaa voittoon, mutta enemmistön pitäisi.

    Testi tarkastelee erityisesti sitä, pyrkiikö algoritmi
    systemaattisesti kohti 2048-laattaa.
    """
    grid = [
        [0, 16, 128, 1024],
        [128, 0, 0, 512],
        [256, 0, 0, 256],
        [4, 0, 0, 0],
    ]

    wins_in_three = 0

    for seed in range(10):
        moves = play_until_2048(grid, seed, max_moves=10, depth=2, trace=True)
        if moves == 3:
            wins_in_three += 1

    assert wins_in_three >= 7
