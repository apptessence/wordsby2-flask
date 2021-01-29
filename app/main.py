from game import Game
from flask import Flask

@app.route('/test')
def main():
    game = Game()
    print(game.bleep())
    return dict(plant=game.bleep())