from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "secret123"

# Connect MongoDB (local for now)
import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["taskdb"]
tasks = db["tasks"]
users = db["users"]
# Home page
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        task = request.form.get("task")
        tasks.insert_one({
        "task": task,
        "priority": request.form.get("priority"),
        "completed": False
        })
    all_tasks = list(tasks.find())
    return render_template("index.html", tasks=all_tasks)

# Delete task
@app.route("/delete/<id>")
def delete(id):
    tasks.delete_one({"_id": ObjectId(id)})
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users.insert_one({
            "username": username,
            "password": password
        })

        return redirect("/login")

    return render_template("register.html")
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.find_one({
            "username": username,
            "password": password
        })

        if user:
            session["user"] = username
            return redirect("/")

    return render_template("login.html")
@app.route("/complete/<id>")
def complete(id):
    tasks.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"completed": True}}
    )
    return redirect("/")
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    task = tasks.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        tasks.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "task": request.form["task"],
                "priority": request.form["priority"]
            }}
        )
        return redirect("/")

    return render_template("edit.html", task=task)
if __name__ == "__main__":
    app.run(debug=True)