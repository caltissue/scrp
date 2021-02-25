import requests, json, functools
from datetime import datetime
from bs4 import BeautifulSoup, element
from bs4.element import Tag
import db_func

# extract function that returns soup from link
# dict function that returns dict from soup
# id function that gives id from soup

def get_soup(link): # string link; returns soup
	job_page = requests.get(link)
	soup = BeautifulSoup(job_page.content, 'html.parser')
	return soup

def get_post_id(soup): # BeautifulSoup object soup; returns int
	post_infos = soup.find(class_='postinginfos')
	id_p = post_infos.p
	post_id = id_p.contents[0].strip("post id:")
	return post_id

def get_filename(soup):
	sitename = 'craigslist'
	post_id = get_post_id(soup)
	filename = sitename + '-' + post_id + '.json'
	return filename

def extract_from_craigslist(soup): # BeautifulSoup object soup; returns dict
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

	sitename = 'craigslist'
	post_id = get_post_id(soup)

	job_desc = {
		'site': sitename,
		'title': title.contents[0].replace("'", ""),
		'location': location,
		'body': bodystring.replace("'", ""),
		'time': time_string,
		'post_id': post_id,
		'filename': get_filename(soup)
	}
	return job_desc
