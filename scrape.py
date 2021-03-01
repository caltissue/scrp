import requests, json, time, os
import extractors as get
import db_func as db
import analytics
from datetime import datetime
from bs4 import BeautifulSoup
from mysql.connector import connect, Error

filefolder = 'logs/extracted-files'
errorfolder = 'logs/error'
logfolder = 'logs/verbose-scrapelog'
start_time = datetime.now()

boardfile = open('boards.json', 'r')
boards = json.loads(boardfile.read())
boardfile.close()

'''
SCRAPE & WRITE
'''
print('scraping...')
scrapelog_filename = logfolder + '/scrapelog-' + start_time.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
scrapelog_file = open(scrapelog_filename, 'x')
scrapelog_file.write('scrape start ' + str(start_time) + '\n')
scrapelog_file.write('boards:\n' )
for key in boards.keys():
	scrapelog_file.write(str(key) + '\n')
scrapelog_file.write('\nstarted with these files already here:')

extant_files = os.listdir(filefolder)
json_files = []
for f in extant_files:
	if '.json' in f:
		json_files.append(f)
		scrapelog_file.write('\n' + f)
scrapelog_file.write('\n-----------')

scrapelog_file.write('\n== scrape begins ==\n')
jobs_results = []
for board in boards.keys():
	results_page = requests.get(boards[board])
	soup = BeautifulSoup(results_page.content, "html.parser")

	board_results = soup.find_all('h3', class_='result-heading')
	for result in board_results:
		jobs_results.append({
			'board': board,
			'result': result
		})

file_count = 0
post_ids = db.get_all_post_ids(including_reposts=True)

for r in jobs_results:
	board = r['board']
	anchor = r['result'].a
	link = anchor['href']
	scrapelog_file.write('\njob link: ' + link)

	id = get.post_id(link)
	scrapelog_file.write('\nwith id: ' + str(id))
	if id not in post_ids:
		# sometimes we write files and then our insert fails
		filename = board.replace(' ', '-') + '-' + get.filename(link)
		scrapelog_file.write('\ngenerated filename: ' + filename)
		if os.path.exists(filefolder + '/' + filename):
			scrapelog_file.write('\nfile exists, skipping\n')
			continue

		# here, we know the file doesn't exist already
		job_dict = get.job_description(link)
		job_dict['site'] = board
		job_dict['filename'] = filename
		job_dict['link'] = link
		file = open(filefolder + '/' + filename, 'x')
		file.write(json.dumps(job_dict))
		file.close()
		scrapelog_file.write('\nwrote file')
		json_files.append(job_dict['filename'])

		file_count += 1
		scrapelog_file.write('\nfile count: ' + str(file_count))
		time.sleep(2)
	else:
		scrapelog_file.write('\npost_id already exists in db')

	scrapelog_file.write('\n')

scrapelog_file.write('\n\n== scrape ends ==\n')
end_time = datetime.now()

result_string = ""
result_string += "\n+ scrape job:"
result_string += "\nstarted " + str(start_time.strftime("%Y-%m-%d %H:%M"))
result_string += "\nended " + str(end_time.strftime("%Y-%m-%d %H:%M"))
result_string += "\ntotal time: " + str(end_time - start_time)
result_string += "\n" + str(file_count) + " files added"
result_string += "\n============================="

logfile = open("logs/scrapelog.txt", "a")
logfile.write(result_string)
logfile.close()

'''
DB INSERT
'''
print('checking & inserting...')
scrapelog_file.write('\n== insert begins ==\n')
# this is a separate step for ease of debugging
for f in json_files:
	filename = filefolder + '/' + f # os can concat these
	file = open(filename, 'r')
	job = json.loads(file.read()) # becomes dict
	file.close()
	scrapelog_file.write('\nloaded file: ' + filename)

	match_id = db.get_previous_post_id(job)
	if match_id:
		scrapelog_file.write('\nthis is a repost; writing as repost')
		db.note_repost(match_id, job['post_id'])
		if os.path.exists(filename):
			os.remove(filename)
	else:
		scrapelog_file.write('\nthis is a new post; inserting')
		db.add_post(job)

scrapelog_file.write('\n== insert ends ==\n')
scrapelog_file.close()

'''
ANALYTICS
'''
print('running analytics...')
db.truncate_table('wordcount_title')
db.truncate_table('wordcount_body')

titlewords = analytics.wordcount('title')
db.insert_records_from_tuples(titlewords, 'wordcount_title')
bodywords = analytics.wordcount('body')
db.insert_records_from_tuples(bodywords, 'wordcount_body')
