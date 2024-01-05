from urllib.parse import quote

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
login = LoginManager(app)

app.secret_key = '56%^&*987^&*(098&*((*&^&*&'
app.config['SQLALCHEMY_DATABASE_URI'] = str.format('mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4'
                                                   % quote ('Tuankiet3172@3'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app=app)
