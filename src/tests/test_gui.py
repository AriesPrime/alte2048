"""GUI-moduulin pytest-testit."""

import pytest
import src.gui as gui


# ---------- apuluokka ----------

class FakeState:
    def __init__(self, grid, score=0, won=False, over=False):
        self.grid = [row[:] for row in grid]
        self.score = score
        self.won = won
        self.over = over
        self.moved = None
        self.move_calls = 0

    def move(self, d):
        self.moved = d
        self.move_calls += 1
        return True


# ---------- render ----------

def test_render_prints_correct_structure(capsys):
    s = FakeState(
        [
            [2, 0, 4, 0],
            [0, 8, 16, 0],
            [0, 0, 0, 0],
            [128, 256, 1024, 2048],
        ],
        score=123,
        won=False,
        over=False,
    )

    gui.render(s)
    out = capsys.readouterr().out

    # ylätiedot
    assert "Pisteet: 123 | Voitto: False | Loppu: False" in out
    # taulun vaakaviivan pitää esiintyä 1 (alussa) + 4 (jokaisen rivin jälkeen) = 5 kertaa
    assert out.count("+----+----+----+----+") == 5
    # tarkista pari riviä tarkasti
    assert "|   2|    |   4|    |" in out
    assert "| 128| 256|1024|2048|" in out


# ---------- read_command ----------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("q", "q"),
        ("Quit", "q"),
        (" exit ", "q"),
        ("ai", "ai"),
        ("W", "up"),
        ("a", "left"),
        ("S", "down"),
        ("d", "right"),
        ("x", None),
        ("", None),
    ],
)
def test_read_command_returns_expected(monkeypatch, raw, expected):
    monkeypatch.setattr("builtins.input", lambda _: raw)
    assert gui.read_command() == expected


# ---------- ai_step ----------

def test_ai_step_calls_best_move_and_move(monkeypatch):
    s = FakeState([[0] * 4 for _ in range(4)])
    # patchataan moduulin sisällä importattu best_move_expecti
    monkeypatch.setattr(gui, "best_move_expecti", lambda state, depth: ("up", 42.0))

    ok, d = gui.ai_step(s, depth=3)

    assert ok is True and d == "up"
    assert s.moved == "up" and s.move_calls == 1


# ---------- print_ai_move ja print_final ----------

def test_print_ai_move_prints(capsys):
    gui.print_ai_move(7, "left")
    out = capsys.readouterr().out
    assert "\nAI:n siirto 7: left" in out

def test_print_final_prints(capsys):
    s = FakeState(
        [[2, 4, 0, 0], [0, 0, 0, 0], [0, 0, 8, 0], [0, 0, 0, 16]],
        score=999,
    )
    gui.print_final(s)
    out = capsys.readouterr().out
    assert "LOPPU - Pisteet: 999 Suurin laatta: 16" in out
