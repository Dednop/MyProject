from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class UserCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()

def add_three_users_daily():
    user_count = UserCount.query.get(1)
    if user_count:
        user_count.count += 3
        db.session.commit()
    else:
        new_user_count = UserCount(id=1, count=3)
        db.session.add(new_user_count)
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(add_three_users_daily, 'interval', days=1, start_date=datetime.now())
scheduler.start()

@app.route('/')
def index():
    user_count = UserCount.query.get(1)

    if user_count is None:
        user_count = UserCount(id=1, count=0)
        db.session.add(user_count)
        db.session.commit()

    return render_template('index.html', user_count=user_count.count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Email не найден. Проверьте свой Email.', 'error')
            return redirect(url_for('login'))

        if not check_password_hash(user.password, password):
            flash('Неверный пароль. Попробуйте снова.', 'error')
            return redirect(url_for('login'))
        
        session['user_id'] = user.id
        flash('Успешный вход!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Пароли не совпадают. Попробуйте снова.', 'error')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email уже существует. Попробуйте другой.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        user_count = UserCount.query.get(1)
        if user_count:
            user_count.count += 1
            db.session.commit()

        flash('Регистрация успешна! Теперь войдите.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('index'))

@app.route('/2rd')
def route_to_2rd():
    return render_template('2rd.html')

@app.route('/3rd')
def route_to_3rd():
    return render_template('3rd.html')

@app.route('/4rd')
def route_to_4rd():
    return render_template('4rd.html')

if __name__ == '__main__':
    app.run(debug=True)
