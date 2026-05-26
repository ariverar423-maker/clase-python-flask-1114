# Importamos Flask y una funcion que permite mostrar un HTML.
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


# Creamos la aplicacion principal.
# Este objeto sera el centro de nuestro proyecto Flask.
app = Flask(__name__)

# Configurar la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Cuando alguien entra a la direccion principal del sitio, Flask ejecuta
# esta funcion y devuelve la pagina `index.html`.
@app.route("/")
def inicio():
    
    nombre_profesor = "Henry Ortegon"
    email_profesor = "henry@kyrbot.com"
    horario = "Miercoles 16:45-18:10 | Jueves 12:30-14:20"
    aula = "215"
    descripcion = "Aprenderemos Python, Flask y construiremos un portal web real"
           
           
     # variable jinja
    nombre_10 = "Andres El steven"
    edad_10 = 16


    return render_template(
        "index.html",
        profesor=nombre_profesor,
        email=email_profesor,
        horario=horario,
        aula=aula,
        descripcion=descripcion,

        # variable jinja
        nombre1=nombre_10,
        edad1=edad_10,



    )




@app.route("/informacion")
def informacion():

    datos = {
        "aula": "215",
        "profesor": "Henry Ortegon",
        "horario": "Miercoles 16:45-18:10 | Jueves 12:30-14:20",
    }

    lista_objetivos = {
        "Aprender Python basico",
        "Entender Flask y aplicaciones web",
        "Construir un portal web real"
        
    }


    return render_template("informacion.html", **datos, objetivos=lista_objetivos)



@app.route("/recursos")
def recursos():

    enlaces = [
        {"nombre": "Documentacion Flask", "url": "https://flask.palletsprojects.com"},
        {"nombre": "Tutorial Python", "url": "https://docs.python.org"},
        {"nombre": "GitHub del Profesor", "url": "https://github.com/hortegon"},
        {"nombre": "MDN - HTML y CSS", "url": "https://developer.mozilla.org"},
    ]    

    return render_template("recursos.html", enlaces=enlaces)



@app.route("/tareas")
def tareas():

    lista_tareas = [
        {"numero": 1, "titulo": "Portal base", "fecha": "25/05/2026"},
        {"numero": 2, "titulo": "Datos dinamicos", "fecha": "30/05/2026"},
        {"numero": 3, "titulo": "Multiple paginas", "fecha": "05/06/2026"}
    ]    

    return render_template("tareas.html", tareas=lista_tareas)

@app.route("/inscripcion", methods=["GET", "POST"])
def inscripcion():
    mensaje = None
    
    if request.method == "POST":
        
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        programa = request.form.get("programa")
        
        # Validación: verifica que no haya campos vacíos
        if not nombre or not email or not programa:
            mensaje = "Por favor completa todos los campos."
        else:
            try:
                # Crear nuevo estudiante
                nuevo_estudiante = Estudiante(
                    nombre=nombre,
                    email=email,
                    programa=programa
                )
                
                # Guardar en BD
                db.session.add(nuevo_estudiante)
                db.session.commit()
                
                mensaje = f"¡Bienvenido {nombre}! Te hemos registrado con éxito."
                
            except Exception as e:
                # Si el email ya existe u ocurre otro error, deshace los cambios
                db.session.rollback()
                mensaje = "Error: Este email ya está registrado o el formato es incorrecto."
    
    # Renderiza la plantilla HTML pasándole la variable del mensaje
    return render_template("inscripcion.html", mensaje=mensaje)


@app.route("/estudiantes")
def estudiantes():
    lista_estudiantes = Estudiante.query.all()
    return render_template("estudiantes.html", estudiantes=lista_estudiantes)

# tarea 6 definicion del modelo

class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    programa = db.Column(db.String(50), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Estudiante {self.nombre}>'




# Este bloque se ejecuta solo si corremos `python app.py` desde la terminal.
if __name__ == "__main__":
    # `debug=True` sirve en desarrollo porque reinicia el servidor
    # cuando detecta cambios y muestra errores con mas detalle.
    app.run(debug=True)
