from flask import Flask, render_template, request, redirect, flash, session as flask_sesion, jsonify
from base import create_db, Session
from model import User, Product, Card, joinedload
from datetime import timedelta
import base64


app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=2)
app.secret_key = "very_secret_key"


@app.get("/")
def index():
    search_query = request.args.get('search', '')
    db_session = Session()

    if search_query:
        products = db_session.query(Product).filter(Product.name.ilike(f"%{search_query}%")).all()
    else:
        products = db_session.query(Product).all()

    for product in products:
        if product.image:
            product.image_base64 = base64.b64encode(product.image).decode('utf-8')

    user_id = flask_sesion.get('id')
    user = db_session.query(User).filter_by(id=user_id).first()

    db_session.close()

    return render_template("index.html", goods=products, user=user)


@app.post("/add_to_card")
def add_to_card():
    db_session = Session()

    product_id = request.form.get("product_id")
    user_id = flask_sesion.get("id")

    if not user_id:
        flash("спочатку увійдіть")
        return redirect("/login")

    product = db_session.query(Product).get(product_id)

    if product:
        new_card_item = Card(user_id=user_id, product_id=product.id, price=product.price)
        db_session.add(new_card_item)
        db_session.commit()
        flash("Товар додано в корзину.")

    else:
        flash("Товар не знайдено.")

    db_session.close()
    return redirect("/card")


@app.get("/card")
def card():
    db_session = Session()
    user_id = flask_sesion.get('id')

    if not user_id:
        flash("Вам потрібно увійти")
        return redirect('/login')

    products = db_session.query(Card).options(joinedload(Card.product)).filter_by(user_id=user_id).all()

    for item in products:
        if item.product.image:
            item.product.image_base64 = base64.b64encode(item.product.image).decode('utf-8')

    db_session.close()

    return render_template("card.html", card=products)


@app.get("/signup")
def registration():
    return render_template("register.html")


@app.post("/signup")
def postregistration():
    db_session = Session()
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    flask_sesion.permanent = True

    try:
        new_user = User(email=email, name=name, password=password)
        db_session.add(new_user)
        db_session.commit()

        flask_sesion["id"] = new_user.id
        flask_sesion["name"] = new_user.name
        flask_sesion["email"] = new_user.email

        flash("Реєстрація успішна")
        return redirect("/")

    except Exception as exception:
        db_session.rollback() #— це метод, який використовується для скасування поточної транзакції
        flash(f"Помилка: {exception}")
    finally:
        db_session.close()

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

    flask_sesion.permanent = True

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
    filename = request.files['image']
    image = filename.read()
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


@app.post("/deletegood")
def delete():
    db_session = Session()

    product_id = request.form.get("product_id")
    user_id = flask_sesion.get("id")

    if not user_id:
        flash("спочатку увійдіть")
        return redirect("/login")

    product = db_session.query(Product).get(product_id)

    cart_item = db_session.query(Card).filter_by(user_id=user_id, product_id=product.id).first()

    if cart_item:
        db_session.delete(cart_item)
        db_session.commit()
        flash("Товар видалено з корзини.")
    return redirect('/card')


@app.get("/profile")
def profile():
    db_session = Session()

    user_id = flask_sesion.get('id')
    if not user_id:
        flash("Спочатку увійдіть")
        return redirect("/login")

    user = db_session.query(User).filter_by(id=user_id).first()
    goods = db_session.query(Product).filter_by(user_id=user_id).all()

    for product in goods:
        if product.image:
            product.image_base64 = base64.b64encode(product.image).decode('utf-8')

    db_session.close()
    return render_template("profile.html", user=user, goods=goods)


@app.post("/deleteprofile")
def deleteprofile():
    db_session = Session()

    user_id = flask_sesion.get('id')
    if not user_id:
        flash("Вам потрібно увійти")
        return redirect("/login")

    product_id = request.form.get('product_id')

    db_session.query(Product).filter_by(id=product_id, user_id=user_id).delete()
    db_session.commit()
    db_session.close()

    flash("Товар успішно видалено.")
    return redirect('/profile')


@app.get('/order')
def order():
    return render_template('order.html')


@app.get('/edit_good/<int:id>')
def editgood(id):
    db_session = Session()
    product = db_session.query(Product).filter_by(id=id).first()

    if product and product.image:
        product.image_base64 = base64.b64encode(product.image).decode('utf-8')

    db_session.close()
    return render_template('edit_tovar.html', product=product)


@app.post('/edit_good/<int:id>')
def edittivar(id):
    db_session = Session()
    product = db_session.query(Product).filter_by(id=id).first()

    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    image = request.files.get('image')

    product.name = name
    product.description = description
    product.price = price

    if image:
        product.image = image.read()

    db_session.commit()
    db_session.close()

    flash('Товар відредаговано!')
    return redirect('/profile')


if __name__ == "__main__":
    app.run(debug=True, port=9900)
