# SCRP

SCRP is a data blog about my job search. We'll be gathering info from job boards, which we'll sort, transform, and try to gain insights from. Everything we learn will be available through an interactive site, where users can learn, interact, and provide feedback.

We're starting with Craigslist, because the HTML is relatively simple. Ideally we'll hit Indeed, Monster, and GitHub, and more.

##### Tools

I'm working with Python 3.8, MySQL 8.0, and Flask 1.1 for the web backend. I haven't picked my JavaScript libraries yet, but there will be js visualization involved.

Come back soon! Connect with me on [Twitter](https://twitter.com/CalTissue) if you want to get involved somehow.

##### Missing log folders

You'll notice that there are missing log folders. I may add an init function eventually to set up the final folder structure, but for now it's evolving. Here's the current structure:
```
logs/
  error/
  extracted-files/
  scrapelog.txt
  verbose-scrapelog/
```
If you create those folders SCRP will log things correctly.
