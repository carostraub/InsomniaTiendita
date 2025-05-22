from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Tabla de asociación para categorías
product_category = db.Table('product_category',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)  # Corregido: descripcton -> description
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    img_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # Relaciones
    order_details = db.relationship('OrderDetail', backref='product', lazy=True)  # Corregido: singular
    reviews = db.relationship('Review', backref='product', lazy=True)
    categories = db.relationship('Category', secondary=product_category, backref='products')  # Corregido: categorias -> categories

class Category(db.Model):
    __tablename__ = 'categories'  # Cambiado a plural para consistencia
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # Relaciones
    orders = db.relationship('Order', backref='client', lazy=True)  # Corregido: backref singular
    addresses = db.relationship('Address', backref='client', lazy=True)  # Corregido: adress -> addresses
    reviews = db.relationship('Review', backref='client', lazy=True)
    coupons = db.relationship('Coupon', backref='client', lazy=True)  # Corregido: cupons -> coupons

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Address(db.Model):  # Corregido: Adress -> Address
    __tablename__ = 'addresses'  # Corregido: adresses -> addresses
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)  # Corregido: clients_id -> client_id
    street = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    comuna = db.Column(db.String(50))
    

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)  # Corregido: clients_id -> client_id
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # Corregido: 'pendiente' -> 'pending'
    shipping_address = db.Column(db.Text, nullable=False)  # Mejor nombre: adress_order -> shipping_address
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)  # Corregido: cupon_id -> coupon_id
    discount_applied = db.Column(db.Float, default=0)  # Corregido: discount_aplied -> discount_applied
    # Relaciones
    details = db.relationship('OrderDetail', backref='order', lazy=True)  # Corregido: orders -> order

class OrderDetail(db.Model):  # Corregido: OrderDetail (antes DetailOrder)
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # Corregido: order -> orders
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Corregido: product -> products
    quantity = db.Column(db.Integer, nullable=False)  # Mejor nombre: amount -> quantity
    unit_price = db.Column(db.Float, nullable=False)  # Mejor nombre: unity_price -> unit_price

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)  # Corregido: client -> clients
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Corregido: product -> products
    rating = db.Column(db.Integer, nullable=False)  # Mejor nombre: calification -> rating
    comment = db.Column(db.Text)  # Corregido: coment -> comment
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Mejor nombre: date -> created_at
    __table_args__ = (
        db.UniqueConstraint('client_id', 'product_id', name='unique_review_per_product'),  # Corregido nombre de constraint
    )

class Coupon(db.Model):  # Corregido: Cupon -> Coupon (inglés)
    __tablename__ = 'coupons'  # Corregido: cupons -> coupons
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # Corregido: codigo -> code
    discount = db.Column(db.Float, nullable=False)
    discount_type = db.Column(db.String(10), default='percentage')  # Corregido: type -> discount_type, 'porcentaje' -> 'percentage'
    valid_from = db.Column(db.DateTime, nullable=False)  # Corregido: since -> valid_from
    valid_to = db.Column(db.DateTime, nullable=False)  # Corregido: until -> valid_to
    max_uses = db.Column(db.Integer, default=1)
    current_uses = db.Column(db.Integer, default=0)  # Corregido: uses -> current_uses
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    # Relaciones
    orders = db.relationship('Order', backref='coupon', lazy=True)  # Corregido: cupon -> coupon