from datetime import datetime, timezone  # Cambio clave aquí
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Tabla de asociación para categorías (opcional)
producto_categoria = db.Table('producto_categoria',
    db.Column('producto_id', db.Integer, db.ForeignKey('producto.id')),
    db.Column('categoria_id', db.Integer, db.ForeignKey('categoria.id'))
)

class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    imagen_url = db.Column(db.String(200))
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # ¡Corregido!
    # Relaciones
    detalles_pedido = db.relationship('DetallePedido', backref='producto', lazy=True)
    reseñas = db.relationship('Reseña', backref='producto', lazy=True)
    categorias = db.relationship('Categoria', secondary=producto_categoria, backref='productos')

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # ¡Corregido!
    # Relaciones
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    direcciones = db.relationship('Direccion', backref='cliente', lazy=True)
    reseñas = db.relationship('Reseña', backref='cliente', lazy=True)
    cupones = db.relationship('Cupon', backref='cliente', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Direccion(db.Model):
    __tablename__ = 'direccion'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    calle = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50))
    codigo_postal = db.Column(db.String(10), nullable=False)
    pais = db.Column(db.String(50), default='México')

class Pedido(db.Model):
    __tablename__ = 'pedido'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)  # ¡Corregido!
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    direccion_envio = db.Column(db.Text, nullable=False)
    cupon_id = db.Column(db.Integer, db.ForeignKey('cupon.id'), nullable=True)
    descuento_aplicado = db.Column(db.Float, default=0)
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

class Reseña(db.Model):
    __tablename__ = 'reseña'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # ¡Corregido!
    __table_args__ = (
        db.UniqueConstraint('cliente_id', 'producto_id', name='una_reseña_por_producto'),
    )

class Cupon(db.Model):
    __tablename__ = 'cupon'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    descuento = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(10), default='porcentaje')
    valido_desde = db.Column(db.DateTime, nullable=False)
    valido_hasta = db.Column(db.DateTime, nullable=False)
    max_usos = db.Column(db.Integer, default=1)
    usos_actuales = db.Column(db.Integer, default=0)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)
    pedidos = db.relationship('Pedido', backref='cupon', lazy=True)