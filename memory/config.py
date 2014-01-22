#!/usr/bin/env python
# -*- coding: utf-8 -*-
DEBUG = False
SECRET_KEY = 'secret test'

SQLALCHEMY_DATABASE_URI = 'mysql://admin:123456@localhost/app_lockphp'
SQLALCHEMY_ECHO = False

UPLOADS_DEFAULT_DEST = '//data0/htdocs/fblog/fblog_website/static/'
UPLOADS_DEFAULT_URL = '/static'

CACHE_TYPE = "simple"
CACHE_DEFAULT_TIMEOUT = 300

THEME = 'blue'

USE_LOCAL_COMMENT = True # if false, to include comment.html

ACCEPT_LANGUAGES = ['en', 'zh']

BABEL_DEFAULT_LOCALE = 'zh'
BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'

# http://twitter.com/oauth_clients/new
TWITTER_KEY = ''
TWITTER_SECRET = ''

PER_PAGE = 20

DEBUG_LOG = 'logs/debug.log'
ERROR_LOG = 'logs/error.log'

ADMINS = ('yourname@domain.com',)

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEBUG = DEBUG
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'
DEFAULT_MAIL_SENDER = 'yourname@domain.com'

HOME_URL = '/'
SITE_NAME = u'这是中文'
