import requests, json, time, os, db_func
import extractors as get
from datetime import datetime
from bs4 import BeautifulSoup
from mysql.connector import connect, Error

filefolder = 'logs/extracted-files'
errorfolder = 'logs/error'
start_time = datetime.now()

boards = {
	'craigslist portland software': 'https://portland.craigslist.org/d/software-qa-dba-etc/search/sof',
	'craigslist portland sys/network': 'https://portland.craigslist.org/d/systems-networking/search/sad',
	'craigslist portland web': 'https://portland.craigslist.org/d/web-html-info-design/search/web',
}

'''
SCRAPE & WRITE
'''
print('scraping...')

extant_files = os.listdir(filefolder)
json_files = []
for f in extant_files:
	if '.json' in f:
		json_files.append(f)

job_headings = []
for board in boards.keys():
	results_page = requests.get(boards[board])
	soup = BeautifulSoup(results_page.content, "html.parser")

	job_headings += soup.find_all('h3', class_='result-heading')

file_count = 0
post_ids = db_func.get_post_ids()

for h in job_headings:
	anchor = h.a
	link = anchor['href']

	id = get.get_post_id_substr(link)

	if id not in post_ids:
		# sometimes we write files and then our insert fails
		filename = get.get_filename_link(link)
		if os.path.exists(filefolder + '/' + filename):
			continue

		# here we know the file doesn't exist already
		job_dict = get.extract_from_craigslist(link)
		file = open(filefolder + '/' + filename, 'x')
		file.write(json.dumps(job_dict))
		file.close()
		json_files.append(job_dict['filename'])

		file_count += 1
		time.sleep(2)

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
# this is a separate step for ease of debugging
for f in json_files:
	filename = filefolder + '/' + f # os can concat these
	file = open(filename, 'r')
	job = json.loads(file.read()) # becomes dict
	file.close()

	match_id = db_func.existing_match(job) # check for same post w new id
	if match_id:
		db_func.increment_encounters(match_id)
		if os.path.exists(filename):
			os.remove(filename)
	else:
		db_func.insert_post(job)
