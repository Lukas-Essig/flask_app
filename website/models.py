from datetime import datetime
from . import db, app
from flask_login import UserMixin, current_user
from sqlalchemy.sql import func
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class Host(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable = False)
    country = db.Column(db.String(30), nullable = False)
    street = db.Column(db.String(50), nullable = False)
    housenumber = db.Column(db.String(6), nullable = False)
    city = db.Column(db.String(30), nullable = False)
    state = db.Column(db.String(30), nullable = False)
    zipcode = db.Column(db.String(10), nullable = False)
    maximumpeople = db.Column(db.String(2), nullable = False)
    h_tent = db.Column(db.String(6))
    h_car = db.Column(db.String(6))
    h_cartrailer = db.Column(db.String(6))
    h_motorhome = db.Column(db.String(6))
    h_toilet = db.Column(db.String(20))
    h_shower = db.Column(db.String(20))
    h_washingmachine = db.Column(db.String(20))
    h_water = db.Column(db.String(6))
    h_trash = db.Column(db.String(6))
    h_note = db.Column(db.String(5000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    on_off = db.Column(db.String(6), default='On')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

class Traveller(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    t_tent = db.Column(db.String(6))
    t_car = db.Column(db.String(6))
    t_cartrailer = db.Column(db.String(6))
    t_motorhome = db.Column(db.String(6))
    numberofpeople = db.Column(db.String(2), nullable = False)
    t_toilet = db.Column(db.String(20))
    t_shower = db.Column(db.String(20))
    t_washingmachine = db.Column(db.String(20))
    t_water = db.Column(db.String(6))
    t_trash = db.Column(db.String(6))
    t_note = db.Column(db.String(5000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable = False)
    surname = db.Column(db.String(50), nullable = False)
    age = db.Column(db.String(3))
    gender = db.Column(db.String(20))
    countryresidence = db.Column(db.String(30))
    language1 = db.Column(db.String(30), nullable = False)
    language2 = db.Column(db.String(30), nullable = False)
    language3 = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(50), unique=True, nullable = False)
    phonenumber = db.Column(db.String(20), nullable = False)
    password = db.Column(db.String(60), nullable = False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    image_file = db.Column(db.String(20), nullable = False, default='default.jpeg')
    host = db.relationship('Host', backref='provider', lazy=True)
    traveller = db.relationship('Traveller', backref='passenger', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)