# -*- coding: utf-8 -*-

from django.core.validators import RegexValidator, EmailValidator, validate_email, email_re
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import re

_mobile_re = re.compile(r'^0{0,1}(13[0-9]|15[0-9]|18[0-9])[0-9]{8}$')
validate_mobile_number = RegexValidator(_mobile_re, _(u'Enter a valid mobile number.'), 'invalid')

# _email_re = re.compile(r'^[_A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$')
# _email_re = re.compile(r'^\w+@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$')
# _email_re = re.compile(
#     r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
#     # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
#     r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
#     r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$)'  # domain
#     r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3)

# FIXME: not needed anymore, using the django default email validate
memory_validate_email = RegexValidator(email_re, _(u'Enter a valid e-mail address.'), 'invalid')


def validate_not_spaces(value):
    """
    校验字段是否空白字符，如空格制表符等.
    """
    if value.strip() == '':
        raise ValidationError(_(u"You must provide more than just whitespace."))

def user_is_exist(value):
    from memory.models import Friend
    is_exist = Friend.objects.filter(user_id=value,is_delete=True).count()
    if is_exist:
        raise ValidationError(_(u"具有 User 的 Friend 已存在。")) 