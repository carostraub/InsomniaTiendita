import os
import cloudinary
from flask_cors import cross_origin, CORS
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import db, product_category, Product, Category, Client, Address, Order, OrderDetail, Review, Coupon
from decorators import admin_required

api = Blueprint("api", __name__)

 #### CLIENTE
@api.route('/register', methods=['POST'])
def register():
    email = request.form.get("email")
    password = request.form.get("password_hash")
    name = request.form.get("name")
    subscribe = request.form.get("subscribe")
    
    if not all(email, password, name):
        return jsonify({"error":"Faltan campos obligatorios"}), 400

    if  Client.query.filter_by(email=email).first():
        return jsonify({"error":"Este mail ya esta registrado"}), 400
    

    client =Client(
    email = email,
    name = name,
    subscribe = subscribe
    )
    client.set_password_hash(password)

    try:
    
        db.session.add(client)
        access_token = create_access_token(identity=str(client.id))
        
        return jsonify({
            "message": "Bienvenido a al club de Insomnia",
            "client": client.serialize(),
            "access_token": access_token
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@api.route('/login', methods=['POST'])
def login():
    
    email= request.json.get('email')
    password = request.json.get('password')
    
    if not email:
        return jsonify({ "error": "El email es requerido"}), 400
    if not password:
        return jsonify({"error": "La constraseña es requerida"}), 400
    
    client = Client.query.filter_by(email=email).first()
    if not client:
        return jsonify({"error":"Datos incorrectos"}), 400
    if not client.verify_password(password):
        return jsonify({"error":"Datos incorrectos"}), 400
    
    access_token = create_access_token(identity=str(client.id))
    return jsonify({
        "access_token": access_token,
        "client": client.serialize()  #  Enviar también los datos del usuario
    }), 200



#### PRODUCTOS
@api.route('/products', methods=['POST'])
@admin_required

@api.route('/products/<int:id>', methods= ['PUT', 'DELETE'])
@admin_required

@api.route('/products', methods=['GET'])
def products():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    img = request.files('img')


