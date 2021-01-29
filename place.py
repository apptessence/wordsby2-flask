class Place :
    
    def __init__ (self, idx, loc=None) : # loc parameter is only on board
        import random
        self.idx = idx
        self.tile = None
        self.loc = loc
        self.last_turn = 0
        self.score = random.randrange(10)

    
