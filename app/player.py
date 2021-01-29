
# Need to implement a protocol where asyncronous issues are dealt with
# **    any random events that affect both players must happen in Game.
# **    any action by a Player that interacts with these, or with game state
#       can be tried in the Player instance, but only becomes official when
#       it is passed to the Game.
# **    The Game must recognize these events (through a change_game_state method)
#       and then notify the Players
# **    The Game must manage Player turns, and notify both players when this changes
# More to come....

import logging


class Player :

    rack = []   # internal to player
    _board = [] # shared with game
    vector = {}
    events = ['fill_pickbox', 'empty_pickbox', 'change_player', 'pick_tile', 'place_tile', 'remove_tile', 'flip_tile']
    active = None
    tile_options = {}
    word_idx_status = None
    score = 0

    def __init__(self, game_mode, game, pickbox, board) :
        self.game_mode = game_mode
        self.game = game
        self.pickbox = pickbox
        self.board = board
        self.rack = []
        logging.info("initialized player")

    def confirm_word_ui(self) :
        # places = self.board.get_word_from_vector(self.vector)
        places = self.board.get_word()
        word = ""
        for p in places :
            word = word + p.tile.get_face()
        if self.game.defined_word(word.lower()) :
            if not self.game.words['first']['complete'] and len(places) >= self.game.first_word_len :
                print(f"Do you want to mark {word} complete? y|n")
                sel = input().lower()
                if sel == "y" :
                    self.game.words['first']['complete'] = True
                    if self.game.defined_word(word.lower(), True) == 1 : # it's a word, but no other words are possible
                        print("No other words possible you win!")
                        self.game.looping = False


    def update_game(self, event) :
        logging.info(f"getting update {event}")
        import os
        if 'event'  in event :
            if event['event'] == 'vector' :
                self.vector = event['vector']
                if id(self) == event['current_player'] :
                    os.system('clear')
                    self.board.show()
                    self.confirm_word_ui()

    def take_turn_ui(self) :
        import os
        os.system('clear')

        
       
        print("BOARD:")
        self.board.show()

        print("SCORES")
        self.board.scores(True)
        if type(self.game.word_complete) == Player and self.game.word_complete != self :
            warning = " Opponent can win on next turn."
        else :
            warning = ""
        print(f"Player {self.game.players['players'].index(self)}{warning}")

        if self.game.word_complete == self : # that means that the player completed word on last turn
            print(f"Win With Word {''.join(self.board.word('str'))} y|n?")
            win = input()
            if win.lower() == "y" :
                return {'win' : True}

        print()
        print("\nRACK:")
        self.show_rack(True)
        print()
        print("\rPICKBOX:")
        self.pickbox.show()
        turn_complete = False
        print()
        print("CHOICES:")
        p = self.game.current_player()
        sel = self.show_turn_choices(self.game.current_player(),self.game_choices(p))
        logging.info(f"show_turn_choices returned {sel}")
        return sel

    def take_turn(self) :
        if len(self.board.word()) > 1 and len(self.rack) > 0 :# check the options between rack and current word
            self.tile_options = self.game.tile_options()
        else :
            self.tile_options = None

        sel = self.take_turn_ui() # move all presentation out of logic
        if type(sel) == dict :
            return sel

        turn = self.game.choices.index(self.game.choices[sel])
        action = self.game.choices[sel]
              
        self.game.set_turn({'action' : action}, self.game.current_turn['player'] != self) 

        if turn == 0 : # fill
            self.fill_pickbox()
        elif turn == 1 : # pick
            self.pick_tile()
        elif turn == 2 : # place
            self.place_tile()          
        elif turn == 3 : # flip
            self.flip_tile()       
        elif turn == 4 : # discard
            self.discard_tile()
        elif turn == 5 : # empty pickbox
            self.empty_pickbox()
        else :
            raise Exception("choice out of range.")
            return
        return 

    def game_choices(self,p) :
        # needs to use legal_turn or set_turn to determine choices
        # ["fill","pick","place", "flip","discard","empty"]
        active = []
        if len(p.rack) > 0 :
            if self.game.current_turn['action'] in ["fill","pick", "flip","discard","empty"] :
                active.append(4)
            if self.game.current_turn['player'] != self :
                active.append(2)
        # if len(p.rack) > 0 or len(self.pickbox.tiles_in_box()) > 0 :
        if len(p.rack) > 0 :
            active.append(3)
        if len(self.pickbox.tiles_in_box()) > 0 :
            active.append(1)
        if len(self.pickbox.tiles_in_box()) < 9 :
            active.append(0)
        if len(self.pickbox.tiles_in_box()) > 0 :
            active.append(5)
        return active

    def get_key_equivalent(self, sel, opts) :
        # keys = self.game.choice_keys()
        keys = self.game.choice_keys(opts)
        if not sel.lower() in keys :
            return False
        logging.info(f"keys are {keys}")
        return keys[sel.lower()]

    def show_turn_choices(self, p, choices) :
        logging.info(choices)
        idx = 0
        menu_choices = {} # correspondence table for menu choices
        for c in choices :
            menu_choices[idx] = c
            print(f"{idx}: {self.game.choices[c]}")
            idx += 1
        # logging.info(f"menu_choices are {menu_choices}")
        print("Make your selection")
        sel = input()
        invalid = True
        while invalid :
            try :
                num = int(sel)
                num = menu_choices[num]
            except :
                num = self.get_key_equivalent(sel, choices)
                logging.info(f"num is {num}; choices are {choices}")
            if num in choices :
                break
            if num is False :
                print ("\033[A                                                        \033[A")
                print ("\033[A                                                        \033[A")
                print("re-enter selection: integers or first letters only.")
                sel = input()
                continue
            else :
                print ("\033[A                                                        \033[A")
                print ("\033[A                                                        \033[A")
                print("re-enter selection: out of range.")
                sel = int(input())
        return num

    def am_active(self) :
        return self.game.current_player() == self
        
    def fill_pickbox(self) :
        return self.game.change_game_state(self,'fill_pickbox')
        
    def empty_pickbox(self) :
        return self.game.change_game_state(self, 'empty_pickbox')

    def pick_tile_ui(self) :
        # moving interaction into player from game
        print("which tile do you want to pick?")
        pick = input()
        tile = self.pickbox.get_tile_by_idx(pick)
        print(tile.faces)
        return tile

    def pick_tile(self, tile=None) :
        # print(f"testing pick_tile: {tile}")
        if tile== None :
            tile = self.pick_tile_ui()
        return self.game.change_game_state(self, 'pick_tile', {'tile_id' : id(tile)})

    def discard_tile(self, tile=None) :
        if not tile :
            if len(self.rack) == 0 :
                raise Exception("no tile to discard")
                return False

            print(f"which tile do you want to discard?")
            sel = int(input())
            tile = self.rack[sel]
        # self.discard_tile(tile)
        return self.game.change_game_state(self,'remove_tile',{'tile_id' : id(tile)})

    def get_char_from_rack(self, sel) :
        for idx, t in enumerate(self.rack) :
            if t.get_face().lower() == sel.lower() :
                return idx

    def get_place_options(self):
        word = self.board.word()
        w_idx = self.board.word('idx')
        if len(word) == 0 :
            # print (f"0-{self.board.board_cols}")
            opts = range(0,self.board.board_cols)
        elif len(word) < 4 : # you can replace only if word is 4 letters long
            opts = []
            if word[0].idx > 0 :
                opts.append(word[0].idx - 1)
            if word[-1].idx + 1 < self.board.board_cols :
                opts.append(word[-1].idx + 1)
            # print( '-'.join(map(str, opts)))
        else : # allow places inside word
            # opts = range(max(0,word[0].idx - 1), min(self.board.board_cols, word[-1].idx + 1))
            opts = range(max(0,word[0].idx - 1), min(self.board.board_cols + 1, max(w_idx) + 2))
        return opts

    def get_validate_mode(self, word_idx, w_idx) :
        mode = [['append','prepend'][word_idx < min(w_idx)],'insert'][word_idx in w_idx]

    def run_validate_sum(self, tgt, mode=False) :
        total = 0
        if mode and mode in tgt :
            try :
                return sum(tgt[mode])
            except:
                return tgt[mode]
        for k in tgt :
            if k == 'player' :
                continue
            try :
                # logging.info(f"k is {k}, mode is {mode}, tgt is {tgt}")
                if type(mode) == str :
                    total += sum(tgt[k][mode])
                else :
                    total += sum(tgt[k]) 
            except:
                if type(mode) == str :
                    total += tgt[k][mode]
                else :
                    total += tgt[k]
        return total

  
    def validate_rack_and_place(self, params) : #{'word_idx': num, 'rack_idx': num}
        rack_idx = None
        word_idx = None
        logging.info(f"values passed are {params}")
        if not self.tile_options :
            return True  
        if 'word_idx' in params :
            word_idx = params['word_idx']
        if 'rack_idx' in params :
            rack_idx = params['rack_idx']             
        tgt = False # assume not focusing on any part of tile_options
        if rack_idx :
            tile = self.rack[rack_idx]
            tgt = self.tile_options[tile.get_face().upper()]
        w_idx = self.board.word('idx')
        # assume no tile/letter to check
        if not tgt : # we need a look for each letter
            total = 0
            for k in self.tile_options :
                if k == 'player' :
                    continue
                # we now go through the letters
                tgt = self.tile_options[k]
                if not word_idx :
                    total += self.run_validate_sum(tgt)
                else : # we are looking at a particular location in the word, for any tile
                    mode = self.get_validate_mode(word_idx, w_idx)
                    total += self.run_validate_sum(tgt, mode) > 0
            return total > 0
        else : # we have a particular letter/tile to check
            if not word_idx :
                return self.run_validate_sum(tgt) > 0
            else :
                mode = self.get_validate_mode(self, word_idx, w_idx)
                return self.run_validate_sum(tgt, mode) > 0

    def get_rack_sel_ui(self, params={}) : # params to pass word_sel
        word_idx = None
        if 'word_idx' in params :
            word_idx = params['word_idx']

        print("select from rack: ")    
        valid_rack_sel = False
        msg = "re-enter selection: out of rack."
        while not valid_rack_sel :                    
            try :
                rack_sel = input() # should go to exception if char is entered
                idx = int(rack_sel)   
                logging.info(f"rack_sel is {rack_sel}")             
            except :
                idx = self.get_char_from_rack(rack_sel)
                logging.info(f"sel from char_from_rack is {idx}")
            try :
                tile = self.rack[idx]
                # return rack_sel
            except :
                # treat this as out of range for now
                print ("\033[A                                                        \033[A")
                print ("\033[A                                                        \033[A")
                print(msg)
                continue # loop through again if there's no tile there
            val = self.validate_rack_and_place({'word_idx' : word_idx, 'rack_idx' : idx})
            self.word_idx_status = val
            if val :
                return idx
            else :
                print ("\033[A                                                        \033[A")
                print ("\033[A                                                        \033[A")
                print("no valid words for that tile in chosen location, try again:")

    def get_word_sel_ui(self, opts, params={}) : # params allow us to pass existing rack sel
        valid_word_sel = False
        print(f"choose position in word: ")
        tries = 0
        while not valid_word_sel :
            if type(opts) == range :
                print (f"{min(opts)}-{max(opts)}")
            else :
                print(f"{','.join(map(str,opts))}")
            sel = abs(int(input()))
            if not (sel in opts) :
                print ("\033[A                                                        \033[A")
                print ("\033[A                                                        \033[A")
                print("re-enter selection: out of range.")
                continue
            # store the current word location validity
            val = self.validate_rack_and_place({'word_idx' : sel})
            if val :
                self.word_idx_status = val
                return sel
            else :
                tries += 1
                if tries > 2 :
                    return False
                print ("\033[A                                                        \033[A")
                print ("\033[A                                                        \033[A")
                print("no valid words for rack in that position, try again:")
            
    def place_tile_loc_ui(self) : # returns valid coordinates to place tile
        opts = self.get_place_options()
        word_idx = self.get_word_sel_ui(opts) # contains loop to get value
        if word_idx is False :
            return False
            # now get the tile from the rack
        rack_idx = self.get_rack_sel_ui({'word_sel': word_idx})

        return [word_idx, rack_idx]

    def place_tile(self, tile=None, loc=None) :
        if loc == None :
            place_vals = self.place_tile_loc_ui()
            if not place_vals or not self.word_idx_status :
                print('no go')
                return False
                # this means there's no way to place the chose tile at the chosen location
                # if we put a limited loop in the ui, this means the user ran out of chances
                # we could give them a chance to see valid options to use up their turn
            else :
                # check if this is a complete word
                
                loc = self.board.get_place_by_coords(place_vals[0])
                tile = self.rack[place_vals[1]]
                rslt = self.game.change_game_state(self, 'place_tile', {'tile_id' : id(tile), 'location_id' : id(loc)})
                if rslt['rslt'] :
                    logging.info(f"placing tile [{tile.get_face()}] at location {loc.loc}")
                    return
                    if 'verify' in rslt and rslt['current_player'] != id(self):
                        self.board.show()
                        print("validate first word? y|n")
                        sel = input().lower()
                        self.game.validate(rslt['verify'], sel == "y")
            # except :
            #     logging.info("fall out on false sel")
            #     self.game.current_turn['remaining'] = 0

    def validate_word(self,letter,word=None,loc=None) :
        if word == None :
            # places = self.board.get_word_from_vector(self.vector)  
            places = self.board.get_word()
            word = ""
            for p in places :
                logging.info(f"place is {p}")
                if p == loc : # this only happens if loc is provided so next clause will not matter
                    word += letter
                    letter = ""
                else :
                    word += p.tile.get_face()
        # returns a tuple pair that are the number of partial matching words for letter and word as combined
        return [self.game.defined_word((word + letter).lower(), True), self.game.defined_word((letter + word).lower(), True) ] 

    def flip_tile(self) :

        # if sel == "r" :
        if len(self.rack) == 1 :
            tile = self.rack[0]
        else :
            print(f"which tile do you want to flip?")
            num = int(input())
            invalid = True
            while invalid :
                if num < len(self.rack) :
                    invalid = False
                else :
                    # print ("\033[A                             \033[A")
                    print ("\033[A                             \033[A")
                    print("re-enter selection: out of range.")
                    num = int(input())
            tile = self.rack[num]

        rslt = self.game.change_game_state(self, 'flip_tile', {'tile_id' : id(tile)})

    # METHODS ABOVE THIS LINE ARE SERVER READY 
    def rack_chars(self) :
        rslt = []
        for t in self.rack :
            rslt.append(t.get_face())
        char_set = set(rslt)
        return list(char_set)


    def show_rack(self, print_rack = False) :
        rack = []
        idx = 0
        for t in self.rack :
            showing = self.board.tile_style(t)
            # showing = t.faces[t.player_face]
            rack.append (f"{idx}: {showing}")
            idx += 1
        ret = "[" + "][".join(rack) + "]"
        if print_rack :
            print(ret)
        return ret



    
