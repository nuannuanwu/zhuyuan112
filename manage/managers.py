# -*- coding: utf-8 -*-
# from memory.models import Group
from django.db import models
from django.contrib.auth.models import User
from userena.models import UserenaSignup
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
# from memory.models import Tile
# from caching.base import CachingMixin, CachingManager
# cache
from django.core.cache import cache
from memory.helpers import CookbookHelper
from memory import helpers

import random
import datetime
from memory import settings
import os
from django.db import transaction


class SoftDeleteManager(models.Manager):
    '''
    | 给所有的查询过滤 ``is_delete`` 字段.
    '''
    use_for_related_fields = True
    def get_query_set(self):
        ''' 重写默认 ``Manager`` 获取 ``QuerySet`` 的对象，过滤已标记为删除的记录 '''
        return super(SoftDeleteManager, self).get_query_set().filter(is_delete=False)

    def all_with_deleted(self):
        ''' 满足需要获得已标记为删除的记录的需求 '''
        return super(SoftDeleteManager, self).get_query_set()

    def deleted_set(self):
        ''' 获得已标记为删除的记录 '''
        return super(SoftDeleteManager, self).get_query_set().filter(is_delete=True)

    #def get(self, *args, **kwargs):
    #    ''' if a specific record was requested, return it even if it's deleted '''
    #    return self.all_with_deleted().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        ''' if pk was specified as a kwarg, return even if it's deleted '''
        if 'is_delete' in kwargs:
            return self.all_with_deleted().filter(*args, **kwargs)
        return self.get_query_set().filter(*args, **kwargs)


class SchoolUserManager(models.Manager):

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the address by lowercasing the domain part of the email
        address.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email



    def create_user(self, username=None, email=None, password=123456):
        """
        Creates and saves a User with the given username, email and password.
        """
        prefix = 'u'
        latest = User.objects.latest('id')
        username = "%s%d" % (prefix, latest.id + 1)
        if User.objects.filter(username = username).count():
            username += '_'+str(random.randint(1,999))
        user = UserenaSignup.objects.create_user(username, email, password, active=True,send_email=True)
        return user

class TileCategoryManager(SoftDeleteManager):

    def get_q_layer(self, layer=None):
        """
        【base - layer】返回主类，子类,以及所有的
        """

        if layer == 'parent':
            q = Q(parent__pk=0)
        elif layer == 'sub':
            q = ~Q(parent__pk=0)
        else:
            q = Q()

        return q

    def get_q_tips(self, tips=None):
        """
        【base - tips】返回推荐，baby,以及所有的
        """

        q = Q(is_tips=tips) if tips != None else Q()

        return q

    def get_q_identity(self, identity=None):
        """
        【base - tips】返回身份，以及所有的
        """

        if identity == 'teacher':
            q = ~(Q(parent__pk=10) | Q(pk=10))
        else:
            q = Q()    

        return q
        

    def get_category(self, layer=None, tips=None, identity=None):
        """
        根据条件，来获取组合分类
        """

        q_layer = self.get_q_layer(layer)
        q_tips = self.get_q_tips(tips)
        q_identity = self.get_q_identity(identity)

        q = q_layer & q_tips & q_identity

        return self.filter(q)


    def get_one_parent_sub(self, parent_id):
        """
        获得一个主类的子类
        """
        tc = self.get(pk=parent_id)

        assert tc.is_parent       

        return self.filter(parent__pk=parent_id)
    

class TileManager(SoftDeleteManager):
    """
    【瓦片等级划分
        1.来自教师的(is_tips=0)
            - 接收对象为个人（user）
            - 接收对象为班级(group)
        2.来自后台推广的（is_tips=1）
            - 接收对象（个人，班级，全部（null））
            - vip（家长用户，is_public 划分）
    】瓦片等级划分
    """

    def get_q_base(self):
        """
        得到基本的限制（start_time,endtime）
        """

        now = datetime.datetime.now()

        return Q(start_time__lte=now, end_time__gte=now)

    def get_q_user(self, user):
        """
        【接收对象 - user or group】得到某个用户的瓦片,可能是个人的，或所属班级的
        """

        q_base = self.get_q_base()

        try:
            group = user.student.group
            if group:
                q = Q(group=group) | Q(user=user)
            else:
                q = Q(user=user)
        except ObjectDoesNotExist:
            q = Q(user=user)

        return q_base & q

    def get_q_all(self):
        """
        【接收对象 - 所有用户 】得到所有用户的瓦片
        """

        q_base = self.get_q_base()
        return q_base
        q = Q(user__isnull=True, group__isnull=True)

        return q_base & q
    
    def get_q_category(self, category=None):
        """
        #【接收对象 - 所有用户 】返回主类，子类tile
        """
        
        if category:
            c = category[0]
            q = Q(category=c) if c.parent_id else Q(category__parent=c)
        else:
            q = Q()
        return q

    def get_q_user_from_teacher(self, user):
        """
        【baby】【瓦片 - 个人或是班级 - 来自教师的】得到某个用户的瓦片,来自教师的
        """
       
        q_user = self.get_q_user(user)
        q = Q(is_tips=0)
        return q_user & q

    def get_q_user_from_recommend(self, user):
        """
        【瓦片 - 个人 - 来自推荐的】得到某个用户的瓦片,来自推荐的
        """
       
        q_user = self.get_q_user(user)
        q = Q(is_tips=1)
        return q_user & q



    def get_q_all_unlogin(self):
        """
        【全部 - 未登录】【教育信息-未登录】得到未登录所有用户的推荐瓦片
        """
        q_all = self.get_q_all()
        q = Q(is_tips=1, is_public=True)

        return q_all & q        

    def get_q_recommend_login(self, user):
        """
        【教育信息】得到已登录用户的推荐瓦片，对vip进行限制
        """
        q_all = self.get_q_all()
        #q_user = self.get_q_user(user)

        if user.get_profile().is_vip:
            q = Q(is_tips=1)
        else:
            q = Q(is_tips=1, is_public=True)

        return q_all & q

    def get_q_all_login(self, user):
        """
        【全部 - 已登录】获得用户以及推荐的所有瓦片
        """
        q_baby = self.get_q_user_from_teacher(user)
        q_recommend = self.get_q_recommend_login(user)

        return q_baby | q_recommend

#========================================

    def get_tiles_all_unlogin(self):
        """
        【全部 - 未登录】的瓦片（未登录的教育信息）
        """
        q = self.get_q_all_unlogin()
        return self.filter(q)

    def get_tiles_all_login(self, user):
        """
        【全部 - 已登录】的瓦片
        """
        q = self.get_q_all_login(user)
        return self.filter(q)

    def get_tiles_baby(self, user):
        """
        【baby】的瓦片
        """
        q = self.get_q_user_from_teacher(user)
        return self.filter(q)

    def get_tiles_edu(self, user):
        """
        【edu】的瓦片
        """
        q = self.get_q_recommend_login(user)
        return self.filter(q)




    def get_tiles_date(self, date, tiles):
        """
        过滤出某天发布的瓦片
        """
        date = datetime.date(date.year, date.month, date.day)
        q = Q(start_time__startswith=date)       

        return tiles.filter(q).reverse()

    def get_tiles_date_grater(self, date, tiles):       
        q = Q(start_time__gte=date)
        return tiles.filter(q)

    def get_tiles_date_less(self, date, tiles):      
        q = Q(start_time__isnull=False, start_time__lte=date)       
        return tiles.filter(q)




    def create_tile(self, user, title, content,creator=None, type=None, group=None):
        """
        添加一个瓦片
        """
        prefix = 'u'
        latest = User.objects.latest('id')
        username = "%s%d" % (prefix, latest.id + 1)
        user = UserenaSignup.objects.create_user(username, email, password, active=True,send_email=True)
        return user

    def count_unread_tiles_for(self, user):
        """
        baby的瓦片的最后一条
        """

        try:
            last_tile_pk = self.get_user_last_tile(user)

            last_tile = self.get(pk=last_tile_pk)
            last_time = last_tile.start_time
            
            baby_tiles = self.get_tiles_baby(user)            

            count = baby_tiles.filter(start_time__gt=last_time).count()

            return count
        except Exception, e:
            return 0   

    def count_unread_push_tiles_for(self, user):
        """
        推荐的瓦片的最后一条
        """

        try:
            last_tile_pk = self.get_user_last_tile(user)

            last_tile = self.get(pk=last_tile_pk)
            last_time = last_tile.start_time
            
            edu_tiles = self.get_tiles_edu(user)            

            count = edu_tiles.filter(start_time__gt=last_time).count()

            return count
        except Exception, e:            
            return 0        

    def set_user_last_tile(self,user,last_tile_id):
        #cache_key = "user_last_tile_"+ str(user.id)
        try:
            rs = user.last_tile
            last_tile_old_id = self.get_user_last_tile(user)
            if last_tile_id > last_tile_old_id:
                rs.last_tile_id = last_tile_id
                rs.save()
                return True
        except Exception:
            tile = super(TileManager, self).get_query_set().latest('id')
            tile.creat_user_last_tile(user.id, last_tile_id)
            return True

    def get_user_last_tile(self,user):
        #cache_key = "user_last_tile_"+ str(user.id)
        #print cache_key,"**********"
        last_tile_id = 0        
        try:
            last_tile = user.last_tile
            if last_tile:
                last_tile_id = last_tile.last_tile_id
        except Exception:
            pass

        return last_tile_id  

      


class SmsManager(SoftDeleteManager):
    def create_sms(self, sender, receiver, mobile=None,content=None, type_id=None):
        """
        添加一条短信
        """
        sms = self.model(sender=sender, receiver=receiver,
                          mobile=mobile, content=content, type_id=type_id,
                          is_send=0)

        sms.save(using=self._db)
        return sms

    def create_send_account_sms(self, sender, receiver, mobile=None,content=None):
        """
        发送一条发送账号密码的短信。类型为100，（所有类型查看model说明）
        """        
        return self.create_sms(sender,receiver,mobile,content,type_id=100)

    def create_verify_sms(self, sender, receiver, mobile=None,content=None):
        """
        发送一条手机验证的短信。类型为101，（所有类型查看model说明）
        """        
        return self.create_sms(sender,receiver,mobile,content,type_id=101)

    def not_send_yet_sms(self):
        """
        返回未发送的短信
        """
        now = datetime.datetime.now()
        sms = self.filter(is_send=0,is_delete=0, is_active=1,send_time__lt=now).exclude(mobile='')
        return sms


class SmsSendManager(SoftDeleteManager):
    def not_send_yet_sms2gate(self):
        """
        返回未发送到电信端口的短信
        """
        now = datetime.datetime.now()
        sms_list = self.filter(is_deal=False,is_delete=False,send_date__lt=now)
        return sms_list


class CookbookSetManager(models.Manager):

    def get_set(self, school = None,):
        """
        得到某学校食谱设置
        """
        cookbook_set_items = {
                'breakfast':{
                    'is_show':True,
                    'name':'早餐'
                },
                'light_breakfast':{
                    'is_show':True,
                    'name':'早点'
                },
                'lunch':{
                    'is_show':True,
                    'name':'午餐'
                },
                'light_lunch':{
                    'is_show':True,
                    'name':'午点'
                },
                'dinner':{
                    'is_show':True,
                    'name':'晚餐'
                },
                'light_dinner':{
                    'is_show':True,
                    'name':'晚点'
                },
        }
        if school:
            cookbook_set = self.filter(school = school)
            
            items = CookbookHelper.get_items()

            if cookbook_set.count() > 0:
                for item in items:
                    cookbook_set_items[item]['is_show'] = getattr(cookbook_set[0], item)

        return cookbook_set_items

class CookbookManager(models.Manager):

    def get_items(self,):
        return CookbookHelper.get_items()

    def get_cookbook_date(self, date, group = None, school = None):
        """
        返回具体某天的学校或班级食谱
        """

        school_cookbook_day = self.filter(school=school,date=date)
        # group_cookbook_day = self.filter(group=group,date=date)

        cur_day_con = {
            'year':date.year,
            'month':date.month,
            'day':date.day,
            'is_pub':False,
            'con':{
                'breakfast':{
                    'con':'',
                    'comefrom':'school'
                },
                'light_breakfast':{
                    'con':'',
                    'comefrom':'school'
                },
                'lunch':{
                    'con':'',
                    'comefrom':'school'
                },
                'light_lunch':{
                    'con':'',
                    'comefrom':'school'
                },
                'dinner':{
                    'con':'',
                    'comefrom':'school'
                },
                'light_dinner':{
                    'con':'',
                    'comefrom':'school'
                },
            },
            'items':[]
        } 

        school_pub = True if school_cookbook_day.count() > 0 else False
        # group_pub = True if group_cookbook_day.count() > 0 else False

        items = CookbookHelper.get_items()

        # school
        if not group:
            if school_pub:
                cur_day_con['is_pub'] = True

                for item in items: 
                    school_con = getattr(school_cookbook_day[0], item)        

                    cur_day_con['con'][item]['con'] = school_con
                    cur_day_con['con'][item]['comefrom'] = 'school' 
        # group
        else:     
            group_cookbook_day = self.filter(group=group,date=date)
            group_pub = True if group_cookbook_day.count() > 0 else False
              
            if school_pub or group_pub:
                cur_day_con['is_pub'] = True               

                for item in items:                 

                    group_con = getattr(group_cookbook_day[0], item) if group_pub else ''
                    school_con = getattr(school_cookbook_day[0], item) if school_pub else ''               

                    # 读取班级
                    if group_con != '':
                        cur_day_con['con'][item]['con'] = group_con
                        cur_day_con['con'][item]['comefrom'] = 'group'

                    # 读取学校
                    else:
                        cur_day_con['con'][item]['con'] = school_con
                        cur_day_con['con'][item]['comefrom'] = 'school' 

        return cur_day_con


class CookbookreadManager(models.Manager):
    """设置单个用户食谱已读状态"""
    def set_cookbook_unread(self,user,cookbook,ty='read'):
        cookbookread = self.filter(user=user,cookbook=cookbook,date=cookbook.date)
        if cookbookread:
            if ty=="read" and not cookbookread[0].is_read:
                cookbookread[0].is_read = True
                cookbookread[0].save(using=self._db)
                return True
            else:
                return False
        else:
            if ty == "send":
                is_read = False
                is_send = True
                read_at = None
            else:
                print ty,'iiiii'
                is_read = True
                is_send = False
                read_at = datetime.datetime.now()
                
            cookbookread = self.model(user=user,cookbook=cookbook,date=cookbook.date,is_send=is_send,is_read=is_read,read_at=read_at)
            cookbookread.save(using=self._db)
            return True
    
    
class VerifySmsManager(models.Manager):
    def get_valid_vsms(self, user):
        """
        获得某个用户的验证短信，无效，或是没有验证码返回None。有效期30分钟
        """        
        vsms = self.filter(user=user,is_active=True)

        if vsms.count() > 0:
            vsms = vsms.latest('ctime')
            time = vsms.ctime
            now = datetime.datetime.now()

            minutes = (now - time).seconds/60
           
            if minutes < 30:
                return vsms
        return None

    def get_vcode(self, user):
        """
        获得某个用户的验证码，无效，或是没有验证码返回None。有效期30分钟
        """
        vsms = self.get_valid_vsms(user)

        if vsms:
            return vsms.vcode
        return None

    def set_vcode_invalid(self, user):
        """
        设置某个用户验证短信无效。
        """
        vsms = self.filter(user=user,is_active=True)

        for v in vsms:
            v.is_active = False
            v.save()

class CharManager(models.Manager):
    def generate(self):
        """
        生成char表
        """
        if self.count() == 0:
            f = open(os.path.join(settings.FILE_PATH,'chars.txt'),'r')
            chars = f.read().decode('utf-8').replace('"','').split(',')
            f.close()

            with transaction.commit_manually():
                for c in chars:
                    cn =c.split(' ')[0]
                    en = c.split(' ')[1]
                    entry = self.model(cn=cn, en=en)
                    entry.save()
                transaction.commit()

    def trans(self, name=''):
        """
        中文字符转换成拼音

        中文就转换，找不到的中文，添加进char表上，等待翻译。非中文，直接添加，不加空格
        """

        pinyin =''
        for c in name:
            is_cn = helpers.is_chinese(c)

            if not is_cn:
                pinyin += c

            else:
                char = self.get_or_create(cn=c)[0].en
                if not char:
                    char = c
                pinyin += char+' '

        return pinyin
       












