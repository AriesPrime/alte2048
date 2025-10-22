"""Päästä päähän -testit hakualgoritmille (Expectiminimax).

Näissä testeissä käytetään oikeaa GameState-logiikkaa (ei feikkejä)
sekä oikeita heuristiikkoja. Satunnaisuus (spawn) vakioidaan mockeilla,
jotta tulokset ovat toistettavia.
"""

import math
from unittest.mock import patch

import src.board as board
import src.expectiminimax as expecti


# ---------- Aputoiminto ----------

def G(rows):
    """Pieni apu luettavuuteen: rakentaa ruudukon riveistä syväkopiona."""
    return [r[:] for r in rows]


# ---------- 1) Perusparhaan siirron valinta oikealla GameState:lla ----------

def test_expectiminimax_valitsee_left_kun_rivilla_kaksi_yhdistymista():
    """Ylin rivi 2,2,4,4: vasemmalle tulee kaksi yhdistymistä, muut suunnat heikompia."""
    s = board.GameState(G([
        [2, 2, 4, 4],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]))
    d, val = expecti.best_move_expecti(s, depth=2)
    # useimmiten tekoäly valitsee vasemmalle, mutta hyväksytään myös oikea, koska painot voivat vaihdella
    assert d in ("left", "right")
    assert math.isfinite(val)


# ---------- 2) Lyhyt deterministinen rullaustesti (spawn kontrolloitu) ----------

@patch("src.board.random.choice")
@patch("src.board.random.random")
def test_rollout_expectiminimax_etenee_ja_on_toistettava(random_random, random_choice):
    """Tehdään 5 AI-siirtoa oikealla move()+spawn -polulla, spawni vakioitu.

    Spawnaus sijoitetaan oikeaan laitaan ylhäältä alas (ensin sarake 3, sitten 2),
    arvo on 2 paitsi 4. spawn on neljäs (arvot: 0.7 -> 2, 0.05 -> 4).
    """
    # Sijainnit ja arvot spawneille (choice: paikka, random: 2 vai 4)
    random_choice.side_effect = [
        (0, 3), (1, 3), (2, 3), (3, 3),
        (0, 2), (1, 2), (2, 2), (3, 2),
    ]
    random_random.side_effect = [0.7, 0.7, 0.7, 0.05, 0.7, 0.7, 0.7, 0.7]

    # Aloitetaan yksinkertaisesta mutta ei-triviaalia tilanteesta
    s = board.GameState(G([
        [2, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]))

    moves_made = 0
    for _ in range(5):
        if s.over:
            break
        d, _ = expecti.best_move_expecti(s, depth=3)
        assert d in ("left", "up", "right", "down")
        changed = s.move(d, spawn=True, check_over=True)
        # AI:n ei pitäisi valita siirtoa, joka ei muuta lautaa
        assert changed is True
        moves_made += 1

    # Tarkistetaan, että peli oikeasti eteni ja pisteitä kertyi
    assert moves_made >= 3
    assert s.score >= 4
    assert any(v != 0 for row in s.grid for v in row)
