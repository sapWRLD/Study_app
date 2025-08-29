from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///questions.db"

db = SQLAlchemy(app)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    anwser = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"<Question {self.id}>"

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == "create":
            return redirect(url_for('create', questions=Questions.query.all()))
        elif action == "remove":
            return redirect(url_for('remove'))
        elif action == "start_quiz":
            return redirect(url_for('quiz'))
    return render_template("index.html")

@app.route("/quiz", methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        anwser = request.form.get('answer')
        if anwser:
            questions = Questions.query.all()
            if anwser == Questions.anwser:
                message = "Correct!"
            else:
                message = "Incorrect!"
        else:
            message = "Please provide an answer."
    return render_template("quizpage.html", message=message, question=Questions.query.order_by(func.random()).first())

@app.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        if question and answer:
            new_question = Questions(question=question, anwser=answer)
            db.session.add(new_question)
            db.session.commit()
            return render_template("create.html", message="Question added!" , questions=Questions.query.all())
        else:
            return render_template("create.html", message="Please fill out both fields.", questions=Questions.query.all())
    return render_template("create.html", questions=Questions.query.all())

@app.route("/remove", methods=['GET', 'POST'])
def remove():
    if request.method == 'POST':
        question_id = request.form.get('questionid')
        question = Questions.query.get(question_id)
        if question:
            db.session.delete(question)
            db.session.commit()
            return render_template("remove.html", message="Question removed!", questions=Questions.query.all())
        else:
            return render_template("remove.html", message="Question not found.", questions=Questions.query.all())
    return render_template("remove.html", questions=Questions.query.all())

app.run(debug=True)