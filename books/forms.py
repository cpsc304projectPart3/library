from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from books.models import *

class UserForm(forms.Form):
    username = forms.CharField(max_length=30)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    type = forms.IntegerField()

    def clean_username(self):
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(("A user with that username already exists."))
        else:
            return self.cleaned_data['username']


    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(("The two password fields didn't match."))
        return self.cleaned_data

TYPE = (
        ('ST', 'student'),
        ('FA', 'faculty'),
        ('SF', 'staff'),
    )


class BorrowerForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput())
    retype_password = forms.CharField(widget=forms.PasswordInput())
    name = forms.CharField(max_length=30)
    address = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=30)
    emailAddress = forms.CharField(widget=forms.EmailInput(),label='email address')
    sinOrStNo = forms.CharField(max_length=10,label='SIN or st.no')
    type = forms.ChoiceField(widget=forms.RadioSelect, choices=TYPE)

    def clean_username(self):
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(("A user with that username already exists."))
        else:
            return self.cleaned_data['username']

    def clean(self):
        if 'password' in self.cleaned_data and 'retype_password' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['retype_password']:
                raise forms.ValidationError(("The two password fields didn't match."))
        return self.cleaned_data


class BookForm(forms.Form):
    isbn = forms.CharField(max_length = 30, label ='isbn')
    title = forms.CharField(max_length = 30, label='title')
    mainAuthor = forms.CharField(max_length = 30, label ='main author')
    publisher = forms.CharField(max_length = 30, label='publisher')
    year = forms.IntegerField(min_value = 800,label='year')
    subject = forms.CharField(max_length = 10, label = 'subject')
