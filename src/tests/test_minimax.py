"""Minimax-moduulin pytest-testit."""

from unittest.mock import patch
import pytest
import src.minimax as ex


# ---------- yleis-fixture ----------

@pytest.fixture(autouse=True)
def _clear_tt():
    # Tyhjennä transpositiotaulu ennen ja jälkeen joka testin
    ex.tt.clear()
    yield
    ex.tt.clear()


# ---------- apuluokka ----------

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
    t = ex.make_key(g, 3, "min")
    assert isinstance(t, tuple) and t[1] == 3 and t[2] == "min"
    g[0][0] = 99
    assert t[0][0][0] == 0  # avain ei muutu takautuvasti

@patch.object(ex, "evaluate", return_value=6.25)
def test_leaf_value_returns_score_plus_heuristic(evaluate):
    s = FakeState([[2, 0, 0, 0]] + [[0]*4 for _ in range(3)], score=10)
    assert ex.leaf_value(s) == 16.25
    evaluate.assert_called_once_with(s.grid)

def test_dynamic_depth_rules():
    assert ex.dynamic_depth(4, 8) == 5         # e >= 8 -> b+1
    assert ex.dynamic_depth(5, 5) == 5         # 2 < e < 8 -> b
    assert ex.dynamic_depth(4, 2) == 3         # e <= 2 -> b-1
    assert ex.dynamic_depth(1, 1) == 1         # ei alle 1


# ---------- best_move_minimax ----------

@patch.object(ex, "min_value")
def test_best_move_minimax_selects_best_and_updates_alpha(min_value):
    # vasen ja ylös mahdollisia
    s = FakeState([[0]*4 for _ in range(4)], movable={"left": True, "up": True})
    # ensimmäinen siirto (left) palauttaa 1.0 -> alpha nousee 1.0
    # toinen siirto (up) palauttaa 3.0 -> paras
    min_value.side_effect = [1.0, 3.0]

    d, val = ex.best_move_minimax(s, depth=4)

    assert d == "up" and val == 3.0
    # tarkista että toisen kutsun alpha on päivittynyt 1.0:aan
    first_call = min_value.mock_calls[0]
    second_call = min_value.mock_calls[1]
    assert first_call.args[2] == float("-inf") and first_call.args[3] == float("inf")
    assert second_call.args[2] == 1.0 and second_call.args[3] == float("inf")


# ---------- max_value (MAX-solmu) ----------

@patch.object(ex, "leaf_value", return_value=42.0)
def test_max_value_returns_leaf_when_depth_zero(leaf_value):
    s = FakeState([[0]*4 for _ in range(4)])
    assert ex.max_value(s, d=0, alpha=-1e9, beta=1e9) == 42.0
    leaf_value.assert_called_once()

@patch.object(ex, "leaf_value", return_value=9.0)
def test_max_value_no_moves_returns_leaf_and_caches(leaf_value):
    s = FakeState([[2, 4, 2, 4],
                   [4, 2, 4, 2],
                   [2, 4, 2, 4],
                   [4, 2, 4, 2]], movable={})
    v = ex.max_value(s, d=2, alpha=-1e9, beta=1e9)
    assert v == 9.0
    key = ex.make_key(s.grid, 2, "max")
    assert key in ex.tt

@patch.object(ex, "min_value")
def test_max_value_selects_best_and_cache_hits(min_value):
    s = FakeState([[0]*4 for _ in range(4)], movable={"left": True, "up": True})
    min_value.side_effect = [1.5, 2.5]  # up parempi
    v1 = ex.max_value(s, d=3, alpha=float("-inf"), beta=float("inf"))
    assert v1 == 2.5
    # toinen kutsu hakee tt:stä -> ei uusia min_value-kutsuja
    v2 = ex.max_value(s, d=3, alpha=float("-inf"), beta=float("inf"))
    assert v2 == 2.5
    assert min_value.call_count == 2  # vain ensimmäisellä kerralla (kaksi siirtoa)

@patch.object(ex, "min_value", return_value=10.0)
def test_max_value_pruning_does_not_cache(min_value):
    # Yksi mahdollinen siirto riittää: heti v=10, alpha=max(-inf,10)=10 >= beta=0 -> katkaisu
    s = FakeState([[0]*4 for _ in range(4)], movable={"left": True})
    v = ex.max_value(s, d=2, alpha=float("-inf"), beta=0.0)
    assert v == 10.0
    key = ex.make_key(s.grid, 2, "max")
    assert key not in ex.tt  # katkaisussa ei talleteta


# ---------- min_value (MIN-solmu) ----------

@patch.object(ex, "leaf_value", return_value=5.0)
def test_min_value_returns_leaf_when_depth_zero(leaf_value):
    s = FakeState([[0]*4 for _ in range(4)])
    assert ex.min_value(s, d=0, alpha=-1e9, beta=1e9) == 5.0
    leaf_value.assert_called_once()

@patch.object(ex, "leaf_value", return_value=7.0)
def test_min_value_no_empties_returns_leaf_and_caches(leaf_value):
    s = FakeState([[2, 2, 2, 2],
                   [4, 4, 4, 4],
                   [8, 8, 8, 8],
                   [16, 32, 64, 128]], empties=[])
    v = ex.min_value(s, d=3, alpha=float("-inf"), beta=float("inf"))
    assert v == 7.0
    key = ex.make_key(s.grid, 3, "min")
    assert key in ex.tt

@patch.object(ex, "max_value")
def test_min_value_checks_all_cells_and_values_and_caches(max_value):
    # kaksi tyhjää -> (0,0), (1,1); MIN valitsee näistä pahimman (MAX:n kannalta pienimmän)
    empties = [(0, 0), (1, 1)]
    s = FakeState([[0]*4 for _ in range(4)], empties=empties)
    # käyntijärjestys:
    # (0,0) val=2, (0,0) val=4, (1,1) val=2, (1,1) val=4
    max_value.side_effect = [6.0, 3.0, 4.0, 8.0]
    # MIN valitsee näistä min( min(6,3), min(4,8) ) = min(3,4) = 3
    v = ex.min_value(s, d=2, alpha=float("-inf"), beta=float("inf"))
    assert v == 3.0
    assert max_value.call_count == 4
    key = ex.make_key(s.grid, 2, "min")
    assert key in ex.tt

@patch.object(ex, "max_value", return_value=1.0)
def test_min_value_cache_hits(max_value):
    s = FakeState([[0]*4 for _ in range(4)], empties=[(0, 0)])
    v1 = ex.min_value(s, d=2, alpha=float("-inf"), beta=float("inf"))
    v2 = ex.min_value(s, d=2, alpha=float("-inf"), beta=float("inf"))
    assert v1 == v2 == 1.0
    # max_value kutsuttiin vain ensimmäisen haun aikana kahdesti (2 ja 4)
    assert max_value.call_count == 2

@patch.object(ex, "max_value", return_value=1.0)
def test_min_value_pruning_does_not_cache(max_value):
    # Ensimmäinen lapsi tuottaa v=1 -> beta=min(inf,1)=1; alpha=5 -> alpha>=beta -> katkaisu
    s = FakeState([[0]*4 for _ in range(4)], empties=[(0, 0)])
    v = ex.min_value(s, d=2, alpha=5.0, beta=float("inf"))
    assert v == 1.0
    key = ex.make_key(s.grid, 2, "min")
    assert key not in ex.tt  # katkaisussa ei talleteta
