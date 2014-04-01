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
        ('ST', 'Student'),
        ('FA', 'Faculty'),
        ('SF', 'Staff'),
    )


class BorrowerForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput())
    retype_password = forms.CharField(widget=forms.PasswordInput())
    name = forms.CharField(max_length=30)
    address = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=30)
    emailAddress = forms.CharField(widget=forms.EmailInput(),label='Email Address')
    sinOrStNo = forms.CharField(max_length=10,label='SIN or Student Number')
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
        existing2 = Borrower.objects.filter(sinOrStNo=self.cleaned_data['sinOrStNo'])
        if existing2.exists():
            raise forms.ValidationError(("A user with that sinOrStNo already exists."))
        else:
            return self.cleaned_data['sinOrStNo']
        return self.cleaned_data


class BookForm(forms.Form):
    isbn = forms.CharField(max_length = 30, label ='ISBN')
    title = forms.CharField(max_length = 30, label='Title')
    mainAuthor = forms.CharField(max_length = 30, label ='Main Author (First Last)')
    publisher = forms.CharField(max_length = 30, label='Publisher')
    year = forms.IntegerField(min_value = 800,label='Year')
    subject = forms.CharField(max_length = 30, label = 'Subject')

class CheckoutForm(forms.Form):
    username = forms.CharField(max_length = 30, label ='Borrower Username')
    callNumber = forms.IntegerField(min_value = 1, label='Call Number')


class ReturnForm(forms.Form):
    callNumber = forms.IntegerField(min_value = 1, label='Call Number')
    copyNo = forms.IntegerField(min_value = 1, label = 'Copy Number')

class HoldForm(forms.Form):
    callNumber = forms.IntegerField(min_value = 1, label = 'Book Call Number')

KTYPE = (
        ('T', 'title'),
        ('A', 'author'),
        ('S', 'subject'),
    )
    
class SearchForm(forms.Form):
    key_word = forms.CharField(max_length = 30, label='Key word')
    key_word_type = forms.ChoiceField(widget=forms.RadioSelect, choices=KTYPE)
    


class PopularForm(forms.Form):
    year = forms.IntegerField(min_value = 2000, label = 'Year')
    limit = forms.IntegerField(min_value = 1, label = 'Max. number of books')

