"""Board-moduulin pytest-testit."""

import copy
from unittest.mock import patch

import src.board as board


# ---------- apufunktiot ----------

def make_grid(rows):
    """Palauttaa syväkopion riveistä (varmistaa erillisen muutettavuuden)."""
    return [row[:] for row in rows]


# ---------- compress_row_left ----------

def test_compress_row_left_basic_merge():
    out, gain = board.compress_row_left([2, 2, 0, 0])
    assert out == [4, 0, 0, 0]
    assert gain == 4

def test_compress_row_left_chain_and_no_double_merge():
    # 2+2 yhdistyy, viimeinen 2 jää ilman paria
    out, gain = board.compress_row_left([2, 2, 2, 0])
    assert out == [4, 2, 0, 0]
    assert gain == 4

    # kaksi erillistä yhdistymistä: 2+2 ja 4+4
    out, gain = board.compress_row_left([2, 2, 4, 4])
    assert out == [4, 8, 0, 0]
    assert gain == 12

def test_compress_row_left_handles_zeros_in_between():
    # nollat rivin välissä eivät estä yhdistymistä
    out, gain = board.compress_row_left([2, 0, 2, 2])
    assert out == [4, 2, 0, 0]
    assert gain == 4


# ---------- slide_left & pisteet ----------

def test_slide_left_updates_grid_and_score_when_changed():
    s = board.GameState(make_grid([[2, 2, 0, 0],
                                   [0, 0, 0, 0],
                                   [2, 0, 2, 0],
                                   [4, 4, 4, 0]]))
    gained = s.slide_left()
    assert s.grid == [[4, 0, 0, 0],
                      [0, 0, 0, 0],
                      [4, 0, 0, 0],
                      [8, 4, 0, 0]]
    assert gained == 4 + 4 + 8
    assert s.score == 16

def test_slide_left_returns_zero_and_no_score_when_no_change():
    s = board.GameState(make_grid([[4, 2, 1, 1],
                                   [2, 4, 8, 16],
                                   [32, 64, 128, 256],
                                   [0, 0, 0, 0]]))
    # muutetaan ylintä riviä niin, ettei yhdistymisiä ole
    s.grid = make_grid([[4, 2, 1, 8],
                        [2, 4, 8, 16],
                        [32, 64, 128, 256],
                        [0, 0, 0, 0]])
    gained = s.slide_left()
    assert gained == 0
    assert s.score == 0  # pisteitä kertyy vain, jos ruudukko muuttuu


# ---------- apply_move (kaikki suunnat) ----------

def test_apply_move_left_right_up_down():
    base = make_grid([[0, 2, 2, 0],
                      [0, 0, 4, 4],
                      [2, 0, 0, 2],
                      [0, 0, 0, 0]])
    # vasemmalle
    s = board.GameState(make_grid(base))
    changed = s.apply_move("left")
    assert changed is True
    assert s.grid == [[4, 0, 0, 0],
                      [8, 0, 0, 0],
                      [4, 0, 0, 0],
                      [0, 0, 0, 0]]
    # oikealle
    s = board.GameState(make_grid(base))
    s.apply_move("right")
    assert s.grid == [[0, 0, 0, 4],
                      [0, 0, 0, 8],
                      [0, 0, 0, 4],
                      [0, 0, 0, 0]]
    # ylös
    s = board.GameState(make_grid(base))
    s.apply_move("up")
    assert s.grid == [[2, 2, 2, 4],
                      [0, 0, 4, 2],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0]]
    # alas
    s = board.GameState(make_grid(base))
    s.apply_move("down")
    assert s.grid == [[0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 2, 4],
                      [2, 2, 4, 2]]


# ---------- move / move_no_spawn ----------

def test_move_calls_spawn_only_when_changed():
    s = board.GameState(make_grid([[2, 0, 0, 0],
                                   [0, 0, 0, 0],
                                   [0, 0, 0, 0],
                                   [0, 0, 0, 0]]))
    with patch.object(s, "spawn_tile") as spawn:
        # vasemmalle ei muuta mitään, joten spawnia ei kutsuta
        assert s.move("left") is False
        spawn.assert_not_called()

        # oikealle muuttaa, joten spawn kutsutaan
        assert s.move("right") is True
        spawn.assert_called_once()

def test_move_updates_won_and_over_flags():
    # 1024 + 1024 yhdistyy -> saavutetaan 2048 ja won = True
    s = board.GameState(make_grid([[1024, 1024, 0, 0],
                                   [2, 2, 4, 4],
                                   [8, 16, 32, 64],
                                   [0, 0, 0, 0]]))
    with patch.object(s, "spawn_tile"):
        s.move("left", spawn=True, check_over=True)
    assert s.won is True
    assert isinstance(s.over, bool)  # over voi vielä olla False, koska siirtoja on jäljellä

def test_move_no_spawn_does_not_spawn_and_does_not_set_over():
    s = board.GameState(make_grid([[2, 2, 0, 0],
                                   [0, 0, 0, 0],
                                   [0, 0, 0, 0],
                                   [0, 0, 0, 0]]))
    s.over = False
    with patch.object(s, "spawn_tile") as spawn:
        changed = s.move_no_spawn("left")
    assert changed is True
    spawn.assert_not_called()
    # over-lippua ei päivitetä tässä
    assert s.over is False


# ---------- is_game_over ----------

def test_is_game_over_false_when_empty_or_adjacent_equal():
    s = board.GameState(make_grid([[2, 0, 4, 8],
                                   [16, 32, 64, 128],
                                   [256, 512, 1024, 2],
                                   [4, 8, 16, 32]]))
    assert s.is_game_over() is False  # koska tyhjä solu on olemassa

    s.grid[0][1] = 2  # ei tyhjiä soluja, mutta vierekkäin olevat samat arvot sallivat siirron
    assert s.is_game_over() is False

def test_is_game_over_true_when_full_and_no_merges():
    # täysi lauta ilman vierekkäisiä samoja -> käydään koko ruudukko ja palataan True
    s = board.GameState(make_grid([[2, 4, 2, 4],
                                   [4, 2, 4, 2],
                                   [2, 4, 2, 4],
                                   [4, 2, 4, 2]]))
    assert s.is_game_over() is True


# ---------- spawn_tile (kontrolloitu satunnaisuus) ----------

@patch("src.board.random.choice")
@patch("src.board.random.random")
def test_spawn_tile_places_2_or_4(random_random, random_choice):
    s = board.GameState(make_grid([[0, 0, 0, 0],
                                   [0, 0, 0, 0],
                                   [0, 0, 0, 0],
                                   [0, 0, 0, 0]]))
    # ensimmäinen laatta on 2, toinen laatta on 4
    random_choice.side_effect = [(0, 0), (0, 1)]
    random_random.side_effect = [0.5, 0.05]  # 0.5 -> 2, 0.05 -> 4 (koska PROB_FOUR=0.1)

    s.spawn_tile()
    s.spawn_tile()
    assert s.grid[0][0] == 2
    assert s.grid[0][1] == 4

def test_spawn_tile_noop_when_no_empty_cells():
    s = board.GameState(make_grid([[2, 4, 2, 4],
                                   [4, 2, 4, 2],
                                   [2, 4, 2, 4],
                                   [4, 2, 4, 2]]))
    before = copy.deepcopy(s.grid)
    s.spawn_tile()
    assert s.grid == before


# ---------- new_game ----------

@patch("src.board.random.choice")
@patch("src.board.random.random")
def test_new_game_spawns_exactly_two_tiles_with_values(random_random, random_choice):
    # pakotetaan ensimmäiset laatat paikkoihin (0,0) ja (0,1), arvot 2 ja 4
    random_choice.side_effect = [(0, 0), (0, 1)]
    random_random.side_effect = [0.7, 0.02]  # ensin 2, sitten 4
    s = board.new_game()

    tiles = [(r, c, v) for r in range(board.SIZE) for c in range(board.SIZE) if (v := s.grid[r][c]) != 0]
    assert len(tiles) == 2
    assert s.grid[0][0] == 2
    assert s.grid[0][1] == 4
    assert s.score == 0 and s.won is False and s.over is False
