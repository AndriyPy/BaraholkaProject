from flask import Flask, render_template, request, redirect
from model import User, Good, db

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")



@app.get("/sign-up")
def registration():
    return render_template("register.html")

@app.post("/sign-up")
def registration():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    db.session.close()
    return render_template('register.html')



if __name__ == "__main__":
    app.run(debug=True, port=9900)