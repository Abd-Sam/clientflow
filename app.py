from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session
import re
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os 
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

app.permanent_session_lifetime = timedelta(minutes=30)

# configuring the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clientflow.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Enquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(40), nullable=False)
    budget = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20),nullable=False, default="new")
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"<Enquiry {self.id}: {self.name}>"



def login_required(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    #pulling each fiels out of the submitted form data
    name = request.form.get("name").strip()
    email = request.form.get("email").strip()
    phone = request.form.get("phone").strip()
    service = request.form.get("service").strip()
    budget = request.form.get("budget").strip()
    notes = request.form.get("notes").strip()
    
    # server side validation
    print(f"DEBUG: service='{service}' budget='{budget}'")
    errors = []
     
    if not name:
        errors.append("Name is a required.")

    if not email or "@" not in email:
        errors.append("A valid email is required")

    if not re.match(r"^\+?[0-9][0-9\s\-]{6,14}[0-9]$",phone):
        errors.append("Phone must be 7-15 digits (spaces, +, and - are allowed).")

    if service not in{
        "financial_planning", "investment_advice","insurance","tax_planning","other"
    }:
        errors.append("Please select a valid service")
    
    if budget not in {"under_50k", "50k_2L", "2L_10L", "10L_plus"}:
        errors.append("Please select a valid budget range.")
    
    if errors:
        print("Validation FAILED")
    
        for err in errors:
            print(f"-{err}")
        print("-----")
        return "<h3>Validation FAILED.</h3>", 400
    
        # print("---- New Enquiry ----") (to check before database config)
    # print(f"Name:     {name}")
    # print(f"Email:    {email}")
    # print(f"Phone:    {phone}")
    # print(f"Service:  {service}")
    # print(f"Budget:   {budget}")
    # print(f"Notes:    {notes}")
    # print(f"--------------------")
 
    #Saving to the database
    new_enquiry = Enquiry(
        name=name,
        email=email,
        phone=phone,
        service=service,
        budget=budget,
        notes=notes if notes else None
    )
    db.session.add(new_enquiry)
    db.session.commit()

    print(f"Saved Enquiry #{new_enquiry.id} from {name}")
    return redirect(url_for("thanks"))


    #Adding a PRG redirecting to a thank you page
    return redirect(url_for("thanks"))

@app.route("/thanks")
def thanks():
    return render_template("thanks.html")


@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session.permanent=True
            session['user_id']=user.id
            return redirect(url_for("admin"))    
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')


@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "Admin dashboard"

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)