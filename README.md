# Project 1

Project hecho en 2022

Requerimientos del project 1:

* Registro: Los usuarios deberían ser capaces de registrarse en tu sitio web, proveyendo (como mínimo) un nombre de usuario y una contraseña.

* Inicio de Sesión: Los usuarios, una vez registrados, deberían ser capaces de iniciar sesión en tu sitio web con su nombre de usuario y contraseña.

* Cierre de sesión: Los usuarios conectados deberían ser capaces de cerrar sesión.

* Importar: Se le proporciona en este proyecto un archivo llamado books.csv, el cual es una hoja de cálculo en formato CSV de 5000 libros diferentes. Cada uno tiene un número ISBN, un título, un autor, y un año de publicación. En un archivo Python llamado import.py separado de tu aplicación web, escriba un programa que tome los libros y los importe a su base de datos PostgreSQL. Primero necesitarás decidir qué tablas crear, qué columnas esas tablas deberían tener, y cómo se deberían relacionar entre ellas. Ejecuta este programa con correr python3 import.py para importar los libros a tu base de datos, y envía este programa con el resto del código de tu proyecto.

* Búsqueda: Una vez que el usuario ha iniciado sesión, deberían ser llevados a una página donde puedan buscar un libro. Los usuarios deberían ser capaces de ingresar el número ISBN de el libro, el título de el libro, o el autor de un libro. Luego de realizar la búsqueda, tu sitio web debería mostrar una lista de posibles coincidencias, o alguna clase de mensaje si no hubieron coincidencias. Si el usuario ingresó solamente parte de un título, ISBN, o nombre del autor, ¡tu página de búsqueda debería encontrar coincidencias para esos igualmente!

* Pagina de Libro Cuando los usuarios hagan click en un libro entre los resultados de la página de búsqueda, deberían ser llevados a una página de libro, con detalles sobre el libro: su título, autor, año de publicación, número ISBN, y cualquier reseña que los usuarios han dejado para ese libro en tu sitio web.

* Envío de Reseña: En la página de libro, los usuarios deberían ser capaces de enviar una reseña: consistiendo en un puntaje en una escala del 1 al 5, al igual que un componente de texto para la reseña donde el usuario pueda escribir su opinión sobre un libro. Los usuarios no deberían ser capaces de enviar múltiples reseñas para el mismo libro.

* Información de Reseña de Goodreads (Google Books API): En la página de libro, también deberías mostrar (si está disponible) el puntaje promedio y cantidad de puntuaciones que el libro ha recibido de Goodreads.

* Acceso a API: Si los usuarios hacen una solicitud GET a la ruta /api/ de tu sitio web, donde es un número ISBN, tu sitio web debería retornar una respuesta JSON conteniendo el título del libro, autor, fecha de publicación, número ISBN, conteo de reseñas, y puntaje promedio. El JSON resultante debería seguir el siguiente formato:
        
        {
            "title": "Memory",
            "author": "Doug Lloyd",
            "year": 2015,
            "isbn": "1632168146",
            "review_count": 28,
            "average_score": 5.0
        }
        
* Si el número ISBN solicitado no está en tu base de datos, tu sitio web debería retornar un error 404.

* Deberías estar usando comandos SQL puros (a través del método execute de SQLAlchemy) para hacer consultas a la base de datos. No deberías usar el ORM de SQLAlchemy (si te es familiar) para este proyecto.

    En README.md, incluye una breve descripción de tu proyecto, qué contiene cada archivo, y (opcionalmente) cualquier otra información adicional que el staff deba saber acerca de tu proyecto.

* Si has añadido algún paquete Python que necesite ser instalado para poder ejecutar tu aplicación web, ¡asegúrate de añadirlo a requirements.txt!
    
* Más allá de estos requerimientos, ¡el diseño y apariencia del sitio web dependen de ti! También eres bienvenido a añadir características extras a tu sitio web, ¡mientras cumplas con los requerimientos expuestos arriba!

Informacion sobre los archivos: 
    error.html---> Tiene un mensaje de error al buscar un libro 
    index.html--> Tiene la pagina principal de mi sitio Web 
    layout.html--> Tiene el layout de mi sitio web
    login.html--> Tiene la pagina para iniciar sesion en mi pagina web 
    paginalibro.html--> Tiene el formato para mostrar la informacion del libro, donde poder nuestra resena y puntuacion 
    registrarse.html--> Tiene la pagina de registro de la pagina 

    application.py--> Tiene la aplicacion de mi de pagina web 

    books.csv--> Tiene informacion sobre los libros 

    import.py--> Archivo que user para importar la informacion de los libros a la base de datos 

    style.scss--> Tiene los estilos de mi pagina web 
