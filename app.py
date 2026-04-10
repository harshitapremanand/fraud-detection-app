from flask import Flask, render_template, request, redirect, session, url_for
import joblib
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "secret123"

model = joblib.load("model.pkl")

users = {"admin": "1234"}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users[username] = password
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/login")

    result = None
    prob = None
    risk_level = "-"

    if request.method == "POST":
        amount = request.form["amount"]
        time = request.form["time"]
        location = request.form["location"]

        try:
            features = [float(amount), float(time), float(location)]
        except:
            features = [random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)]

        raw_prob = model.predict_proba([features])[0][1]
        display_prob = min(raw_prob * 20, 1.0)
        prob = round(display_prob * 100, 2)

        # Risk classification
        if prob < 30:
            risk_level = "Low"
            result = f"Safe ({prob}%)"
        elif prob < 60:
            risk_level = "Medium"
            result = f"Fraud ({prob}%)"
        else:
            risk_level = "High"
            result = f"Fraud ({prob}%)"

        # Stats
        session["total_transactions"] = session.get("total_transactions", 0) + 1
        if prob > 30:
            session["fraud_count"] = session.get("fraud_count", 0) + 1

        # History
        if "history" not in session:
            session["history"] = []

        session["history"].append({
            "amount": amount,
            "time": time,
            "location": location,
            "result": result,
            "prob": prob
        })

        # Graph
        labels = ["Safe", "Fraud"]
        values = [100 - prob, prob]

        plt.figure()
        plt.bar(labels, values)
        plt.title("Fraud Analysis")

        if not os.path.exists("static"):
            os.makedirs("static")

        plt.savefig("static/graph.png")
        plt.close()

    return render_template(
        "index.html",
        result=result,
        prob=prob,
        risk=risk_level,
        total=session.get("total_transactions", 0),
        fraud=session.get("fraud_count", 0),
        history=session.get("history", [])
    )


if __name__ == "__main__":
    app.run(debug=True)