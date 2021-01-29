import unittest
from game import Game
from board import Board
from player import Player
from pickbox import Pickbox
from tiles import Tiles
from tile import Tile

import logging

class TestPickbox(unittest.TestCase) :

    def setUp(self) :
        self.game = Game()
        self.p1 = self.game.current_player()
        self.px = self.game.pickbox
        self.px.empty()   

    def test_empty(self) :
        self.px.empty()
        self.assertEqual(len(self.px.tiles_in_box()), 0)

    def test_fill(self) :
        self.px.fill()
        self.assertEqual(len(self.px.tiles), 9)

    def test_no_pick_when_empty(self) :
        self.px.empty()
        rslt = self.px.pick_player_tile(self.p1)
        self.assertFalse(rslt)

    def test_pick_player_tile(self) :
        r = len(self.p1.rack)
        self.px.fill()
        self.assertEqual(len(self.px.tiles), 9)
        self.assertEqual(len(self.p1.rack), r)
        t = self.px.pick_player_tile(self.p1)
        self.assertIsInstance(t, Tile)


        