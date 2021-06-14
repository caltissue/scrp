import requests, json, os
import extractors as get, db_func as db, analytics, log
from datetime import datetime
from bs4 import BeautifulSoup
from mysql.connector import connect, Error

starttime = datetime.now()
boards = json.loads(open('boards.json').read())

'''
SCRAPE & WRITE
'''
print('scraping...')
verboselog = log.get_verboselog(starttime.strftime('%Y-%m-%d_%H-%M-%S'))
log.write(verboselog, header='boards', content=list(boards.keys()))

json_files = [f for f in os.listdir(log.FILES) if '.json' in f]
log.write(verboselog, 'started with these here:', json_files)

log.write(verboselog, '== scrape begins ==')
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
	id = get.post_id(link)

	if id not in post_ids:
		# check a file doesn't already exist for this post
		filename = board.replace(' ', '-') + '-' + get.filename(link)
		log.write(verboselog, 'job info', [
			'link: %s\n' % link,
			'post id: %s\n' % id,
			'filename: %s\n' % filename
		])
		if os.path.exists(os.path.join(log.FILES, filename)):
			log.write(verboselog, 'above file already exists, skipped')
			continue

		# add file
		job = get.job_description(link)
		job['site'] = board
		job['filename'] = filename
		job['link'] = link
		open(os.path.join(log.FILES, filename), 'w').write(json.dumps(job))
		json_files.append(filename)

		file_count += 1
		log.write(verboselog, 'wrote file, filecount = %s' % str(file_count))
	else:
		log.write(verboselog, 'post_id already exists in db')

log.write(verboselog, '== scrape ends ==')
endtime = datetime.now()

log.write(os.path.join(log.ROOT,'scrapelog.txt'), '+ scrape job:', [
	'started %s' % starttime.strftime("%Y-%m-%d %H:%M"),
	'ended %s' % endtime.strftime("%Y-%m-%d %H:%M"),
	'total time: %s' % str(endtime - starttime),
	'%s files added' % str(file_count),
	'============================='
])


'''
DB INSERT
'''
print('checking & inserting...')
log.write(verboselog, '== insert begins ==')
for f in json_files:
	filename = os.path.join(log.FILES, f)
	job = json.loads(open(filename).read())

	match_id = db.get_previous_post_id(job)
	status = 'repost noted'
	if match_id:
		db.note_repost(match_id, job['post_id'])
	else:
		status = 'new post inserted'
		db.add_post(job)

	log.write(verboselog, 'loaded file:', [filename, status])
	if os.path.exists(filename): os.remove(filename) # Log??

log.write(verboselog, '== insert ends ==')

'''
ANALYTICS
'''
for table in ['wordcount_title', 'wordcount_body', 'wordpairs']:
	db.truncate_table(table)

print('starting wordcounts', datetime.now())
titlewords = analytics.wordcount('title')
db.insert_records_from_tuples(titlewords, 'wordcount_title')

bodywords = analytics.wordcount('body')
db.insert_records_from_tuples(bodywords, 'wordcount_body')

print('starting wordpair count', datetime.now())
wordpairs = analytics.word_pairs()
print('wordpair insert', datetime.now())
db.insert_wordpair_counts(wordpairs)

log.write(verboselog, 'inserted:', ['title wordcounts', 'body wordcounts', 'wordpair counts'])
print('finished at', datetime.now())
