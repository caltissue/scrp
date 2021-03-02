import os
import db_func as db

def wordcount(column):
    wordmap = {}
    wordcountlist = []

    titles = db.get_dataset_as_list('SELECT %s FROM craigslist_jobs' % column)
    for t in titles:
        title = t[0]
        junk_chars = [
        '/', '(', ')', ',', '. ', '.\n', '.\r', '.\t', '..', '!', '?', '|', ':', '*',
        '=', '•', '●', '"', '\n', '\r', '\t', '_', '“', '”', ';', '·', '📺', '👉',
        '‘', '`', '[', ']', '{', '}', ' +', '►', '✭',
        ]
        for j in junk_chars:
            title = title.replace(j, ' ')

        title = title.lower()
        word_list = title.split(' ')

        for w in word_list:
            w = w.replace('’', '')
            w = w.strip()
            if len(w) > 0:
                if w not in wordmap.keys():
                    wordmap[w] = 1
                else:
                    wordmap[w] += 1

    for w in wordmap:
        tup = (wordmap[w], w)
        wordcountlist.append(tup)

    wordcountlist.sort(reverse=True)
    return wordcountlist
