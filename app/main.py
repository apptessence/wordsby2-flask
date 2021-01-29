# from game import Game
from flask import Flask

app = Flask(__name__)

@app.route('/test/', methods=['GET'])

def main():
    return "hello world"
    # game = Game()
    # print(game.bleep())
    # return dict(plant=game.bleep())