from app import app, render_template, jsonify






@app.get("/payment")
def payment():
    return render_template("payment.html")

@app.post("/payment")
def postpayment():
    return jsonify({'paymentID':'PAYMENTID'})