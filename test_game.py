import unittest
from game import Game
from board import Board
from player import Player
from pickbox import Pickbox
from tiles import Tiles
from tile import Tile

import random
import logging

class TestGame(unittest.TestCase) :

    def setUp(self) :
        logging.info("----------------------------")
        self.game = Game()
        self.p1 = self.game.current_player()
        # print(self.p1)
        self.p_ = self.game.inactive_player()
        self.px = self.game.pickbox
        self.game.words = {'first': {'complete' : False, 'letters' : []}, "player_0" : [], "player_1" : []}

    def tearDown(self) :
        for t in self.game.tiles.tiles :
            t.phase = 0
            t.owner = None
        self.p1.rack.clear()
 
    def test_setup (self) :
        
        logging.info("test_setup")
        game = self.game
        self.assertEqual(len(game.tiles.tiles), 225)
        self.assertIsInstance(game.board, Board)
        self.assertIsInstance(game.current_player(), Player)
        self.assertEqual(len(game.players), 2)
        self.assertIsInstance(game.pickbox, Pickbox)
        self.assertIsInstance(game.tiles, Tiles)
        self.assertIsInstance(game.tiles.tiles[0], Tile)
        # self.assertEqual(self.game.current_turn['player'], self.game.current_player())
        self.assertEqual(self.game.current_turn['action'], None)
        self.assertEqual(self.game.current_turn['remaining'], 0)

    def test_fill_pickbox(self) :  
        logging.info("test_fill_pickbox")  
        self.assertEqual(len(self.px.tiles), 9)
       
    def test_empty_pickbox(self) :
        logging.info("test_empty_pickbox")
        self.game.empty_pickbox()
        self.assertEqual(len(self.px.tiles_in_box()), 0)
    
    def test_cant_overfill_pickbox(self) :
        logging.info("test_cant_overfill_pickbox")
        bt = self.game.tiles.in_bag()
        self.game.fill_pickbox() # acts as extra fill, since game has just been initialized
        self.assertEqual(self.game.tiles.in_bag(), bt)
        self.assertEqual(len(self.px.tiles), 9)

    def test_pick_tile(self) :
        logging.info("test_pick_tile")
        l = len(self.p1.rack)
        tile = random.choice(self.px.tiles).tile
        self.p1.pick_tile(tile)
        self.assertEqual(len(self.p1.rack), l+1)
        self.assertEqual(len(self.px.tiles_in_box()), 8)

    def test_can_fill_partial_pickbox(self) :
        logging.info("test_can_fill_partial_pickbox")
        tile = random.choice(self.game.pickbox.tiles)
        self.game.pick_tile(tile.tile)

        self.assertEqual(len(self.px.tiles_in_box()), 8)
        self.game.fill_pickbox()
        self.assertEqual(len(self.px.tiles_in_box()), 9)

    def test_tiles_move_to_pickbox(self) :
        logging.info("test_tiles_move_to_pickbox")
        self.game.empty_pickbox()
        self.assertEqual(self.game.tiles.in_bag(), 225)
        self.assertEqual(len(self.game.pickbox.tiles_in_box()),0)

    def test_discard_player_tile(self) :
        logging.info("test_discard_player_tile")
        place = random.choice(self.game.pickbox.tiles)
        self.game.pick_tile(place.tile)
        r = len(self.p1.rack)
        t = self.p1.rack[0]
        self.assertIsInstance(t, Tile)
        t = self.game.remove_player_tile(self.p1, t)
        self.assertEqual(r-1, len(self.p1.rack))

    def test_first_word_column(self) :
        logging.info("test_first_word_column")
        self.assertFalse(self.game.words['first']['complete'])
        tile = self.game.pickbox.tiles[0].tile
        self.assertIsInstance(tile, Tile)

    def test_first_word_validation(self) :
        logging.info("test_first_word_validation")
        fw_col = int(self.game.board.board_cols/2)
        self.assertFalse( self.game.board.validate_location([0,0],self.p1))
        self.assertTrue( self.game.board.validate_location([0, fw_col ], self.p1))
        self.assertFalse(self.game.board.validate_location([40,fw_col], self.p1))
        self.assertTrue(self.game.board.validate_location([random.randrange(self.game.board.board_rows),fw_col], self.p1))
        t1 = self.px.tiles[0].tile
        l1 = self.game.board.get_place_by_coords([3,fw_col])
        self.p1.pick_tile(t1)
        self.p1.place_tile(t1,l1)
        fw = self.game.board.first_word()
        self.assertTrue(len(fw) == 1)
        self.assertFalse(self.game.board.validate_location([5,fw_col], self.p1))
        self.assertTrue(self.game.board.validate_location([4,fw_col], self.p1))
        
        self.assertFalse(self.game.board.validate_location([1,fw_col], self.p1))
        self.assertTrue(self.game.board.validate_location([2,fw_col], self.p1))

    def test_autocomplete_first_word(self) :
        logging.info("test_autocomplete_first_word")
        # For now, this test assumes that 6 letters in the wall word == complete, as does Game.place_tile
        fw_col = int(self.game.board.board_cols/2)
        for idx in range(6) :
            
            p1 = self.game.current_player(idx == 3)
            t = self.px.tiles[idx].tile
            p = self.game.board.places[idx][fw_col]
            p1.pick_tile(t)
        print(f"rack 0 {self.game.players['players'][0].rack}")
        print(f"rack 1 {self.game.players['players'][1].rack}")
        for idx in range(6) :
            # x = int(idx/2)
            t = self.game.current_player().rack[0]
            p = self.game.board.get_place_by_coords([idx,fw_col])
            self.game.current_player().place_tile(t,p)
            self.assertEqual(self.game.words['first']['complete'], idx==5)

    def test_player_switch(self) :
        logging.info("test_player_switch")
        player = self.game.current_player()
        self.game.current_player(True)
        self.assertTrue(player != self.game.current_player())

    def get_tile_from_px(self, px_idx=0, player=None) :
        logging.info("get_tile_from_px")
        if player == None :
            player = self.game.current_player()
        t = self.px.tiles[px_idx].tile
        player.pick_tile(t)
        return t

    def test_set_turn(self) :
        logging.info("test_set_turn")
        # set the current_turn to place
        self.game.set_turn({}, True)
        self.assertTrue(self.game.current_turn['action'] == None)
        self.assertTrue(self.game.current_turn['remaining'] == 0)
        self.assertTrue(self.game.current_turn['player'] == self.game.current_player())

        # self.game.set_turn({'action' : 'place'}, True)
        # self.assertEqual(self.game.current_turn['remaining'], 1)
        self.game.set_turn({'action' : 'place'},True)
        self.assertEqual(self.game.current_turn['remaining'], 0)

        self.game.set_turn({'action' : 'fill'}, True)
        self.assertEqual(self.game.current_turn['remaining'],2)
        self.game.set_turn({'action' : 'decrement'})
        self.assertEqual(self.game.current_turn['remaining'], 1)
        self.game.set_turn({'action' : 'discard'})
        self.assertEqual(self.game.current_turn['remaining'], 0)

        self.game.set_turn({'action' : 'place'}, True)
        self.assertFalse(self.game.legal_turn('discard'))
        self.game.set_turn({'action' : 'discard'}, True)
        self.assertFalse(self.game.legal_turn('place'))
        self.assertTrue(self.game.legal_turn('fill'))


    