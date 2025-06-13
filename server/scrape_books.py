# scrape_books.py

import requests
from bs4 import BeautifulSoup
from model import db, Author, Book
from flask import current_app, jsonify


BOOKS_SOURCE_URL = "https://example.com/books.html" 

def scrape_and_store_books():
    response = requests.get(BOOKS_SOURCE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    books_added = 0
    authors_added = 0

    for book_item in soup.select(".book"):  
        title = book_item.select_one(".title").text.strip()
        author_name = book_item.select_one(".author").text.strip()
        pub_year = int(book_item.select_one(".year").text.strip())

        
        author = Author.query.filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            authors_added += 1
            db.session.flush()  

    
        book_exists = Book.query.filter_by(title=title, author_id=author.id).first()
        if not book_exists:
            book = Book(title=title, publication_year=pub_year, author_id=author.id)
            db.session.add(book)
            books_added += 1

    db.session.commit()
    return {"books_added": books_added, "authors_added": authors_added}
