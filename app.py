from flask import Flask, render_template, request, redirect, flash, session as flask_sesion
from base import create_db, Session
from model import User, Product, Card


app = Flask(__name__)
app.secret_key = "very_secret_key"


@app.get("/")
def index():
    db_session = Session()
    products = db_session.query(Product)
    db_session.close()
    return render_template("index.html", goods=products)


@app.post("/add_to_card")
def add_to_card():
    db_session = Session()

    product_id = request.form.get("product_id")
    user_id = flask_sesion.get("id")

    if not user_id:
        flash("вам потрібно увійти")
        return redirect("/login")

    else:
        product = db_session.query(Product).get(product_id)
        new_card_item = Card(user_id=user_id, product_id=product.id, price=product.price)
        db_session.add(new_card_item)
        db_session.commit()
        db_session.close()
        return redirect("card")



@app.get("/signup")
def registration():
    return render_template("register.html")

@app.post("/signup")
def postregistration():
    session = Session()
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        new_user = User(email, name, password)
        session.add(new_user)
        session.commit()
        session.close()
        return redirect("/")
    except Exception as exception:
        session.rollback()  #session.rollback() — це метод, який використовується в бібліотеці SQLAlchemy для скасування поточної транзакції та повернення до стану, який був до початку цієї транзакції.
        flash(f"Error: {exception}", "сталася помилка")
    finally:
        session.close()
    return render_template("register.html")


@app.get("/login")
def login():
    return render_template("login.html")

@app.post("/login")
def postlogin():
    db_session = Session()

    email = request.form.get('email')
    password = request.form.get('password')

    user = db_session.query(User).filter_by(email=email).first()

    if user and user.check_password(password):
        flask_sesion["id"] = user.id
        flask_sesion["name"] = user.name
        flask_sesion["email"] = user.email
        flash("Вхід виконано успішно!")
        db_session.close()
        return redirect("/")
    else:
        flash("Неправильний email або пароль")
        db_session.close()
        return render_template("login.html")



@app.route("/logout", methods=["GET", "POST"])
def logout():
    flask_sesion.clear()
    flash("Ви вийшли з акаунту.")
    return redirect("/")


@app.get("/add_good")
def add_good():
    return render_template("add_good.html")

@app.post("/add_good")
def postadd_good():
    db_session = Session()

    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    image = request.form.get('image')
    user_id = flask_sesion.get('id')

    new_product = Product(name=name, description=description, price=price, image=image, user_id=user_id)

    if not user_id:
        flash("Увійдіть в профіль")
        return redirect("/login")
    else:
        db_session.add(new_product)
        db_session.commit()
        db_session.close()
    return render_template("add_good.html")


@app.get("/card")
def card():
    db_session = Session()
    user_id = flask_sesion.get('id')

    if not user_id:
        flash("Вам потрібно увійти")
        return redirect('/login')

    else:
        products = db_session.query(Card).filter_by(user_id=user_id).all()
        db_session.close()

    return render_template("card.html", card=products)


if __name__ == "__main__":
    app.run(debug=True, port=9900)
