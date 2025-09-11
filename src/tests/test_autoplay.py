"""Autoplay-moduulin testit.

Testataan että run-funktio:
- suorittaa tekoälypelin silmukan oikein
- kutsuu render, best_move, print_ai_move ja print_final oikeassa järjestyksessä
- toimii sekä yhden että useamman siirron tilanteissa
"""

import unittest
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


class TestAutoplay(unittest.TestCase):
    @patch.object(autoplay, "print_final")
    @patch.object(autoplay, "print_ai_move")
    @patch.object(autoplay, "render")
    @patch.object(autoplay, "best_move")
    @patch.object(autoplay, "new_game")
    def test_run_one_iteration(self, new_game, best_move, render, print_ai, print_final):
        """Testaa että peli päättyy yhden siirron jälkeen."""
        s = FakeState(1)
        new_game.return_value = s
        best_move.return_value = ("left", 0.0)

        autoplay.run(depth=7)

        # render: kerran alussa ja kerran siirron jälkeen
        self.assertEqual(render.call_count, 2)
        # best_move saa parametrina oikean tilan ja syvyyden
        best_move.assert_called_once_with(s, depth=7)
        # AI-siirto tulostetaan
        print_ai.assert_called_once_with(1, "left")
        # Lopputulos tulostetaan
        print_final.assert_called_once()

    @patch.object(autoplay, "print_final")
    @patch.object(autoplay, "print_ai_move")
    @patch.object(autoplay, "render")
    @patch.object(autoplay, "best_move")
    @patch.object(autoplay, "new_game")
    def test_run_three_iterations(self, new_game, best_move, render, print_ai, print_final):
        """Testaa että peli toimii kolmen siirron ajan ja päättyy oikein."""
        s = FakeState(3)
        new_game.return_value = s
        best_move.return_value = ("up", 123.0)

        autoplay.run(depth=4)

        # render: kerran alussa ja kolme kertaa siirtojen jälkeen
        self.assertEqual(render.call_count, 4)
        # tekoäly tekee kolme siirtoa
        self.assertEqual(print_ai.call_count, 3)
        self.assertEqual(print_ai.mock_calls,
                         [call(1, "up"), call(2, "up"), call(3, "up")])
        # Lopputulos tulostetaan
        print_final.assert_called_once()
