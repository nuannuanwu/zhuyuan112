# -*- coding: utf-8 -*-
from django.db.models import get_model
from django.template import Library, Node, TemplateSyntaxError, Variable, resolve_variable,defaultfilters
from django.utils.translation import pgettext, ungettext, ugettext as _
from django.core.urlresolvers import resolve, reverse, get_script_prefix
from django.core.exceptions import ObjectDoesNotExist
from memory import helpers
from django.contrib.comments import Comment
import datetime,time
from django.db.models import Q
from userena.contrib.umessages.models import Message

from django import template
from memory import settings
import re
import inspect

from memory.models import Tile,TileCategory
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
import datetime
# cache
from django.core.cache import cache

try:
    import simplejson as json
except ImportError:
    import json


register = Library()


def is_active(url, arg, has_replied=False):
    if not url:
        return False
    print url
    print arg
    return True


register.filter('is_active', is_active)  #注册该函数，函数名称，过滤函数本身

def bbcode(context, s, has_replied=False):
    if not s:
        return ""
    tag_data = {'has_replied': has_replied}
    html = _postmarkup(s, #cosmetic_replace=False,
            tag_data=tag_data,
            auto_urls=getattr(settings, 'BBCODE_AUTO_URLS', True))
    context['hide_attachs'] = tag_data.get('hide_attachs', [])
    return html

@register.filter
def natural_time(value,time_range="86400"):
    """
    For date and time values in time_range shows how many seconds, minutes or hours ago
    compared to current timestamp returns representing string.
    """
    if not isinstance(value, datetime.date): # datetime is a subclass of date
        return value

    now = datetime.datetime.now()
    delta_time = now + datetime.timedelta(seconds = -int(time_range))
    if value > delta_time and value < now:
        delta = now - value
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s ago'
            ) % {'delta': defaultfilters.timesince(value)}
        elif delta.seconds == 0:
            return _(u'now')
        elif delta.seconds < 60:
            return ungettext(
                u'a second ago', u'%(count)s seconds ago', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                u'a minute ago', u'%(count)s minutes ago', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                u'an hour ago', u'%(count)s hours ago', count
            ) % {'count': count}
    else:
        if value.year == now.year:
            return datetime.datetime.strftime(value,"%m月%d日 %H:%M")
        else:
            return datetime.datetime.strftime(value,"%Y年%m月%d日 %H:%M")

@register.simple_tag(takes_context=True)
def active_checker(context, action, style="active"):
    """
    获取当前页面对应的 ``view`` 名称，高亮对应连接元素

    :param context:
        该请求上下文信息

    :param action:
        当前 url

    :param style:
        高亮样式的命名.
    """
    request = context.get("request")
    path = request.get_full_path()[1:-1].split("/")
    if len(path) > 1:
        path = path[1]
    return "active" if path == action else ""


@register.filter
def belongs_to(value, args):
    """
    某元素是否在列表中.

    :param value:
        任何值

    :param args:
        列表.
    """
    return value in args


@register.simple_tag(takes_context=True)
def media_path(context, image, size="normal"):
    """
    输出可访问图片地址，并对其进行缓存.

    :param context:
        当前上下文

    :param image:
        ImageField 对象

    :param size:
        图像的大小，在 ``settings.py`` 自定义
    """
   

    if isinstance(image, str):       
        return image

    # add cache
    cache_key = "storage_image_"+ str(image) +'_'+size
    #print cache_key,"**********"
    try:
        url = cache.get(cache_key)
        if url:
            return url
    except Exception:
        pass
    
#    try:
#        default_url = image.url
#    except:
    default_url = context.get("STATIC_URL") + context.get("memory_DEFAULT_AVATAR")
        
    if not image:
        return default_url
    try:
        url = image[size].url
        rs = cache.set(cache_key, url)
        return url
    except Exception, e:
        try:
            default_url = image.url
        except:
            pass   
        return default_url


@register.filter
def truncatestr(value, role=":140"):
    """
    截取长字符串

    :param value:
        长字符串

    :param role:
        要截取的个数, 格式: ``:%d``
    """
    role = role.split(":")
    start = int(role[0]) if role[0] else 0
    end = int(role[1]) if role[1] else 0
    tail = " ......" if end < len(value) else ""
    return value[start:end] + tail

@register.filter
def code_to_img(value):
    """
    [: :]格式的表情编码转换为<img>标签
    """
    match = re.findall(r'\[:(\d{3})\:]',value)
    if match:
        for i in range(len(match)):
            pic_num = str(int(match[i]))
            strinfo = re.compile(r'\[:('+match[i]+')\:]')
            url = settings.STATIC_URL+'memory/img/emo/emo/'+ pic_num +'.png'
            b = strinfo.sub('<img src='+url+'>',value)
            value = b
    
    emo = re.findall(r'\[(.*?)\]',value)
    if emo:
        for e in emo:
            
            try:
                pic_url = helpers.emo_config().get(str(e))['url']
            except:
                pic_url = ''
            if pic_url:
                strinfo = re.compile(r'\[('+e+')\]')
                b = strinfo.sub('<img src='+pic_url+'>',value)
                value = b
    
    return value


@register.filter
def code_to_video(value):
    """
    [[ ]]格式的视频编码转换为<video>标签
    """
    try:
        #match = re.findall(r'\[\[(.*?)\]\]',value)
        match = re.findall(r'\[\[([a-zA-z]+://[^\s]*?)\]\]',value)
        if match:
            for i in range(len(match)):
                strinfo = re.compile(r'\[\[('+match[i]+')\]\]')
                html = '<div class="videoDiv"><video class="html5video" controls="controls" width="550" height="380" poster="http://99.pyflask.sinaapp.com/_static/memory/img/bg_video.png"><source src="' + match[i] + '" type="video/mp4" /></video></div>'
                value = strinfo.sub(html,value)
    except:
        pass
    return value


@register.filter
def category_img(value, is_gray):
    """
    匹配日常生活记录图标
    """
    img_class = ''
    if value== 4:
        img_class = 'kq_bg'
    if value== 5:
        img_class = 'tw_bg'
    if value== 6:
        img_class = 'yc_bg'
    if value== 7:
        img_class = 'qx_bg'
    if value== 8:
        img_class = 'pb_bg'
    if value== 101:
        img_class = 'wsh_bg'
    if value== 102:
        img_class = 'hsh_bg'
    if not is_gray:
        img_class = 'gray_' + img_class
    return img_class


@register.filter
def category_report_img(value, is_gray):
    """
    匹配日常生活记录图标
    """
    img_class = ''
    if value== 4:
        img_class = 'kq_bg'
    if value== 5:
        img_class = 'tw_bg'
    if value== 6:
        img_class = 'yc_bg'
    if value== 7:
        img_class = 'qx_bg'
    if value== 8:
        img_class = 'pb_bg'
    if value== 101:
        img_class = 'wsh_bg'
    if value== 102:
        img_class = 'hsh_bg'
    if not is_gray:
        img_class = 'huise_' + img_class
    else:
        img_class = 'zc' + img_class
    return img_class


@register.filter
def liked_by_user(obj, user):
    """
    检查是否被某个用户喜欢，用于家长首页 `Tile` 是否被喜欢的状态.

    :param obj:
        Model 对象, 目前只是 ``Tile`` 对象

    :param user:
        登录用户
    """
    return obj.likes.filter(user=user).exists()


@register.filter
def get_user(obj):
    return obj.user


@register.simple_tag(takes_context=True)
def gen_tag_q(context, tag):
    """
    产生标签请求 url, 详细查看 ``memory.helpers.gen_tile_tag_q``

    :param tag:
        原有的标签请求 url
    """
    tag_q = context.get("tag_q")
    return helpers.gen_tile_tag_q(tag_q, tag.id)


@register.simple_tag(takes_context=True)
def gen_type(context, ty, item):
    """
    产生标签请求 url, 详细查看 ``memory.helpers.gen_tile_tag_q``

    :param ty:
        原有的标签请求 url
    :param item
    get参数名称
    """
    tag_q = context.get(item)
    return helpers.gen_tile_tag_q(tag_q, ty.id)


@register.simple_tag(takes_context=True)
def gen_sel_cat(context, ty, item):
    """
    产生标签请求 url,单选

    :param ty:
        原有的标签请求 url
    :param item
    get参数名称
    """
    tag_q = context.get(item)
    if tag_q == str(ty.id):
        return ''
    return str(ty.id)


@register.simple_tag(takes_context=True)
def gen_exclude_par(context, ty, item):
    """
    产生瓦片分类标签请求 url, 详细查看 ``memory.helpers.gen_tile_tag_q``

    :param ty:
        原有的标签请求 url
    :param item
    get参数名称    
    """
    tag_q = context.get(item)
    tag_list = tag_q.split(",")
    
    # 选中子类时移除父类id
    par_id = ty.parent_id
    try:
        tag_list.remove(str(par_id))
        tag_q = ",".join(tag_list)
    except:
        pass
    return helpers.gen_tile_tag_q(tag_q, ty.id)


@register.simple_tag(takes_context=True)
def gen_exclude_sub(context, ty,category_relation=None):
    """
    产生瓦片分类标签请求 url, 详细查看 ``memory.helpers.gen_tile_tag_q``

    :param ty:
        原有的标签请求 url
    :param item
    get参数名称    
    """
    tag_q = context.get('scat_id')
    tag_list = tag_q.split(",")
    # 选中父类时移除子类id
    for r in category_relation:
        if r['pid'] == ty.id:
            sub_str = r['sid']
      
    sub_list = sub_str.split(",")
    #sub_list = [x.id for x in TileCategory.objects.filter(parent_id=ty.id)]
    pub_list = [item for item in sub_list if str(item) in tag_list]
    for s in pub_list:
        if str(s) in tag_list:
            tag_list.remove(str(s))
    tag_q = ",".join(tag_list)
    return helpers.gen_tile_tag_q(tag_q, ty.id)


@register.assignment_tag(takes_context=True)
def out_of_range(context, image,size="normal",height=800):
    """
    图片高度超过height，在<img>后面加<span>,并设置缓存
    :param image:图片对象
    :param size:图片size
    :param height:指定的高度
    """
    #size="normal"
    #height=800
    attr = helpers.media_attr(image,size)
    if attr:
        if attr['height'] > height:
            return True
    return ''


@register.filter
def in_tag_q(value, tag_q):
    """
    查看某个标签的 id 是否在标签请求参数中.

    :param value:
        ``int``, 某个标签的 id

    :param tag_q:
        ``str``, 原有标签请求参数
    """
    tag_list = tag_q.split(",")
    return str(value) in tag_list


@register.filter
def is_subclass_selected(value, tag_q):
    """
    查看某个父类瓦片分类下有没有子类被选中

    :param value:
        ``int``, 某个父类的 id

    :param tag_q:
        ``str``, 原有子类请求参数
    """
    sub_list = [x.id for x in TileCategory.objects.filter(parent_id=value)]
    tag_list = tag_q.split(",")
    pub_list = [item for item in sub_list if str(item) in tag_list]
    return pub_list

@register.assignment_tag(takes_context=True)
def latest_tiles_by_date(context, year, month, day, max=4):
    """
    根据日期获取该日期最新数条瓦片(Tile), 目前用于日历页

    :param year:
        年

    :param month:
        月

    :param day:
        日

    :param max:
        显示条数.
    """
    request = context.get('request')

    date = datetime.date(year, month, day)

    tiles = Tile.objects.get_tiles_baby(request.user)
    try:
        day_category = TileCategory.objects.get(pk=10)
        if day_category:
            tiles = tiles.exclude(category__parent=day_category)
    except:
        pass
    # for empty string
    # tempalte can pass None type into here
    if not isinstance(max, int):
        max = None
    return tiles.filter(start_time__startswith=date)[:max]

from userena.contrib.umessages.models import MessageContact
@register.assignment_tag(takes_context=True)
def quick_contact_list(context, count=4):
    request = context.get('request')
    queryset = MessageContact.objects.get_contacts_for(request.user)[:count]
    #queryset = MessageContact.objects.get_contacts_for(request.user).filter(latest_message__sender_deleted_at__isnull=True)[:count]
    return queryset


@register.filter
def zfill(value, x=2):
    """
    数值补 0. 如 3 => 03, 3 => 003

    :param value:
        某个数

    :param x:
        位数
    """
    return str(value).zfill(x)


@register.filter
def chinese_weekday(value):
    """
    将星期数字 1 - 7 的数字转换成中文

    :param value:
        某个数字
    """
    c_nums = u'一 二 三 四 五 六 日'
    num_map = {}
    for i, cn in enumerate(c_nums.split()):
        num_map.update({i + 1: cn})

    try:
        return num_map[value]
    except KeyError:
        return value


@register.filter
def isToday(date):
    """
    判断给出的日期是否是当天.

    :param date:
        日期, datetime.date 对象
    """
    return date.date() == datetime.datetime.today().date()


@register.assignment_tag
def daily_setting(desc):
    """
    | 由于日常安排，情绪，评语等瓦片分类都是由 ``json`` 格式组成.
    | 这里会解析 ``json`` 字符串，根据 ``type_id`` 查处对应的数据.

    :param desc:
        json 字符串
    """
    try:        
        daily = json.loads(desc)
        for items in daily.values():
            for i in items:
                type_id = i.get("type_id")
                i['type'] = 1
    except Exception, e:
        print e
        return {}
    return daily


@register.filter
def cut_str(str, length=10):
    """
    截取字符串，使得字符串长度等于length，并在字符串后加上省略号
    """
    is_encode = False
    try:
        str_encode = str.encode('gb18030') #为了中文和英文的长度一致（中文按长度2计算）
        is_encode = True
    except:
        pass
    if is_encode:
        l = length*2
        if l < len(str_encode):
            l = l - 3
            str_encode = str_encode[:l]
            try:
                str = str_encode.decode('gb18030') + '...'
            except:
                str_encode = str_encode[:-1]
                try:
                    str = str_encode.decode('gb18030') + '...'
                except:
                    is_encode = False
    if not is_encode:
        if length < len(str):
            length = length - 2
            return str[:length] + '...'
    return str

# tag for debug in template
print_regex = re.compile(r'^\s*print\s+(.*)$')


def do_print(parser, token):
    m = re.match(print_regex, token.contents)
    if m:
        exp = m.group(1)
        return PrintNode(exp)
    else:
        raise template.TemplateSyntaxError('{% print expression %}')


class PrintNode(template.Node):
    def __init__(self, expression):
        self.expression = expression

    def render(self, context):
        obj = eval(self.expression, {}, context)
        return str(obj)

register.tag('print', do_print)


@register.assignment_tag(takes_context=True)
def get_userena_message_count_for(context, to_user):
    from_user = context.get('request').user
    return Message.objects.get_conversation_between(from_user, to_user).count()



@register.assignment_tag(takes_context=True)
def get_latest_message(context, contact):
    #直接使用 last_message 字段
    message = contact.latest_message
    if message:
        return message
    else:
        return None

    from_user = context.get('request').user
    if from_user == contact.from_user:
        to_user = contact.to_user
    else:
        to_user = contact.from_user

    message = Message.objects.get_conversation_between(from_user, to_user)[:1]
    if message:
        for one in message:
            return one
    else:
        #remove the contact if there is no last message
        contact.delete()

@register.filter
def date_forward(date, days=1):
    """
    向后移动数天

    :param date:
        日期, datetime.date 对象

    :param days:
        移动的天数.
    """
    return date + datetime.timedelta(days=days)

@register.filter
def str_add(value, arg):
    return value + arg

@register.filter
def list(array, num):
    return array[num]

@register.filter
def replace_n(value):    
    result, number = re.subn(r'\n','&nbsp;',value)
    return result

# 判断用户是否具有某个权限
@register.assignment_tag(takes_context=True)
def has_perm(context, p):
    user = context.get('request').user
    return user.has_perm(p)


@register.filter
def add_css(field, css):
    """
    让field添加class
    """ 
    old_css = field.field.widget.attrs.get('class','')
    field.field.widget.attrs['class'] = old_css + ' ' + css
    return field

class ActiverNode(template.Node):
    def __init__(self, activer_name):
        self.activer_set = {
            'care':[
                'home',
                'tile_view',
                'memory_cal',
            ],
            'talk':[
                'userena_umessages_list',
                'user_umessages_history',
                'userena_umessages_quick_contact',
            ],
            'look':[
                'memory_introduction',
            ],
            'schedule':[
                'manage_schedule_teacher',
            ]
        }
        self.activer_name = activer_name

    def render(self, context):
        style = 'hover'
        request = context.get('request')
        try:
            url_name = resolve(request.path).url_name
            # print url_name
            activer_name = self.activer_name
            ac = self.activer_set.get(self.activer_name)
            if ac:
                if url_name in ac:
                    return style
        except Exception, e:
            pass
        return ''

@register.tag
def activer(parser, token):  
    """
    根据某个activer，返回 style
    """
    try:
        tag_name, activer_name = token.split_contents()
    except:       
        raise template.TemplateSyntaxError,\
        "%r 标签语法错误，参数为需要激活的activer" % token.split_contents[0]                    

    return ActiverNode(activer_name)

@register.assignment_tag(takes_context=True)
def is_advanced_user(context, user):
    is_advanced = False

    try:
        if not is_advanced: 
            user.student
            is_advanced = True
    except Exception, e:
        pass

    try:
        if not is_advanced: 
            user.teacher
            is_advanced = True
    except Exception, e:
        pass

    try:
        if not is_advanced: 
            user.mentor
            is_advanced = True
    except Exception, e:
        pass


    return is_advanced

   
