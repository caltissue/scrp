from mysql.connector import connect, Error
from datetime import datetime
from getpass import getpass
import os, json

# get folder extracted-files
extant_files = os.listdir('extracted-files')
for f in extant_files:
	if '.json' not in f:
		extant_files.remove(f)

# read in every file and make a big list/array
# consider pandas dataframes when this grows
posts = []
for f in extant_files:
	filename = 'extracted-files/' + f
	file = open(filename, 'r')
	job = json.loads(file.read()) # json to dict
	file.close()
	posts.append(job)

base_query = '''
INSERT INTO jobs_craigslist (
	site, 
	title, 
	location, 
	body, 
	time, 
	post_id, 
	times_encountered
) VALUES 

'''

# swap the loop into the try block to avoid opening a new cnxn every time
for p in posts:
	values = ''
	values += '('
	values += "'" +  p['site'] + "',"
	values += "'" +  p['title'] + "',"
	values += "'" +  p['location'] + "',"
	values += "'" +  p['body']+ "',"
	values += "'" +  p['time'] + "',"
	values += "'" +  p['post_id'] + "',"
	values += '1' # times_encountered; we will check/increment this later
	values += ')'

	query = base_query + values

	try:
		with connect(
			host="localhost",
			user="root",
			password=getpass("pw: "), # just put this in an env var and import it
			database="scrp",
		) as connection:
			with connection.cursor() as cursor:
				cursor.execute(query)
				connection.commit()
	except Error as e:
		errorfile = 'sql-insert-logs/error/error-' + p['post_id'] + '.txt'
		errorlog = open(errorfile, 'x')
		errorlog.write('ERROR:\n' + e + '\n========\nQUERY:\n' + query)
		errorlog.close()
		print('error during insert - logged')
	else:
		insertfile = 'sql-insert-logs/insert/insert-' + p['post_id'] + '.txt'
		insertlog = open(insertfile, 'x')
		insertlog.write('QUERY:\n' + query)
		insertlog.close()
		originalfile = 'extracted-files/craigslist-' + p['post_id'] + '.json'
		if os.path.exists(originalfile):
			os.remove(originalfile)
	 

''' # here we test the output
query = query[:-1]
query_file = open('query.txt', 'x')
query_file.write(query)
query_file.close()

'''

# add check against title & body that it's actually a new post // else increment times_encountered
# timestr = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
