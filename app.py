from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os

# Inicialización de la aplicación y la base de datos
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tableros.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Definir modelo para los tableros y los ítems
class Tablero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', backref='tablero', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tablero_id = db.Column(db.Integer, db.ForeignKey('tablero.id'), nullable=False)

# Inicializar la base de datos
@app.before_request
def crear_tablas():
    db.create_all()

# Ruta principal que renderiza la interfaz
@app.route('/')
def index():
    tableros = Tablero.query.all()
    return render_template('index.html', tableros=tableros)

# Crear un tablero
@socketio.on('crear_tablero')
def crear_tablero(data):
    nuevo_tablero = Tablero(nombre=data['nombre'])
    db.session.add(nuevo_tablero)
    db.session.commit()
    # Emitir actualización de tableros a todos los clientes
    tableros = Tablero.query.all()
    emit('actualizar_tableros', {'tableros': [{'id': t.id, 'nombre': t.nombre, 'items': [{'id': i.id, 'nombre': i.nombre} for i in t.items]} for t in tableros]}, broadcast=True)

# Eliminar un tablero
@socketio.on('eliminar_tablero')
def eliminar_tablero(data):
    tablero = Tablero.query.get(data['id'])
    if tablero:
        db.session.delete(tablero)
        db.session.commit()
        tableros = Tablero.query.all()
        emit('actualizar_tableros', {'tableros': [{'id': t.id, 'nombre': t.nombre, 'items': [{'id': i.id, 'nombre': i.nombre} for i in t.items]} for t in tableros]}, broadcast=True)

# Agregar un ítem a un tablero
@socketio.on('agregar_item')
def agregar_item(data):
    tablero = Tablero.query.get(data['tableroId'])
    if tablero:
        nuevo_item = Item(nombre=data['item'], tablero_id=data['tableroId'])
        db.session.add(nuevo_item)
        db.session.commit()
        # Emitir actualización de tableros a todos los clientes
        tableros = Tablero.query.all()
        emit('actualizar_tableros', {'tableros': [{'id': t.id, 'nombre': t.nombre, 'items': [{'id': i.id, 'nombre': i.nombre} for i in t.items]} for t in tableros]}, broadcast=True)

# Eliminar un ítem de un tablero
@socketio.on('eliminar_item')
def eliminar_item(data):
    item = Item.query.get(data['itemId'])
    if item:
        db.session.delete(item)
        db.session.commit()
        tableros = Tablero.query.all()
        emit('actualizar_tableros', {'tableros': [{'id': t.id, 'nombre': t.nombre, 'items': [{'id': i.id, 'nombre': i.nombre} for i in t.items]} for t in tableros]}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
