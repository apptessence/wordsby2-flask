from tile import Tile 
import logging

# In a client/server context, the tiles implementation only exists on the
# server, and the Game and Tiles instances push tiles out to, and receive
# tile information back from the clients. 

class Tiles :

    tiles = []
    list = {
        "E" : 56.88, 
        "M" : 15.36, 
        "A" : 43.31, 
        "H" : 15.31, 
        "R" : 38.64, 
        "G" : 12.59, 
        "I" : 38.45, 
        "B" : 10.56, 
        "O" : 36.51, 
        "F" : 9.24, 
        "T" : 35.43, 
        "Y" : 9.06, 
        "N" : 33.92, 
        "W" : 6.57, 
        "S" : 29.23, 
        "K" : 5.61, 
        "L" : 27.98, 
        "V" : 5.13, 
        "C" : 23.13,
        "X" : 1.48, 
        "U" : 18.51, 
        "Z" : 1.39, 
        "D" : 17.25, 
        "J" : 1.00, 
        "P" : 16.14, 
        "Q" : 1
    }

    def __init__(self, game) :
        self.game = game
        self.make_tile_set ()
        if len(self.tiles) == 0 : # preventer – in testing, tiles are somehow getting made more than once
            self.make_tiles()
        logging.info('initialized %s tiles' % (len(self.tiles)))

    def in_bag(self) :
        amount = 0
        for t in self.tiles :
            if t.phase == 0 :
                amount += 1
        return amount

    def by_id(self, id) :
        for t in self.tiles:
            if t.get_data()['id'] == id:
                return t
        return None
    
    def letter_list (self, len=200) :
        ret = {}
        total = sum(self.list.values())
        f = total/len
        import math
        for cursor in self.list.keys() :
            ret[cursor] = math.ceil(self.list[cursor] / f)
        return(ret)

    def make_letter_set(self, list_base, letters_1, letters_2) :
        for cursor in list_base.keys() : # go through the list, creating arrays with letters reflecting frequency
            idx = list_base[cursor]
            for _ in range(idx) :
                letters_1.append(cursor)
                letters_2.append(cursor)

    def pair_letters(self, ret,letters_1, letters_2) :
        for idx, l in enumerate(letters_1) : # now pair letters from the two lists, forming each side of a given tile.
            ret.append([l,letters_2[idx]])

    def add_blanks(self, ret, list_base) :
        for _ in range(10) :
            tile = [" ", " "]
            import random
            if random.randrange(3) > 0 :
                side = random.randrange(2)
                tile[side] = random.choice(list(list_base))
            ret.append(tile)

    def make_tile_set (self) :
        list_base = self.letter_list() # get the standard list of game letters with frequency
        letters_1 = []
        letters_2 = []
        self.make_letter_set(list_base, letters_1, letters_2)
        import random
        # now, take the two identical lists, and shuffle them, each separately
        random.shuffle(letters_1)
        random.shuffle(letters_2)
        rslt = []
        self.pair_letters(rslt,letters_1, letters_2)
        # self.add_blanks(rslt,list_base)
        random.shuffle(rslt)
        self.tile_data = rslt
        return True

    def make_tiles(self) :
        self.in_bag()
        for tile in self.tile_data :
            self.tiles.append(Tile(tile))

