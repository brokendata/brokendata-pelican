#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Ryan Wheeler'
SITENAME = u'Broken Data'
SITEURL = ''

PATH = 'content'
TIMEZONE = 'Europe/Paris'


DEFAULT_LANG = u'en'
DISPLAY_PAGES_ON_MENU =False
DEFAULT_CATEGORY = 'Blog'

MENUITEMS = (
            ('About','/index.html'),)


THEME = 'pelican-bootstrap3'
# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)
NOTEBOOK_DIR = '/home/ryan/site/brokendata/notebooks/'
DEFAULT_PAGINATION = 10
PLUGIN_PATHS = 'pelican-plugins'
PLUGINS = ['liquid_tags.img', 'liquid_tags.video',
           'liquid_tags.youtube', 'liquid_tags.vimeo',
           'liquid_tags.include_code', 'liquid_tags.notebook']
# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
