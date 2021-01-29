from ../game import Game
from flask import Flask
from gunicorn import Gunicorn
app = Flask(__name__)

@app.route('/')
def main():
    game = Game()
    print(game.bleep())
    return dict(plant=game.bleep())