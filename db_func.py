from mysql.connector import connect, Error
import os, traceback
from difflib import SequenceMatcher

def print_error_info(e, query):
    print(e)
    print('\nQUERY:', query[:350])
    print('\nTRACEBACK:')
    traceback.print_exc()
    print('\nSTACK:')
    traceback.print_stack()

'''
    EXECUTE_QUERY
    1 command, autocommit on, returns optional list of tuples (or None)
'''
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
        print_error_info(e, query)
    return res

def truncate_table(table):
    q = 'TRUNCATE TABLE %s' % table
    execute_query(q)

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

    for p in posts:
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
    execute_query('''
    INSERT INTO craigslist_jobs
    (site, title, location, body, time, post_id, times_encountered)
    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')
    ''' % (
        p['site'], p['title'], p['location'], p['body'],
        p['time'], p['post_id'], '1'
    ))

'''
    INSERT_LARGE_QUERY_FROM_LIST
    builds paged query for large inserts, issues multiple commands, autocommit off
    no return value
'''
def insert_large_query_from_list(querybase, value_list):
    try:
        with connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASS'),
            database='scrp'
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SET autocommit=0;')
                while value_list:
                    try:
                        query = querybase + ' '
                        insertcount = 100000
                        insertrange = min(len(value_list), insertcount)
                        for i in range(insertrange):
                            query += value_list[i] + ', '
                        query = query[:-2] + ';'
                        value_list = value_list[insertcount:]
                        cursor.execute(query)
                    except Error:
                        cursor.execute('ROLLBACK;')
                        raise
                cursor.execute('COMMIT;')
                connection.commit()
    except Error as e:
        sample_values = value_list[:10]
        query = '(truncated) ' + querybase + ' '
        for i in range(len(sample_values)):
            q += sample_values[i]
        print_error_info(e, query)

def insert_records_from_tuples(t_list, table):
    querybase = "INSERT INTO %s (count, word) VALUES" % table
    values = ["( %s, '%s' )" % (str(t[0]), t[1]) for t in t_list]
    insert_large_query_from_list(querybase, values)

def insert_wordpair_counts(wordpairs):
    querybase = "INSERT INTO wordpairs (word1, word2, count) VALUES"
    values = ["( '%s', '%s', %s )" % (k[0], k[1], wordpairs[k]) for k in wordpairs]
    insert_large_query_from_list(querybase, values)
