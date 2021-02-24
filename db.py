from mysql.connector import connect, Error
from datetime import datetime
from getpass import getpass

timestr = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

try:
	with connect(
		host="localhost",
		user="root",
		password=getpass("pw: "),
		database="scrp",
	) as connection:
		query = '''
		INSERT INTO jobs_craigslist (site, title, location, body, time, post_id, times_encountered)
		VALUES (
		'craigslist',
		'Job From DB.py',
		'My House',
		'this is a proper post. it even has three sentences. And one is even capitalized! we dont want you to work for us, pleb',
		'
		''' + timestr + '''
		',
		'1203998-12847-1231',
		'1'
		)
		'''
		with connection.cursor() as cursor:
			cursor.execute(query)
			connection.commit()
except Error as e:
	print (e)

