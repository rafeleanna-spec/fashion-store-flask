from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from datetime import datetime

db = SQLAlchemy()

favoritos = db.Table(
    "favoritos",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("product_id", db.Integer, db.ForeignKey("products.id"))
)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(200), default="sem-imagem.png")
    categoria = db.Column(db.String(100))
    visivel = db.Column(db.Boolean, default=True)
    estoque = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Product {self.nome}>'

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)  
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    favoritos = db.relationship(
    "Product",
    secondary=favoritos,
    backref=db.backref("favoritado_por", lazy="dynamic")
)
    def __repr__(self):
        return f'<User {self.email}>'



class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('CartItem', backref='cart', lazy=True)


class CartItem(db.Model):
    __tablename__ = 'cart_item'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantidade = db.Column(db.Integer, default=1)

    product = db.relationship('Product')

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)  # <<< ESSA LINHA É OBRIGATÓRIA

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref='orders')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(20), default="Pendente")