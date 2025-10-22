"""Heuristiikka-moduulin pytest-testit (päivitetty nykyiselle heuristiikalle)."""

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
# Uusi toteutus valitsee parhaan neljästä "käärme"-suunnasta (rotaatiot),
# joten yksittäisen kulman absoluuttista painoa ei voi testata suoraan.
# Testataan kulmien symmetriaa ja "käärmemäisen" rivin suosimista.

def test_snake_score_corners_are_symmetric_for_single_tile():
    # Sama yksittäinen laatta missä tahansa kulmassa -> sama maksimipiste
    boards = [
        G([[2, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]]),  # (0,0)
        G([[0, 0, 0, 2],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]]),  # (0,3)
        G([[0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [2, 0, 0, 0]]),  # (3,0)
        G([[0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 2]]),  # (3,3)
    ]
    scores = [h.snake_score(b) for b in boards]
    assert all(math.isfinite(s) for s in scores)
    # kaikkien kulmien pisteen tulee olla sama
    assert scores.count(scores[0]) == len(scores)

def test_snake_score_prefers_monotonic_snake_row():
    # Monotoninen rivi 8,4,2,0 vs. "rikottu" asettelu
    snake_like = G([[8, 4, 2, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]])
    broken = G([[8, 0, 4, 2],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]])
    assert h.snake_score(snake_like) > h.snake_score(broken)


# ---------- smoothness ----------
# Smoothness on negatiivinen log-erojen summa (vain ei-nollaparit).

def test_smoothness_equal_neighbors_no_penalty():
    # vierekkäiset identtiset laatat -> ero 0 -> ei rangaistusta
    g = G([[2, 2, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]])
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
# Uusi evaluate sisältää: empties, snake, smoothness, merge-potential, corner-bonus.
# Testataan suhteita ja käyttäytymistä, ei tarkkoja kertoimia.

def test_evaluate_is_finite_and_monotonic_with_empties():
    # Pidä "käärme" ja max-laatta kulmassa samana; lisää useita ei-vierekkäisiä laattoja,
    # jotta tyhjien väheneminen dominoi.
    g_sparse = G([[2, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]])
    g_denser = G([[2, 0, 0, 0],
                  [0, 2, 0, 2],   # valittu ei-vierekkäisiä: (1,1) ja (1,3)
                  [0, 0, 2, 0],   # diagonaali (2,2) ei vierekkäinen
                  [0, 0, 0, 0]])
    vs = h.evaluate(g_sparse)
    vd = h.evaluate(g_denser)
    assert math.isfinite(vs) and math.isfinite(vd)
    assert vs > vd  # enemmän tyhjää on parempi

def test_evaluate_corner_bonus_helps_when_max_in_corner():
    # Sama sisältö, mutta maksimi kulmassa vs. keskellä
    corner = G([[32, 0, 0, 0],
                [0,  0, 0, 0],
                [0,  0, 0, 0],
                [0,  0, 0, 0]])
    center = G([[0,  0, 0, 0],
                [0, 32, 0, 0],
                [0,  0, 0, 0],
                [0,  0, 0, 0]])
    assert h.evaluate(corner) > h.evaluate(center)

def test_evaluate_rewards_merge_potential():
    # Vierekkäinen pari vs. erillään olevat samat: merge-potential suosii paria
    paired = G([[2, 2, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]])
    split  = G([[2, 0, 2, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]])
    assert h.evaluate(paired) > h.evaluate(split)
