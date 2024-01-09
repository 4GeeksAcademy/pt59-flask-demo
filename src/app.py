"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from typing import List, Union
from flask import Flask, request, jsonify, url_for

from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

class Calc:
    display: float
    register: float
    operation: Union[str, None]
    tape: List[dict]

    def __init__(self) -> None:
        self.display = 0.0
        self.register = 0.0
        self.operation = None
        self.tape = []

    def serialize(self):
        return {
            "display": self.display,
            "register": self.register,
            "operation": self.operation,
            "tape": self.tape,
        }
    
    def perform_operation(self):
        match(self.operation):
            case "addition":
                result = self.register + self.display
                self.tape.append({
                    "display": self.display,
                    "register": self.register,
                    "operation": self.operation,
                    "result": result
                })
                self.display = result
                self.register = 0.0
            case _:
                return
        self.operation = None


calc = Calc()

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route("/helloworld", methods=["GET"])
def hello_world():
    return jsonify(hello="world"), 418


# Calculator app

@app.route("/calculator", methods=["GET"])
def get_calc():
    return jsonify(calc.serialize())


@app.route("/calculator", methods=["PUT"])
def change_calc_value():
    data = request.json
    # This is minor magic
    for k,v in data.items():
        setattr(calc, k, v)
    return jsonify(calc.serialize())


@app.route("/calculator", methods=["POST"])
def complete_op():
    calc.perform_operation()
    return jsonify(calc.serialize())


@app.route("/calculator", methods=["DELETE"])
def ce():
    calc = Calc()
    return jsonify(calc.serialize())


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
