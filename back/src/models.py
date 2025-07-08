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
    description = db.Column(db.Text)  
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    img = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # Relaciones
    order_details = db.relationship('OrderDetail', backref='product', lazy=True)  
    reviews = db.relationship('Review', backref='product', lazy=True)
    categories = db.relationship('Category', secondary=product_category, backref='products')  

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price else None,  
            "stock": self.stock,
            "image_url": self.img,  
            "categories": [category.serialize() for category in self.categories], #Relación
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Category(db.Model):
    __tablename__ = 'categories'  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    subscribe = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # Relaciones
    orders = db.relationship('Order', backref='client', lazy=True)  
    addresses = db.relationship('Address', backref='client', lazy=True)  
    reviews = db.relationship('Review', backref='client', lazy=True)
    coupons = db.relationship('Coupon', backref='client', lazy=True)  

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def serialize(self):
        return{
            "id":self.id,
            "name":self.name,
            "email":self.email,
            "subscribe":self.subscribe,
            "phone":self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Address(db.Model):  
    __tablename__ = 'addresses' 
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)  
    street = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    comuna = db.Column(db.String(50))
    

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)  
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  
    shipping_address = db.Column(db.Text, nullable=False)  
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True) 
    discount_applied = db.Column(db.Float, default=0)  
    # Relaciones
    details = db.relationship('OrderDetail', backref='order', lazy=True)  


class OrderDetail(db.Model):  
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False) 
    quantity = db.Column(db.Integer, nullable=False) 
    unit_price = db.Column(db.Float, nullable=False)  

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)  
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  
    rating = db.Column(db.Integer, nullable=False) 
    comment = db.Column(db.Text)  
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) 
    __table_args__ = (
        db.UniqueConstraint('client_id', 'product_id', name='unique_review_per_product'),  
    )

class Coupon(db.Model):  
    __tablename__ = 'coupons'  
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  
    discount = db.Column(db.Float, nullable=False)
    discount_type = db.Column(db.String(10), default='percentage')  
    valid_from = db.Column(db.DateTime, nullable=False)  
    valid_to = db.Column(db.DateTime, nullable=False)  
    max_uses = db.Column(db.Integer, default=1)
    current_uses = db.Column(db.Integer, default=0)  
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    # Relaciones
    orders = db.relationship('Order', backref='coupon', lazy=True)  