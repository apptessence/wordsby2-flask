
# In a client/server context, clients would have a Board class instance that 
# drives their client's representation of the board. On the server, the Board
# instance is a purely logical representation that can be used for logging.
# In both cases, asyncio needs to keep both player boards synced up.

from place import Place
from tile import Tile
import logging

class Board :
    
    # import colored
    # from colored import stylize
    tiles = []
    places = []
    # board_rows = 1
    board_cols = 11

    # std_bg = colored.bg(244)
    # alt_bg = colored.bg(104)
    # alt_bg = colored.bg(1)
    # p1_fg = colored.fg(0)
    # p0_fg = colored.fg(15)
    
    def __init__ (self, game) :
        self.places = [] * self.board_cols
        for idx in range(self.board_cols):
            self.places.append(Place(idx, idx))
        self.game = game

    def tile_style(self, tile) :
        # import colored
        # from colored import stylize

        tile_bg = [self.alt_bg,self.std_bg][self.game.players['players'].index(tile.player) == tile.player_face]
        tile_fg = [self.p0_fg, self.p1_fg][self.game.players['players'].index(tile.player)]
        rslt = stylize(tile.get_face(), tile_fg+tile_bg)
        return rslt
            
    def show(self) :
        row = []
        for x in self.places :
            if x.tile == None :
                row.append( " ")
            else:
                row.append(self.tile_style(x.tile))
        print( f"|{'|'.join(row)}|")

    def get_place_by_coords(self, data) :
        # print(f"get_place_by_coords sent {data}")
        if type(data) == int :
            return self.places[data]
        if isinstance(data, Place) :
            return data

    def word(self,mode="place") :
        rslt = []
        for idx, place in enumerate(self.places) :
            if isinstance(place.tile, Tile) :
                if mode is True or mode == "place":
                    rslt.append(place)
                elif mode == "idx":
                    rslt.append(idx)
                elif mode == "str" and type(place.tile) == Tile :
                    rslt.append(place.tile.get_face())
        return rslt

    def wall(self) :
        return int((self.board_cols)/2)

    def get_word(self) :
        word = []
        for int, p in enumerate( self.places) :
            if type( p.tile) == Tile :
                word.append(p)
        return word

    def get_turns(self) :
        turns = []
        for p in self.places :
            turns.append(p.last_turn)
        logging.info(f"turn are {turns}")
        return turns

    def scores(self, display=False) :
        scores = [0,0]
        scoreboard_txt = f"PLAYER 0: {scores[0]}     PLAYER 1:  {scores[1]}"
        scored = [i for i in self.get_turns() if i != 0]
        if len(scored) == 0 :
            if display :
                print (scoreboard_txt)
            return scores
        # need a reverse lookup by turn
        turns = {}
        for idx, p in enumerate(self.places) :
            if p.last_turn != 0 :
                turns[p.last_turn] = idx       
        params = [[turns[scored[0]],turns[scored[-1]],1],[turns[scored[-1]],turns[scored[0]],-1]][scored[0] > scored[-1]]
        for i, idx in enumerate(range(params[0],params[1]+params[2], params[2])) :
            score = 2**(i + 1)
            place = self.places[idx]
            player = place.tile.player
            split = self.game.players['players'].index(player) != place.tile.player_face
            if split :
                scores[0] += int(score/2)
                scores[1] += int(score/2)
            else :
                scores[self.game.players['players'].index(player)] += int(score)
        if display:
            print(f"PLAYER 0: {scores[0]}     PLAYER 1:  {scores[1]}")
        return scores
        

    def place_tile(self, tile, loc, player) : # loc is a Place instance, or coordinates
        free = self.space_free(loc)
        rslt = self.validate_location(loc, player)
        place = self.get_place_by_coords(loc)
        if isinstance(place.tile, Tile) :
            place.tile.return_to_bag()
        place.tile = tile
        place.last_turn = self.game.turn
        self.tiles.append(tile)
        tile.set_player(player)
        tile.set_phase(3)
        return ({'event': 'place_tile', 'rslt': 1})

    def validate_location(self,loc,player,replace=False) :
        print( f"loc is {loc}")
        if isinstance(loc, Place) and loc.loc != None :
            loc = loc.loc

        row_range = range(0,self.board_cols)
        if not loc in row_range :
            return False
        # ok, the loc is a legal board position
        word = self.get_word()
        if len(word) == 0 :
            return True # this is the first letter in the first word
        
        place = self.get_place_by_coords(loc)
        if isinstance(place.tile, Tile) :
            if not replace :
                return False # any occupied space is invalid – unless replacing tile
        # prevented collisions with existing tiles
        # now check for word range.
        word_range = range(word[0].idx - 1, word[-1].idx + 1)
        if loc in word_range :
            if len(word) == 1 : #checking min max of range when bounds are the same throws erro
                return True
            if not loc == min(word_range) or loc == max(word_range) :
                return False
        return True

    def place_by_id(self, id_p) :
        print( id_p)
        for p in self.places :
            if id(p) == id_p :
                return p

    def space_free(self, coords) :
        found = self.get_place_by_coords(coords)
        return found.tile == None

