from flask import Flask, redirect, render_template, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import func
import os
from datetime import timedelta 
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///questions.db"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")
db = SQLAlchemy(app)

login_manager = LoginManager(app) 
class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(100), nullable=False, unique=True) 
    password_hash = db.Column(db.String(200), nullable=False) 
    questions = db.relationship('Questions', backref='owner', lazy=True)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    anwser = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"<Question {self.id}>"


@login_manager.user_loader 
def load_user(user_id): return User.query.get(int(user_id)) 

@app.route("/", methods=['GET', 'POST']) 
def login(): 
    if request.method == 'POST':   
        user = User.query.filter_by(username=request.form["name"]).first()
        if user and check_password_hash(user.password_hash, request.form["password"]):
            login_user(user, remember=False)
            return redirect(url_for("home"))

    return render_template("login.html") 

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"]) 
def register(): 
    if request.method == 'POST': 
        username = request.form.get("name") 
        password = request.form.get("password") 
        if username and password:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Username already taken!")
                return render_template("register.html")
            password_hash = generate_password_hash(password)
            new_user = User(username=username, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()
            flash("User created!")
            return redirect(url_for("home"))
        else:
            flash("Please fill out both fields")
            return render_template("register.html")
    return render_template("register.html")

@app.route("/index", methods=['GET', 'POST'])
@login_required
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
@login_required
def quiz():
    message = None
    question = None

    if request.method == 'POST':
        # Retrieve the stored question ID from session
        question_id = session.get('current_question_id')
        if question_id:
            question = Questions.query.get(question_id)
            if question:
                user_answer = request.form.get('answer', '').strip()
                if not user_answer:
                    message = "Please provide an answer."
                elif user_answer.lower() == question.anwser.strip().lower():
                    message = "✅ Correct!"
                else:
                    message = f"❌ Incorrect! The correct answer was: {question.anwser}"
            else:
                message = "Question not found."
        else:
            message = "No active question. Please try again."

        # Pick a new random question for next round
        question = Questions.query.order_by(func.random()).first()
        if question:
            session['current_question_id'] = question.id

    else:  # GET request → start quiz with a random question
        question = Questions.query.order_by(func.random()).first()
        if question:
            session['current_question_id'] = question.id

    return render_template("quizpage.html", message=message, question=question)

@app.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        if question and answer:
            new_question = Questions(question=question, anwser=answer, user_id=current_user.id)
            db.session.add(new_question)
            db.session.commit()
            return render_template("create.html", message="Question added!" , questions=Questions.query.all())
        else:
            return render_template("create.html", message="Please fill out both fields.", questions=Questions.query.all())
    return render_template("create.html", questions=Questions.query.all())

@app.route("/remove", methods=['GET', 'POST'])
@login_required
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

if __name__ == "__main__":
    with app.app_context(): #Creates any tables that do not yet exist in the db
        db.create_all()
    app.run(debug=True)