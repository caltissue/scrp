import requests, json, time, os
import extractors as get
import db_func as db
import analytics
from datetime import datetime
from bs4 import BeautifulSoup
from mysql.connector import connect, Error

logs = 'logs'
filefolder = 'logs/extracted-files'
errorfolder = 'logs/error'
verbose_scrapelog = 'verbose-scrapelog'
start_time = datetime.now()

boards = json.loads(open('boards.json').read())

'''
SCRAPE & WRITE
'''
print('scraping...')
verboselogfile = 'scrapelog' + start_time.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
scrapelog_filename = os.path.join(logs, verbose_scrapelog, verboselogfile)
scrapelog_file = open(scrapelog_filename, 'w')
scrapelog_file.write('scrape start ' + str(start_time) + '\n')
scrapelog_file.write('boards:\n' )
for key in boards.keys():
	scrapelog_file.write(str(key) + '\n')

scrapelog_file.write('\nstarted with these files already here:')
json_files = [f for f in os.listdir(filefolder) if '.json' in f]
for f in json_files: scrapelog_file.write('\n' + f)
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
		if os.path.exists(os.path.join(filefolder, filename)):
			scrapelog_file.write('\nfile exists, skipping\n')
			continue

		# here, we know the file doesn't exist already
		job_dict = get.job_description(link)
		job_dict['site'] = board
		job_dict['filename'] = filename
		job_dict['link'] = link
		open(os.path.join(filefolder, filename), 'w').write(json.dumps(job_dict))
		scrapelog_file.write('\nwrote file')
		json_files.append(job_dict['filename'])

		file_count += 1
		scrapelog_file.write('\nfile count: ' + str(file_count))
		time.sleep(0.5)
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

open("logs/scrapelog.txt", "a").write(result_string)

'''
DB INSERT
'''
print('checking & inserting...')
scrapelog_file.write('\n== insert begins ==\n')
# this is a separate step for ease of debugging
for f in json_files:
	filename = os.path.join(filefolder, f)
	job = json.loads(open(filename).read())
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

'''
ANALYTICS
'''
print('running analytics...')
db.truncate_table('wordcount_title')
db.truncate_table('wordcount_body')
db.truncate_table('wordpairs')

titlewords = analytics.wordcount('title')
db.insert_records_from_tuples(titlewords, 'wordcount_title')
scrapelog_file.write('\ninserted title wordcounts')

bodywords = analytics.wordcount('body')
db.insert_records_from_tuples(bodywords, 'wordcount_body')
scrapelog_file.write('\ninserted body wordcounts')

print('starting crossjoin at ', datetime.now())
wordpairs = analytics.word_pairs()
db.insert_wordpair_counts(wordpairs)
scrapelog_file.write('\ninserted wordpair crossjoin counts')

scrapelog_file.close()
print('finished at ', datetime.now())
