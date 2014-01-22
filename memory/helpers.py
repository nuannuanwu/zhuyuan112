# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
import simplejson
import datetime
import calendar
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.contrib.sites.models import Site
from memory.settings import CTX_CONFIG, STATIC_URL
from django.contrib.auth.models import User
from memory import settings

from django.core.mail import send_mail
from django.core.mail import EmailMessage 

try:
    import simplejson as json
except ImportError:
    import json
    
import sys
reload(sys)
sys.setdefaultencoding('utf8') 
    
SITE_INFO = Site.objects.get_current()
# from memory.profiles.models import Profile as Profiles


def get_redir_url(request):
    """
    获得跳转url， 默认为 GET 参数优先， 如果为空，则返回上次访问页面的url
    """
    redir = request.GET.get("redir")
    if not redir:
       redir = request.META['HTTP_REFERER']
    return redir



def HttpResponseAjax(message='',con='',type='ok',notification='true',forwardUrl='',callbackType='',code='100000'):

    result = {
        "type":type,
        "message":message,
        "notification":notification,
        "callbackType":callbackType,
        "forwardUrl":forwardUrl,
        "code":code,
        "con":con
    }
    result = simplejson.dumps(result)
    return HttpResponse(result)

def ajax_ok(message,con='',type='ok',notification='true',forwardUrl='',callbackType='',code='100000'):
    """
    封装ajax 返回json
    """
    return HttpResponseAjax(message,con,type,notification,forwardUrl,callbackType,code=code)

def ajax_error(message,con='',type='error',notification='true',forwardUrl='none',callbackType='none', code='100000'):
    """
    封装ajax 返回json
    """
    return HttpResponseAjax(message,con,type,notification,forwardUrl,callbackType,code=code)


def gen_tile_tag_q(tag_q, tag_id=None):
    """
    | 应用场景: 多选标签，可反选.
    | 这个 helper 用于重新组装标签: 清除重复项(反选)

    **args/kwargs**

    * *tag_q:*  url 投递的标签参数, 类似于: "1,2,3,4"
    * *tag_id:*  当前点击的标签，选择或者反选
    """
    tag_list = tag_q.split(",")
    if tag_id:
        tag_list.append(str(tag_id))
    tag_list = filter(None, tag_list)
    tag_list = [x for x in tag_list if tag_list.count(x) == 1]
    tag_q = ",".join(tag_list)
    return tag_q


def clean_birthday_rang(birth_date):
    """
    用于 form 校验. 检查输入的日期，限定日期范围: 1800-07-05 ~ 当前日期

    **args**

    * *birth_date:* ``datetime.date`` 对象
    """
    if not birth_date:
        return birth_date
    least = datetime.datetime.strptime("1800-07-05", "%Y-%m-%d")
    if birth_date > datetime.datetime.today().date() or birth_date <= least.date():
        raise forms.ValidationError(_("Out of range: 1800-07-05 ~ Today"))
    return birth_date


def calculate_age(birth_date):
    """
    根据日期计算用户年龄

    **args**

    * *birth_date:* ``datetime.date`` 对象
    """
    if not birth_date:
        return ""

    today = datetime.date.today()
    # Raised when birth date is February 29 and the current year is not a
    # leap year.
    try:
        birthday = birth_date.replace(year=today.year)
    except ValueError:
        day = today.day - 1 if today.day != 1 else today.day + 2
        birthday = birth_date.replace(year=today.year, day=day)

    age = today.year - birth_date.year
    return age - 1 if birthday > today else age


def move_month(when, direction="+"):
    """
    向前或者向后移动一个月. 处理了跨年的情况.

    **kwargs**

    * *when:* 日期: *datetime.date* 对象
    * *direction:* "+" => 加一个月，"-" => 减一个月.

    """
    days = calendar.monthrange(when.year, when.month)[1]
    if direction == "+":
        return when + datetime.timedelta(days=days)
    else:
        first_day = datetime.date(day=1, month=when.month, year=when.year)
        prev_month_end = first_day - datetime.timedelta(days=1)
        return prev_month_end

def return_query(request):
    """
    在分页的时候可以使用，返回去掉page后的querystring

    **kwargs**

    * *request:* request对象   

    """    
    query_string = request.GET.copy()

    if 'page' in query_string:
        del query_string['page']
    if len(query_string.keys()) > 0:
        new_query_string = "&%s" % query_string.urlencode()
    else:
        new_query_string = ''
    return new_query_string

def pagination(request,objects,per_page_num):
    """
    view中分页用

    **kwargs**

    * *request:* request对象   
    * *objects:* 分页列表对象
    * *per_page_num:* 每页记录数  

    """    
    query = return_query(request)

    paginator = Paginator(objects,per_page_num)

    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    return objects,query

class CookbookHelper(object):
    """docstring for CookbookHelper"""
    def __init__(self, arg):
        super(CookbookHelper, self).__init__()
        self.arg = arg

    @staticmethod
    def get_items():
        item = [
            'breakfast',
            'light_breakfast',
            'lunch',
            'light_lunch',
            'dinner',
            'light_dinner'
        ]
        return item

def mark_cookbook_as_read(request,cookbook):
    from memory.models import CookbookRead
    if request.user and cookbook:
        is_read = CookbookRead.objects.set_cookbook_unread(user=request.user,cookbook=cookbook)
    return None

def media_path(image, size="normal"):
    """
    将 ImageField 的内容转换成可访问的图片地址.
    加入了缓存机制

    **args/kwargs**

    * *image:*  ImageField 对象
    * *size:*  图片大小，在 setting.py 设置
    """
    # add cache
    cache_key = "storage_image_" + str(image) + '_' + size
    #print cache_key,"**********"
    try:
        url = cache.get(cache_key)
        if url:
            return url
    except Exception:
        pass

    if not image:
        return ''
    try:
        url = image[size].url
        cache.set(cache_key, url)
        return url
    except Exception:
        return ''


def media_attr(image, size="normal"):
    """
    将 ImageField 的内容转换成可访问的图片地址.
    加入了缓存机制

    **args/kwargs**

    * *image:*  ImageField 对象
    * *size:*  图片大小，在 setting.py 设置
    """
   
    cache_key = "storage_image_attr_" + str(image) + '_' + size
    try:
        attr = cache.get(cache_key)
        if attr:
            return attr
    except Exception:
        pass

    if not image:
        return None
    try:
        width = image[size].image.size[0]
        height = image[size].image.size[1]
        attr = {'width':width,'height':height}
        cache.set(cache_key, attr)
        return attr
    except Exception:
        return None
    
    
def get_domain():
    current_site = Site.objects.get_current()
    return current_site.domain

def get_avatar(size='large'):
    # domain = get_domain()

    avatar_url = CTX_CONFIG['DEFAULT_AVATAR'] if size == 'small' else CTX_CONFIG['DEFAULT_AVATAR_LARGE']
    # full_url = "http://"+ domain + STATIC_URL + avatar_url
    full_url = STATIC_URL + avatar_url

    return full_url

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def emo_config():
    emo = {
           "惊讶":{"code":"[:000:]","title":"惊讶","url":settings.STATIC_URL+'memory/img/emo/emo/0.png'},
           "撇嘴":{"code":"[:001:]","title":"撇嘴","url":settings.STATIC_URL+'memory/img/emo/emo/1.png'},
           "色":{"code":"[:002:]","title":"色","url":settings.STATIC_URL+'memory/img/emo/emo/2.png'},
           "发呆":{"code":"[:003:]","title":"发呆","url":settings.STATIC_URL+'memory/img/emo/emo/3.png'},
           "得意":{"code":"[:004:]","title":"得意","url":settings.STATIC_URL+'memory/img/emo/emo/4.png'},
           "哭":{"code":"[:005:]","title":"哭","url":settings.STATIC_URL+'memory/img/emo/emo/5.png'},
           "闭嘴":{"code":"[:007:]","title":"闭嘴","url":settings.STATIC_URL+'memory/img/emo/emo/7.png'},
           "睡":{"code":"[:008:]","title":"睡","url":settings.STATIC_URL+'memory/img/emo/emo/8.png'},
           "大哭":{"code":"[:009:]","title":"大哭","url":settings.STATIC_URL+'memory/img/emo/emo/9.png'},
           "呲牙":{"code":"[:013:]","title":"呲牙","url":settings.STATIC_URL+'memory/img/emo/emo/13.png'},
           "微笑":{"code":"[:014:]","title":"微笑","url":settings.STATIC_URL+'memory/img/emo/emo/14.png'},
           "难过":{"code":"[:015:]","title":"难过","url":settings.STATIC_URL+'memory/img/emo/emo/15.png'},
           "偷笑":{"code":"[:020:]","title":"偷笑","url":settings.STATIC_URL+'memory/img/emo/emo/20.png'},
           "白眼":{"code":"[:022:]","title":"白眼","url":settings.STATIC_URL+'memory/img/emo/emo/22.png'},
           "饥饿":{"code":"[:024:]","title":"饥饿","url":settings.STATIC_URL+'memory/img/emo/emo/24.png'},
           "困":{"code":"[:025:]","title":"困","url":settings.STATIC_URL+'memory/img/emo/emo/25.png'},
           "惊恐":{"code":"[:026:]","title":"惊恐","url":settings.STATIC_URL+'memory/img/emo/emo/26.png'},
           "流汗":{"code":"[:027:]","title":"流汗","url":settings.STATIC_URL+'memory/img/emo/emo/27.png'},
           "憨笑":{"code":"[:028:]","title":"憨笑","url":settings.STATIC_URL+'memory/img/emo/emo/28.png'},
           "奋斗":{"code":"[:030:]","title":"奋斗","url":settings.STATIC_URL+'memory/img/emo/emo/30.png'},
           "晕":{"code":"[:034:]","title":"晕","url":settings.STATIC_URL+'memory/img/emo/emo/34.png'},
           "再见":{"code":"[:039:]","title":"再见","url":settings.STATIC_URL+'memory/img/emo/emo/39.png'},
           "猪头":{"code":"[:046:]","title":"猪头","url":settings.STATIC_URL+'memory/img/emo/emo/46.png'},
           "拥抱":{"code":"[:049:]","title":"拥抱","url":settings.STATIC_URL+'memory/img/emo/emo/49.png'},
           "蛋糕":{"code":"[:053:]","title":"蛋糕","url":settings.STATIC_URL+'memory/img/emo/emo/53.png'},
           "咖啡":{"code":"[:060:]","title":"咖啡","url":settings.STATIC_URL+'memory/img/emo/emo/60.png'},
           "饭":{"code":"[:061:]","title":"饭","url":settings.STATIC_URL+'memory/img/emo/emo/61.png'},
           "太阳":{"code":"[:074:]","title":"太阳","url":settings.STATIC_URL+'memory/img/emo/emo/74.png'},
           "月亮":{"code":"[:075:]","title":"月亮","url":settings.STATIC_URL+'memory/img/emo/emo/75.png'},
           "强":{"code":"[:076:]","title":"强","url":settings.STATIC_URL+'memory/img/emo/emo/76.png'},
           "握手":{"code":"[:078:]","title":"握手","url":settings.STATIC_URL+'memory/img/emo/emo/78.png'},
           "胜利":{"code":"[:079:]","title":"胜利","url":settings.STATIC_URL+'memory/img/emo/emo/79.png'},
           "西瓜":{"code":"[:089:]","title":"西瓜","url":settings.STATIC_URL+'memory/img/emo/emo/89.png'},
           "乒乓":{"code":"[:115:]","title":"乒乓","url":settings.STATIC_URL+'memory/img/emo/emo/115.png'},
           "示爱":{"code":"[:116:]","title":"示爱","url":settings.STATIC_URL+'memory/img/emo/emo/116.png'},
           "抱拳":{"code":"[:118:]","title":"抱拳","url":settings.STATIC_URL+'memory/img/emo/emo/118.png'},
           "拳头":{"code":"[:120:]","title":"拳头","url":settings.STATIC_URL+'memory/img/emo/emo/120.png'},
           "OK":{"code":"[:124:]","title":"OK","url":settings.STATIC_URL+'memory/img/emo/emo/124.png'},
           }
    #return json.dumps(emo)
    return emo
       
def send_staff_mobile(mobile,msg): 
    from memory.models import Sms
    mes = Sms()
    mes.sender_id = 1
    mes.receiver_id = -1
    mes.mobile = mobile
    mes.type_id = 99
    mes.content = msg
    mes.save()
    return True
    

def send_staff_email(email,msg):
    email_list = []
    email_list.append(email)
    try:
        send_mail(SITE_INFO.name + '未读提醒', msg, settings.EMAIL_HOST_USER, email_list)
        return True
    except:
        return False


class StaffTrans:
    """
    发送职员提醒处理
    """
    _msg = False
    
    def __init__(self):
        pass

    def run(self):
        pass

    def memory_notice_to_staff(self,staff_id,unread_mentors,unread_waiters):
        """
        发送一名职员提醒
        """
        from memory.models import RelevantStaff   
        try:
            s = RelevantStaff.objects.get(id=staff_id)
            if s.send_mentor and unread_mentors and s.email:
                msg = "<" + SITE_INFO.name + ">导师留言后台有" + str(unread_mentors) + "条新客户留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('aq')
                send_staff_email(s.email,msg)
            if s.send_waiter and unread_waiters and s.email:
                msg = "<" + SITE_INFO.name + ">客服后台有" + str(unread_waiters) + "条新客服留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('waiter')
                send_staff_email(s.email,msg)

        except:
            pass

