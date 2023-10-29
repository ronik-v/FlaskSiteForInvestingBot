from flask import Flask, render_template, url_for, request, redirect, json
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from waitress import serve
from sqlalchemy.sql import func
from werkzeug import Response
from config import admin
from datetime import datetime

from config import db_name, secret_key
HOST: str = '0.0.0.0'
PORT: int = 8888


app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key
db = SQLAlchemy(app)


class Person(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(100), unique=True, nullable=False)
	second_name = db.Column(db.String(200), unique=True, nullable=False)
	email = db.Column(db.String(300), unique=True, nullable=False)

	def __init__(self, first_name, second_name, email):
		self.first_name = first_name
		self.second_name = second_name
		self.email = email

	def __repr__(self):
		return f'<{Person.__name__} {self.email}>'


class News(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(300), unique=True, nullable=False)
	text = db.Column(db.Text, nullable=False)
	pub_date = db.Column(db.DateTime(timezone=True), server_default=func.now())

	def __init__(self, title, text, pub_date):
		self.title = title
		self.text = text
		self.pub_date = pub_date

	def __repr__(self):
		return f'<{News.__name__} {self.title}>'


class Admin(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True, nullable=False)
	password = db.Column(db.String(40), unique=True, nullable=False)

	def __init__(self, name, password):
		self.name = name
		self.password = password


def add_with_verification(person: Person):
	try:
		db.session.add(person)
		db.session.commit()
		return redirect('/home')
	except:
		return 'При отправке данных произошла ошибка...'


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index() -> str:
	if request.method == 'POST':
		first_name = request.form['first_name']
		second_name = request.form['second_name']
		email = request.form['email']
		person = Person(first_name=first_name, second_name=second_name, email=email)
		add_with_verification(person)
	return render_template('index.html')


@app.route('/about', methods=['GET'])
def about() -> str:
	return render_template('about.html')


@app.route('/news', methods=['GET'])
def news() -> str:
	news = News.query.all()
	return render_template('news.html', news=news)

@app.route('/admin', methods=['GET', 'POST'])
def admin_page() -> Response | str:
	if request.method == 'POST':
		admin_name_r, admin_password_r  = request.form['admin_name'], request.form['admin_password']
		_admin = db.session.query(Admin).filter(Admin.name == admin_name_r, Admin.password == admin_password_r).all()
		if _admin:
			return redirect(url_for('add_news', key=admin['key']))
		else:
			return 'Неправильное имя или пароль...\nПопробуйте еще раз'
	return render_template('admin_login.html')

@app.route('/admin/add/<key>', methods=['GET', 'POST'])
def add_news(key=None) -> None | str:
	if key:
		if request.method == 'POST':
			title, text = request.form['news_title'], request.form['news_text']
			new_news = News(title=title, text=text, pub_date=datetime.now())
			db.session.add(new_news)
			db.session.commit()
		return render_template('add_news.html')
	else:
		pass


if __name__ == '__main__':
	app.debug = True
	with app.app_context():
		db.create_all()
		serve(app, host=HOST, port=PORT)
