import requests, json, time, os
from datetime import datetime
from bs4 import BeautifulSoup
from extractors import extract_from_craigslist

results_url = 'https://portland.craigslist.org/d/software-qa-dba-etc/search/sof'
results_page = requests.get(results_url)
soup = BeautifulSoup(results_page.content, "html.parser")

job_headings = soup.find_all('h3', class_='result-heading')

start_time = datetime.now()
file_count = 0

for h in job_headings:
	anchor = h.a
	link = anchor['href']
	
	time.sleep(2)

	job_dict = extract_from_craigslist(link) 

	if job_dict is not None:
		filename = job_dict['site'] + '-' + job_dict['post_id'] + '.json'
		extant_files = os.listdir('extracted-files')

		if filename not in extant_files:
			file = open('extracted-files/' + filename, 'x', encoding='utf-8')
			file.write(json.dumps(job_dict))
			file.close()	
			file_count += 1

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
