from mysql.connector import connect, Error
from datetime import datetime
import os, json, db_func

filefolder = 'extracted-files'
errorfolder = 'logs/error'
posts = []

extant_files = os.listdir(filefolder)

json_files = []
for f in extant_files:
	if '.json' in f:
		json_files.append(f)

for f in json_files:
	filename = filefolder + '/' + f # os can concat these
	file = open(filename, 'r')
	job = json.loads(file.read()) # becomes dict
	file.close()
	posts.append(job)

for p in posts:
	match_id = db_func.existing_match(p)
	if match_id > 0:
		db_func.increment_encounters(match_id)
	else:
		db_func.insert_post(p)

# timestr = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
