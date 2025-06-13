from sqlalchemy import Table, Column, Integer, ForeignKey,String
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from flask import Flask, jsonify,request
from model import db, Author, Book, Review
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify([{
        "id": b.id,
        "title": b.title,
        "publication_year": b.publication_year,
        "author": b.author.name,
        "reviews": [{"rating":r.rating, "comment": r.comment} for r in b.reviews]
 }for b in books], 200
   )
@app.route("/books/<int:id>",methods =['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify({
        "id": book.id,
        "title": book.title,
        "publication_year": book.publication_year,
        "author": book.author.name,
        "reviews": [{"rating": r.ratingc, "comment": r.comment} for r in book.reviews]
    })
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not all(k in data for k in ['title', 'publication_year', 'author_id']):
        return jsonify({'error': 'Missing fields'}), 400
    try:
        book = Book(title=data['title'], publication_year=data['publication_year'], author_id=data['author_id'])
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

if __name__ == '__main__':
    app.run(debug=True)