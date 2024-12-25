import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve MongoDB connection string from environment variable
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MongoDB URI is not set in environment variables.")

client = MongoClient(mongo_uri)
db = client['project']

def get_valid_object_id(prompt):
    """
    Validates and retrieves an ObjectId from user input.
    """
    while True:
        object_id = input(prompt).strip()
        if ObjectId.is_valid(object_id):
            return ObjectId(object_id)
        print("Invalid ObjectId. Please enter a valid 24-character hex string.")

def get_valid_float(prompt, allow_empty=False):
    """
    Validates and retrieves a float value from user input.
    """
    while True:
        value = input(prompt).strip()
        if allow_empty and not value:
            return None
        try:
            return float(value)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def create_entity(entity_type):
    """
    Handles creation of entities: Authors, Books, Customers, and Orders.
    """
    try:
        if entity_type == 1:  # Authors
            author = {
                "name": input("Enter author name: ").strip(),
                "nationality": input("Enter author's nationality: ").strip()
            }
            result = db.Authors.insert_one(author)
            print(f"Author created with ID: {result.inserted_id}")

        elif entity_type == 2:  # Books
            author_name = input("Enter author name for the book: ").strip()
            author = db.Authors.find_one({"name": author_name})
            if not author:
                print("Author not found!")
                return

            book = {
                "title": input("Enter book title: ").strip(),
                "genre": input("Enter book genre: ").strip(),
                "price": get_valid_float("Enter book price: "),
                "authorId": author["_id"]
            }
            if book["price"] is None:
                print("Book creation canceled due to invalid price.")
                return
            result = db.Books.insert_one(book)
            print(f"Book created with ID: {result.inserted_id}")

        elif entity_type == 3:  # Customers
            customer = {
                "name": input("Enter customer name: ").strip(),
                "email": input("Enter customer email: ").strip(),
                "address": input("Enter customer address: ").strip()
            }
            result = db.Customers.insert_one(customer)
            print(f"Customer created with ID: {result.inserted_id}")

        elif entity_type == 4:  # Orders
            customer_name = input("Enter customer name for the order: ").strip()
            customer = db.Customers.find_one({"name": customer_name})
            if not customer:
                print("Customer not found!")
                return

            books_titles = input("Enter the book titles (comma separated): ").split(',')
            books = []
            for title in books_titles:
                book = db.Books.find_one({"title": title.strip()})
                if book:
                    books.append(book["_id"])
                else:
                    print(f"Book '{title.strip()}' not found.")

            if not books:
                print("No valid books found. Order creation canceled.")
                return

            order = {
                "customerId": customer["_id"],
                "orderDate": input("Enter order date (YYYY-MM-DD): ").strip(),
                "books": books,
                "total": get_valid_float("Enter total amount: ")
            }
            if order["total"] is None:
                print("Order creation canceled due to invalid total amount.")
                return
            result = db.Orders.insert_one(order)
            print(f"Order created with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error creating entity: {e}")

def read_entity(entity_type):
    """
    Handles reading of entities: Authors, Books, Customers, and Orders.
    """
    try:
        if entity_type == 1:  # Authors
            for author in db.Authors.find():
                print(f"Name: {author['name']}, Nationality: {author['nationality']}")

        elif entity_type == 2:  # Books
            for book in db.Books.find():
                author = db.Authors.find_one({"_id": book["authorId"]})
                author_name = author["name"] if author else "Unknown"
                print(f"Title: {book['title']}, Genre: {book['genre']}, Price: {book['price']}, Author: {author_name}")

        elif entity_type == 3:  # Customers
            for customer in db.Customers.find():
                print(f"Name: {customer['name']}, Email: {customer['email']}, Address: {customer['address']}")

        elif entity_type == 4:  # Orders
            for order in db.Orders.find():
                customer = db.Customers.find_one({"_id": order["customerId"]})
                books = db.Books.find({"_id": {"$in": order["books"]}})
                book_titles = [book['title'] for book in books]
                print(f"Order ID: {order['_id']}, Customer: {customer['name'] if customer else 'Unknown'}, "
                      f"Books: {', '.join(book_titles)}, Total: {order['total']}, Date: {order['orderDate']}")
    except Exception as e:
        print(f"Error reading entity: {e}")

def update_entity(entity_type):
    """
    Handles updates for Authors, Books, and Orders.
    """
    try:
        if entity_type == 1:  # Authors
            author_id = get_valid_object_id("Enter the author ID to update: ")
            author = db.Authors.find_one({"_id": author_id})
            if not author:
                print("Author not found!")
                return

            update_fields = {
                "name": input(f"Enter new name (current: {author['name']}): ").strip() or author["name"],
                "nationality": input(f"Enter new nationality (current: {author['nationality']}): ").strip() or author["nationality"]
            }
            db.Authors.update_one({"_id": author_id}, {"$set": update_fields})
            print(f"Author with ID {author_id} updated.")

        elif entity_type == 2:  # Books
            book_id = get_valid_object_id("Enter the book ID to update: ")
            book = db.Books.find_one({"_id": book_id})
            if not book:
                print("Book not found!")
                return

            update_fields = {
                "title": input(f"Enter new title (current: {book['title']}): ").strip() or book["title"],
                "genre": input(f"Enter new genre (current: {book['genre']}): ").strip() or book["genre"],
                "price": get_valid_float(f"Enter new price (current: {book['price']}): ", allow_empty=True) or book["price"]
            }
            db.Books.update_one({"_id": book_id}, {"$set": update_fields})
            print(f"Book with ID {book_id} updated.")

        elif entity_type == 4:  # Orders
            order_id = get_valid_object_id("Enter the order ID to update: ")
            order = db.Orders.find_one({"_id": order_id})
            if not order:
                print("Order not found!")
                return

            total = get_valid_float(f"Enter new total (current: {order['total']}): ", allow_empty=True) or order["total"]
            db.Orders.update_one({"_id": order_id}, {"$set": {"total": total}})
            print(f"Order with ID {order_id} updated.")
    except Exception as e:
        print(f"Error updating entity: {e}")

def delete_entity(entity_type):
    """
    Handles deletion of Authors, Books, and Orders.
    """
    try:
        id_type_map = {1: "Authors", 2: "Books", 4: "Orders"}
        entity_id = get_valid_object_id(f"Enter the {id_type_map[entity_type]} ID to delete: ")

        collection = db[id_type_map[entity_type]]
        result = collection.delete_one({"_id": entity_id})
        if result.deleted_count:
            print(f"{id_type_map[entity_type]} with ID {entity_id} deleted.")
        else:
            print(f"{id_type_map[entity_type]} not found!")
    except Exception as e:
        print(f"Error deleting entity: {e}")

def menu():
    while True:
        print("\n--- Bookstore CRUD Operations ---")
        print("1. Create\n2. Read\n3. Update\n4. Delete\n5. Exit")
        choice = input("Choose an operation (1-5): ").strip()

        try:
            if choice == "1":
                print("\n--- Choose Entity to Create ---\n1. Authors\n2. Books\n3. Customers\n4. Orders")
                create_entity(int(input("Enter entity number (1-4): ").strip()))

            elif choice == "2":
                print("\n--- Choose Entity to Read ---\n1. Authors\n2. Books\n3. Customers\n4. Orders")
                read_entity(int(input("Enter entity number (1-4): ").strip()))

            elif choice == "3":
                print("\n--- Choose Entity to Update ---\n1. Authors\n2. Books\n4. Orders")
                update_entity(int(input("Enter entity number (1, 2, 4): ").strip()))

            elif choice == "4":
                print("\n--- Choose Entity to Delete ---\n1. Authors\n2. Books\n4. Orders")
                delete_entity(int(input("Enter entity number (1, 2, 4): ").strip()))

            elif choice == "5":
                print("Exiting...")
                break

            else:
                print("Invalid choice! Please try again.")
        except ValueError:
            print("Invalid input! Please enter a number corresponding to the options.")

if __name__ == "__main__":
    menu()
