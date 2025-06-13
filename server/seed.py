from app import app, db
from model import Author, Book, Review
def seed_data():
    # Create authors
    author1 = Author(name="J.K. Rowling")
    author2 = Author(name="George R.R. Martin")

    # Create books
    book1 = Book(title="Harry Potter and the Philosopher's Stone", publication_year=1997, author=author1)
    book2 = Book(title="A Game of Thrones", publication_year=1996, author=author2)

    # Create reviews
    review1 = Review(comment="Amazing book!", rating=5, books=[book1])
    review2 = Review(comment="A thrilling read.", rating=4, books=[book2])

    # Add to session and commit
    db.session.add_all([author1, author2, book1, book2, review1, review2])
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables
        seed_data()      # Seed the database with initial data
        print("Database seeded successfully.")
        app.run(debug=True)