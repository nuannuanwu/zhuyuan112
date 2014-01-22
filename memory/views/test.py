# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from memory import helpers
from django.conf import settings
from memory.models import Tile
from django.core.urlresolvers import resolve, reverse
import sys, socket 
import oss.oss_api
import oss.oss_util
from oss_extra.storage import AliyunStorage

def test(request):
    oss = AliyunStorage()
    dir = oss.listdir()
    print dir
    tile_list = [t.img for t in Tile.objects.all()]
    n = 0
    for i in dir:
        if  i.startswith('tiles'):
            t = Tile()
            t.creator_id = 1
            t.user_id = 1
            t.img = i
            t.title = 'beauty_' + str(n)
            t.save()
            n = n + 1
    return HttpResponse()



