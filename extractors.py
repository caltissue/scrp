import requests, json, functools
from datetime import datetime
from bs4 import BeautifulSoup, element
from bs4.element import Tag
import db_func

def post_id(link):
	return link[link.rindex('/') + 1 : link.index('.html')]

def filename(link):
	id = post_id(link)
	return sitename + '-' + id + '.json'

def job_description(link): # string link; returns dict
	id = post_id(link)

	job_page = requests.get(link)
	soup = BeautifulSoup(job_page.content, 'html.parser')

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
	time_contents = time.contents[0].strip(" \n")
	time_contents_as_datetime = datetime.strptime(time_contents, '%Y-%m-%d %H:%M')
	time_string = str(time_contents_as_datetime.strftime('%Y-%m-%d %H:%M:%S'))

	job_desc = {
		'title': title.contents[0].replace("'", ""),
		'location': location,
		'body': bodystring.replace("'", ""),
		'time': time_string,
		'post_id': id,
	}
	return job_desc
