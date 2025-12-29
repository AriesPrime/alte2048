"""Heuristiikka-moduulin pytest-testit (paivitetty nykyiselle heuristiikalle)."""

import math
import src.heuristics as h


def G(rows):
    return [row[:] for row in rows]


def rot90(g):
    return [list(col) for col in zip(*g[::-1])]


def test_log_value_basic_and_zero():
    assert h.log_value(0) == 0.0
    assert h.log_value(2) == 1.0
    assert h.log_value(4) == 2.0
    assert h.log_value(8) == 3.0


def test_count_empties_counts_zeros_only():
    g = G(
        [
            [0, 2, 0, 4],
            [8, 0, 16, 0],
            [0, 0, 0, 0],
            [2, 4, 8, 16],
        ]
    )
    assert h.count_empties(g) == 8


def test_snake_score_corners_are_symmetric_for_single_tile():
    boards = [
        G([[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
        G([[0, 0, 0, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
        G([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0]]),
        G([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]]),
    ]
    scores = [h.snake_score(b) for b in boards]
    assert all(math.isfinite(s) for s in scores)
    assert scores.count(scores[0]) == len(scores)


def test_snake_score_is_rotation_invariant_on_dense_board():
    g = G(
        [
            [512, 256, 128, 64],
            [32, 16, 8, 4],
            [2, 4, 8, 16],
            [32, 64, 128, 256],
        ]
    )
    s0 = h.snake_score(g)
    s1 = h.snake_score(rot90(g))
    s2 = h.snake_score(rot90(rot90(g)))
    s3 = h.snake_score(rot90(rot90(rot90(g))))
    assert s0 == s1 == s2 == s3


def test_snake_score_prefers_monotonic_snake_row():
    snake_like = G([[8, 4, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    broken = G([[8, 0, 4, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    assert h.snake_score(snake_like) > h.snake_score(broken)


def test_snake_score_prefers_large_tile_on_snake_path():
    good = G(
        [
            [512, 256, 128, 64],
            [32, 16, 8, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
    )
    bad = G(
        [
            [256, 128, 64, 32],
            [16, 8, 4, 512],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
    )
    assert h.snake_score(good) > h.snake_score(bad)


def test_snake_score_prefers_corner_over_edge_on_dense_board():
    corner = G(
        [
            [512, 8, 4, 2],
            [16, 8, 4, 2],
            [16, 8, 4, 2],
            [16, 8, 4, 2],
        ]
    )
    edge = G(
        [
            [8, 512, 4, 2],
            [16, 8, 4, 2],
            [16, 8, 4, 2],
            [16, 8, 4, 2],
        ]
    )
    assert h.snake_score(corner) > h.snake_score(edge)


def test_smoothness_equal_neighbors_no_penalty():
    g = G([[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    assert h.smoothness(g) == 0.0


def test_smoothness_penalizes_large_diffs():
    g = G([[2, 32, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    diff = abs(h.log_value(2) - h.log_value(32))
    assert h.smoothness(g) == -diff


def test_smoothness_ignores_zeros_in_pairs():
    g = G([[4, 0, 8, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    assert h.smoothness(g) == 0.0


def test_smoothness_counts_both_horizontal_and_vertical():
    g = G([[2, 2, 0, 0], [2, 4, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    h_sum = 0 + 1
    v_sum = 0 + 1
    assert h.smoothness(g) == -(h_sum + v_sum)


def test_evaluate_is_finite_and_monotonic_with_empties():
    g_sparse = G([[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    g_denser = G([[2, 0, 0, 0], [0, 2, 0, 2], [0, 0, 2, 0], [0, 0, 0, 0]])
    vs = h.evaluate(g_sparse)
    vd = h.evaluate(g_denser)
    assert math.isfinite(vs) and math.isfinite(vd)
    assert vs > vd


def test_evaluate_corner_bonus_helps_when_max_in_corner_on_dense_board():
    corner = G(
        [
            [512, 8, 4, 2],
            [16, 8, 4, 2],
            [16, 8, 4, 2],
            [16, 8, 4, 2],
        ]
    )
    centerish = G(
        [
            [8, 4, 2, 8],
            [16, 512, 4, 2],
            [16, 8, 4, 2],
            [16, 8, 4, 2],
        ]
    )
    assert h.evaluate(corner) > h.evaluate(centerish)


def test_evaluate_rewards_merge_potential_on_dense_board():
    paired = G(
        [
            [64, 64, 32, 16],
            [8, 4, 2, 2],
            [16, 8, 4, 2],
            [2, 4, 8, 16],
        ]
    )
    split = G(
        [
            [64, 32, 64, 16],
            [8, 4, 2, 2],
            [16, 8, 4, 2],
            [2, 4, 8, 16],
        ]
    )
    assert h.evaluate(paired) > h.evaluate(split)
