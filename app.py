from flask import Flask, render_template, redirect, request

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("")


if __name__ =="__main__":
    app.run(debug=True, port=9999)
