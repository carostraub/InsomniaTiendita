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
    password = request.form.get("password")
    name = request.form.get("name")
    subscribe = request.form.get("subscribe", "false").lower() == "true"
    
    if not all([email, password, name]):
        return jsonify({"error":"Faltan campos obligatorios"}), 400

    if  Client.query.filter_by(email=email).first():
        return jsonify({"error":"Este mail ya esta registrado"}), 409
    

    client =Client(
    email = email,
    name = name,
    subscribe = subscribe,
    admin=False
    )
    client.set_password(password)

    try:
    
        db.session.add(client)
        db.session.commit()
        access_token = create_access_token(identity=client.id)
        
        return jsonify({
            "message": "Bienvenido a al club de Insomnia",
            "client": client.serialize(),
            "access_token": access_token
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error en el servidor"}), 500
    
@api.route('/login', methods=['POST'])
def login():
    
    email= request.json.get('email')
    password = request.json.get('password')
    
    if not email or not password:
        return jsonify({ "error": "Email y contraseña requeridos"}), 400
    
    
    client = Client.query.filter_by(email=email).first()
    if not client or not client.check_password(password):
        return jsonify({"error":"Datos incorrectos"}), 401
    
    
    access_token = create_access_token(identity=client.id)
    return jsonify({
        "access_token": access_token,
        "client": client.serialize()
    }), 200



#### PRODUCTOS
@api.route('/products', methods=['POST'])
@admin_required

@api.route('/products/<int:id>', methods= ['PUT'])
@admin_required

@api.route('/products/<int:id>', methods= ['DELETE'])
@admin_required

@api.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.serialize() for product in products]), 200
    
@api.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(product.serialize()), 200

####CATEGORIAS
@api.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([category.serialize() for category in categories]), 200

@api.route('/categories', methods=['POST'])
@admin_required
def new_category():
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({"error":"El nombre es obligatorio"}), 400
    
    if Category.query.filter_by(name=data['name']).first(): 
        return jsonify({"error":"Esta categoria ya existe"}), 409
    
    try:
        category = Category(
            name=data['name'],
            description=data.get('description','')
        )

        db.session.add(category)
        db.session.commit()
        return jsonify({
            "message":"Categoría creada",
            "category":category.serialize()
        }), 201 
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

@api.route('/categories/<int:id>', methods=['PUT'])
@admin_required
def edit_category(id):
    category = Category.query.get(id)

    if not category:
        return jsonify({"error":"Categoría no encontrada"}), 404
    
    data = request.get_json() #Donde guardar los datos nuevos
    if not data:
        return jsonify({"error":"Datos no proporcionados"}), 400
    try:
        if 'name' in data:
            if Category.query.filter(Category.id != Category.name == data['name']).first():
                return jsonify({"error":"Ya existe una categoria con este nombre"}), 409
            category.name=data['name']

            if 'description' in data:
                category.description = data['description']


        db.session.commit()
        return jsonify({
            "message":"Se pudo realizar los cambios exitosamente.",
            "category":category.serialize()
            }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":"No se pudo realizar cambios:"+str(e)}), 500
    

@api.route('/categories/<int:id>', methods=['DELETE'])
@admin_required
def delete_category(id):
    category = Category.query.get(id)

    if not category:
        return jsonify({"error":"Categoría no encontrada"}), 404
    
    try:
        db.session.delete(category)  
        db.session.commit()
        return jsonify({"message": "Categoría eliminada correctamente"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "No se pudo eliminar: " + str(e)}), 500