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


class Recipe:
    id: int = 0
    title: str
    ingredients: List[str]
    prep_time: int
    cook_time: int
    steps: List[str]

    def __init__(
            self,
            title="",
            ingredients=[],
            prep_time=0,
            cook_time=0,
            steps=[],
            id=0,
    ) -> None:
        self.id = id
        self.title = title
        self.ingredients = ingredients
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.steps = steps

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "ingredients": self.ingredients,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "steps": self.steps,
        }


recipes = [
    Recipe(
        id=1,
        title="Chocolate Chip Cookies",
        ingredients=[
            "1/2 c. chocolate chips",
            "3 1/2 c. all purpose flour",
            "1 stick soft butter",
            "2 large eggs",
            "1/2 tsp. baking powder",
            "1/2 c. white sugar",
            "1/2 c. brown sugar",
            "1 tsp vanilla extract",
            "1/2 tsp. salt",
        ],
        prep_time=20,
        cook_time=15,
        steps=[]
    ),
    Recipe(
        id=2,
        title="Fritatta",
        ingredients=[
            "eggs",
            "cheese",
            "asst. diced veggies",
            "milk",
        ]
    )
]


# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route("/recipes", methods=["GET"])
def get_all_recipes():
    json_recipes = [recipe.serialize() for recipe in recipes]
    return jsonify(recipes=json_recipes)


@app.route("/recipes/<int:id>", methods=["GET"])
def get_single_recipe(id: int):
    selected_recipe = list(filter(
        # (recipe) => recipe.id === id
        lambda recipe: recipe.id == id,
        recipes
    ))
    if not len(selected_recipe):
        return jsonify(message="Recipe not found"), 404
    return jsonify(selected_recipe.pop().serialize())


@app.route("/recipes/<int:id>", methods=["PUT", "PATCH"])
def update_recipe(id: int):
    selected_recipe = list(filter(
        # (recipe) => recipe.id === id
        lambda x: x[1].id == id,
        [(idx, rec) for idx, rec in enumerate(recipes)]
    ))
    
    if not len(selected_recipe):
        return jsonify(message="Recipe not found"), 404
    
    idx, recipe = selected_recipe.pop()
    data = request.get_json()
    for k, v in data.items():
        setattr(recipe, k, v)
    recipes[idx] = recipe
    return jsonify(recipe.serialize())


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
