import requests
from inspect import Attribute
import os
from tkinter import NO
from tokenize import String

from dotenv import load_dotenv
from flask import *
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine, null
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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
    if request.method == "POST":
        busqueda = request.form.get("busqueda")
        busqueda = str.capitalize(busqueda)
        libro = db.execute("SELECT * FROM books WHERE isbn LIKE :busqueda OR title LIKE :busqueda OR author LIKE :busqueda",
                            {"busqueda":"%"+busqueda+"%"}).fetchall()

        if len(libro) == 0:
            return render_template("error.html")

        return render_template("index.html", libros = libro)
    else:
        return render_template("index.html")

@app.route("/registrarse", methods = ['GET', 'POST'])
def registrarse():
    session.clear()
    if request.method == "POST":
        # Tomamos los datos del usuario 
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")
 
        # buscamos los datos en la tabla de usarios
        rows = db.execute("SELECT * FROM users WHERE username = :username AND hash = :hash", 
                            {"username":correo,"hash":contrasena}).fetchall()
        
        # Verificamos que haya introducido con len(rows) != 0 si es igual a 0 no esta registrado 
        if len(rows) != 0:
            return render_template("registrarse.html")

        # Insertamos los datos en la tabla los datos del usuario 
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", {"username":correo,"hash":contrasena})
        db.commit()

        # redireccionamos al index 
        return redirect("/login")
    else:
        return render_template("registrarse.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":
        # Tomamos los datos del usuario 
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")

        # buscamos los datos en la tabla de usarios
        rows = db.execute("SELECT * FROM users WHERE username = :username AND hash = :hash",
                            {"username": correo, "hash": contrasena}).fetchall()

        # Verificamos que haya introducido correctamente la informacion 
        #  con len(rows) == 1 sabemos que el usuario esta registrado 
        if len(rows) == 1:
            # como el usuario esta registrado lo enviamos al index 
            session["id"] = rows[0]["id"]
            return render_template("index.html")
        else:
            # Ya que el usuario no tiene cuenta lo redirigimos al registro 
            return render_template("registrarse.html")
    else:
        # print("hola")
        return render_template("login.html") 

@app.route("/logout", methods = ['GET', 'POST'])
def logout():
    session.clear()
    return redirect("/login")

# recibe un string isbn 
@app.route("/paginalibro/<string:isbn>", methods = ['GET', 'POST'])
def paginalibro(isbn):
    if request.method == "POST":
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
        try:
            descripcion = response ["items"][0]["volumeInfo"]["description"]
        except:
            descripcion = "Descripcion no disponible"

        try:
            averageRating = response ["items"][0]["volumeInfo"]["averageRating"]
        except:
            averageRating = "Puntaje promerio no disponible"        

        try:
            ratingsCount = response ["items"][0]["volumeInfo"]["ratingsCount"]         
        except:
            ratingsCount = "Numero de puntuaciones no disponible " 

        try:
            imagen = response ["items"][0]["volumeInfo"]["imageLinks"]
        except:
            imagen = "https://th.bing.com/th/id/R.74654977efcc4ed97f49758d1490c66a?rik=UfxlrZKQU0Vhhg&riu=http%3a%2f%2fimg2.wikia.nocookie.net%2f__cb20140827124248%2fmonsterhunterespanol%2fes%2fimages%2fa%2faa%2fImagen-no-disponible-282x300.png&ehk=H4Cryldwr99UjRttRTd5V4ZIqR%2blqG%2fQoggdMl7yECo%3d&risl=&pid=ImgRaw&r=0"
    
        # reviews = db.execute("SELECT * FROM review WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        nombres = db.execute("SELECT username, score, review FROM users JOIN reviews ON users.id = reviews.user_id WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
        print(nombres) 

        info = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        puntuacion = request.form.get("puntuacion")
        resena = request.form.get("resena") 

        

        comprobacion = db.execute("SELECT * FROM reviews WHERE user_id = :usuario AND isbn = :isbn", {"usuario": session["id"], "isbn": isbn})        

        if comprobacion.rowcount == 1:
            return "Ya existe"
        
        else: 
            db.execute("INSERT INTO reviews (score, review, isbn, user_id) VALUES (:score, :review, :isbn, :user_id)", {"score":puntuacion, "review":resena, "isbn":isbn,"user_id":session["id"]})
            db.commit()
         
        """
        if not resena:
            return render_template("paginalibro.html", isbn=isbn,info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen)

        if not puntuacion:
            return render_template("paginalibro.html", isbn=isbn,info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen)

        """
        return render_template("paginalibro.html", isbn=isbn,info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen, reviews=reviews)
     
    else:
        """nombres = db.execute("SELECT username, score, review FROM users JOIN reviews ON users.id = :reviews.user_id WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
        print(nombres) """

        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
        try:
            descripcion = response ["items"][0]["volumeInfo"]["description"]
        except:
            descripcion = "Descripcion no disponible"

        try:
            averageRating = response ["items"][0]["volumeInfo"]["averageRating"]
        except:
            averageRating = "Puntaje promerio no disponible"        

        try:
            ratingsCount = response ["items"][0]["volumeInfo"]["ratingsCount"]         
        except:
            ratingsCount = "Numero de puntuaciones no disponible " 
               
        try:
            imagen = response ["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
        except:
            imagen = "https://th.bing.com/th/id/R.74654977efcc4ed97f49758d1490c66a?rik=UfxlrZKQU0Vhhg&riu=http%3a%2f%2fimg2.wikia.nocookie.net%2f__cb20140827124248%2fmonsterhunterespanol%2fes%2fimages%2fa%2faa%2fImagen-no-disponible-282x300.png&ehk=H4Cryldwr99UjRttRTd5V4ZIqR%2blqG%2fQoggdMl7yECo%3d&risl=&pid=ImgRaw&r=0"

        info = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        # reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        reviews = db.execute("SELECT username, score, review FROM users JOIN reviews ON users.id = reviews.user_id WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
        print(reviews)

        return render_template("paginalibro.html", info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen, reviews=reviews)
