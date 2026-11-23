# CASE STUDY 5: Smart College Library Management System
# Concepts: classes, objects, inheritance, polymorphism, encapsulation,
# abstraction, exception handling and file handling.

import json
from abc import ABC, abstractmethod

DATA_FILE = "library_data.json"

class LibraryUser(ABC):
    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name

    @abstractmethod
    def user_type(self):
        pass

class Student(LibraryUser):
    def user_type(self):
        return "Student"

class Faculty(LibraryUser):
    def user_type(self):
        return "Faculty"

class Book:
    def __init__(self, book_id, title, author, quantity):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.quantity = quantity

class Library:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.transactions = []
        self.load_data()

    # Encapsulation: data is stored within the Library object.
    def save_data(self):
        data = {
            "books": {
                key: vars(book) for key, book in self.books.items()
            },
            "members": {
                key: {
                    "name": member.name,
                    "type": member.user_type()
                } for key, member in self.members.items()
            },
            "transactions": self.transactions
        }
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except OSError as error:
            print("Could not save library data:", error)

    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            for key, details in data.get("books", {}).items():
                self.books[key] = Book(**details)

            for key, details in data.get("members", {}).items():
                if details["type"] == "Faculty":
                    self.members[key] = Faculty(key, details["name"])
                else:
                    self.members[key] = Student(key, details["name"])

            self.transactions = data.get("transactions", [])
        except FileNotFoundError:
            # First run: the data file will be created when data is saved.
            pass
        except (json.JSONDecodeError, OSError, TypeError, KeyError) as error:
            print("Could not load saved data:", error)

    def add_book(self):
        book_id = input("Book ID: ").strip().upper()
        if not book_id or book_id in self.books:
            print("Book ID is empty or already exists.")
            return
        title = input("Book title: ").strip()
        author = input("Author: ").strip()
        quantity = int(input("Quantity: "))
        if not title or not author or quantity < 0:
            print("Invalid book details.")
            return
        self.books[book_id] = Book(book_id, title, author, quantity)
        self.save_data()
        print("Book added.")

    def update_book(self):
        book_id = input("Enter Book ID to update: ").strip().upper()
        if book_id not in self.books:
            print("Book not found.")
            return
        book = self.books[book_id]
        title = input(f"New title [{book.title}]: ").strip()
        author = input(f"New author [{book.author}]: ").strip()
        quantity = input(f"New quantity [{book.quantity}]: ").strip()
        if title:
            book.title = title
        if author:
            book.author = author
        if quantity:
            new_quantity = int(quantity)
            if new_quantity < 0:
                print("Quantity cannot be negative.")
                return
            book.quantity = new_quantity
        self.save_data()
        print("Book updated.")

    def search_book(self):
        query = input("Enter Book ID or title: ").strip().lower()
        matches = [
            book for book in self.books.values()
            if query == book.book_id.lower() or query in book.title.lower()
        ]
        if not matches:
            print("No matching book found.")
        for book in matches:
            print(f"{book.book_id}: {book.title} by {book.author} "
                  f"(Available: {book.quantity})")

    def remove_book(self):
        book_id = input("Enter Book ID to remove: ").strip().upper()
        if book_id not in self.books:
            print("Book not found.")
            return
        if any(t["book_id"] == book_id and t["status"] == "Issued"
               for t in self.transactions):
            print("Cannot remove a book that is currently issued.")
            return
        del self.books[book_id]
        self.save_data()
        print("Book removed.")

    def register_member(self):
        member_id = input("Member ID: ").strip().upper()
        if not member_id or member_id in self.members:
            print("Member ID is empty or already registered.")
            return
        name = input("Member name: ").strip()
        kind = input("Member type (student/faculty): ").strip().lower()
        if not name or kind not in ("student", "faculty"):
            print("Invalid member details.")
            return
        # Inheritance and polymorphism: Student and Faculty implement user_type().
        if kind == "faculty":
            self.members[member_id] = Faculty(member_id, name)
        else:
            self.members[member_id] = Student(member_id, name)
        self.save_data()
        print("Member registered.")

    def issue_book(self):
        book_id = input("Book ID: ").strip().upper()
        member_id = input("Member ID: ").strip().upper()
        if book_id not in self.books:
            print("Book not found.")
            return
        if member_id not in self.members:
            print("Member not registered.")
            return
        if self.books[book_id].quantity <= 0:
            print("Book is not available.")
            return

        self.books[book_id].quantity -= 1
        self.transactions.append({
            "book_id": book_id,
            "member_id": member_id,
            "status": "Issued"
        })
        self.save_data()
        print("Book issued successfully.")

    def return_book(self):
        book_id = input("Book ID: ").strip().upper()
        member_id = input("Member ID: ").strip().upper()

        for transaction in self.transactions:
            if (transaction["book_id"] == book_id
                    and transaction["member_id"] == member_id
                    and transaction["status"] == "Issued"):
                transaction["status"] = "Returned"
                self.books[book_id].quantity += 1
                self.save_data()
                print("Book returned successfully.")
                return
        print("No matching active issue record found.")

    def show_records(self):
        print("\nBOOKS")
        for book in self.books.values():
            print(f"{book.book_id} | {book.title} | {book.author} | "
                  f"Available: {book.quantity}")

        print("\nMEMBERS")
        for member in self.members.values():
            # Calls the correct subclass implementation: polymorphism.
            print(f"{member.member_id} | {member.name} | {member.user_type()}")

        print("\nTRANSACTIONS")
        for transaction in self.transactions:
            print(transaction)

def main():
    library = Library()

    while True:
        print("\n===== COLLEGE LIBRARY MANAGEMENT =====")
        print("1. Add book")
        print("2. Update book")
        print("3. Search book")
        print("4. Remove book")
        print("5. Register member")
        print("6. Issue book")
        print("7. Return book")
        print("8. Display all records")
        print("9. Exit")

        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                library.add_book()
            elif choice == "2":
                library.update_book()
            elif choice == "3":
                library.search_book()
            elif choice == "4":
                library.remove_book()
            elif choice == "5":
                library.register_member()
            elif choice == "6":
                library.issue_book()
            elif choice == "7":
                library.return_book()
            elif choice == "8":
                library.show_records()
            elif choice == "9":
                library.save_data()
                print("Library data saved. Goodbye!")
                break
            else:
                print("Invalid menu choice.")
        except ValueError:
            print("Invalid number entered. Please try again.")
        except (OSError, KeyError) as error:
            print("An operation could not be completed:", error)

if __name__ == "__main__":
    main()
