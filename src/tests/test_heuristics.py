"""Heuristiikka-moduulin pytest-testit."""

import math
import src.heuristics as h


# ---------- apu ----------

def G(rows):
    """Pieni apu luettavuuteen: rakentaa ruudukon riveistä."""
    return [row[:] for row in rows]


# ---------- log_value ----------

def test_log_value_basic_and_zero():
    assert h.log_value(0) == 0.0
    assert h.log_value(2) == 1.0
    assert h.log_value(4) == 2.0
    assert h.log_value(8) == 3.0


# ---------- count_empties ----------

def test_count_empties_counts_zeros_only():
    g = G([[0, 2, 0, 4],
           [8, 0, 16, 0],
           [0, 0, 0, 0],
           [2, 4, 8, 16]])
    # nollien määrä: 8 kpl
    assert h.count_empties(g) == 8


# ---------- snake_score ----------

def test_snake_score_single_tile_weighting():
    # yksi laatta painavassa kulmassa -> suuri pistelisä
    g1 = G([[2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]])
    # log2(2) * paino(0,0)=15 -> 1*15 = 15
    assert h.snake_score(g1) == 15.0

    # sama laatta kevyessä nurkassa (alavasen paino 0) -> 0 pistettä
    g2 = G([[0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 0, 0, 0]])
    assert h.snake_score(g2) == 0.0

def test_snake_score_multiple_tiles_sum():
    g = G([[2, 4, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 2]])
    # (0,0): log2(2)=1 * 15 = 15
    # (0,1): log2(4)=2 * 14 = 28
    # (3,3): log2(2)=1 * 3  = 3
    assert h.snake_score(g) == 46.0  # 15 + 28 + 3


# ---------- smoothness ----------

def test_smoothness_equal_neighbors_no_penalty():
    # vierekkäiset identtiset laatat -> ero 0 -> ei rangaistusta
    g = G([[2, 2, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]])
    # yksi vaakapari: |log2(2)-log2(2)| = 0 -> -(0) = 0
    assert h.smoothness(g) == 0.0

def test_smoothness_penalizes_large_diffs():
    # 2 ja 32 vierekkäin -> suuri ero log-asteikolla
    g = G([[2, 32, 0, 0],
           [0,  0, 0, 0],
           [0,  0, 0, 0],
           [0,  0, 0, 0]])
    diff = abs(h.log_value(2) - h.log_value(32))  # |1 - 5| = 4
    assert h.smoothness(g) == -diff  # -(4)

def test_smoothness_ignores_zeros_in_pairs():
    # nolla katkaisee parin: (4,0), (0,8) ja (8,0) sivuutetaan -> summa 0
    g = G([[4, 0, 8, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]])
    assert h.smoothness(g) == 0.0

def test_smoothness_counts_both_horizontal_and_vertical():
    g = G([[2, 2, 0, 0],
           [2, 4, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]])
    # vaakasuunnassa: (2,2)->0, (2,4)->1
    h_sum = 0 + 1
    # pystysuunnassa: (2,2)->0, (2,4)->1
    v_sum = 0 + 1
    assert h.smoothness(g) == -(h_sum + v_sum)  # -(2) = -2.0


# ---------- evaluate (yhdistelmä) ----------

def test_evaluate_combines_terms_with_weights():
    g = G([[2, 0, 0, 0],
           [0, 4, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]])
    empties = h.count_empties(g)
    snake   = h.snake_score(g)
    smooth  = h.smoothness(g)
    expected = 7.0 * empties + 1.5 * snake + 0.2 * smooth
    assert math.isclose(h.evaluate(g), expected, rel_tol=1e-12, abs_tol=1e-12)

def test_evaluate_prefers_more_empties_all_else_equal():
    # Harvempi: vain yksi laatta painavassa kulmassa
    g_sparse = G([[2, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]])
    # Tiheämpi: lisätään yksi laatta kohtaan, jonka paino on 0 (3,0)
    # -> snake ei muutu ja smoothness ei saa pareja lisää, mutta tyhjiä on vähemmän.
    g_dense = G([[2, 0, 0, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0],
                 [2, 0, 0, 0]])

    assert h.evaluate(g_sparse) > h.evaluate(g_dense)
