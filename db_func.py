from mysql.connector import connect, Error
import os
from difflib import SequenceMatcher

# TODO: get_post_ids and get_post_basics are the same func with different params; consolidate
def get_post_ids():
    ids = []

    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp',
        ) as connection:
            query = 'SELECT post_id FROM jobs_craigslist'
            with connection.cursor() as cursor:
                cursor.execute(query)
                for t in cursor.fetchall():
                    ids.append(t[0])
    except Error as e:
        print(e)

    return ids

def get_post_basics():
    posts = []

    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp',
        ) as connection:
            query = 'SELECT post_id, title, body FROM jobs_craigslist'
            with connection.cursor() as cursor:
                cursor.execute(query)
                for t in cursor.fetchall():
                    posts.append(t[0])
    except Error as e:
        print(e)

    return posts

def existing_match(post_to_check): # dict post_to_check; returns id of match
    posts = get_post_basics()
    for p in posts:
        title_match = SequenceMatcher('\n', p['title'], post_to_check['title'])
        if title_match > .9:
            content_match = SequenceMatcher('\n', p['body'], post_to_check['body'])
            if content_match > .85:
                return p['post_id']
    return 0

def increment_encounters(post_id): # string post_id
    update = '''
    UPDATE jobs_craigslist
    SET times_encountered = times_encountered + 1
    WHERE id = %s
    '''
    db_pass = os.getenv('DB_PASS')
    try:
    	with connect(
    		host='localhost',
    		user='root',
            password=os.getenv('DB_PASS'),
    		database='scrp',
    	) as connection:
    		with connection.cursor() as cursor:
    			cursor.execute(update % post_id)
    			cursor.commit()
    except Error as e:
    	print(e)

def insert_post(p): # dict post
    base_query = '''
    INSERT INTO jobs_craigslist
    (site, title, location, body, time, post_id, times_encountered)
    VALUES
    ('%s', '%s', '%s', '%s', '%s', '%s', '%s')
    '''
	try:
		with connect(
			host='localhost',
			user='root',
			password=os.getenv('DB_PASS'),
			database='scrp',
		) as connection:
			insert = base_query % (
				p['site'], p['title'], p['location'],
				p['body'], p['time'],  p['post_id'],
				'1' # times_encountered
			)
			with connection.cursor() as cursor:
				cursor.execute(insert)
				connection.commit()
	except Error as e:
		errorfile = 'logs/error' + '/' + p['post_id'] + '.txt'
		errorlog = open(errorfile, 'x')
		errorlog.write('ERROR:\n' + e + '\n========\nQUERY:\n' + query)
		errorlog.close()
		print('error during insert - logged')
	else:
        originalfile = 'extracted-files' + '/' + p['filename']
		if os.path.exists(originalfile):
			os.remove(originalfile)
