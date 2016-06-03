#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

from functools import partial

AUTHOR = "amazingant"
SITENAME = "Tech Babble"
SITEDESC = "the random musings of a techie"
SITEURL = ""
TIMEZONE = "Etc/UTC"
DEFAULT_LANG = "en"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"

# Pelican's generator says that I probably don't want these? And I don't really
# disagree.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Links and social stuff -- Following the example code for https://eev.ee,
# adding a bit of extra information not typically present here
LINKS_EX = (
    (
        "Blag",
        "/blog/",
        "#00A3C0",
        "gir.png",
        "The babbling about tech that you're here for"
    ),
)

SOCIAL_EX = (
    (
        "Twitter",
        "https://twitter.com/amazingant",
        "#66757F",
        "others/twitter-logo.png",
        "I twit on tweeter sometimes? Usually to complain about something."
    ),(
        "GitHub",
        "https://github.com/amazingant/",
        "#4078c0",
        "others/octocat.png",
        "Many useless bits of code I've written can be found here"
    )
)

TWITTER_USERNAME = "amazingant"
GITHUB_URL = "https://github.com/amazingant/"

# Back to site config

SEARCH_BOX = False
DEFAULT_PAGINATION = 10
DEFAULT_ORPHANS = 4
PAGINATION_PATTERNS = (
    (1, "{base_name}/", "{base_name}/index.html"),
    (2, "{base_name}/page/{number}/", "{base_name}/page/{number}/index.html")
)

THEME = "theme"
MD_EXTENSIONS = [
    # GitHub-style fenced code blocks
    "fenced_code"
]

PATH = "content/"
PAGE_PATHS = ["../pages/"]
PATH_METADATA = "../pages/(?P<fullpath>.+)[.].+"
STATIC_PATHS = ["favicon.png", "media/"]

TEMPLATE_PAGES = {
    "../theme/templates/home.html": "index.html",
    "../theme/templates/wp-archives.php": "wp-archives/index.php",
}


# URL Schema
ARCHIVES_URL = "everything/archives/"
ARCHIVES_SAVE_AS = "everything/archives/index.html"
ARTICLE_URL = "{category}/{date:%Y}/{date:%m}/{date:%d}/{slug}/"
ARTICLE_SAVE_AS = "{category}/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html"
AUTHOR_SAVE_AS = False
CATEGORIES_URL = "everything/categories/index.html"
CATEGORIES_SAVE_AS = "everything/categories/index.html"
CATEGORY_URL = "{slug}/"
CATEGORY_SAVE_AS = "{slug}/index.html"
# This is the blog's index, not the main site's index
INDEX_SAVE_AS = "everything/index.html"
INDEX_URL = "everything/"
PAGE_URL = "{fullpath}/"
PAGE_SAVE_AS = "{fullpath}/index.html"
TAG_URL = "everything/tags/{slug}/"
TAG_SAVE_AS = "everything/tags/{slug}/index.html"
TAGS_URL = "everything/tags/"
TAGS_SAVE_AS = "everything/tags/index.html"
FILENAME_METADATA = "(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.*)"

JINJA_FILTERS = dict(
    sort_by_article_count=partial(
        sorted,
        key=lambda pairs: len(pairs[1]),
        reverse=True,
    ),
)
