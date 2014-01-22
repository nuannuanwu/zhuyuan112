# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models

# from django.utils.translation import ugettext as _
from memory.models import Tile,TileCategory,Friend,Website
from oauth2app.models import Client, AccessToken, Code

from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.admin import widgets, helpers
from django.contrib.admin.util import unquote

from memory.widgets import AdminImageWidget
from memory import settings
from django.contrib.comments import Comment
from django.core.urlresolvers import reverse  
 
class TileAdmin(admin.ModelAdmin):
    
    class Media:
        js = (
              settings.STATIC_URL + 'media/js/tinymce/jscripts/tiny_mce/tiny_mce.js',
              settings.STATIC_URL + 'media/js/textareas.js',
         )
    search_fields = ('title','description')
    date_hierarchy = 'start_time'
    list_display = ('title','category','is_public','user','creator','n_likers', 'picture','start_times','end_times')
    list_filter = ('is_public','category','creator','user')
    prepopulated_fields = {"description": ("title",)}
    readonly_fields = ('n_likers',)
    ordering = ['-start_time']

    def start_times(self, obj):
        return obj.start_time.strftime('%Y-%m-%d %H:%M:%S')
    start_times.short_description = '起始时间'
    start_times.admin_order_field = 'start_time'

    def end_times(self, obj):
        return obj.end_time.strftime('%Y-%m-%d %H:%M:%S')
    end_times.short_description = '结束时间'
    end_times.admin_order_field = 'end_time'


class WebsiteAdmin(admin.ModelAdmin):
    
    search_fields = ('name','domain','uname')
    list_display = ('name','domain','uname','start','edit')
    ordering = ['-ctime']

    def start(self, obj):
        return obj.ctime.strftime('%Y-%m-%d %H:%M:%S')
    start.short_description = '创建时间'
    start.admin_order_field = 'start'

    def edit(self, obj):
        return obj.mtime.strftime('%Y-%m-%d %H:%M:%S')
    edit.short_description = '修改时间'
    edit.admin_order_field = 'edit'

admin.site.register(Tile,TileAdmin)
admin.site.register(TileCategory)
admin.site.register(Friend)
admin.site.register(Website,WebsiteAdmin)





