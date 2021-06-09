from mysql.connector import connect, Error
import os, traceback
from difflib import SequenceMatcher

def execute_query(query):
    res = []
    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp'
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                res = cursor.fetchall()
                connection.commit()
    except Error as e:
        print(e)
        print('\nQUERY:', query)
        print('\nTRACEBACK:')
        traceback.print_exc()
        print('\nSTACK:')
        traceback.print_stack()
    return res

'''
    TODO: build complete list, pass to abitrary insert method (when exists)
'''
def insert_records_from_tuples(t_list, table):
    query = "INSERT INTO %s (count, word) VALUES ( %s, '%s' )"
    for t in t_list: execute_query(query % (table, str(t[0]), t[1]))

def truncate_table(table):
    q = 'TRUNCATE TABLE %s' % table
    execute_query(q)

'''
    TODO: extract general arbitrary method to batch large queries from lists
'''
def insert_wordpair_counts(wordpairs):
    querybase = '''
    INSERT INTO wordpairs (word1, word2, count)
    VALUES
    '''
    insert_list = []
    for k in wordpairs:
        insert_list.append("( '%s', '%s', %s )" % (k[0], k[1], wordpairs[k]))
    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp'
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SET autocommit=0;')
                while insert_list:
                    query = querybase + ' '
                    insertcount = 100000
                    for i in range(min(len(insert_list), insertcount)):
                        query += insert_list[i] + ', '
                    query = query[:-2] + ';'
                    insert_list = insert_list[insertcount:]
                    cursor.execute(query)
                cursor.execute('COMMIT;')
                connection.commit()
    except Error as e:
        print(e)

def get_all_post_ids(including_reposts):
    query = 'SELECT post_id FROM craigslist_jobs'
    if including_reposts:
        query += ' UNION SELECT post_id FROM craigslist_reposts'
    id_results = execute_query(query)
    ids = [t[0] for t in id_results]
    return ids

def get_previous_post_id(newpost): # dict newpost; returns id of match if any
    posts = []
    post_results = execute_query('SELECT post_id, title, body FROM craigslist_jobs')
    posts = [{'post_id':r[0], 'title':r[0], 'body':r[2]} for r in post_results]

    for p in posts: # this comes after to avoid return from try
        title_match = SequenceMatcher(None, p['title'], newpost['title']).ratio()
        if title_match > .9:
            content_match = SequenceMatcher(None, p['body'], newpost['body']).ratio()
            if content_match > .9:
                return p['post_id']

def note_repost(original_id, repost_id):
    execute_query('''
    UPDATE craigslist_jobs
    SET times_encountered = times_encountered + 1
    WHERE post_id = '%s'
    ''' % repost_id)
    execute_query('''
    INSERT IGNORE INTO craigslist_reposts (post_id, original_post_id)
    VALUES ('%s', '%s')
    ''' % (repost_id, original_id))

def add_post(p): # dict post
    q = '''
    INSERT INTO craigslist_jobs
    (site, title, location, body, time, post_id, times_encountered)
    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')
    ''' % (
    p['site'], p['title'], p['location'], p['body'], p['time'], p['post_id'],
    '1' # times_encountered (this is a new post in theory)
    )
    execute_query(q)
