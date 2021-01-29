# Need to implement a protocol where asyncronous issues are dealt with
# **    any random events that affect both players must happen in Game.
# **    any action by a Player that interacts with these, or with game state
#       can be tried in the Player instance, but only becomes official when
#       it is passed to the Game.
# **    The Game must recognize these events (through a change_game_state method)
#       and then notify the Players
# **    The Game must manage Player turns, and notify both players when this changes
# More to come....


from tiles import Tiles
from tile import Tile
from board import Board
from pickbox import Pickbox
from player import Player

import os
try :
    os.remove("wordloops.log")
except :
    print("no log file")

import logging
logging.basicConfig(filename='wordloops.log', level=logging.DEBUG)

import random

# In the client/server context, the Game instance only exists on the server.
# It is will run the websocket that allows the client Player instances to 
# talk to the game.

class Game :
    tiles = None
    pickbox = None
    player_0 = None
    player_1 = None
    board = None
    first_word_len = 6
    non_place_turn_len = 3
    turn = 0
    word_complete = False

    import random
    import os
    game_modes = ['local','web']
    tiles = None
    choices = ["Fill","Choose","Place", "Turn","Discard","Empty"]

    def __init__(self, game_mode='local') :
        # logging.info("----------------------------")
        logging.info("STARTING GAME INITIALIZATION")
        if game_mode in self.game_modes :
            self.game_mode = game_mode # this is the switch for web 
        # if type(self.tiles) == Tiles :
        #     logging.info (self.tiles)   
        self.tiles = Tiles(self) # done as bag
        self.board = Board(self) # done
        self.pickbox = Pickbox(self) # done
        self.player_0 = Player(self.game_mode, self, self.pickbox, self.board) # add a 'self' argument to pass game to player?
        self.player_1 = Player(self.game_mode, self, self.pickbox, self.board)
        players = [self.player_0, self.player_1]
        self.players = {'players' : players, 'current' : random.choice(players)}
        self.fill_pickbox()
        self.current_turn = {}
        self.set_turn({'initialize' : True}, True) # do a reset on the current turn
        # print(self.current_turn)
        # this is probably not required, won't be included in Swift version
        self.words={'first': {'complete' : False, 'letters' : []}, 
                    "player_0" : {'letters': [], 'vector': {'dir': 'col', 'idx': self.board.wall()}, 'words' : []}, 
                    "player_1" : {'letters': [], 'vector': {'dir': 'col', 'idx': self.board.wall()}, 'words' : []}}

                    # {'dir': 'col', 'idx': self.board.wall(), 'origin': location.loc}
        # end omitted Swift code
        logging.info("GAME READY")

    def set_turn(self, params={}, reset=False ) :
        if reset :
            self.current_turn['player'] = [self.current_player(), None]['initialize' in params]
            self.current_turn['action'] = None
            self.current_turn['remaining'] = 0
        if 'action' in params :
            action = params['action']
            if reset :
                self.current_turn['remaining'] = [1,self.non_place_turn_len][action != 'place']         
            self.current_turn['action'] = action
            self.current_turn['remaining'] = self.current_turn['remaining'] - 1  
        logging.info(f"set_turn : {self.current_turn}")             

    def remaining_turns(self) :
        return self.current_turn['remaining']

    def legal_turn(self, action) :
        if not type(action) == list :
            action = [action]
        if self.current_turn['remaining'] == 0 and self.current_turn['action'] != None:
            return False
        # if type(action) == list :
        for a in action :
            if a != 'place' and self.current_turn['action'] == 'place' :
                return False
            if a == 'place' and self.current_turn['action'] != 'place' :
                return False
        return True        

    def inactive_player(self) : # convenience method
        players= self.players['players']
        idx = players.index(self.current_player())
        return players[(idx + 1) % 2]

    def manage_game_state(self, permitted):
        logging.info("manage game state")

    def current_player(self, change=False) :
        if change :
            self.turn += 1
            logging.info("changing player")
            p = self.players['current']
            idx = self.players['players'].index(p)
            idx = (idx + 1) % 2
            self.players['current'] = self.players['players'][idx]
            logging.info(f"current player : {id(self.players['current'])}")
        return self.players['current']

    def loop(self) :
        self.game_loop()

    def declare_winner(self, player) :
        print( "WINNER!!")

    def game_loop(self) :
        self.looping = True
        while self.looping :
            logging.info(f"------ Loop {self.current_player()} -------")
            turn = self.current_player().take_turn()
            logging.info(f"remaining: {self.current_turn['remaining']}, player: {self.current_turn['player']}, turn: {turn}")
            if type(turn) == dict :
                if 'win' in turn and turn['win'] == True :
                    self.declare_winner(self.current_player())
                    break
            self.current_player(self.current_turn['remaining'] == 0 and self.current_turn['player'] == self.current_player()) # switch players      

    def change_game_state(self, player, action, params={}) :
        # this is the definitive entry point for moves etc.
        # when game shifts to online, this will be called by players
        # opportunity to evaluate action and params here, otherwise proceed

        if  type(params) not in [dict, str, int] :
            raise Exception("params must be dict or string")
            return False
        if type(params) == str :
            try :
                params = eval(params)
            except :
                raise Exception("params not formed correctly")
                return

        # parse any standard params here
        if 'tile_id' in params :
            tile = self.tiles.by_id(params['tile_id'])
        if 'location_id' in params :
            loc = self.board.place_by_id(params['location_id'])

        if player is self.current_player() :
            if action == 'flip_tile' :
                rslt = self.flip_tile(tile)
            elif action == "fill_pickbox" :
                rslt = self.fill_pickbox()
            elif action == "empty_pickbox" :
                rslt = self.empty_pickbox() 
            elif action == "pick_tile" :
                rslt = self.pick_tile(tile) 
            elif action == "remove_tile" :
                rslt = self.remove_player_tile(player, tile) 
            elif action == 'place_tile' :
                # print(f" player is {player}")
                # if self.pre_validate_place_tile(player, tile, loc) :
                rslt = self.place_tile(player, tile, loc)
            else :
                logging.warning(f"action not recognized : {event['event']}")
                raise Exception("action not permitted") 
        else :
            raise Exception("Non active player attempting to change game state")
            return False
        self.notify_players(rslt)
        return rslt

    def pre_validate_place_tile(self, player, tile, loc) :
        logging.info("prevalidation: not implemented")
        return True

    def search_word_db(self,str,con=False, srch="") :
        import sqlite3 as sl
        my_con = [con,sl.connect('words.sqlite3')][con == False]
        if srch == "" :
            srch = "SELECT * FROM WORDS WHERE WORD LIKE '%{0}%'"
        return con.execute(srch.format(str))
         
    def tile_options(self) :
        import sqlite3 as sl
        con = sl.connect('words.sqlite3')  
        rslt = {'player': self.current_player()}

        word = "".join(self.board.word("str"))
        chars = self.current_player().rack_chars()
        for char in chars :
            rslt[char] = {}
            tgt = rslt[char]
            token = chars[0] + word
            tgt['prepend'] = len(self.search_word_db(token,con).fetchall())
            token = word + chars[0]
            tgt['append'] = len(self.search_word_db(token,con).fetchall())
            tgt['inserts'] = []
            for idx in range(len(word)) :
                token = list(word)
                token[idx] = char
                token = "".join(token)
                # cursor = con.execute(srch.format(token))
                tgt['inserts'].append(len(self.search_word_db(token,con).fetchall()))
        con.close()
        return rslt
    
    def defined_word(self, word, partial=False) :
        import sqlite3 as sl
        con = sl.connect('words.sqlite3')      
        if partial :
            cursor = con.execute(f"SELECT * from WORDS WHERE WORD LIKE '%{word.lower()}%'")
        else :
            cursor = con.execute(f"SELECT * from WORDS WHERE WORD IS '{word.lower()}'")
        rslt = (len(cursor.fetchall()))
        con.close()
        return rslt

    def bleep(self) :
        return "bloop"

    def validate(self, data, flag) :
        self.looping = True
        print(f"validation {['denied','confirmed'][flag]}")
        self.game_loop()

    def check_complete(self) :
        word = self.board.word('str')
        import sqlite3 as sl
        con = sl.connect('words.sqlite3')  
        cursor = con.execute(f"SELECT * FROM WORDS WHERE WORD IS '{''.join(word).lower()}'")
        rslt = cursor.fetchall()
        logging.info(f"rslt is {rslt}")
        con.close()
        return len(rslt) == 1

    def notify_players(self, event) :
        for p in self.players['players'] :
            event['current_player'] = id(self.current_player())
            p.update_game(event)

    # METHODS BELOW ARE CALLED FROM PLAYERS

    def fill_pickbox(self) :
        self.pickbox.fill()
        return ({'event': 'fill_pickbox', 'rslt': 1})
        
    def empty_pickbox(self) :
        self.pickbox.empty()
        return ({'event': 'empty_pickbox', 'rslt': 1})

    def pick_tile(self, tile=None) :
        if type(tile) != Tile :
            raise Exception("error picking tile")
        if tile == False :
            logging.info( "no tiles I guess")
            return ({'event': 'pick_tile', 'rslt': -1}) # add code to indicate what tile next
        tile.player = self.current_player()
        self.current_player().rack.append(tile)
        self.pickbox.remove_tile(tile)
        logging.info(tile.get_data())
        return ({'event': 'pick_tile', 'rslt': 1})

    def remove_player_tile(self, player, tile) : # player sends tile back to bag
        if player != self.current_player() :
            raise Exception("inactive player cannot discard tiles")
        player.rack.remove(tile.return_to_bag())
        return ({'event': 'remove_tile', 'rslt': 1})

    def flip_tile(self, tile):
        tile.flip()
        return({'event' : 'flip_tile', 'tile_id' : id(tile), 'rslt': 1})

    def place_tile(self, player, tile, location) :
        rslt =  self.board.place_tile(tile, location, player)
        if rslt['rslt'] == 1 :
            player.rack.remove(tile)  
        rslt['tile_id'] = id(tile)
        rslt[ 'location_id'] = id(location)
        if self.check_complete() :
            self.word_complete = self.current_player()
        else :
            self.word_complete = False
        logging.info(f"word_complete is {self.word_complete}")
        self.current_player(True)
        return rslt

    def choice_keys(self, opts) :
        rslt = {}
        for num in opts :
            rslt[self.choices[num][0].lower()] = num
        return rslt

def play(game) :
    game.game_loop()

    



