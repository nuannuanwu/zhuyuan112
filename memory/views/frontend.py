# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from memory.helpers import get_redir_url,media_path
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.comments import Comment
from django.contrib.comments.views.moderation import perform_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib import comments
from django.contrib.auth.decorators import login_required, permission_required
from memory.models import Tile,TileCategory,Friend
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from memory import helpers
import datetime,calendar,time
from django.http import Http404
from django.http import HttpResponse
from memory import helpers
from django.contrib.auth.models import User
from django.core.cache import cache
from memory.settings import STATIC_URL,CTX_CONFIG
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from memory.forms import MobileForm, PwdResetForm, PwdMobileForm
from memory.profiles.models import Profile
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import get_current_site
from django.db import connection
from django.http import Http404
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.models import Site
try:
    import simplejson as json
except ImportError:
    import json

import random
from django.db.models import Max

def index(request, template_name="memory/tile_index.html"):
    ctx ={}
    tile_list = []
    friends = Friend.objects.all()
    q = request.GET.get("q",'')
    if not q:
        tiles = Tile.objects.filter(is_public=True)
    else:
        if q == 'all':
            userid_list = [f.user_id for f in friends]
            tiles = Tile.objects.filter(user_id__in=userid_list)
        else:
            tiles = Tile.objects.filter(user_id=q)
            q = int(q)
    ctx['tiles'] = tiles
    ctx['friends'] = friends
    ctx['q'] = q
    if request.is_ajax():
        page = int(request.GET.get("page",'1'))
        start = (page - 1) * 15
        end = page * 15
        tiles = tiles[start:end]
        ctx['tiles'] = tiles
        template_name = "memory/tile_index_container.html"
        return render(request, template_name, ctx)
    return render(request, template_name, ctx)


@login_required
def get_user_info(request):
    """ 鼠标移动到头像，显示用户详情信息 """
    uid = request.GET.get('uid')
    if not uid:
        return helpers.ajax_error('失败')
    uid = int(uid)
    try:
        user = User.objects.get(pk=uid)
    except Exception, e:
        return helpers.ajax_error('失败')
    
    try:       
        pro = user.get_profile()       
        about_me = pro.about_me
        user_name = pro.chinese_name_or_username()       
        image = pro.mugshot
        if not pro.can_view_profile(request.user): about_me = ''
    except Exception, e:      
        image = ''
        about_me = ''
        user_name = user.username

    url = media_path(image)    
    # 消息对话链接    
    talk_link = reverse('user_umessages_history',kwargs={'uid':user.id})
    show_talk = True if user.id != request.user.id else False
    info = {
        "about_me":about_me,
        "user_name":user_name,
        "avatar":url,
        "talk_link":talk_link,
        "show_talk":show_talk
    }
    return helpers.ajax_ok('成功',con=info)

@login_required
def vcar(request, template_name="memory/includes/vcar.html"):
    """ 鼠标移动到头像，显示用户详情信息 """
    uid = request.GET.get('uid')
    if not uid:
        return helpers.ajax_error('失败')
    uid = int(uid)
    try:
        user = User.objects.get(pk=uid)
    except Exception, e:
        return helpers.ajax_error('失败')
    
    is_mentor = False
    try:       
        pro = user.get_profile()
        is_mentor = pro.is_mentor
        if is_mentor:
            about_me = user.mentor.description
            appellation = user.mentor.appellation
        else:
            appellation = ''
            about_me = pro.about_me
        user_name = pro.chinese_name_or_username()       
        image = pro.mugshot
        if not pro.can_view_profile(request.user): about_me = ''
    except Exception, e: 
        appellation = ''     
        image = ''
        about_me = ''
        user_name = user.username
    
    url = media_path(image, size="avatar")   
    url = url if url else STATIC_URL + CTX_CONFIG['DEFAULT_AVATAR']
    
    # 消息对话链接    
    talk_link = reverse('user_umessages_history',kwargs={'uid':user.id})
    show_talk = True if user.id != request.user.id else False
    info = {
        "uid":uid,    
        "about_me":about_me,
        "user_name":user_name,
        "avatar":url,
        "user":user,
        "is_mentor":is_mentor,
        "talk_link":talk_link,
        "show_talk":show_talk,
        "appellation":appellation
    }
    data = render(request, template_name, info)
    con=data.content
    return helpers.ajax_ok('成功',con)

def view(request, tile_id, template_name="memory/tile_view.html"):
    ctx = {}
    tile = get_object_or_404(Tile, pk=tile_id)
    q = request.GET.get("q",'')
    if not q:
        tiles = Tile.objects.filter(is_public=True)
    else:
        if q == 'all':
            friends = Friend.objects.all()
            userid_list = [f.user_id for f in friends]
            tiles = Tile.objects.filter(user_id__in=userid_list)
        else:
            tiles = Tile.objects.filter(user_id=q)

    try:
        last_tile = tiles.filter(microsecond__gt=tile.microsecond).order_by("start_time","microsecond")[0]  
    except:
        last_tile = None
    try:
        next_tile = tiles.filter(microsecond__lt=tile.microsecond).order_by("-start_time","-microsecond")[0]      
    except:
        next_tile = None

    comments = Comment.objects.for_model(tile).select_related('user')\
            .order_by("-submit_date").filter(is_public=True).filter(is_removed=False)
    emo_config = helpers.emo_config()
    ctx.update({"tile": tile,"comments":comments,"emo_config":emo_config,"next_tile":next_tile,"last_tile":last_tile,"q":q})
    return render(request, template_name, ctx)

def delete_comment(request, comment_id):

    comment = get_object_or_404(comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)
    if request.user == comment.user:
        perform_delete(request, comment)
        comment.content_object.after_del_comments()
        messages.success(request, _("Comment deleted success"))
    else:
        messages.error(request, _("You can't delete this comment"))

    # Flag the comment as deleted instead of actually deleting it.
    return redirect(get_redir_url(request))

