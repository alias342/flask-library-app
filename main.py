from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import Integer, String, Float
import os

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
app = Flask(__name__)

class Base(DeclarativeBase): 
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/fake-books-collection.db"

db = SQLAlchemy(model_class=Base)
db.init_app(app)
class Booki(db.Model): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[String] = mapped_column(String, unique=True, nullable=False)
    author: Mapped[String] = mapped_column(String, nullable=False)
    rating: Mapped[Float] = mapped_column(Float, nullable=False)

with app.app_context(): 
    db.create_all()

all_books = []

@app.route("/delete")
def delete(): 
    id = int(request.args.get("id"))
    specific_book = db.session.execute(db.select(Booki).where(Booki.id == id)).scalar()
    db.session.delete(specific_book)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/')
def home():
    result = db.session.execute(db.select(Booki).order_by(Booki.title))
    books = result.scalars().all()
    return render_template("index.html", books_list=books)

@app.route('/edit', methods=["POST", "GET"])
def edit(): 
    id = int(request.args.get("book_id"))
    specific_book = db.session.execute(db.select(Booki).where(Booki.id == id)).scalar()
    if request.method == 'POST': 
        specific_book.rating = float(request.form["new_rating"])
        db.session.commit()
        # print(request.form["new_rating"])

    return render_template("edit.html", book_name=specific_book.title, book_rating = specific_book.rating, book_id = specific_book.id)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST": 
        name = request.form["name"]
        author = request.form["author"]
        rating = float(request.form["rating"])
        add_dict = {
            "title": name, 
            "author": author, 
            "rating": rating
        }
        all_books.append(add_dict)
        print(all_books)
        print(add_dict)
        new_book = Booki(title=name, author=author, rating=rating)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html")

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()  # ✅ Closes the session properly after each request

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

