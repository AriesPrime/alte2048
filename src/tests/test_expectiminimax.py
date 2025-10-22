"""Expectiminimax-moduulin pytest-testit."""

from unittest.mock import patch
import pytest
import src.expectiminimax as ex


# ---------- yleis-fixture ----------

@pytest.fixture(autouse=True)
def _clear_cache():
    # Tyhjennä välimuistit ennen ja jälkeen joka testin
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
    """

    def __init__(self, grid, empties=None, score=0):
        self.grid = [row[:] for row in grid]
        self.score = score
        self._empties = list(empties or [])

    def empty_cells(self):
        return list(self._empties)

    def copy(self):
        return FakeState(self.grid, empties=self._empties, score=self.score)


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

@patch.object(ex, "eval_cached", return_value=7.5)
def test_leaf_value_returns_score_plus_heuristic(eval_cached):
    s = FakeState([[2, 0, 0, 0]] + [[0]*4 for _ in range(3)], score=100)
    assert ex.leaf_value(s) == 107.5
    eval_cached.assert_called_once_with(s.grid)

def test_dynamic_depth_rules():
    # Palvelulogiikka: paljon tyhjiä -> syvemmälle; vähän tyhjiä -> matalammalle;
    # iso laatan ollessa jo suuri ja tyhjää vähän -> lisää hieman syvyyttä.
    assert ex.dynamic_depth(4, 8, largest=0) >= 5      # +1 kun e >= 8
    assert ex.dynamic_depth(4, 12, largest=0) >= 6     # +2 kun e >= 12
    assert ex.dynamic_depth(5, 5, largest=0) == 5      # väliarvot -> perus
    assert ex.dynamic_depth(4, 2, largest=0) == 3      # vähän tyhjää -> -1 (mutta >=1)
    assert ex.dynamic_depth(1, 1, largest=0) == 1
    # jos iso laatta on jo suuri ja tila tiukka, syvyyttä lisätään hieman
    assert ex.dynamic_depth(4, 4, largest=2048) >= 5


# ---------- best_move_expecti ----------

@patch.object(ex, "exp_value")
def test_best_move_expecti_selects_best_direction(exp_value):
    # Tee kaksi toteuttamiskelpoista siirtoa:
    # - vasen: (0,1)=2 siirtyy vasemmalle
    # - ylös:  (1,0)=2 siirtyy ylöspäin
    s = FakeState([
        [0, 2, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])
    # MOVE_ORDER = (left, up, right, down) -> arvot vastaavat tätä järjestystä
    exp_value.side_effect = [10.0, 5.0]  # vasen parempi kuin ylös

    d, val = ex.best_move_expecti(s, depth=4)

    assert d == "left" and val == 10.0
    # exp_value kutsutaan vain kahdesti (vain toteuttamiskelpoiset siirrot)
    assert exp_value.call_count == 2

@patch.object(ex, "exp_value")
def test_best_move_expecti_uses_dynamic_depth(exp_value):
    # 15 tyhjää (yksi laatta) -> base depth=4, e>=12 -> dynamic_depth = 6 -> exp saa d-1 = 5
    s = FakeState([
        [0, 2, 0, 0],  # vasen on mahdollinen
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])
    exp_value.return_value = 1.0
    ex.best_move_expecti(s, depth=4)
    # varmistetaan että exp_value:n toinen argumentti oli 5
    _, args, _ = exp_value.mock_calls[0]
    assert args[1] == 5

    # tiukka tila (<=2 tyhjää) alentaa syvyyttä: esim. d=4, e=2 -> dyn=3 -> exp d-1=2
    tight = FakeState(
        [[2, 2, 2, 2],
         [4, 4, 4, 4],
         [8, 8, 8, 8],
         [16, 0, 32, 0]]
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
    # val=2 ja val=4 (kaksi arvoa) vain ensimmäisellä kerralla
    assert max_value.call_count == 2

@patch.object(ex, "leaf_value", return_value=7.0)
def test_exp_value_with_no_empties_returns_leaf_and_caches(leaf_value):
    s = FakeState([[2, 2, 2, 2],
                   [4, 4, 4, 4],
                   [8, 8, 8, 8],
                   [16, 32, 64, 128]],
                  empties=[])
    # Ei tyhjiä -> leaf + cache
    v1 = ex.exp_value(s, d=3)
    v2 = ex.exp_value(s, d=3)
    assert v1 == 7.0 and v2 == 7.0
    leaf_value.assert_called_once()  # toinen kerta tuli välimuistista


# ---------- max_value (MAX-solmu) ----------

@patch.object(ex, "leaf_value", return_value=123.0)
def test_max_value_returns_leaf_when_no_moves(leaf_value):
    # tee lauta, jossa mikään suunta ei muuta laattoja (täysi ja ei-yhdistyvä)
    s = FakeState([[2, 4, 2, 4],
                   [4, 2, 4, 2],
                   [2, 4, 2, 4],
                   [4, 2, 4, 2]])
    assert ex.max_value(s, d=3) == 123.0
    leaf_value.assert_called_once()

@patch.object(ex, "exp_value")
def test_max_value_selects_best_move(exp_value):
    # molemmat siirrot mahdollisia (ks. best_move-testin asettelu)
    s = FakeState([
        [0, 2, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])
    exp_value.side_effect = [1.5, 3.0]  # ylös parempi

    res = ex.max_value(s, d=2)
    assert res == 3.0

    # tarkista että exp_value kutsuttiin kahdesti ja d-1 välittyi
    assert exp_value.call_count == 2
    for _, args, _ in exp_value.mock_calls:
        assert args[1] == 1

@patch.object(ex, "leaf_value", return_value=9.0)
@patch.object(ex, "exp_value", return_value=5.0)
def test_max_value_cache_hits(exp_value, leaf_value):
    # vähintään yksi mahdollinen siirto -> cache täyttyy
    s = FakeState([
        [0, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])
    v1 = ex.max_value(s, d=3)
    v2 = ex.max_value(s, d=3)
    assert v1 == v2 == 5.0
    exp_value.assert_called_once()
