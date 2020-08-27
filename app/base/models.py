import time
from bcrypt import gensalt, hashpw
from flask_login import UserMixin
from flask import Flask, abort, request, jsonify, g, url_for
from sqlalchemy import (Binary, Boolean, Column, DateTime, ForeignKey, Integer, Date,
                        String, Float, func)
from app import db, login_manager, auth
from flask_httpauth import HTTPBasicAuth
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import datetime

ACCESS = {
    'guest': 0,
    'user': 1,
    'billing': 2,
    'admin': 3
}


class User(db.Model, UserMixin):
    """
    User table entity
    """

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)
    password_hash = Column(String(64))
    access = Column(String)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            if property == 'password':
                value = hashpw(value.encode('utf8'), gensalt())
            # if property == 'password_hash':
            #     value = hashpw(value.encode('utf8'), gensalt())
            if property == 'access':
                if value == '':
                    value = 'operator'
            setattr(self, property, value)

    def is_admin(self):
        return self.access == ACCESS['admin']

    def allowed(self, access_level):
        return self.access >= access_level

    def __repr__(self):
        return str(self.username)

    def get_hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        c = Config()
        jwt_encode_str = jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            c.SECRET_KEY, algorithm='HS256')
        return jwt_encode_str

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, Config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])

    @staticmethod
    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            c = Config()
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                c.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            c = Config()
            payload = jwt.decode(auth_token, c.SECRET_KEY)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


@auth.verify_password
def verify_password_user_entity(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@login_manager.user_loader
def user_loader(param_id):
    return User.query.filter_by(id=param_id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None


class WelcomeModel:
    def __init__(self):
        self.message = "Hello World!"


class PodCast(db.Model, UserMixin):
    """
    PodCast table
    """

    __tablename__ = 'PodCast'

    id = Column(Integer, primary_key=True)
    artistName = Column(String, unique=False)
    podCastId = Column(Integer, unique=False)
    releaseDate = Column(Date, unique=False)
    name = Column(String, unique=False)
    kind = Column(String, unique=False)
    copyright = Column(String, unique=False)
    artistId = Column(Integer, unique=False)
    contentAdvisoryRating = Column(String, unique=False)
    artistUrl = Column(String, unique=False)
    artworkUrl100 = Column(String, unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value)


class Genre(db.Model, UserMixin):
    """
        Genre table
    """

    __tablename__ = 'Genre'

    id = Column(Integer, primary_key=True)
    genreId = Column(Integer, unique=False)
    name = Column(String, unique=False)
    url = Column(String, unique=False)
    podCast = Column(Integer, ForeignKey('PodCast.id'))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value)
