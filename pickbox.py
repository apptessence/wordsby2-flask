    
# In the client/server context, a Pickbox instance exists on both sides. the
# client uses it to represent the pickbox graphically, and the server maintains 
# it as a reference object for both players.

from player import Player
from place import Place
from tile import Tile

import logging
import random

class Pickbox :

    tiles = []
    spaces = 4 * 4
    pick_rows = 3
    pick_cols = 3
    flip_spaces = spaces - (pick_cols * pick_rows)
    phase = 1 # use this to set the phase of the tile

    def __init__(self, game) :   
        self.game = game
        # create the locations where the pickbox tiles will go when filling
        self.init_picks()
        # self.init_flips()

    def generate_matrix(self, n) :
        for i in range(0, len(self.tiles), n):
            yield self.tiles[i:i + n]

    def show(self, n = pick_rows) :
        # separate presentation, and maintain a single object, so 
        #convert simple list into 2D array when needed
        ret = []
        idx = 0
        for x in self.generate_matrix(self.pick_rows) :
            row_ = []
            for p in x :
                if p.tile == None :
                    row_.append(f"{idx}: -")
                elif type(p.tile) == Tile :
                    row_.append(f"{idx}: {p.tile.get_face()}")
                idx += 1
            ret.append(f"[{']['.join(row_)}]")
        print ("\n".join(ret)) 

        return
        print(pbox)
        idx = 0
        rslt = []
        for row in pbox :
            row_ = []
            for p in row :
                p.idx = idx
                
                idx +=1
            rslt.append()
        return "\n".join(rslt)

    def get_my_idx(self) :
        return (self.game.players.index(self))

    def init_picks(self) : # creates an empty pickbox, populated with Place instances, no tiles
        self.tiles = [None] * self.pick_rows * self.pick_cols
        bag_tiles = self.get_fill_candidates()
        idx = 0
        for i in range(self.pick_rows * self.pick_cols) :
            self.tiles[i] = Place(idx)
            idx += 1

    def tiles_in_box(self) :
        found = []
        for p in self.tiles :
            if type(p.tile) == Tile :
                found.append(p.tile)
        return found

    def get_fill_candidates(self) :
        bag_tiles = []
        for t in self.game.tiles.tiles :
            if t.phase == 0 : # in the bag
                bag_tiles.append(t)
        return bag_tiles

    def fill(self) :
        bag_tiles = self.get_fill_candidates()
        idx = 0
        for p in self.tiles :
            p.idx = idx
            if type(p.tile) != Tile :
                p.tile = random.choice(bag_tiles)
                bag_tiles.remove(p.tile)
                p.tile.set_phase(self.phase)
            idx +=1

    def empty(self) :
        for p in self.tiles :
            if type(p.tile) == Tile :
                p.tile.return_to_bag()
                p.tile = None
                

    def remove_tile(self, tile) :
        for p in self.tiles :
            if p.tile == tile :
                p.tile = None
        # self.tiles.remove(tile)

    def remove_from_picks(self, tile) :
        for p in self.tiles :
            if p.tile == tile :
                p.tile = None

    def get_tile_by_idx(self, pick) :
        try :
            idx = int(pick)
            p = self.tiles[idx]
            if type(p.tile) == Tile :
                return p.tile
        except :
            for idx, p in enumerate(self.tiles) :
                try :
                    if p.tile.get_face().lower() == pick.lower() :
                        return p.tile
                except :
                    logging.info(f"fell out of find tile by char")
        return False

    def pick_player_tile(self, player, tile=None) :
        if type(player) != Player :
            raise Exception("player provided is not of Player type")
            return -1
        t_count = 0
        for p in self.tiles :
            if type(p.tile) == Tile :
                t_count += 1
        if t_count == 0 :
            return (False)
        else :
            if type(tile) == Tile :
                t = Tile
            else :
                t = random.choice(self.tiles).tile
            t.set_player(player)
            self.remove_from_picks(t)
            rslt = t.set_phase(self.phase + 1)
            return (t)
