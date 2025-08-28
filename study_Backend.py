from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///questions.db"

db = SQLAlchemy(app)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"<Question {self.id}>"

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")

@app.route("/create")
def create():
    return render_template("create.html")
@app.route("/remove")
def remove():
    return render_template("remove.html")

app.run(debug=True)