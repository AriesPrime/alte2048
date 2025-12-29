"""Expectiminimax-moduulin pytest-testit."""

from unittest.mock import patch
import pytest
import src.expectiminimax as ex


# ---------- yleis-fixture ----------

@pytest.fixture(autouse=True)
def _clear_cache():
    # Tyhjennä välimuistit ennen ja jälkeen joka testin
    ex.cache.clear()
    ex._eval_cache.clear()
    yield
    ex.cache.clear()
    ex._eval_cache.clear()


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
    assert ex.dynamic_depth(4, 8, largest=0) >= 5
    assert ex.dynamic_depth(4, 12, largest=0) >= 6
    assert ex.dynamic_depth(5, 5, largest=0) == 5
    assert ex.dynamic_depth(4, 2, largest=0) == 3
    assert ex.dynamic_depth(1, 1, largest=0) == 1
    assert ex.dynamic_depth(4, 4, largest=2048) >= 5


# ---------- best_move_expecti ----------
# Huom: monkeypatchataan _ordered_moves, jotta ohjataan tarkasti montako siirtoa arvioidaan.

@patch.object(ex, "exp_value")
def test_best_move_expecti_selects_best_direction(exp_value, monkeypatch):
    # Rakennetaan siirrot: vasen ja ylös (täsmälleen 2 haaraa)
    s = FakeState([
        [0, 2, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])

    # Generoi kaksi toteuttamiskelpoista siirtoa olemassa olevalla logiikalla
    left_grid, left_gain = ex.MOVE_FUN["left"](s.grid)
    up_grid, up_gain = ex.MOVE_FUN["up"](s.grid)

    def fake_ordered_moves(_s):
        # proxy-arvolla ei väliä tässä, palautetaan kiinteä lista
        return [
            ("left", left_grid, left_gain, 0.0),
            ("up",   up_grid,   up_gain,   0.0),
        ]

    monkeypatch.setattr(ex, "_ordered_moves", fake_ordered_moves)
    exp_value.side_effect = [10.0, 5.0]  # vasen parempi kuin ylös

    d, val = ex.best_move_expecti(s, depth=4)
    assert d == "left" and val == 10.0
    assert exp_value.call_count == 2

@patch.object(ex, "exp_value")
def test_best_move_expecti_uses_dynamic_depth(exp_value, monkeypatch):
    s = FakeState([
        [0, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])
    # Yksi ainoa haara, jotta tarkistetaan d-1 täsmällisesti
    left_grid, left_gain = ex.MOVE_FUN["left"](s.grid)
    monkeypatch.setattr(
        ex, "_ordered_moves",
        lambda _s: [("left", left_grid, left_gain, 0.0)]
    )
    exp_value.return_value = 1.0
    ex.best_move_expecti(s, depth=4)
    _, args, _ = exp_value.mock_calls[0]
    assert args[1] == 5  # dynamic depth 6 -> exp depth 5

    # tiukka tila (<=2 tyhjää) alentaa syvyyttä
    tight = FakeState(
        [[2, 2, 2, 2],
         [4, 4, 4, 4],
         [8, 8, 8, 8],
         [16, 0, 32, 0]]
    )
    # Tehdään myös tälle vain yksi haara
    tg, gg = ex.MOVE_FUN["left"](tight.grid)
    exp_value.reset_mock()
    exp_value.return_value = 2.0
    monkeypatch.setattr(
        ex, "_ordered_moves",
        lambda _s: [("left", tg, gg, 0.0)]
    )
    ex.best_move_expecti(tight, depth=4)
    _, args, _ = exp_value.mock_calls[0]
    assert args[1] == 2  # dynamic depth=3 -> exp d-1


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

@patch.object(ex, "exp_value")
def test_max_value_selects_best_move(exp_value, monkeypatch):
    # Varmistetaan, että vain 2 haaraa arvioidaan ja järjestys pysyy deterministisenä
    s = FakeState([
        [0, 2, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])
    left_grid, left_gain = ex.MOVE_FUN["left"](s.grid)
    up_grid, up_gain = ex.MOVE_FUN["up"](s.grid)

    monkeypatch.setattr(
        ex, "_ordered_moves",
        lambda _s: [("left", left_grid, left_gain, 0.0),
                    ("up",   up_grid,   up_gain,   0.0)]
    )

    exp_value.side_effect = [1.5, 3.0]  # ylös parempi
    res = ex.max_value(s, d=2)
    assert res == 3.0
    assert exp_value.call_count == 2
    for _, args, _ in exp_value.mock_calls:
        assert args[1] == 1  # d-1

@patch.object(ex, "leaf_value", return_value=9.0)
@patch.object(ex, "exp_value", return_value=5.0)
def test_max_value_cache_hits(exp_value, leaf_value, monkeypatch):
    # Yksi ainoa haara -> exp_value tulisi kutsua tasan kerran (ja sitten cache osuu)
    s = FakeState([
        [0, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])
    left_grid, left_gain = ex.MOVE_FUN["left"](s.grid)
    monkeypatch.setattr(
        ex, "_ordered_moves",
        lambda _s: [("left", left_grid, left_gain, 0.0)]
    )

    v1 = ex.max_value(s, d=3)
    v2 = ex.max_value(s, d=3)
    assert v1 == v2 == 5.0
    exp_value.assert_called_once()

@patch.object(ex, "leaf_value", return_value=123.0)
def test_max_value_returns_leaf_when_no_moves(leaf_value):
    # tee lauta, jossa mikään suunta ei muuta laattoja (täysi ja ei-yhdistyvä)
    s = FakeState([[2, 4, 2, 4],
                   [4, 2, 4, 2],
                   [2, 4, 2, 4],
                   [4, 2, 4, 2]])
    assert ex.max_value(s, d=3) == 123.0
    leaf_value.assert_called_once()


# ---------- lisätestit algoritmin käyttäytymisestä ----------

def test_order_cells_prefers_corners_then_edges_then_center():
    # Tarkistetaan deterministinen järjestys: kulmat ennen reunoja ennen keskusta.
    g = [[0]*4 for _ in range(4)]
    cells = [(1,1), (0,1), (0,0), (2,3), (3,3), (1,0)]
    got = ex._order_cells(g, cells)
    assert got[:2] == [(0, 0), (3, 3)]
    assert (1, 1) == got[-1]

def test_exp_value_thins_cells_to_top_six_when_many_empties_and_deep(monkeypatch):
    # Kun tyhjiä on paljon ja d>=3, vain 6 paikkaa käytetään.
    # Tehdään ruudukko jossa 12 tyhjää. Varmistetaan että max_value kutsutaan 6*2 kertaa (2- ja 4-laatat).
    empties = [(r, c) for r in range(3) for c in range(4)]  # 12 kpl
    s = FakeState([[0]*4 for _ in range(3)] + [[2,2,2,2]], empties=empties)

    calls = {"n": 0}
    def fake_max_value(_s, _d):
        calls["n"] += 1
        return 0.0

    monkeypatch.setattr(ex, "max_value", fake_max_value)
    ex.exp_value(s, d=3)
    assert calls["n"] == 12  # 6 solua * 2 arvoa

def test_best_move_returns_left_and_leaf_when_no_moves(monkeypatch):
    # Ei toteuttamiskelpoisia siirtoja -> palautetaan "left" ja leaf_value
    s = FakeState([[2,4,2,4],[4,2,4,2],[2,4,2,4],[4,2,4,2]], score=100)
    monkeypatch.setattr(ex, "leaf_value", lambda _s: 123.0)
    d, val = ex.best_move_expecti(s, depth=4)
    assert d == "left" and val == 123.0

def test_eval_cached_stores_and_reuses(monkeypatch):
    # Varmistetaan että evaluate kutsutaan vain kerran samalle gridille.
    called = {"n": 0}
    def fake_evaluate(g):
        called["n"] += 1
        return 7.0
    monkeypatch.setattr(ex, "evaluate", fake_evaluate)

    g = [[2,0,0,0]] + [[0]*4 for _ in range(3)]
    v1 = ex.eval_cached(g)
    v2 = ex.eval_cached(g)
    assert v1 == v2 == 7.0
    assert called["n"] == 1  # cache is working

def test_best_move_clears_caches_before_search(monkeypatch):
    # Tarkistetaan, että ENNEN hakua olemassa olleet avaimet tyhjennetään,
    # vaikka haku itsessään täyttäisi välimuistin uudelleen.
    ex.cache[("x",)] = 1.0
    ex._eval_cache[("y",)] = 2.0

    s = FakeState([[0,2,0,0]] + [[0]*4 for _ in range(3)])
    # Rajataan haku yhteen haaraan, jotta testistä tulee deterministinen
    left_grid, left_gain = ex.MOVE_FUN["left"](s.grid)
    monkeypatch.setattr(
        ex, "_ordered_moves",
        lambda _s: [("left", left_grid, left_gain, 0.0)]
    )
    monkeypatch.setattr(ex, "exp_value", lambda *_: 0.0)

    ex.best_move_expecti(s, depth=4)

    # Vanhojen avainten pitää olla poissa:
    assert ("x",) not in ex.cache
    assert ("y",) not in ex._eval_cache

def test_ordered_moves_uses_proxy_sorting(monkeypatch):
    # Tehdään kaksi toteuttamiskelpoista siirtoa ja annetaan proxy-arvot eri suuruisiksi.
    # Tarkistetaan että järjestys vastaa proxy-arvoa.
    s = FakeState([
        [0, 2, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])
    orig_proxy = ex._proxy_child_score
    def fake_proxy(new_grid, gained, base_score):
        # jos vasemmalle, new_grid[0][0] on 2
        return 100.0 if new_grid[0][0] == 2 else 0.0
    monkeypatch.setattr(ex, "_proxy_child_score", fake_proxy)

    moves = ex._ordered_moves(s)
    # Ensimmäinen liike listassa on se jolla suurin proxy, eli vasen
    assert moves and moves[0][0] == "left"

    # Palauta alkuperäinen funktio
    monkeypatch.setattr(ex, "_proxy_child_score", orig_proxy)

def test_proxy_child_score_includes_gained_and_empties():
    # Varmistetaan että gained ja empties vaikuttavat arvoon.
    base = 10.0
    # new_grid jossa 16 tyhjää, gained 8 -> arvon tulisi kasvaa molemmista
    g_all_zero = [[0]*4 for _ in range(4)]
    v1 = ex._proxy_child_score(g_all_zero, gained=8, base_score=base)
    # new_grid lähes täynnä, gained 0 -> selvästi pienempi
    g_full = [[2]*4 for _ in range(4)]
    v2 = ex._proxy_child_score(g_full, gained=0, base_score=base)
    assert v1 > v2
