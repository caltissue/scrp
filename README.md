# SCRP

SCRP is a little craigslist web scraper that feeds a database of job postings. I used Craigslist for its relatively simple page layouts. The main app consists of python scripts and a MySQL database.

##### Logs & files

The app assumes the following file structure in the top level directory. These are all for logging purposes.
```
logs/
  error/
  extracted-files/
  scrapelog.txt
  verbose-scrapelog/
```

I added job boards and their links to `boards.json` in the main folder as follows.
```
{
  "craigslist portland software": "https://portland.craigslist.org/d/software-qa-dba-etc/search/sof",
  ...
}
```

##### Schema

See the mysqldump file for a list of `CREATE table` statements. 
