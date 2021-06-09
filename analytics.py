import os
import db_func as db
import string

def my_common_words():
    return [
    'but', 'and', 'so', 'if', 'because', 'a', '', ' ', '-', '--', 'has', 'one',
    'well', 'then',
    ]

def junk_char_list():
    return [
    '/', '(', ')', ',', '. ', '.\n', '.\r', '.\t', '..', '!', '?', '|', ':', '*',
    '=', '•', '●', '"', '\n', '\r', '\t', '_', '“', '”', ';', '·', '📺', '👉',
    '‘', '`', '[', ']', '{', '}', ' +', '►', '✭',
    ]

def ok_chars():
    return string.ascii_lowercase + string.digits + string.whitespace

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

    for w in my_common_words():
        commonwords.append(w)

    return commonwords

def word_pairs():
    wordpair_counts = {}
    post_bodies = db.get_dataset_as_list('SELECT body FROM craigslist_jobs')
    commons = get_common_words()
    okchars = ok_chars()
    for b in post_bodies:
        body = b[0].lower()

        body = ''.join([c for c in body if c in okchars])

        words = set([word for word in body.split() if word not in commons])

        pairs = set([tuple(sorted((i,j))) for i in words for j in words if i != j])

        for tup in pairs:
            if tup in wordpair_counts: wordpair_counts[tup] += 1
            else: wordpair_counts[tup] = 1

    return wordpair_counts

def get_high_occurence_pairs(word, mincount):
    pairs = word_pairs()
    mytups = [t for t in pairs.keys() if word in t]
    mypairs = {}
    for t in mytups: mypairs[t] = pairs[t]
    my_highoccurence_tups = [t for t in mypairs.keys() if mypairs[t] >= mincount]
    return my_highoccurence_tups

def wordcount(column):
    wordmap = {}
    wordcountlist = []
    commons = get_common_words()
    okchars = ok_chars()
    titles = db.get_dataset_as_list('SELECT %s FROM craigslist_jobs' % column)

    for t in titles:
        title = t[0].lower()
        title = ''.join([c for c in title if c in okchars])

        wordlist = set([word for word in title.split() if word not in commons])

        for word in wordlist:
            if word in wordmap: wordmap[word] += 1
            else: wordmap[word] = 1

    for word in wordmap:
        wordcountlist.append((wordmap[word], word))

    wordcountlist.sort(reverse=True)
    return wordcountlist
