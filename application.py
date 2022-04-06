# from crypt import methods
import os

from dotenv import load_dotenv
from flask import *
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# load_dotenv()

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))

db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods = ['GET', 'POST'])
def index():
    session.clear()
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("login.html")
