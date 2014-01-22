# -*- coding: utf-8 -*-
from django.conf.urls import patterns,  url

urlpatterns = patterns('',
    url(r'^login/$', 'manage.views.admin.login', name='manage_login'),
    url(r'^change_username/$', 'manage.views.admin.change_username', name="manage_change_username")
)

