from main import News, db, app
from datetime import datetime


def read_data(file_path) -> dict:
	try:
		result = dict()
		file_path = f'bot_news/{file_path}'
		iter = 1
		text = ''
		with open(file_path) as file:
			for line in file:
				match iter:
					case 1:
						result['title'] = line
					case _:
						text += line
				iter += 1
			result['text'] = text
		return result
	except IOError as er:
		print("\033[31m{}".format(f'{file_path} - {er}'))
		exit(1)
	finally:
		print("\033[32m{}".format(f'Read {file_path} ok'))


def to_db(file_path) -> None:
	data = read_data(file_path)
	with app.app_context():
		news = News(title=data['title'], text=data['text'], pub_date=datetime.now())
		db.session.add(news)
		db.session.commit()


"""
	Call with another file name for add new news at site
"""
to_db('1.txt')
