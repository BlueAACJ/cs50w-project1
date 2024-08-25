# Project-1 
import requests
from flask import *
from flask import Flask, session
from config import *
from flask_mysqldb import MySQL

#configuracion de flask 
try:
    app = Flask(__name__)
    app.config.from_object(FlaskConfig)
except Exception as ex:
    print("Error durante la configuracion de Flask {}".format(ex))

# Configuración de MySQL
try:
    mysql = MySQL(app)
    app.config.from_object(MySQLConfig)
except Exception as ex:
    print("Error durante la conexión: {}".format(ex))

# Ruta para el index de la pagina 
@app.route("/", methods = ['GET', 'POST'])
def index():
    if request.method == "POST":
        db = mysql.connection.cursor()
        # request para obtener la busqueda del usuario 
        busqueda = request.form.get("busqueda")

        # capitalize para convertir el formato de la busqueda le asignamos el nuevo valor a la variable 
        busqueda = str.capitalize(busqueda)

        # ejecutamos la base de datos para buscar el libro que el usuario  busca 
        query="SELECT * FROM books WHERE isbn LIKE %s OR title LIKE %s OR author LIKE %s"
        db.execute(query,(busqueda,busqueda,busqueda,))
        libro = db.fetchall()
        
        # verificamos si el libro esta en la base de datos, 0 si no lo esta 
        if libro == ():
            # renderizamos la pagina con un mensaje de error al usuario
            return render_template("error.html")
        
        db.close()
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
        db = mysql.connection.cursor()
        # Tomamos los datos del usuario 
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")

        # verificamos si el usuario esta en la base de datos
        rows = db.execute("SELECT username FROM users WHERE username = %s", (correo,))
        
        # si es igual rows = 0 no esta registrado
        if rows != 0:
            # redireccionamos al index 
            return redirect("/login")

        # Insertamos los datos en la tabla los datos del usuario 
        query1="INSERT INTO users (username, hash) VALUES(%s,%s)"
        db.execute(query1, (correo,contrasena,))
        mysql.connection.commit()
        db.close()

        # redireccionamos al index 
        return redirect("/login")
    else:
        return render_template("registrarse.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":

        db = mysql.connection.cursor()
        # Tomamos los datos del usuario 
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")

        # buscamos los datos en la tabla de usarios
        query="SELECT * FROM users WHERE username = %s AND hash = %s"
        db.execute(query,(correo,contrasena,))
        rows = db.fetchone()

        db.close()

        # Verificamos que haya introducido correctamente la informacion 
        if rows != None:

            # como el usuario esta registrado lo enviamos al index 
            session["id"] = rows[0]
            return render_template("index.html")
        else:
            return redirect("/registrarse")
    else:
        return render_template("login.html") 

@app.route("/logout", methods = ['GET', 'POST'])
def logout():
    # cerramos sesion 
    session.clear()
    # redireccionamos al login 
    return redirect("/login")

# Ruta para la pagina que mostrara el libro 
# recibe un string isbn 
@app.route("/paginalibro/<string:isbn>", methods = ['GET', 'POST'])
def paginalibro(isbn):
    if request.method == "POST":
        # buscamos el libro con la api
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=%s+isbn"+isbn).json()

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

        db = mysql.connection.cursor()

        # ejecutamos la base de datos buscando la informacion del libro
        query="SELECT * FROM books WHERE isbn = %s"
        db.execute(query, (isbn,))
        info = db.fetchall()

        # tomamos la critica y puntuacion del usuario 
        puntuacion = request.form.get("puntuacion")
        resena = request.form.get("resena") 

        # Comprobamos si el usuario hizo alguna critica antes sobre el libro 
        query1="SELECT * FROM reviews WHERE user_id = %s AND isbn = %s"
        db.execute(query1, (session["id"], isbn,))     
        comprobacion = db

        # buscamos las criticas de los usuarios 
        query2="SELECT username, score, review FROM users JOIN reviews ON users.id = reviews.user_id WHERE isbn = %s"
        db.execute(query2, (isbn,))
        reviews = db.fetchall()

        # comprobamos si el usuario ya hizo una critica 
        # si la comprobacion == 0 significa que no hay review 
        if comprobacion.rowcount == 0:
            # guardamos la review en la base de datos 
            db.execute("INSERT INTO reviews (score, review, isbn, user_id) VALUES (%s, %s, %s, %s)", (puntuacion, resena, isbn,session["id"],))
            mysql.connection.commit()  
            imagen = response ["items"][0]["volumeInfo"]["imageLinks"]

            db.close()
            # cargamos la pagina del libro 
            return redirect('/paginalibro/'+ isbn)
        else: 
            db.close()
            # Renderizamos la pagina con un mensaje al usuario sobre que ya hizo una critica del libro 
            return render_template("paginalibro.html", isbn=isbn,info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen, reviews=reviews)
    else:

        db = mysql.connection.cursor()

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

        # ejecutamos la base de datos buscando la informacion del libro
        query="SELECT * FROM books WHERE isbn = %s"
        db.execute(query, (isbn,))
        info = db.fetchall()
        
        # Tomamos las review de la base de datos 
        query1="SELECT username, score, review FROM users JOIN reviews ON users.id = reviews.user_id WHERE isbn = %s"
        db.execute(query1, (isbn,))
        reviews = db.fetchall()

        # comprobamos si el usuario ya hizo una critica 
        query2="SELECT * FROM reviews WHERE user_id = %s AND isbn = %s"
        db.execute(query2, (session["id"],isbn,))        
        comprobacion = db

        # si la critica existe ==1 
        if comprobacion.rowcount == 1:

            db.close()
            # renderizamos la pagina con un mensae sobre que el usuario ya hizo una critica 
            return render_template("paginalibro.html", isbn=isbn,info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen, reviews=reviews)

        db.close()
        # Renderizamos la pagina con un mensaje al usuario sobre que ya hizo una critica del libro 
        return render_template("paginalibro.html", info=info,descripcion=descripcion, averageRating = averageRating, ratingsCount = ratingsCount,imagen=imagen, reviews=reviews, comprobacion=comprobacion)

# Ruta para la pagina que mostrara en formato Json mi informacion sobre el libro  
# recibe un string isbn 
@app.route("/api/<string:isbn>")
def api(isbn):  
    
    db = mysql.connection.cursor()
    # Ejecutamos la base de datos para buscar informacion sobre el libro  
    query="SELECT * FROM books WHERE isbn = %s"
    db.execute(query,(isbn,))
    libro = db.fetchall()

    # definimos el error 404 para enviarlo enformato JSon
    error = "404"   

    # Verificamos si el libron esta en la base de datos si == 0 signifia que no esta en la base datos 
    if len(libro) == 0:
        # Mandomos el formato Json con el error 404
        return jsonify ({"error": error})
    
    # Ejecutamos la base de datos para selccionar el contador de review
    query1="SELECT COUNT(isbn) FROM reviews WHERE isbn = %s"
    db.execute(query1,(isbn,))
    review_count = db.fetchone()

    # Accedemos al valor de las variables que mandaremos en formato Json 
    title = libro[0][2]
    author = libro[0][3]
    year = libro[0][4]

    # Ejecutamos la base de datos para seleccionar el promedio de puntuación
    query2 = "SELECT AVG(score) FROM reviews WHERE isbn = %s"
    db.execute(query2, (isbn,))
    average_score = db.fetchone()

    # Redondeamos la puntuación
    if average_score and average_score[0] is not None:
        average_score = round(average_score[0], 2)
    else:
        average_score = 0  # Valor predeterminado si no hay reseñas
    
    db.close()
    # mandamos el formato Json con la informacion del libro 
    return jsonify ({"title ": title,"author": author,"year": year,"isbn": isbn,"review_count": review_count[0],"average_score": average_score})
