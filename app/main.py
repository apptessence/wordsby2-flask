# from game import Game
from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])

def index():
    return "hello world"
    # game = Game()
    # print(game.bleep())
    # return dict(plant=game.bleep())