"""Autoplay-moduulin pytest-testit (Expectiminimax-only)."""

from unittest.mock import patch, call
import src.autoplay as autoplay


class FakeState:
    """Yksinkertainen feikkitila pelille.

    moves_to_over määrittää montako siirtoa kestää ennen kuin peli päättyy.
    """

    def __init__(self, moves_to_over=1):
        self.over = False
        self.moves_left = moves_to_over

    def move(self, _):
        """Vähentää laskuria ja asettaa pelin päättyneeksi kun laskuri loppuu."""
        self.moves_left -= 1
        if self.moves_left <= 0:
            self.over = True


# ---------- Expectiminimax ----------

@patch.object(autoplay, "print_final")
@patch.object(autoplay, "print_ai_move")
@patch.object(autoplay, "render")
@patch.object(autoplay, "best_move_expecti")
@patch.object(autoplay, "new_game")
def test_run_one_iteration_expecti(new_game, best_move_expecti, render, print_ai, print_final):
    s = FakeState(1)
    new_game.return_value = s
    best_move_expecti.return_value = ("left", 0.0)

    autoplay.run(depth=7)  # engine-parametria ei enää ole

    assert render.call_count == 2
    best_move_expecti.assert_called_once_with(s, depth=7)
    print_ai.assert_called_once_with(1, "left")
    print_final.assert_called_once()


@patch.object(autoplay, "print_final")
@patch.object(autoplay, "print_ai_move")
@patch.object(autoplay, "render")
@patch.object(autoplay, "best_move_expecti")
@patch.object(autoplay, "new_game")
def test_run_three_iterations_expecti(new_game, best_move_expecti, render, print_ai, print_final):
    s = FakeState(3)
    new_game.return_value = s
    best_move_expecti.return_value = ("up", 123.0)

    autoplay.run(depth=4)

    assert render.call_count == 4
    assert print_ai.call_count == 3
    assert print_ai.mock_calls == [call(1, "up"), call(2, "up"), call(3, "up")]
    print_final.assert_called_once()


@patch.object(autoplay, "print_final")
@patch.object(autoplay, "print_ai_move")
@patch.object(autoplay, "render")
@patch.object(autoplay, "best_move_expecti")
@patch.object(autoplay, "new_game")
def test_run_zero_iterations_expecti(new_game, best_move_expecti, render, print_ai, print_final):
    class DoneState:
        over = True
        def move(self, _):  # pragma: no cover
            raise AssertionError("move() ei saa koskaan kutsua kun peli on jo ohi")
    new_game.return_value = DoneState()

    autoplay.run(depth=4)

    render.assert_called_once()
    best_move_expecti.assert_not_called()
    print_ai.assert_not_called()
    print_final.assert_called_once()


@patch.object(autoplay, "print_final")
@patch.object(autoplay, "print_ai_move")
@patch.object(autoplay, "render")
@patch.object(autoplay, "best_move_expecti")
@patch.object(autoplay, "new_game")
def test_call_order_expecti(new_game, best_move_expecti, render, print_ai, print_final):
    s = FakeState(2)
    new_game.return_value = s
    best_move_expecti.return_value = ("left", 0.0)

    order = []
    def log(name):
        def _(*args, **kwargs):
            order.append(name)
        return _
    render.side_effect = log("render")
    best_move_expecti.side_effect = [("left", 0.0), ("left", 0.0)]
    print_ai.side_effect = log("print_ai_move")
    print_final.side_effect = log("print_final")

    autoplay.run(depth=3)

    assert order == ["render", "print_ai_move", "render", "print_ai_move", "render", "print_final"]


# ---------- CLI smoke tests (engine poistettu) ----------

@patch.object(autoplay, "run")
def test_cli_main_invokes_run_with_args(run_mock):
    autoplay.main(["--depth", "5"])
    run_mock.assert_called_once_with(depth=5)

@patch.object(autoplay, "run")
def test_cli_main_defaults_to_expecti(run_mock):
    autoplay.main([])
    run_mock.assert_called_once_with(depth=4)
