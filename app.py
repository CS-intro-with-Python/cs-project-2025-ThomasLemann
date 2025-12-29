from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:password@localhost:5432/library"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, db.CheckConstraint("year BETWEEN -2000 AND 2026"))
    genre = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
        }

@app.route("/allbooks", methods=["GET"])
def allbooks():
    books = Book.query.all()

    response = []
    for book in books:
        response.append(book.to_dict())

    return jsonify(response)

@app.route("/allbooks/<string:genre>", methods=["GET"])
def allbooks_genre(genre):
    books = Book.query.filter_by(genre=genre).all()

    response = []
    for book in books:
        if book is not None:
            response.append(book.to_dict())

    return jsonify(response)

@app.route("/books", methods=["POST", "GET"])
def addbook():
    data = request.get_json()

    year = data.get("year", 0)
    genre = data.get("genre", None)

    book = Book(
        title=data["title"],
        author=data["author"],
        year=year,
        genre=genre,
    )

    db.session.add(book)
    db.session.commit()
    db.session.close()

    return {"message": "Book added"}, 201

if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")