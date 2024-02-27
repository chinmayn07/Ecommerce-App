from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from werkzeug.security import check_password_hash
import datetime
from functools import wraps
from bson.objectid import ObjectId
from flask_caching import Cache

app = Flask(__name__)

MONGO_URI = "mongodb://localhost:27017/ecommerce"
JWT_SECRET_KEY = "secret-key"
CACHE_TIMEOUT = 60

app.config["MONGO_URI"] = MONGO_URI
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["CACHE_TYPE"] = "simple"
app.config["CACHE_DEFAULT_TIMEOUT"] = CACHE_TIMEOUT

user_data = {
    "username": "admin",
    "password": "admin",
    "email": "admin@example.com",
    "role": "admin",
}

mongo = PyMongo(app)
jwt = JWTManager(app)
cache = Cache(app)


# Error handler
@app.errorhandler(Exception)
def handle_error(error):
    message = getattr(error, "message", "An error occurred")
    status_code = getattr(error, "status_code", 500)
    return jsonify({"message": message}), status_code


# Authorization decorator for role check
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        if current_user.get("role") != "admin":
            return jsonify(message="Admins only!"), 403
        return f(*args, **kwargs)

    return decorated_function


# Authentication endpoint
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = mongo.db.users.find_one({"username": username})

    if user and check_password_hash(user["password"], password):
        access_token = create_access_token(
            identity={"username": user["username"], "role": user["role"]}
        )
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message="Invalid credentials"), 401


# Products endpoints
@app.route("/products", methods=["GET"])
@cache.cached(timeout=60)
def get_products():
    products = list(mongo.db.products.find({}, {"_id": 0}))
    return jsonify(products), 200


@app.route("/products", methods=["POST"])
@jwt_required()
@admin_required()
def add_product():
    data = request.get_json()
    product_id = mongo.db.products.insert_one(data).inserted_id
    cache.clear()
    return (
        jsonify(message="Product added successfully", product_id=str(product_id)),
        201,
    )


@app.route("/products/<product_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_product(product_id):
    data = request.get_json()

    result = mongo.db.products.update_one({"_id": ObjectId(product_id)}, {"$set": data})

    if result.modified_count:
        return jsonify(message="Product updated successfully"), 200
    else:
        return jsonify(message="Product not found"), 404


@app.route("/products/<product_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_product(product_id):
    result = mongo.db.products.delete_one({"_id": ObjectId(product_id)})

    if result.deleted_count:
        return jsonify(message="Product deleted successfully"), 200
    else:
        return jsonify(message="Product not found"), 404


# Endpoint for searching products
@app.route("/products/search", methods=["GET"])
def search_products():
    query = request.args.get("query")
    # Perform text search using MongoDB's $text operator
    products = list(mongo.db.products.find({"$text": {"$search": query}}))
    return jsonify(products), 200


# Endpoint for filtering products
@app.route("/products/filter", methods=["GET"])
def filter_products():
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    filter_query = {}
    if min_price:
        filter_query["price"] = {"$gte": float(min_price)}
    if max_price:
        filter_query.setdefault("price", {}).update({"$lte": float(max_price)})

    products = list(mongo.db.products.find(filter_query))
    return jsonify(products), 200


# Endpoint for sorting products
@app.route("/products/sort", methods=["GET"])
def sort_products():
    sort_field = request.args.get("sort_field")
    sort_order = int(request.args.get("sort_order", 1))  # Default ascending order
    sort_query = [(sort_field, sort_order)]
    # Execute sort query
    products = list(mongo.db.products.find().sort(sort_query))
    return jsonify(products), 200


# Orders endpoints
@app.route("/orders", methods=["GET"])
@jwt_required()
def get_orders():
    current_user = get_jwt_identity()
    user_id = current_user.get("username")
    orders = list(mongo.db.orders.find({"user_id": user_id}, {"_id": 0}))
    return jsonify(orders), 200


@app.route("/orders", methods=["POST"])
@jwt_required()
def place_order():
    data = request.get_json()
    total_price = 0
    for item in data["products"]:
        product = mongo.db.products.find_one({"_id": item["product_id"]})
        if not product:
            raise Exception("Product not found", 404)
        total_price += product["price"] * item["quantity"]

    order_date = datetime.datetime.now()
    order = {
        "user_id": data["user_id"],
        "products": data["products"],
        "total_price": total_price,
        "order_date": order_date,
    }

    order_id = mongo.db.orders.insert_one(order).inserted_id
    return jsonify(message="Order placed successfully", order_id=str(order_id)), 201


if __name__ == "__main__":
    app.run(port=5000)
