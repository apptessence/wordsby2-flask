from flask import Flask
from app.main import index

app = Flask(__name__)

if __name__ == "__main__":
  app.run()