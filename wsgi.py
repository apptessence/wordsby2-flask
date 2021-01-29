from flask import Flask

from app.index import main
app = Flask(__name__)

if __name__ == "__main__":
  app.run()