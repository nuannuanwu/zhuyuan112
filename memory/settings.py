# -*- coding: utf-8 -*-
import os.path
######################
# MEZZANINE SETTINGS #
######################
APP_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.dirname(APP_DIR))

GRAPPELLI_ADMIN_TITLE = 'memory'

SITE_TITLE = 'memory'

ADMINS = (
	# ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

TIME_ZONE = None

#时区设置
TIME_ZONE = 'Asia/Shanghai'

#设置django界面语言
LANGUAGE_CODE = 'zh-cn'

LANGUAGES = (
	('zh_CN', 'Chinese Simplified'),
	('en', 'English'),
)

DEBUG = False

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SITE_ID = 1

USE_I18N = True

USE_L10N = True

INTERNAL_IPS = ("127.0.0.1",)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	"django.template.loaders.filesystem.Loader",
	"django.template.loaders.app_directories.Loader",
)

AUTHENTICATION_BACKENDS = (
	'userena.backends.UserenaAuthenticationBackend',
	'guardian.backends.ObjectPermissionBackend',
	'django.contrib.auth.backends.ModelBackend',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	"django.contrib.staticfiles.finders.FileSystemFinder",
	"django.contrib.staticfiles.finders.AppDirectoriesFinder",
#	'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

try:
	import sae.const
except:
	pass
from os import environ

#根据环境定义数据库连接参数
islocalhost = not environ.get("APP_NAME","")

if islocalhost:
	mysql_name = 'zhuyuan'
	mysql_user = 'root'
	mysql_pass = ''
	mysql_host = '127.0.0.1'
	mysql_port = '3306'
	mysql_host_s = '127.0.0.1'
	DEBUG = True
else:#sae上
	mysql_name = sae.const.MYSQL_DB
	mysql_user = sae.const.MYSQL_USER
	mysql_pass = sae.const.MYSQL_PASS
	mysql_host = sae.const.MYSQL_HOST
	mysql_port = sae.const.MYSQL_PORT
	mysql_host_s = sae.const.MYSQL_HOST_S
	DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
	"default": {
		# Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
		"ENGINE": "django.db.backends.mysql",
		# DB name or path to database file if using sqlite3.
		"NAME": mysql_name,
		# Not used with sqlite3.
		"USER": mysql_user,
		# Not used with sqlite3.
		"PASSWORD": mysql_pass,
		# Set to empty string for localhost. Not used with sqlite3.
		"HOST": mysql_host,
		# Set to empty string for default. Not used with sqlite3.
		"PORT": mysql_port,
		'OPTIONS': {
            'init_command': 'SET storage_engine=MyISAM',
        },
	},
	"master": {
		# Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
		"ENGINE": "django.db.backends.mysql",
		# DB name or path to database file if using sqlite3.
		"NAME": mysql_name,
		# Not used with sqlite3.
		"USER": mysql_user,
		# Not used with sqlite3.
		"PASSWORD": mysql_pass,
		# Set to empty string for localhost. Not used with sqlite3.
		"HOST": mysql_host,
		# Set to empty string for default. Not used with sqlite3.
		"PORT": mysql_port,
		'OPTIONS': {
            'init_command': 'SET storage_engine=MyISAM',
        },
	},
	"slave": {
		# Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
		"ENGINE": "django.db.backends.mysql",
		# DB name or path to database file if using sqlite3.
		"NAME": mysql_name,
		# Not used with sqlite3.
		"USER": mysql_user,
		# Not used with sqlite3.
		"PASSWORD": mysql_pass,
		# Set to empty string for localhost. Not used with sqlite3.
		"HOST": mysql_host_s,
		# Set to empty string for default. Not used with sqlite3.
		"PORT": mysql_port,
		'OPTIONS': {
            'init_command': 'SET storage_engine=MyISAM',
        },
	}		
}
class DataBaseRouter(object):
	"""
	A router to control all database operations.
	"""
	def db_for_read(self, model,  *args, **kwargs):
		"""
		Attempts to read.
		"""
		return "slave"

	def db_for_write(self, model,  *args, **kwargs):
		"""
		Attempts to write .
		"""
		return "master"
	   
	def allow_relation(self, obj1, obj2, **hints):
		"Allow any relation between two objects in the db pool"
		db_list = ('master','slave')
		if obj1._state.db in db_list and obj2._state.db in db_list:
			return True
		return None

	def allow_syncdb(self, db, model):
		"Explicitly put all models on all databases."
		return True
	   
	   
DATABASE_ROUTERS = [DataBaseRouter()]

import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]

CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_DIRNAME

MEDIA_ROOT = os.path.join(PROJECT_DIR, '_media')
MEDIA_URL = '/_media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, '_static')
STATIC_URL = '/_static/'


FILE_PATH = os.path.join(PROJECT_ROOT, 'file')

ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"

ROOT_URLCONF = "%s.urls" % PROJECT_DIRNAME

TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates"),)


################
# APPLICATIONS #
################

INSTALLED_APPS = (
	'grappelli',
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.redirects",
	"django.contrib.sessions",
	"django.contrib.sites",
	"django.contrib.sitemaps",
	"django.contrib.staticfiles",

	'django.contrib.comments',
	'django.contrib.markup',
	'django.contrib.humanize',

	"sae_extra",
	"oss",
	"oss_extra",
	#"debug_toolbar",
	# 主程序
	'memory',
	'manage',

	# 分页功能
	'pagination',
	# 用户扩展信息
	'memory.profiles',
	'bootstrap',
	# 前台用户注册登录功能 + 附加message
	'userena', 'guardian', 'easy_thumbnails', 'userena.contrib.umessages',
	
	# 喜欢功能
	'likeable',
	'storages',
	# 'piston'
	'bootstrapform',
	'captcha',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	# 可以在模板使用 user 和 perms
	"django.contrib.auth.context_processors.auth",
	"django.contrib.messages.context_processors.messages",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.static",
	"django.core.context_processors.media",
	"django.core.context_processors.request",

	# 配置全局变量
	"memory.context_processors.ctx_config",
)

# 在 memory.context_processors.ctx_config 会读取以下配置
CTX_CONFIG = {
	'memory_TITLE':u'记忆童年',
	'memory_TAGLINE':u'成长',
	'memory_SUB_TITLE':u'童年',
	'STUDENT_PAGE_SIZE': 50,
	'memory_PAGE_SIZE': 6,
	'memory_DEFAULT_AVATAR':'img/avatar_128.png',
	'memory_DEFAULT_GROUP_IMG':'img/group_128.png',
	'DEFAULT_AVATAR':'img/avatar_64.png',
	'DEFAULT_AVATAR_LARGE':'img/avatar_128.png',
}


MIDDLEWARE_CLASSES = (
	"django.middleware.common.CommonMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.redirects.middleware.RedirectFallbackMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	# gzip
	'django.middleware.gzip.GZipMiddleware',
	'pagination.middleware.PaginationMiddleware',
)

PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"


AUTHENTICATION_BACKENDS = (
	'userena.backends.UserenaAuthenticationBackend',
	'guardian.backends.ObjectPermissionBackend',
	'django.contrib.auth.backends.ModelBackend',
)

OAUTH2_ACCESS_TOKEN_EXPIRATION = 3600*24*30

THUMBNAIL_ALIASES = {
	'': {
		'mini': {'size': (48, 48), 'crop': True},
		'small': {'size': (64, 64)},
		'normal': {'size': (192, 0), 'crop': True},
		'big': {'size': (384, 0), 'crop': True},
		"large": {'size':(650,0)},
		"avatar": {'size':(64,64)},
		"avatar_normal": {'size':(128,128)},
		"avatar_large": {'size':(192, 192)},
	},
}

LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'
AUTH_PROFILE_MODULE = 'profiles.Profile'

USERENA_DISABLE_PROFILE_LIST = True
USERENA_MUGSHOT_SIZE = 140
USERENA_REDIRECT_ON_SIGNOUT = '/'
USERENA_SIGNIN_REDIRECT_URL = '/'

# Guardian
ANONYMOUS_USER_ID = -1

EMAIL_BACKEND = 'sae_extra.smtp.EmailBackend'
# email config
EMAIL_HOST='smtp.sina.com'
EMAIL_PORT=25
EMAIL_HOST_USER='yii4sae@sina.com'
EMAIL_HOST_PASSWORD='123456'
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'yii4sae@sina.com'

CACHEMACHINE_DEPEND_SILENC = True

CACHE_COUNT_TIMEOUT = 3600
THUMBNAIL_SUBDIR = "thumbs"
THUMBNAIL_EXTENSION = "png"

try:
	if not islocalhost:
		THUMBNAIL_DEFAULT_STORAGE = 'sae_extra.storage.SaeStorage'
		DEFAULT_FILE_STORAGE =  'sae_extra.storage.SaeStorage'

		CACHES = {
			'default': {
				'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
				'LOCATION': '127.0.0.1:11211',
				'TIMEOUT': 3600*24*30
			},
			'database': {
				'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
				'LOCATION': 'django_cache',
				'TIMEOUT': 3600*24*30
			}	

		}

		#GRIDFS_DATABASE = 'mongodb_storage'
		OSS_ACCESS_KEY_ID = 'bAHPulP6qvCmtEqk'
		OSS_SECRET_ACCESS_KEY = 'VquojH5AO6oE0hmDzhJp9qq7iTzLyl'
		OSS_HOST = 'oss.aliyuncs.com'
	else:
		CACHES = {
		    'default': {
		        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
		        'LOCATION': 'django_cache',
		        'TIMEOUT': 3600*24*30
		    }
		}

		EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
		DEFAULT_FILE_STORAGE = 'oss_extra.storage.AliyunStorage'
		THUMBNAIL_DEFAULT_STORAGE = 'oss_extra.storage.AliyunStorage'
		#GRIDFS_DATABASE = 'mongodb_storage'
		OSS_ACCESS_KEY_ID = 'bAHPulP6qvCmtEqk'
		OSS_SECRET_ACCESS_KEY = 'VquojH5AO6oE0hmDzhJp9qq7iTzLyl'
		OSS_HOST = 'oss.aliyuncs.com'

except:
	pass

#########################
# OPTIONAL APPLICATIONS #
#########################

# These will be added to ``INSTALLED_APPS``, only if available.
OPTIONAL_APPS = (
	"django_extensions",
	"compressor",
	PACKAGE_NAME_FILEBROWSER,
	PACKAGE_NAME_GRAPPELLI,
)

# debug 功能
#DEBUG_TOOLBAR_PANELS = (
#	'debug_toolbar.panels.version.VersionDebugPanel',
#	'debug_toolbar.panels.timer.TimerDebugPanel',
#	'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
#	'debug_toolbar.panels.headers.HeaderDebugPanel',
#	'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
#	'debug_toolbar.panels.template.TemplateDebugPanel',
#	'debug_toolbar.panels.sql.SQLDebugPanel',
#	'debug_toolbar.panels.signals.SignalDebugPanel',
#	'debug_toolbar.panels.logger.LoggingPanel',
#)

INTERNAL_IPS = ('127.0.0.1','183.15.162.124','192.168.1.110')
#DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False,'HIDE_DJANGO_SQL': False,}

#############
# piston
############
PISTON_IGNORE_DUPE_MODELS = True
# PISTON_DISPLAY_ERRORS = True


##################
# LOCAL SETTINGS #
##################


SEND_ACCOUNT_TIMEDELTA = 300
CHANGE_USERNAME_TIMEDELTA = 2592000
####################
# DYNAMIC SETTINGS #
####################
NOTIFY_USE_JSONFIELD =True

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y年m月d日 H点i分'