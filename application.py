# from crypt import methods
#from crypt import methods
from cgitb import lookup
from inspect import Attribute
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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registrarse", methods = ['GET', 'POST'])
def registrarse():
    session.clear()
    if request.method == "POST":
        ## Tomamos los datos del usuario 
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")

        ## buscamos los datos en la tabla de usarios 
        rows = db.execute("SELECT * FROM users WHERE username = :username AND hash = :hash", 
                            {"username":correo,"hash":contrasena}).fetchall()
        
        ## Verificamos que haya introducido con len(rows) != 0 si es igual a 0 no esta registrado 
        if len(rows) != 0:
            return render_template("registrarse.html")

        ## Insertamos los datos en la tabla los datos del usuario 
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", {"username":correo,"hash":contrasena})
        db.commit()

        ## redireccionamos al index 
        return redirect("/")
    else:
        return render_template("registrarse.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")
    else:
        return render_template("login.html")
