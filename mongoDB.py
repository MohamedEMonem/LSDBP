import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MongoDB URI is not set in environment variables.")

client = MongoClient(mongo_uri)
db = client['project']

def get_valid_object_id(prompt):
    while True:
        object_id = input(prompt).strip()
        if ObjectId.is_valid(object_id):
            return ObjectId(object_id)
        print("Invalid ObjectId. Please enter a valid 24-character hex string.")

def get_valid_float(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if allow_empty and not value:
            return None
        try:
            return float(value)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def create_entity(entity_type):
    try:
        if entity_type == 1:
            author = {
                "name": input("Enter author name: ").strip(),
                "nationality": input("Enter author's nationality: ").strip()
            }
            result = db.Authors.insert_one(author)
            print(f"Author created with ID: {result.inserted_id}")

        elif entity_type == 2:
            author_name = input("Enter author name for the book: ").strip()
            author = db.Authors.find_one({"name": author_name})
            if not author:
                print("Author not found!")
                return

            book = {
                "title": input("Enter book title: ").strip(),
                "genre": input("Enter book genre: ").strip(),
                "price": get_valid_float("Enter book price: "),
                "authorId": ObjectId(author["_id"])
            }
            if book["price"] is None:
                print("Book creation canceled due to invalid price.")
                return
            result = db.Books.insert_one(book)
            print(f"Book created with ID: {result.inserted_id}")

        elif entity_type == 3:
            customer = {
                "name": input("Enter customer name: ").strip(),
                "email": input("Enter customer email: ").strip(),
                "address": input("Enter customer address: ").strip()
            }
            result = db.Customers.insert_one(customer)
            print(f"Customer created with ID: {result.inserted_id}")

        elif entity_type == 4:
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
                    books.append(ObjectId(book["_id"]))
                else:
                    print(f"Book '{title.strip()}' not found.")

            if not books:
                print("No valid books found. Order creation canceled.")
                return

            order = {
                "customerId": ObjectId(customer["_id"]),
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

def read_entity(entity_type, read_all=False):
    try:
        if read_all:
            if entity_type == 1:
                authors = db.Authors.find()
                for author in authors:
                    print(f"ID: {author['_id']}, Name: {author['name']}, Nationality: {author['nationality']}")
            elif entity_type == 2:
                books = db.Books.find()
                for book in books:
                    author = db.Authors.find_one({"_id": ObjectId(book["authorId"])})
                    author_name = author["name"] if author else "Unknown"
                    print(f"ID: {book['_id']}, Title: {book['title']}, Genre: {book['genre']}, Price: {book['price']}, Author: {author_name}")
            elif entity_type == 3:
                customers = db.Customers.find()
                for customer in customers:
                    print(f"ID: {customer['_id']}, Name: {customer['name']}, Email: {customer['email']}, Address: {customer['address']}")
            elif entity_type == 4:
                orders = db.Orders.find()
                for order in orders:
                    customer = db.Customers.find_one({"_id": ObjectId(order["customerId"])})
                    books = db.Books.find({"_id": {"$in": [ObjectId(book_id) for book_id in order["books"]]}})
                    book_titles = [book['title'] for book in books]
                    print(f"Order ID: {order['_id']}, Customer: {customer['name'] if customer else 'Unknown'}, "
                          f"Books: {', '.join(book_titles)}, Total: {order['total']}, Date: {order['orderDate']}")
            return

        if entity_type == 1:
            identifier = input("Enter author name or ID: ").strip()
            if ObjectId.is_valid(identifier):
                author = db.Authors.find_one({"_id": ObjectId(identifier)})
            else:
                author = db.Authors.find_one({"name": identifier})
            if author:
                print(f"Name: {author['name']}, Nationality: {author['nationality']}")
            else:
                print("Author not found!")

        elif entity_type == 2:
            identifier = input("Enter book title or ID: ").strip()
            if ObjectId.is_valid(identifier):
                book = db.Books.find_one({"_id": ObjectId(identifier)})
            else:
                book = db.Books.find_one({"title": identifier})
            if book:
                author = db.Authors.find_one({"_id": ObjectId(book["authorId"])})
                author_name = author["name"] if author else "Unknown"
                print(f"Title: {book['title']}, Genre: {book['genre']}, Price: {book['price']}, Author: {author_name}")
            else:
                print("Book not found!")

        elif entity_type == 3:
            identifier = input("Enter customer name or ID: ").strip()
            if ObjectId.is_valid(identifier):
                customer = db.Customers.find_one({"_id": ObjectId(identifier)})
            else:
                customer = db.Customers.find_one({"name": identifier})
            if customer:
                print(f"Name: {customer['name']}, Email: {customer['email']}, Address: {customer['address']}")
            else:
                print("Customer not found!")

        elif entity_type == 4:
            identifier = input("Enter order ID: ").strip()
            if ObjectId.is_valid(identifier):
                order = db.Orders.find_one({"_id": ObjectId(identifier)})
                if order:
                    customer = db.Customers.find_one({"_id": ObjectId(order["customerId"])})
                    books = db.Books.find({"_id": {"$in": [ObjectId(book_id) for book_id in order["books"]]}})
                    book_titles = [book['title'] for book in books]
                    print(f"Order ID: {order['_id']}, Customer: {customer['name'] if customer else 'Unknown'}, "
                          f"Books: {', '.join(book_titles)}, Total: {order['total']}, Date: {order['orderDate']}")
                else:
                    print("Order not found!")
            else:
                print("Invalid Order ID!")
    except Exception as e:
        print(f"Error reading entity: {e}")

def update_entity(entity_type):
    try:
        if entity_type == 1:
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

        elif entity_type == 2:
            book_id = get_valid_object_id("Enter the book ID to update: ")
            book = db.Books.find_one({"_id": ObjectId(book_id)})
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

        elif entity_type == 4:
            order_id = get_valid_object_id("Enter the order ID to update: ")
            order = db.Orders.find_one({"_id": ObjectId(order_id)})
            if not order:
                print("Order not found!")
                return

            total = get_valid_float(f"Enter new total (current: {order['total']}): ", allow_empty=True) or order["total"]
            db.Orders.update_one({"_id": order_id}, {"$set": {"total": total}})
            print(f"Order with ID {order_id} updated.")
    except Exception as e:
        print(f"Error updating entity: {e}")

def delete_entity(entity_type):
    try:
        id_type_map = {1: "Authors", 2: "Books",3: 'Customer', 4: "Orders"}
        entity_id = get_valid_object_id(f"Enter the {id_type_map[entity_type]} ID to delete: ")

        collection = db[id_type_map[entity_type]]
        result = collection.delete_one({"_id": ObjectId(entity_id)})
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
                entity_type = int(input("Enter entity number (1-4): ").strip())
                read_all = input("Read all? (y/n): ").strip().lower() == 'y'
                read_entity(entity_type, read_all)

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
