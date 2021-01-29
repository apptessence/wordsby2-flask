import unittest
from game import Game
from board import Board
from player import Player
from pickbox import Pickbox
from tiles import Tiles
from tile import Tile

import logging
import random

class TestPickbox(unittest.TestCase) :

    def setUp(self) :
        logging.info("----------------------------")
        self.game = Game()
        self.p1 = self.game.current_player()
        self.p_ = self.game.inactive_player()
        self.px = self.game.pickbox

    def get_random_board_place(self) :
        board = self.game.board
        return random.choice(random.choice(board.places))

    def test_player_fill_pickbox(self) :
        logging.info("test_player_fill_pickbox")
        self.game.empty_pickbox()
        rslt = self.p1.fill_pickbox()
        # TESTS
        self.assertIsInstance(rslt, dict)
        self.assertEqual(rslt['rslt'], 1)

    def test_player_empty_pickbox(self) :
        logging.info("test_player_empty_pickbox")
        self.game.fill_pickbox()
        rslt = self.p1.empty_pickbox()
        # TESTS
        self.assertIsInstance(rslt, dict)
        self.assertEqual(rslt['rslt'], 1)

    def test_inactive_player_cannot_fill_pickbox(self) :
        logging.info("test_inactive_player_cannot_fill_pickbox")
        self.assertRaises(Exception, self.p_.fill_pickbox)

    def test_inactive_player_cannot_empty_pickbox(self) :
        logging.info("test_inactive_player_cannot_empty_pickbox")
        self.assertRaises(Exception, self.p_.empty_pickbox)

    def test_player_pick_tile(self) :
        logging.info("test_player_pick_tile")
        tile = random.choice(self.px.tiles).tile
        rslt = self.p1.pick_tile(tile)
        # TESTS
        self.assertIsInstance(rslt, dict)
        self.assertEqual(rslt['rslt'], 1)
    
    def test_player_discard_tile(self) :
        logging.info("test_player_discard_tile")
        if len(self.p1.rack) == 0 :
            tile = random.choice(self.px.tiles).tile
            self.p1.pick_tile(tile)
        r = len(self.p1.rack)
        tile = self.p1.rack[0]
        in_bag = self.game.tiles.in_bag()
        rslt = self.p1.discard_tile(tile)
        # TESTS
        self.assertEqual(len(self.p1.rack), r-1)
        self.assertEqual(self.game.tiles.in_bag(), in_bag + 1)

    def test_player_place_tile(self) :
        logging.info("test_player_place_tile")
        place = self.get_random_board_place()
        self.p1.pick_tile(self.px.tiles_in_box()[0])
        r = len(self.p1.rack)
        tile = random.choice(self.p1.rack)
        rslt = self.p1.place_tile(tile, place)
        # TESTS
        self.assertEqual(tile.phase, 3)
        self.assertTrue(place.tile == tile)
        self.assertEqual(len(self.p1.rack), r-1)

    def test_player_validate_tile(self) :
        logging.info("test_player_validate_tile")
        self.assertTrue(self.game.current_player().validate_tile("n","pytho"))
        self.assertFalse(self.game.current_player().validate_tile("x","pytho"))

    def test_reject_validate_string_length(self) :
        logging.info("test_reject_validate_string_length")
        self.assertRaises(BaseException, self.game.current_player().validate_tile, "tt")
        self.assertRaises(BaseException, self.game.current_player().validate_tile, "")
        self.assertRaises(BaseException, self.game.current_player().validate_tile, "9")

    def test_first_word_as_tiles(self) :
        logging.info("test_first_word_as_tiles")
        for c in "PYTHO" :
            self.game.words['first']['letters'].append(Tile([c,c]))
        word = ""
        for c in self.game.words['first']['letters'] :
                word = word + c.get_face()
        self.assertTrue(word == "PYTHO")        
        self.assertTrue(self.game.current_player().validate_tile("n"))
        self.assertFalse(self.game.current_player().validate_tile("x"))
        




    