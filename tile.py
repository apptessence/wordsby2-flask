from player import Player
import logging

# In a client/server context, the Game instance and the client player
# instances both have Tile access. The client uses this as a way to 
# perform operations on their own tiles that are only represented in
# the client. The server uses it to manage tiles in the pickbox and bag.
# When a tile is picked by the client, the data is sent to the client 
# which constructs that tile using Tile. 

class Tile :

    faces = []
    import random
    player_face = random.randrange(2) # tile sets its orientation on creation
    player = None
    phase = 0
    owner_options = ["bag","pickbox","rack","in_play"] # this is the basic cycle, from bag to pickbox to rack or inplay.

    def __init__ (self,faces) : # by default, tiles are owned by the bag, and have no player when created.
        self.faces = faces

    def get_data(self) :
        return {
            "player" : self.player, 
            "player_face" : self.player_face, 
            "phase" : self.phase, 
            "faces" : self.faces,
            "id" : id(self) # we'll use this as a shared identifier in client server version
            }

    def flip(self) :
        self.player_face += 1
        self.player_face = self.player_face % 2
        return self
    
    def get_player(self) :
        return self.player

    def set_player(self, player) :
        # logging.info(f"current player is {player}")
        if type(player) != Player :
            return False
        self.player = player
        return True
    
    def return_to_bag(self) :
        self.owner = None
        self.set_phase(0)
        return self

    def set_unowned(self) :
        self.player = None

    # owner is the status in the game (see owner_options)
    def get_phase(self) :
        return self.owner_options[self.phase]

    def set_phase (self, phase) : # without argument, moves tile between owner in sequence; or specify new owner with argument.
        # if moving to rack or in play, requires a player be set, or provided.
        if phase > 1 :
            if not isinstance(self.player, Player) :
                raise Exception(f"{self.player} tile requires player if owner is greater than 1")
                return False
        if phase < 2 :
            self.player = None
        self.phase = phase
        return self

    # face is the face the tile shows in the game (anywhere but bag)
    def set_face(self, player_face=None ) : # without argument, flips the tile
        if self.owner == 0 : # in the bag
            raise Exception ("can't change face while in bag")
        if player_face == None :
            player_face = self.player_face + 1            
        player_face = player_face % 2 # ensure that the value is either 1 or zero
        self.player_face = player_face
        return self.get_face()

    def get_face(self) :
        return self.faces[self.player_face]

    def get_faces(self) : # get the faces that the tile has
        return self.faces


