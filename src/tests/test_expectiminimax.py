"""Expectiminimax-moduulin pytest-testit."""

from unittest.mock import patch
import pytest
import src.expectiminimax as ex


# ---------- yleis-fixture ----------

@pytest.fixture(autouse=True)
def _clear_cache():
    # Tyhjennä välimuisti ennen ja jälkeen joka testin, jotta testit ovat riippumattomia
    ex.cache.clear()
    yield
    ex.cache.clear()


# ---------- apuluokat ----------

class FakeState:
    """Kevyt pelitilan korvike testejä varten.

    Ominaisuudet:
    - grid: 4x4 ruudukko (listojen lista)
    - score: kokonaispisteet (float/int)
    - empty_cells(): palauttaa ennalta määritellyn listan tyhjiä koordinaatteja
    - copy(): palauttaa uuden FakeState-olion, jolla on kopio gridistä
    - move_no_spawn(dir): palauttaa esiasetetun totuusarvon per suunta
    """

    def __init__(self, grid, empties=None, movable=None, score=0):
        self.grid = [row[:] for row in grid]
        self.score = score
        self._empties = list(empties or [])
        # movable-kartta: {"left": True/False, ...}
        default = {"left": False, "up": False, "right": False, "down": False}
        default.update(movable or {})
        self._movable = default

    def empty_cells(self):
        return list(self._empties)

    def copy(self):
        return FakeState(
            self.grid, empties=self._empties, movable=self._movable, score=self.score
        )

    def move_no_spawn(self, d):
        return bool(self._movable.get(d, False))


# ---------- make_key / leaf_value / dynamic_depth ----------

def test_make_key_is_deterministic():
    g = [[0, 2], [4, 0]]
    t = ex.make_key(g, 3, "chance")
    assert isinstance(t, tuple)
    # tuple(grid), depth, node-tyyppi
    assert t[1] == 3 and t[2] == "chance"
    # muutokset gridiin eivät muuta avainta retroaktiivisesti
    g[0][0] = 99
    assert t[0][0][0] == 0

@patch.object(ex, "evaluate", return_value=7.5)
def test_leaf_value_returns_score_plus_heuristic(evaluate):
    s = FakeState([[2, 0, 0, 0]] + [[0]*4 for _ in range(3)], score=100)
    assert ex.leaf_value(s) == 107.5
    evaluate.assert_called_once_with(s.grid)

def test_dynamic_depth_rules():
    # e >= 8 -> b+1
    assert ex.dynamic_depth(4, 8) == 5
    assert ex.dynamic_depth(2, 12) == 3
    # 2 < e < 8 -> b
    assert ex.dynamic_depth(5, 5) == 5
    # e <= 2 -> max(1, b-1)
    assert ex.dynamic_depth(4, 2) == 3
    assert ex.dynamic_depth(1, 1) == 1  # ei pudota alle 1


# ---------- best_move_expecti ----------

@patch.object(ex, "exp_value")
def test_best_move_expecti_selects_best_direction(exp_value):
    # vasen ja ylös ovat mahdollisia, oikea/alaspäin eivät
    s = FakeState([[0]*4 for _ in range(4)], movable={"left": True, "up": True})
    # MOVE_ORDER = (left, up, right, down) -> arvot vastaavat tätä järjestystä
    exp_value.side_effect = [10.0, 5.0]  # vasen parempi kuin ylös

    d, val = ex.best_move_expecti(s, depth=4)

    assert d == "left" and val == 10.0
    # exp_value kutsutaan vain kahdesti (vain toteuttamiskelpoiset siirrot)
    assert exp_value.call_count == 2

@patch.object(ex, "exp_value")
def test_best_move_expecti_uses_dynamic_depth(exp_value):
    # 16 tyhjää -> dynamic_depth(depth=4, e=16) = 5 -> exp_value saa d-1 = 4
    s = FakeState([[0]*4 for _ in range(4)], movable={"left": True})
    exp_value.return_value = 1.0
    ex.best_move_expecti(s, depth=4)
    # varmistetaan että exp_value:n toinen argumentti oli 4
    _, args, _ = exp_value.mock_calls[0]
    assert args[1] == 4

    # e <= 2 -> depth pienenee yhdellä (mutta vähintään 1)
    tight = FakeState(
        [[2, 2, 2, 2], [4, 4, 4, 4], [8, 8, 8, 8], [16, 0, 32, 64]],
        movable={"up": True},
    )
    exp_value.reset_mock()
    exp_value.return_value = 2.0
    ex.best_move_expecti(tight, depth=4)
    _, args, _ = exp_value.mock_calls[0]
    assert args[1] == 2  # dynamic_depth=3 -> d-1


# ---------- exp_value (CHANCE-solmu) ----------

@patch.object(ex, "leaf_value", return_value=42.0)
def test_exp_value_returns_leaf_when_depth_zero(leaf_value):
    s = FakeState([[0]*4 for _ in range(4)])
    assert ex.exp_value(s, d=0) == 42.0
    leaf_value.assert_called_once()

@patch.object(ex, "max_value")
def test_exp_value_computes_expected_value_over_all_cells_and_values(max_value):
    # kaksi tyhjää solua -> (r,c) = (0,0), (1,1)
    empties = [(0, 0), (1, 1)]
    s = FakeState([[0]*4 for _ in range(4)], empties=empties)

    # max_value kutsutaan järjestyksessä:
    # (0,0) val=2, (0,0) val=4, (1,1) val=2, (1,1) val=4
    max_value.side_effect = [1.0, 5.0, 3.0, 7.0]

    pf = ex.PROB_FOUR
    expected_total = (
        (1.0 - pf) * 1.0 + pf * 5.0 +     # solu (0,0)
        (1.0 - pf) * 3.0 + pf * 7.0       # solu (1,1)
    )
    expected = expected_total / len(empties)

    assert ex.exp_value(s, d=3) == expected
    # varmistetaan että max_value kutsuttiin neljä kertaa
    assert max_value.call_count == 4

@patch.object(ex, "max_value")
def test_exp_value_uses_cache_for_same_state(max_value):
    empties = [(0, 0)]
    s = FakeState([[0]*4 for _ in range(4)], empties=empties)
    max_value.return_value = 2.0

    # Ensimmäinen kutsu täyttää välimuistin
    v1 = ex.exp_value(s, d=2)
    # Toinen kutsu samaan tilaan ja syvyyteen -> ei uusia max_value-kutsuja
    v2 = ex.exp_value(s, d=2)

    assert v1 == v2
    assert max_value.call_count == 2  # val=2 ja val=4 (kaksi arvoa) vain ensimmäisellä kerralla

@patch.object(ex, "leaf_value", return_value=7.0)
def test_exp_value_with_no_empties_returns_leaf_and_caches(leaf_value):
    s = FakeState([[2, 2, 2, 2], [4, 4, 4, 4], [8, 8, 8, 8], [16, 32, 64, 128]], empties=[])
    # Ei tyhjiä -> leaf + cache
    v1 = ex.exp_value(s, d=3)
    v2 = ex.exp_value(s, d=3)
    assert v1 == 7.0 and v2 == 7.0
    leaf_value.assert_called_once()  # toinen kerta tuli välimuistista


# ---------- max_value (MAX-solmu) ----------

@patch.object(ex, "leaf_value", return_value=123.0)
def test_max_value_returns_leaf_when_no_moves(leaf_value):
    # kaikki suunnat ovat mahdottomia
    s = FakeState([[2, 4, 2, 4],
                   [4, 2, 4, 2],
                   [2, 4, 2, 4],
                   [4, 2, 4, 2]],
                  movable={"left": False, "up": False, "right": False, "down": False})
    assert ex.max_value(s, d=3) == 123.0
    leaf_value.assert_called_once()

@patch.object(ex, "exp_value")
def test_max_value_selects_best_move(exp_value):
    # vasen ja ylös mahdollisia
    s = FakeState([[0]*4 for _ in range(4)], movable={"left": True, "up": True})
    exp_value.side_effect = [1.5, 3.0]  # ylös parempi

    res = ex.max_value(s, d=2)
    assert res == 3.0

    # tarkista että exp_value kutsuttiin kahdesti
    assert exp_value.call_count == 2
    # tarkista että toinen argumentti oli aina d-1 = 1
    for _, args, _ in exp_value.mock_calls:
        assert args[1] == 1

@patch.object(ex, "leaf_value", return_value=9.0)
@patch.object(ex, "exp_value", return_value=5.0)
def test_max_value_cache_hits(exp_value, leaf_value):
    # yksi mahdollinen siirto -> ensimmäinen kutsu täyttää välimuistin
    s = FakeState([[0]*4 for _ in range(4)], movable={"left": True})
    v1 = ex.max_value(s, d=3)
    v2 = ex.max_value(s, d=3)
    assert v1 == v2 == 5.0
    exp_value.assert_called_once()
