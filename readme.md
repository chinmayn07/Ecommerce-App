# Simple E-Commerce API Documentation

## Introduction

This document outlines the API endpoints and functionality provided by the Simple E-Commerce API. The API is built using OAuth authentication with JWT tokens, allowing users to perform CRUD operations for managing products and orders. Additionally, it supports searching, sorting, and filtering of products. Role-based validation is enforced for certain endpoints, and general error handling is implemented. Caching is utilized for both responses and database queries using Flask-Caching.

## Prerequisites

Before running the application, ensure you have the following packages installed:

- Flask
- Flask-PyMongo
- Flask-JWT-Extended
- Flask-Caching

You can install these dependencies using pip:

```bash
pip install Flask Flask-PyMongo Flask-JWT-Extended Flask-Caching
```

## Populating the Database

Before running the application, you may want to populate the database with sample data. You can do this by running the `load-data.py` script provided in the project. Make sure your MongoDB server is running before running the script.

```bash
python load-data.py
```

This script will populate the database with sample user, product, and order data.

## Running the Application

Once the database is populated, you can run the Flask application using the following command:

```bash
python app.py
```

The application will start running on http://localhost:5000/.

## Authentication

To access protected endpoints, users need to authenticate via the `/login` endpoint and obtain an access token. The access token should be included in the Authorization header of subsequent requests.

### Login

- **URL:** `/login`
- **Method:** POST
- **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "admin"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "<access_token>"
  }
  ```

## Product Endpoints

### Get All Products

- **URL:** `/products`
- **Method:** GET
- **Request Headers:**
  - Authorization: Bearer <access_token>
- **Response Example:**
  ```json
  [
    {
      "name": "Product 1",
      "description": "Description of Product 1",
      "price": 10.99,
      "quantity_available": 100
    },
    {
      "name": "Product 2",
      "description": "Description of Product 2",
      "price": 20.99,
      "quantity_available": 50
    }
  ]
  ```

### Add Product

- **URL:** `/products`
- **Method:** POST
- **Request Headers:**
  - Authorization: Bearer <access_token>
- **Request Body:**
  ```json
  {
    "name": "New Product",
    "description": "Description of New Product",
    "price": 15.99,
    "quantity_available": 200
  }
  ```
- **Response Example:**
  ```json
  {
    "message": "Product added successfully",
    "product_id": "<product_id>"
  }
  ```

## Order Endpoints

### Get User Orders

- **URL:** `/orders`
- **Method:** GET
- **Request Headers:**
  - Authorization: Bearer <access_token>
- **Response Example:**
  ```json
  [
    {
      "user_id": "user123",
      "products": [
        {
          "product_id": "<product_id>",
          "quantity": 2
        },
        {
          "product_id": "<product_id>",
          "quantity": 1
        }
      ],
      "total_price": 45.97,
      "order_date": "2024-02-27T09:30:00"
    }
  ]
  ```

### Place Order

- **URL:** `/orders`
- **Method:** POST
- **Request Headers:**
  - Authorization: Bearer <access_token>
- **Request Body:**
  ```json
  {
    "user_id": "user123",
    "products": [
      {
        "product_id": "<product_id>",
        "quantity": 2
      },
      {
        "product_id": "<product_id>",
        "quantity": 1
      }
    ]
  }
  ```
- **Response Example:**
  ```json
  {
    "message": "Order placed successfully",
    "order_id": "<order_id>"
  }
  ```

## Caching

Both responses and database queries are cached using built-in Flask-Caching. Cached responses are stored for a default timeout of 60 seconds, and cached database queries are cleared as needed.

## Scalability

To achieve scalability, multiple instances of the Flask application can be created and deployed behind a load balancer. This allows for distributing requests across multiple servers, ensuring high availability and improved performance.
