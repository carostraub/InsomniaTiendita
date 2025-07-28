import os
import cloudinary.uploader
from flask_cors import cross_origin, CORS
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import db, product_category, Product, Category, Client, Address, Order, OrderDetail, Review, Coupon
from decorators import admin_required
from config import allowed_files, obtener_public_id

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
def new_product():

    if 'name' not in request.form or not request.form['name']:
        return jsonify({"error":"El nombre es obligatorio"}), 400
    if  'description' not in request.form or not request.form['description'] :
        return jsonify({"error":"La descripción es obligatoria"}), 400
    if 'price' not in request.form or not request.form['price']:
        return jsonify({"error":"El precio es obligatorio"}), 400
    
    image_url=None
    if 'photo' in request.files:
        image=request.files['photo']
     
    if image.filename == "":
        return jsonify({"error":"Nombre del archivo vacío"}), 400
    if not allowed_files(image.filename):
        return jsonify({"error":"Formato de archivo no permitido"}), 400
    
    try: #para subir la imagen a cloudinary
        upload_result = cloudinary.uploader.upload(image, folder="products")
        image_url=upload_result['secure_url']

    except Exception as e:
            return jsonify({"error": f"Error al subir imagen: {str(e)}"}), 500
    try:
        new_product = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            img=image_url
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({
            "msg":"Producto creado",
            "product":new_product.serialize()
            }), 201
    except ValueError:
        db.session.rollback()
        return jsonify({"error":"Precio o stock inválido"}), 400
    except Exception as e:  # Otros errores de BD
        db.session.rollback()
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500

    




@api.route('/products/<int:id>', methods= ['PUT'])
@admin_required
def edit_product(id):
    product = Product.query.get(id)

    if not product:
        return jsonify({"error":"Producto no encontrado"}), 404
    
    data =request.get_json()
    if not data:
        return jsonify({"error":"Datos no proporcionados"}), 400
    try:
        if 'name' in data and data['name'] != product.name:
            existing = Product.query.filter(Product.id != id,
                                             Product.name == data['name']).first()
            if existing:
                return({"error":"Ya existe un producto con este nombre"}),409
            product.name =data['name']

            if 'description' in data:
                product.description = data['description']

            if 'price' in data:
                try:
                    product.price = float(data['price'])
                except ValueError:
                    return jsonify({"error":"El precio debe ser un número válido"}), 400

            if 'image_file' in request.files:
                file = request.files['image_file']
                upload_result = cloudinary.uploader.upload(file)
                product.img = upload_result['secure_url']

        db.session.commit()
        return jsonify({
            "message":"Se realizon los cambios",
            "product": product.serialize()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":"No se pudieron realizar los cambios:"+str(e)}), 500

@api.route('/products/<int:id>', methods= ['DELETE'])
@admin_required
def delete_product(id):
    product = Product.query.get(id)

    if not product:
        return jsonify({"error":"No se encontro el producto"}), 404
    
    try:
        if product.img:
            public_id = obtener_public_id(product.img)
            cloudinary.uploader.destroy(public_id)

        db.session.delete(product)
        db.session.commit()
        return jsonify({"msg":"Producto eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":"No se pudo eliminar producto:" + str(e)}),500

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
            existing = Category.query.filter(Category.id != id,
                                     Category.name == data['name']
                                     ).first()
            if existing:
                return jsonify({"error":"Ya existe una categoria con este nombre"}), 409
            category.name = data['name']

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



        #####ORDERS
@api.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()

    if not data or 'items' not in data or data['items']:
        return jsonify({"error":"No hay productos en la compra"}), 400
    new_order = Order(
        client_id=data.get('client.id'),
        total= data.get('total'),
        shipping_address =data['shipping_address'],
        coupon_id =data.get('coupon_id'),
        discount_applied= data.get('discount_applied'),
        status ='pending',
        payment_method ='transferencia'
    )
    db.session.add(new_order)
    db.session.commit
    
    for item in data['items']:
        product= Product.query.get(item['product_id'])
        if not product or product.stock < item('quantity'):
            db.session.rollback()
            return jsonify({"error":f"Producto {item['product_id']} no disponible"}), 400
        OrderDetail.create(
            order_id=new_order.id,
            product_id= product.id,
            quantity=item['quantity'],
            unit_price= product.current_price,
        )
    new_order.calculate_total()
    db.session.commit()

    return jsonify({
        "message": "¡Pedido creado! Confirma el pago por transferencia y envía el comprobante.",
        "order": new_order.serialize(),
        
    }), 201   

@api.route('/orders/<int:id>/status', methods=['PUT'])
@admin_required
def update_order_status(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({"error": "Orden no encontrada"}), 404

    new_status = request.json.get('status')
    if new_status not in ['pending', 'paid', 'shipped', 'cancelled']:
        return jsonify({"error": "Estado inválido"}), 400

    order.status = new_status
    db.session.commit()

    return jsonify({"message": f"Estado actualizado a '{new_status}'"}), 200

@api.route('/admin/orders', methods=['GET'])
@admin_required
def get_all_orders():
    orders = Order.query.all()
    return jsonify([order.serialize() for order in orders]), 200

