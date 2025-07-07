import os
from flask_cors import cross_origin, CORS
from flask import Blueprint, request, jsonify
from models import db, product_category, Product, Category, Client, Address, Order, OrderDetail, Review, Coupon

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
    client.set_password(password)

    try:
    
        db.session.add(client)
        db.session.commit()
        return jsonify({"msg":"Usuario registrado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#### PRODUCTOS
@api.route('/products', methods=['GET'])
def products():
    name = request.json