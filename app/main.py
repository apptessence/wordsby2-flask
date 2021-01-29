from game import Game
from flask import Flask

app = Flask(__name__)

@app.route('/test')
def main():
    game = Game()
    print(game.bleep())
    return dict(plant=game.bleep())