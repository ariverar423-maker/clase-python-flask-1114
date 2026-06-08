# Importamos Flask y una funcion que permite mostrar un HTML.
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# Importación para convertir el texto del formulario en objeto fecha
from datetime import datetime


# Creamos la aplicacion principal.
# Este objeto sera el centro de nuestro proyecto Flask.
app = Flask(__name__)

# Configurar la base de datos

app.secret_key = "clave-secreta-super-segura-1114"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# tarea 7 
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # "profesor" o "estudiante"

    def establecer_contraseña(self, contraseña):
        self.contraseña = generate_password_hash(contraseña)

    def verificar_contraseña(self, contraseña):
        return check_password_hash(self.contraseña, contraseña)

    def __repr__(self):
        return f'<Usuario {self.usuario}>'

with app.app_context():
    db.create_all()
    
    # Crear profesor
    if not Usuario.query.filter_by(usuario="henry").first():
        profesor = Usuario(usuario="henry", rol="profesor")
        profesor.establecer_contraseña("password123")
        db.session.add(profesor)
        db.session.commit()
        print("Profesor creado")


@app.route("/login", methods=["GET", "POST"])
def login():
    mensaje = None
    
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")
        
        user = Usuario.query.filter_by(usuario=usuario).first()
        
        if user and user.verificar_contraseña(contraseña):
            session['usuario_id'] = user.id
            session['usuario_nombre'] = user.usuario
            session['rol'] = user.rol
            
            if user.rol == "profesor":
                return redirect(url_for("panel_profesor"))
            else:
                return redirect(url_for("panel_estudiante"))
        else:
            mensaje = "Usuario o contraseña incorrectos."
    
    return render_template("login.html", mensaje=mensaje)





#paso 6 tara 7 


@app.route("/panel-profesor")
def panel_profesor():
    # Verificar que esta logueado y es profesor
    if 'usuario_id' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))
    
    return render_template("panel_profesor.html", usuario=session['usuario_nombre'])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))

# paso 8 tarea 7 

@app.route("/panel-estudiante")
def panel_estudiante():
    if 'usuario_id' not in session or session['rol'] != 'estudiante':
        return redirect(url_for("login"))
    
    tareas = Tarea.query.all()
    return render_template("panel_estudiante.html", usuario=session['usuario_nombre'], tareas=tareas)


# Cuando alguien entra a la direccion principal del sitio, Flask ejecuta
# esta funcion y devuelve la pagina `index.html`.





#paso 1 tarea 8 

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    creada_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.now())

    profesor = db.relationship('Usuario', backref='tareas')

    def __repr__(self):
        return f'<Tarea {self.titulo}>'
    


#paso 2 tarea 8 


with app.app_context():
    db.create_all()
    print("Tabla Tarea creada")

@app.route("/crear-tarea", methods=["GET", "POST"])
def crear_tarea():
    # Solo profesor
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))
    
    if request.method == "POST":
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        fecha_entrega_texto = request.form.get("fecha_entrega")
        
        # Conversión del texto del formulario a un objeto de tipo fecha real
        fecha_entrega_objeto = datetime.strptime(fecha_entrega_texto, '%Y-%m-%d').date()
        
        nueva_tarea = Tarea(
            titulo=titulo,
            descripcion=descripcion,
            fecha_entrega=fecha_entrega_objeto,
            creada_por=session['usuario_id']
        )
        
        db.session.add(nueva_tarea)
        db.session.commit()
        
        return redirect(url_for("mis_tareas"))
    
    return render_template("crear_tarea.html")

@app.route("/mis-tareas")
def mis_tareas():
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))
    
    tareas = Tarea.query.all()
    return render_template("mis_tareas.html", tareas=tareas)

#paso 5 tarea 8

@app.route("/editar-tarea/<int:id>", methods=["GET", "POST"])
def editar_tarea(id):
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))
    
    tarea = Tarea.query.get_or_404(id)
    
    if request.method == "POST":
        tarea.titulo = request.form.get("titulo")
        tarea.descripcion = request.form.get("descripcion")
        
        fecha_entrega_texto = request.form.get("fecha_entrega")
        # Conversión del texto a objeto fecha también al editar
        tarea.fecha_entrega = datetime.strptime(fecha_entrega_texto, '%Y-%m-%d').date()
        
        db.session.commit()
        return redirect(url_for("mis_tareas"))
    
    return render_template("editar_tarea.html", tarea=tarea)

#paso 7 tarea 8

@app.route("/eliminar-tarea/<int:id>")
def eliminar_tarea(id):
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))
    
    tarea = Tarea.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()
    
    return redirect(url_for("mis_tareas"))


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
    # Cambiado para consultar todas las tareas reales de la base de datos
    lista_tareas = Tarea.query.all()    

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
# ponerr seguridad paginas importabtes paso 10 tarea 7    
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))
    
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