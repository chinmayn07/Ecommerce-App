from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

# Sample user data
users = [
    {
        "username": "admin",
        "password": generate_password_hash("admin"),
        "email": "admin@example.com",
        "role": "admin",
    },
    {
        "username": "user1",
        "password": generate_password_hash("user1"),
        "email": "user1@example.com",
        "role": "customer",
    },
    {
        "username": "user2",
        "password": generate_password_hash("user2"),
        "email": "user2@example.com",
        "role": "customer",
    },
]

# Sample product data
products = [
    {
        "name": "Smartphone",
        "description": "A high-end smartphone",
        "price": 699.99,
        "quantity_available": 100,
    },
    {
        "name": "Laptop",
        "description": "A powerful laptop",
        "price": 1299.99,
        "quantity_available": 50,
    },
    {
        "name": "Tablet",
        "description": "A versatile tablet",
        "price": 399.99,
        "quantity_available": 200,
    },
]

# Sample order data
orders = [
    {
        "user_id": "user1",
        "products": [
            {
                "product_id": db.products.find_one({"name": "Smartphone"})["_id"],
                "quantity": 2,
            },
            {
                "product_id": db.products.find_one({"name": "Tablet"})["_id"],
                "quantity": 1,
            },
        ],
        "total_price": (2 * 699.99) + 399.99,
        "order_date": datetime.now(),
    },
    {
        "user_id": "user2",
        "products": [
            {
                "product_id": db.products.find_one({"name": "Laptop"})["_id"],
                "quantity": 1,
            }
        ],
        "total_price": 1299.99,
        "order_date": datetime.now(),
    },
]

# Insert sample data into MongoDB collections
db.users.insert_many(users)
db.products.insert_many(products)
db.orders.insert_many(orders)

print("Sample data inserted successfully.")
