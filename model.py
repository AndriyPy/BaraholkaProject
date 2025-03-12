from flask_sqlalchemy import SQLAlchemy
from app import app
import bcrypt


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.baraholka'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(500), nullable=True)
    goods = db.relationship('Goods', backref='owner', lazy=True)#зв'язок товару та юзера

    def __init__(self, email, name, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

class Good(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) #зв'язок товару та юзера


with app.app_context():
    db.create_all()
    print("База даних створена!")