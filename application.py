# from crypt import methods
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

# Ruta para el index de la pagina 
@app.route("/", methods = ['GET', 'POST'])
def index():
    if request.method == "POST":
        # request para obtener la busqueda del usuario 
        busqueda = request.form.get("busqueda")
        # capitalize para convertir el formato de la busqueda le asignamos el nuevo valor a la variable 
        busqueda = str.capitalize(busqueda)
        # ejecutamos la base de datos para buscar el libro que el usuario  busca 
        libro = db.execute("SELECT * FROM books WHERE isbn LIKE :busqueda OR title LIKE :busqueda OR author LIKE :busqueda",
                            {"busqueda":"%"+busqueda+"%"}).fetchall()
        
        # verificamos si el libro esta en la base de datos, 0 si no lo esta 
        if len(libro) == 0:
            # renderizamos la pagina con un mensaje de error al usuario
            return render_template("error.html")

        # si el libro existe renderizamos el index con la lista de libros 
        return render_template("index.html", libros = libro)
    else:
        # Renderizamos el index normal (con una imagen de estanteria de fondo )
        return render_template("index.html")

# Ruta para registrarse 
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
    # cerramos sesion 
    session.clear()
    # redireccionamos al login 
    return redirect("/login")

# Ruta oara la pagina que mostrara el libro 
# # recibe un string isbn 
@app.route("/paginalibro/<string:isbn>", methods = ['GET', 'POST'])
def paginalibro(isbn):
    if request.method == "POST":
        # buscamos el libro con la api
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()

        # tomamos la descripcion del Json de la api 
        try:
            descripcion = response ["items"][0]["volumeInfo"]["description"]
        except:
            # mensaje de error al encontrar el elemento 
            descripcion = "Descripcion no disponible"

        # tomamos el puntaje promedio del Json de la api 
        try:
            averageRating = response ["items"][0]["volumeInfo"]["averageRating"]
        except:
            # mensaje de error al encontrar el elemento 
            averageRating = "Puntaje promerio no disponible"     

        # tomamos el numero de puntuaciones del Json de la api 
        try:
            ratingsCount = response ["items"][0]["volumeInfo"]["ratingsCount"]         
        except:
            # mensaje de error al encontrar el elemento 
            ratingsCount = "Numero de puntuaciones no disponible " 

        # tomamos la imagen del Json de la api 
        try:
            imagen = response ["items"][0]["volumeInfo"]["imageLinks"]["smallThumbnail"]
        except:
            # mensaje de error al encontrar el elemento 
            imagen = "https://th.bing.com/th/id/R.74654977efcc4ed97f49758d1490c66a?rik=UfxlrZKQU0Vhhg&riu=http%3a%2f%2fimg2.wikia.nocookie.net%2f__cb20140827124248%2fmonsterhunterespanol%2fes%2fimages%2fa%2faa%2fImagen-no-disponible-282x300.png&ehk=H4Cryldwr99UjRttRTd5V4ZIqR%2blqG%2fQoggdMl7yECo%3d&risl=&pid=ImgRaw&r=0"

        # ejecutamos la base de datos buscando la informacion del libro
        info = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        # tomamos la critica y puntuacion del usuario 
        puntuacion = request.form.get("puntuacion")
        resena = request.form.get("resena") 

        # Comprobamos si el usuario hizo alguna critica antes sobre el libro 
        comprobacion = db.execute("SELECT * FROM reviews WHERE user_id = :usuario AND isbn = :isbn", {"usuario": session["id"], "isbn": isbn})     
        
        # buscamos las criticas de los usuarios 
        reviews = db.execute("SELECT username, score, review FROM users JOIN reviews ON users.id = reviews.user_id WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        # comprobamos si el usuario ya hizo una critica 
        # si la comprobacion == 0 significa que no hay review 
        if comprobacion.rowcount == 0:
            # guardamos la review en la base de datos 
            db.execute("INSERT INTO reviews (score, review, isbn, user_id) VALUES (:score, :review, :isbn, :user_id)", {"score":puntuacion, "review":resena, "isbn":isbn,"user_id":session["id"]})
            db.commit()  
            imagen = response ["items"][0]["volumeInfo"]["imageLinks"]
            # cargamos la pagina del libro 
            return redirect('/paginalibro/'+ isbn)
        else: 
            # Renderizamos la pagina con un mensaje al usuario sobre que ya hizo una critica del libro 
            return render_template("paginalibro.html", isbn=isbn,info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen, reviews=reviews)
     
    else:
        # buscamos el libro en la api 
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()

        # tomamos la descripcion del Json de la api 
        try:
            descripcion = response ["items"][0]["volumeInfo"]["description"]
        except:
            # mensaje de error al buscar la imagen 
            descripcion = "Descripcion no disponible"

        # tomamos el puntaje promedio del Json de la api 
        try:
            averageRating = response ["items"][0]["volumeInfo"]["averageRating"]
        except:
            # Mensaje de error al buscar el puntaje promesio 
            averageRating = "Puntaje promerio no disponible"        

        # tomamos el numero de puntuaciones del Json de la api 
        try:
            ratingsCount = response ["items"][0]["volumeInfo"]["ratingsCount"]         
        except:
            # MEnsaje de error al buscar el numero de puntuaciones 
            ratingsCount = "Numero de puntuaciones no disponible " 

        # tomamos la descripcion del Json de la api   
        try:
            imagen = response ["items"][0]["volumeInfo"]["imageLinks"]["smallThumbnail"]
        except:
            # mensaje de error al buscar la imagen 
            imagen = "https://th.bing.com/th/id/R.74654977efcc4ed97f49758d1490c66a?rik=UfxlrZKQU0Vhhg&riu=http%3a%2f%2fimg2.wikia.nocookie.net%2f__cb20140827124248%2fmonsterhunterespanol%2fes%2fimages%2fa%2faa%2fImagen-no-disponible-282x300.png&ehk=H4Cryldwr99UjRttRTd5V4ZIqR%2blqG%2fQoggdMl7yECo%3d&risl=&pid=ImgRaw&r=0"

        # Selccionamos la informacion del libro en la base de datos 
        info = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
        
        # Tomamos las review de la base de datos 
        reviews = db.execute("SELECT username, score, review FROM users JOIN reviews ON users.id = reviews.user_id WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        # comprobamos si el usuario ya hizo una critica 
        comprobacion = db.execute("SELECT * FROM reviews WHERE user_id = :usuario AND isbn = :isbn", {"usuario": session["id"], "isbn": isbn})        

        # si la critica existe ==1 
        if comprobacion.rowcount == 1:
            # renderizamos la pagina con un mensae sobre que el usuario ya hizo una critica 
            return render_template("paginalibro.html", isbn=isbn,info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen, reviews=reviews)

        # Renderizamos la pagina con un mensaje al usuario sobre que ya hizo una critica del libro 
        return render_template("paginalibro.html", info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen, reviews=reviews, comprobacion=comprobacion)

@app.route("/api/<string:isbn>", methods = ['GET'])
def api(isbn):
    if request.method == "GET":
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
        
        libro = db.execute("SELECT * FROM books WHERE isbn LIKE :busqueda OR title LIKE :busqueda OR author LIKE :busqueda",
                            {"busqueda":"%"+isbn+"%"}).fetchall()

        if len(libro) == 0:
            return render_template("404.html"),404           

        title = response ["items"][0]["volumeInfo"]["title"]

        author = response ["items"][0]["volumeInfo"]["authors"]      

        year = response ["items"][0]["volumeInfo"]["publishedDate"]         

        review_count = response ["items"][0]["volumeInfo"]["ratingsCount"]         

        average_score = response ["items"][0]["volumeInfo"]["averageRating"]         

        return render_template("api.html", title=title,author=author,year=year,isbn=isbn,review_count=review_count,average_score=average_score)
