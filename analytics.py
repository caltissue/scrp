import os
import db_func as db

def junk_char_list():
    return [
    '/', '(', ')', ',', '. ', '.\n', '.\r', '.\t', '..', '!', '?', '|', ':', '*',
    '=', '•', '●', '"', '\n', '\r', '\t', '_', '“', '”', ';', '·', '📺', '👉',
    '‘', '`', '[', ']', '{', '}', ' +', '►', '✭',
    ]

def get_common_words():
    query = '''
    SELECT word
    FROM wordcount_body
    WHERE count > (
        SELECT COUNT(id) / 2
        FROM craigslist_jobs
    )
    '''
    commonwords = []
    commonword_results = db.get_dataset_as_list(query)
    for c in commonword_results:
        commonwords.append(c[0])

    return commonwords

def word_pairs():
    common_words = get_common_words()
    common_words.append('')
    common_words.append(' ')
    common_words.append('-')
    common_words.append('--')
    wordpair_counts = {}

    post_bodies = db.get_dataset_as_list('SELECT body FROM craigslist_jobs')

    for b in post_bodies:
        body = b[0].lower()
        for c in junk_char_list(): body = body.replace(c, ' ')

        words = set([word for word in body.split() if word not in common_words])

        pairs = set([tuple(sorted((i,j))) for i in words for j in words if i != j])

        for tup in pairs:
            if tup in wordpair_counts: wordpair_counts[tup] += 1
            else: wordpair_counts[tup] = 1

    return wordpair_counts

def wordcount(column):
    wordmap = {}
    wordcountlist = []

    titles = db.get_dataset_as_list('SELECT %s FROM craigslist_jobs' % column)
    for t in titles:
        title = t[0]
        junk_chars = junk_char_list()
        for char in junk_chars:
            title = title.replace(char, ' ')

        title = title.lower()
        word_list = title.split(' ')

        for w in word_list:
            w = w.replace('’', '')
            w = w.strip()
            if len(w) > 0:
                if w in wordmap.keys():
                    wordmap[w] += 1
                else:
                    wordmap[w] = 1

    for w in wordmap:
        tup = (wordmap[w], w)
        wordcountlist.append(tup)

    wordcountlist.sort(reverse=True)
    return wordcountlist
