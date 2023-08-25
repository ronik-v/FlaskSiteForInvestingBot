from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from waitress import serve
from sqlalchemy.sql import func

from config import db_name, secret_key
HOST: str = '0.0.0.0'
PORT: int = 8000


app = Flask(__name__)
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


if __name__ == '__main__':
	app.debug = False
	serve(app, host=HOST, port=PORT)
