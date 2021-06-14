import sys, os

ROOT = 'logs'
FILES = os.path.join(ROOT, 'extracted-files')
ERROR = os.path.join(ROOT, 'error')
VERBOSE = os.path.join(ROOT, 'verbose-scrapelog')

def get_verboselog(timestr):
    filename = 'scrapelog-%s.txt' % timestr
    path = os.path.join(VERBOSE, filename)
    open(path, 'w').write('scrape start ' + str(timestr) + '\n')
    return path

def write(filename, header='', content=[]):
    lines = content.copy()
    with open(filename, 'a') as f:
        f.write('\n%s\n' % header)
        for s in lines: f.write(s + '\n')
