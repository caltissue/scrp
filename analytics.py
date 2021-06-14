import os
import db_func as db
import string

ok_chars = string.ascii_lowercase + string.digits + string.whitespace

'''
    Creating data
'''
def get_common_words():
    commonword_res = db.execute_query('''
    SELECT word FROM wordcount_body
    WHERE count > (SELECT COUNT(id) / 2 FROM craigslist_jobs)
    ''')
    commonwords = [c[0] for c in commonword_res]

    commonwords.extend([
    'but', 'and', 'so', 'if', 'because', 'a', '', ' ', '-', '--', 'has', 'one',
    'well', 'then', 'they', 'their', 'by'
    ])
    return commonwords

def word_pairs():
    wordpair_counts = {}
    post_bodies = db.execute_query('SELECT body FROM craigslist_jobs')
    commons = get_common_words()
    for b in post_bodies:
        body = b[0].lower()
        body = ''.join([c for c in body if c in ok_chars])

        words = set([word for word in body.split() if word not in commons])

        pairs = set([tuple(sorted((i,j))) for i in words for j in words if i != j])
        for tup in pairs:
            if tup in wordpair_counts: wordpair_counts[tup] += 1
            else: wordpair_counts[tup] = 1

    return wordpair_counts

def wordcount(column):
    wordmap = {}
    wordcountlist = []
    commons = get_common_words()
    titles = db.execute_query('SELECT %s FROM craigslist_jobs' % column)

    for t in titles:
        title = t[0].lower()
        title = ''.join([c for c in title if c in ok_chars])

        wordlist = set([word for word in title.split() if word not in commons])

        for word in wordlist:
            if word in wordmap: wordmap[word] += 1
            else: wordmap[word] = 1

    for word in wordmap:
        wordcountlist.append((wordmap[word], word))

    wordcountlist.sort(reverse=True)
    return wordcountlist

'''
    Queries against the final data
'''

def get_frequent_pairs(word, mincount):
    return db.execute_query('''
    SELECT word1, word2 FROM wordpairs
    WHERE '%s' in (word1, word2)
    AND count > %s
    ''' % (word, mincount))

def get_frequent_pairs_with_uncommon_words(word): # TODO this has 3-levels of subquery
    return db.execute_query('''
    WITH tops AS (
        SELECT word FROM wordcount_body
        WHERE word NOT IN (
            SELECT word FROM wordcount_body
            WHERE count > (SELECT COUNT(id) / 2 FROM craigslist_jobs)
        )
    ) SELECT * FROM wordpairs
    WHERE %s in (word1, word2)
    AND word1 NOT IN (SELECT * FROM tops)
    AND word2 NOT IN (SELECT * FROM tops)
    ORDER BY count DESC;
    ''' % word)
