# -*- coding: utf-8 -*-


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from volute.models import Many

class LoginForm(forms.Form):
    username = forms.CharField(label=u'Имя пользователя', required=True)
    password = forms.CharField(label=u'Пароль', widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        if not self.errors:
            user = auth.authenticate(username=cleaned_data['username'], password=cleaned_data['password'])
            if user is None:
                raise forms.ValidationError(u'Имя пользователя и пароль не подходят')
            self.user = user
        return cleaned_data

    def get_user(self):
        return self.user or None

class RegForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
             user.save()
        return user

class AddForm(forms.ModelForm):
    class Meta:
        model = Many
        fields = ['date', 'sum', 'comment', 'category']

    def __init__(self, **kwargs):
        queryset = kwargs.pop("queryset")
        super(AddForm, self).__init__(**kwargs)
        self.fields['category'].queryset = queryset

class DateForm(forms.Form):
    date_start = forms.DateField(label=u'Дата начала периода')
    date_end = forms.DateField(label=u'Дата окончания периода')

    def clean(self):
        cd = super(DateForm, self).clean()
        if not self.errors:
            if cd['date_start'] > cd['date_end']:
                raise forms.ValidationError(u'Дата начала периода не может быть больше даты окончания периода')
        return cd

class EmailForm(forms.Form):
    name = forms.CharField(label=u'Ваше имя')
    email = forms.EmailField(label=u'Ваш email')
    subj = forms.CharField(label=u'Тема')
    text = forms.CharField(widget=forms.Textarea,label=u'Введите текст письма')