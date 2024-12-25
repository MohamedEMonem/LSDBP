from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime
from dotenv import load_dotenv
import os
from bson import ObjectId

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.project
faker = Faker()

authors_collection = db.Authors
books_collection = db.Books
customers_collection = db.Customers
orders_collection = db.Orders

authors_collection.delete_many({})
books_collection.delete_many({})
customers_collection.delete_many({})
orders_collection.delete_many({})

authors = []
for _ in range(50):
    authors.append({
        "name": faker.name(),
        "nationality": faker.country()
    })
author_ids = authors_collection.insert_many(authors).inserted_ids

books = []
genres = ["Fantasy", "Science Fiction", "Mystery", "Romance", "Non-Fiction", "Historical"]
for _ in range(200):
    books.append({
        "title": faker.text(max_nb_chars=20),
        "genre": random.choice(genres),
        "price": round(random.uniform(10, 50), 2),
        "authorId": ObjectId(random.choice(author_ids))
    })
book_ids = books_collection.insert_many(books).inserted_ids

customers = []
for _ in range(100):
    customers.append({
        "name": faker.name(),
        "email": faker.email(),
        "address": faker.address()
    })
customer_ids = customers_collection.insert_many(customers).inserted_ids

orders = []
for _ in range(300):
    customer_id = ObjectId(random.choice(customer_ids))
    order_books = [ObjectId(book_id) for book_id in random.sample(list(book_ids), k=random.randint(1, 5))]
    total = sum(books_collection.find_one({"_id": book_id})["price"] for book_id in order_books)
    orders.append({
        "customerId": customer_id,
        "orderDate": faker.date_time_between(start_date="-1y", end_date="now"),
        "books": order_books,
        "total": round(total, 2)
    })
orders_collection.insert_many(orders)

print("Data insertion completed successfully.")
