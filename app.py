from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Load model
model = joblib.load("model.pkl")

# Dummy users
users = {"admin": "1234"}


# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        if user in users and users[user] == pwd:
            session["user"] = user
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


# 📝 SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        users[user] = pwd
        return redirect(url_for("login"))

    return render_template("signup.html")


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# 🏠 DASHBOARD
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    result = None
    prob = None

    if request.method == "POST":
        values = list(request.form.values())

        if any(v.strip() == "" for v in values[:3]):
            result = "Please fill all fields"
            return render_template("index.html", result=result)

        # Prepare features
        features = []
        for x in values:
            try:
                features.append(float(x))
            except:
                features.append(random.uniform(-1, 1))

        # Prediction
        raw_prob = model.predict_proba([features])[0][1]
        display_prob = min(raw_prob * 20, 1.0)
        prob = display_prob * 100

        # Update stats
        session["total_transactions"] = session.get("total_transactions", 0) + 1

        if display_prob > 0.3:
            session["fraud_count"] = session.get("fraud_count", 0) + 1
            result = f"Fraud ({prob:.2f}%)"
        else:
            result = f"Safe ({prob:.2f}%)"

        # Save history
        if "history" not in session:
            session["history"] = []

        session["history"].append({
            "amount": values[0],
            "time": values[1],
            "location": values[2],
            "result": result,
            "prob": round(prob, 2)
        })

        # 📊 Generate graph
        labels = ["Safe", "Fraud"]
        values_chart = [100 - prob, prob]

        plt.figure()
        plt.bar(labels, values_chart)
        plt.title("Fraud Analysis")

        if not os.path.exists("static"):
            os.makedirs("static")

        plt.savefig("static/graph.png")
        plt.close()

    return render_template(
        "index.html",
        result=result,
        prob=prob,
        total_transactions=session.get("total_transactions", 0),
        fraud_count=session.get("fraud_count", 0),
        history=session.get("history", [])
    )


if __name__ == "__main__":
    app.run(debug=True)