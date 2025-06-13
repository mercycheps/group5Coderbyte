from flask import Flask, jsonify, request
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from model import db, Author, Book, Review

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return "<h1>Welcome to the Book Review API</h1>"

@app.route("/books", methods=["GET"])
def get_books():
    books = Book.query.join(Author).all()
    result = []
    for book in books:
        result.append({
            "id": book.id,
            "title": book.title,
            "publication_year": book.publication_year,
            "author": book.author.name,
            "reviews": [
                {"id": r.id, "rating": r.rating, "comment": r.comment}
                for r in book.reviews
            ]
        })
    return jsonify(result), 200

@app.route("/books/<int:id>", methods=["GET"])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify({
        "id": book.id,
        "title": book.title,
        "publication_year": book.publication_year,
        "author": book.author.name,
        "reviews": [{"rating": r.rating, "comment": r.comment} for r in book.reviews]
    })

@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not all(k in data for k in ['title', 'publication_year', 'author_id']):
        return jsonify({'error': 'Missing fields'}), 400
    try:
        book = Book(
            title=data['title'],
            publication_year=data['publication_year'],
            author_id=data['author_id']
        )
        db.session.add(book)
        db.session.commit()
        return jsonify({'message': 'Book created', 'id': book.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Author not found"}), 404

@app.route('/books/<int:id>', methods=['PATCH'])
def update_book(id):
    book = Book.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
    if 'title' in data:
        book.title = data['title']
    if 'publication_year' in data:
        book.publication_year = data['publication_year']
    db.session.commit()
    return jsonify({'message': 'Book updated'})

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})

from scrape_books import scrape_and_store_books

@app.route('/scrape', methods=['GET'])
def scrape_books_route():
    result = scrape_and_store_books()
    return jsonify({
        "message": "Scraping completed",
        "books_added": result["books_added"],
        "authors_added": result["authors_added"]
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
