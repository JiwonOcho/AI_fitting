# -*- coding: utf-8 -*-

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

import accounts
import clothes
import oauth
import recommendation
import tryon
from config import DB_URL

## efficientnet 모델 적재코드 (주석 해제시 clothes의 코드 수정)
# from models.efficientnet.load_model import Load_Model
# lm = Load_Model()
# male_model, female_model = lm.set_model()

app = Flask(__name__)
CORS(app)
app.register_blueprint(oauth.kakao)
app.register_blueprint(accounts.accounts)
app.register_blueprint(recommendation.recommendation)
app.register_blueprint(clothes.clothes)
app.register_blueprint(tryon.tryon)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_POOL_SIZE'] = 100
db = SQLAlchemy(app)
db.init_app(app)


@app.teardown_appcontext
def teardown_db(error):
    db.session.remove()

@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
