# -*- coding: utf-8 -*-

from django.forms import ModelForm, CharField, PasswordInput
from django import forms
from bootstrap.forms import BootstrapForm, Fieldset, BootstrapMixin
from memory.models import ChangeUsername
from memory.profiles.models import Profile
from django.utils.translation import ugettext as _
from memory.validators import validate_mobile_number
from django.contrib.auth.models import User
from userena import settings as userena_settings
from memory import helpers

class ChangeUsernameForm(BootstrapForm):
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput({'class': 'required'}),
                                label=_("Username"),
                                error_messages={'invalid': _('Username must contain only letters, numbers and underscores.')})

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already in use.
        Also validates that the username is not listed in
        ``USERENA_FORBIDDEN_USERNAMES`` list.

        """
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            pass
        else:
            raise forms.ValidationError(_('This username is already taken.'))
        if self.cleaned_data['username'].lower() in userena_settings.USERENA_FORBIDDEN_USERNAMES:
            raise forms.ValidationError(_('This username is not allowed.'))
        return self.cleaned_data['username']

    def save(self, user):
        user.username = self.cleaned_data['username']
        change = ChangeUsername(user_id = user.id,name = self.cleaned_data['username'])
        change.save()
        # import datetime
        # user.get_profile().update_username_at = datetime.date.today()
        user.save()
