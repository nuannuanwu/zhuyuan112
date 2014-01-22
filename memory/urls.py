# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from memory import settings
from memory.forms import KSignupForm, KChangeEmailForm, KEditProfileForm, KAuthenticationForm


# handler404 = "memory.views.errors.handler404"
handler500 = "memory.views.errors.handler500"

urlpatterns = patterns("memory.views.frontend",
        url('^index/$', "index", name="home"),
        url(r'^$', "index", name='home'),
        url('^tile/(?P<tile_id>\d+)/$', "view", name='tile_view'),
        url(r'^get_user_info/$', "get_user_info", name="memory_get_user_info"), 
        url(r'^vcar/$', "vcar", name="memory_vcar"),
        url('^tile/comment/(?P<comment_id>\d+)/delete/$', "delete_comment", name='tile_delete_comment'),
)
                       
# 找回密码各项
urlpatterns += patterns("memory.views.account",
    url(r'^accounts/pwd_back_mail/$', "pwd_back_mail", name="memory_pwd_back_mail"),
    url(r'^accounts/pwd_back_mail_done/$', "pwd_back_mail_done", name="memory_pwd_back_mail_done"),
    url(r'^accounts/pwd_back_mail_reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
     'pwd_back_mail_reset',
   name='memory_pwd_back_mail_reset'),


    url(r'^accounts/pwd_back_mobile/$', "pwd_back_mobile", name="memory_pwd_back_mobile"),
    url(r'^accounts/pwd_back_mobile_get_vcode/$', "pwd_back_mobile_get_vcode", name="memory_pwd_back_mobile_get_vcode"),

    url(r'^accounts/pwd_back_pwd_reset/$', "pwd_back_pwd_reset", name="memory_pwd_back_pwd_reset"),
    url(r'^accounts/pwd_back_success/$', "pwd_back_success", name="memory_pwd_back_success"),        
)
urlpatterns += patterns('',                
    url(r'^admin/', include('memory.views.admin.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),
    # # Edit profile
    url(r'^accounts/(?P<username>[\.\w]+)/edit/$',
       "userena.views.profile_edit", {'edit_profile_form': KEditProfileForm},
       name='userena_profile_edit'),
    url(r'^account_setting/$', 'userena.views.account_setting', name="userena_account_setting"),
    url(r'^accounts/signup/$',
       "userena.views.signup", {'signup_form': KSignupForm},
       name='userena_signup'),
    # Change email and confirm it
    url(r'^accounts/(?P<username>[\.\w]+)/email/$',
       "userena.views.email_change", {"email_form": KChangeEmailForm},
       name='userena_email_change'),
    url(r'^accounts/signin/$',
       "userena.views.signin", {"auth_form": KAuthenticationForm},
       name='userena_signin'),
    (r'^accounts/', include('userena.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^manage/', include('manage.urls')),
    (r'^photologue/', include('photologue.urls')),

    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/_static/img/favicon.ico'}),

)

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)

urlpatterns += patterns('memory.views.test',
    url(r'^tests/', 'test'),
)

urlpatterns += patterns('',
    # media 目录
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
        'django.views.static.serve', {"document_root": settings.MEDIA_ROOT}),
)

urlpatterns += patterns('',
    # media 目录
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:],
        'django.views.static.serve', {"document_root": settings.STATIC_ROOT}),
)

if settings.DEBUG is False:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
