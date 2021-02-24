import requests, json, functools
from bs4 import BeautifulSoup, element
from bs4.element import Tag

def extract_from_craigslist(link): # string link; returns dict
	
	# get the page first
	job_page = requests.get(link)
	soup = BeautifulSoup(job_page.content, "html.parser")

	# checking if we've seen the post id before
	post_infos = soup.find(class_='postinginfos')
	id_p = post_infos.p
	post_id = id_p.contents[0].strip("post id:")

	logfile = open('logs/cl-post-id-log.txt', 'r')
	log = logfile.read()
	logfile.close()

	post_ids = log.split(",")
	if post_id in post_ids:
		return None

	# if we're here we can log this baby
	logfile = open('logs/cl-post-id-log.txt', 'a')
	logfile.write(post_id + ',')

	# now we can collect & write this info
	title = soup.find(id='titletextonly')
	super_title = soup.find(class_='postingtitletext')
	location = "not listed"
	if super_title.small:
		location = super_title.small.contents[0].strip("() ")

	body = soup.find(id='postingbody')
	body.div.extract()
	
	bodystring = ""
	for s in body.contents:
		if isinstance(s, str):
			bodystring += s
		if isinstance(s, element.Tag):
			for d in s.descendants:
				if isinstance(d, str):
					bodystring += str(d)
				
	time = soup.find(class_='date timeago')

	job_desc = {
		'site': 'craigslist',
		'title': title.contents[0],
		'location': location,
		'body': bodystring,
		'time': time.contents[0].strip(" \n"),
		'post_id': post_id,
	}
	return job_desc
