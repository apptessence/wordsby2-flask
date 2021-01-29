from game import Game
from flask import Flask
app = Flask(__name__)

@app.route('/')
def main():
    game = Game()
    print(game.bleep())
    return dict(plant='dog')

if __name__ == '__main__' :
    app.run(debug=True)