"""grid_ops-moduulin pytest-testit."""

import pytest
from src.grid_ops import (
    _compress_line_left,
    _move_generic,
    move_left_grid,
    move_right_grid,
    move_up_grid,
    move_down_grid,
    MOVE_FUN,
)

# ---------- _compress_line_left ----------

def test_compress_merges_and_scores():
    # 2+2=4, loput nollilla
    uusi, gain = _compress_line_left([2, 2, 0, 0])
    assert uusi == [4, 0, 0, 0]
    assert gain == 4

def test_compress_no_merge_keeps_order():
    uusi, gain = _compress_line_left([2, 4, 8, 16])
    assert uusi == [2, 4, 8, 16]
    assert gain == 0

def test_compress_removes_gaps_before_merging():
    # välinolla poistuu -> 2 ja 2 yhdistyvät
    uusi, gain = _compress_line_left([2, 0, 2, 2])
    assert uusi == [4, 2, 0, 0]
    assert gain == 4

def test_compress_two_merges_in_one_row():
    uusi, gain = _compress_line_left([2, 2, 4, 4])
    assert uusi == [4, 8, 0, 0]
    assert gain == 12

def test_compress_no_double_merge_in_chain():
    # 2,2,2 -> vain eka pari yhdistyy
    uusi, gain = _compress_line_left([2, 2, 2, 0])
    assert uusi == [4, 2, 0, 0]
    assert gain == 4

def test_compress_four_twos_become_two_fours():
    uusi, gain = _compress_line_left([2, 2, 2, 2])
    assert uusi == [4, 4, 0, 0]
    assert gain == 8


# ---------- _move_generic ja julkiset siirrot ----------

def test_move_generic_left_basic_logic():
    g = [
        [2, 0, 2, 4],
        [0, 0, 0, 0],
        [4, 4, 8, 8],
        [2, 2, 2, 2],
    ]
    uusi, gain = _move_generic(g, reverse=False, transpose=False)
    assert uusi == [
        [4, 4, 0, 0],
        [0, 0, 0, 0],
        [8, 16, 0, 0],
        [4, 4, 0, 0],
    ]
    # rivi- ja pysty-yhdistykset: 4 + 8 + 16 + 4 + 4 = 36
    assert gain == (4 + 8 + 16 + 4 + 4)

def test_move_generic_right_basic_logic():
    g = [
        [2, 0, 2, 4],
        [0, 2, 2, 0],
        [4, 4, 8, 8],
        [0, 0, 2, 2],
    ]
    uusi, gain = _move_generic(g, reverse=True, transpose=False)
    assert uusi == [
        [0, 0, 4, 4],
        [0, 0, 0, 4],
        [0, 0, 8, 16],
        [0, 0, 0, 4],
    ]
    assert gain == (4 + 4 + 8 + 16 + 4)

@pytest.mark.parametrize(
    "fun,reverse,transpose",
    [
        (move_left_grid,  False, False),
        (move_right_grid, True,  False),
        (move_up_grid,    False, True),
        (move_down_grid,  True,  True),
    ],
)
def test_public_moves_match_move_generic(fun, reverse, transpose):
    g = [
        [0, 2, 0, 2],
        [2, 2, 0, 0],
        [0, 4, 4, 0],
        [2, 0, 2, 0],
    ]
    odotettu, od_gain = _move_generic(g, reverse=reverse, transpose=transpose)
    uusi, gain = fun(g)
    assert uusi == odotettu and gain == od_gain

def test_moves_do_not_mutate_input_grid():
    g = [
        [2, 0, 2, 0],
        [0, 2, 0, 2],
        [4, 0, 4, 0],
        [0, 0, 0, 0],
    ]
    g_kopio = [r[:] for r in g]
    _ = move_left_grid(g)
    assert g == g_kopio  # puhtaat funktiot: ei mutaatioita

def test_full_grid_no_merges_no_movement_no_gain():
    g = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    for fun in (move_left_grid, move_right_grid, move_up_grid, move_down_grid):
        uusi, gain = fun(g)
        assert uusi == g
        assert gain == 0

def test_empty_grid_stays_empty_all_directions():
    g = [[0, 0, 0, 0] for _ in range(4)]
    for fun in (move_left_grid, move_right_grid, move_up_grid, move_down_grid):
        uusi, gain = fun(g)
        assert uusi == g
        assert gain == 0

def test_vertical_merges_work_up_and_down():
    g = [
        [2, 0, 0, 0],
        [2, 0, 4, 0],
        [0, 0, 4, 0],
        [0, 0, 0, 0],
    ]
    uusi_up, gain_up = move_up_grid(g)
    assert uusi_up == [
        [4, 0, 8, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    assert gain_up == 12

    uusi_down, gain_down = move_down_grid(g)
    assert uusi_down == [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [4, 0, 8, 0],
    ]
    assert gain_down == 12


# ---------- MOVE_FUN-sanakirja ----------

def test_move_fun_contains_all_directions_and_callables():
    for key in ("left", "right", "up", "down"):
        assert key in MOVE_FUN
        assert callable(MOVE_FUN[key])

@pytest.mark.parametrize(
    "dirkey, direct_fun",
    [
        ("left", move_left_grid),
        ("right", move_right_grid),
        ("up", move_up_grid),
        ("down", move_down_grid),
    ],
)
def test_move_fun_matches_direct_call(dirkey, direct_fun):
    g = [
        [0, 2, 2, 0],
        [0, 0, 0, 0],
        [4, 4, 0, 0],
        [0, 2, 0, 2],
    ]
    via_dict, gain_dict = MOVE_FUN[dirkey](g)
    direct, gain_direct = direct_fun(g)
    assert via_dict == direct and gain_dict == gain_direct
