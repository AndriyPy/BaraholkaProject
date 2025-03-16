from flask import Flask, render_template, request, redirect, session, flash
from base import create_db, Session, engine
from model import User, Product
from flask_login import login_required


app = Flask(__name__)
app.secret_key = "very_secret_key"

@login_required
@app.get("/")
def index():
    return render_template("index.html")


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
        flash(f"Error: {exception}", "danger")
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
    user = db_session.execute(User.query.filter_by(email=email).statement).scalars().first()  # Пошук юзера за email
    if user and user.check_password(password):
        db_session["user_id"] = user.id
        db_session["name"] = user.name
        db_session["email"] = user.email
        flash("Вхід виконано успішно!", "success")
        return redirect("/")
    else:
        flash("Неправильний email або пароль")
        return render_template("login.html")
    db_session.close()



@app.get("/add_good")
def add_good():
    return render_template("good.html")


@app.post("/add_good")
def postadd_good():
    db_session = Session()

    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    photo = request.form.get('photo')
    new_product = Product(name=name, description=description, price=price, photo=photo)
    try:
        db_session.add(new_product)
        db_session.commit()
        db_session.close()
    except Exception as exception:
        db_session.rollback()  # session.rollback() — це метод, який використовується в бібліотеці SQLAlchemy для скасування поточної транзакції та повернення до стану, який був до початку цієї транзакції.
        flash(f"Error: {exception}", "danger")
    finally:
        db_session.close()


if __name__ == "__main__":
    create_db()
    app.run(debug=True, port=9900)