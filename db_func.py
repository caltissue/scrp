from mysql.connector import connect, Error
import os
from difflib import SequenceMatcher

def truncate_table(table):
    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp'
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute('TRUNCATE TABLE %s' % table)
                connection.commit()
    except Error as e:
        print(e)

def get_dataset_as_list(query):
    list = []
    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp'
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                for r in cursor.fetchall():
                    list.append(r)
    except Error as e:
        print(e)

    return list

def insert_records_from_tuples(list, table): # list of tuples
    query = '''
    INSERT INTO %s (count, word)
    VALUES ( %s, '%s' )
    '''
    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp'
        ) as connection:
            with connection.cursor() as cursor:
                for t in list:
                    cursor.execute(query % (table, str(t[0]), t[1]))
                connection.commit()
    except Error as e:
        print(e)

def insert_wordpair_counts(wordpairs):
    query = '''
    INSERT INTO wordpairs (word1, word2, count)
    VALUES ( '%s', '%s', %s )
    '''
    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp'
        ) as connection:
            with connection.cursor() as cursor:
                for t in wordpairs:
                    cursor.execute(query % (t[0], t[1], wordpairs[t]))
                connection.commit()
    except Error as e:
        print(e)

def get_all_post_ids(including_reposts):
    query = 'SELECT post_id FROM craigslist_jobs'
    if including_reposts:
        query += ' UNION SELECT post_id FROM craigslist_reposts'

    ids = []

    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp',
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                for t in cursor.fetchall():
                    ids.append(t[0])
    except Error as e:
        print(e)

    return ids

def get_previous_post_id(newpost): # dict newpost; returns id of match if any
    posts = []

    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp',
        ) as connection:
            query = 'SELECT post_id, title, body FROM craigslist_jobs'
            with connection.cursor() as cursor:
                cursor.execute(query)
                for t in cursor.fetchall():
                    p = { 'post_id': t[0], 'title': t[1], 'body': t[2] }
                    posts.append(p)
    except Error as e:
        print(e)

    for p in posts: # this comes after to avoid return from try
        title_match = SequenceMatcher(None, p['title'], newpost['title']).ratio()
        if title_match > .9:
            content_match = SequenceMatcher(None, p['body'], newpost['body']).ratio()
            if content_match > .9:
                return p['post_id']
    return ''

def note_repost(original_id, repost_id):
    update = '''
    UPDATE craigslist_jobs
    SET times_encountered = times_encountered + 1
    WHERE post_id = '%s'
    '''
    insert = '''
    INSERT IGNORE INTO craigslist_reposts (post_id, original_post_id)
    VALUES ('%s', '%s')
    '''
    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp',
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(update % repost_id)
                cursor.execute(insert % (repost_id, original_id))
                connection.commit()
    except Error as e:
        print(e)

def add_post(p): # dict post
    base_query = '''
    INSERT INTO craigslist_jobs
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
        originalfile = 'logs/extracted-files' + '/' + p['filename']
        if os.path.exists(originalfile):
            os.remove(originalfile)
