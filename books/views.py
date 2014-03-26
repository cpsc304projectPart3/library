from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from books.forms import *
from books.models import *
from django.contrib.auth.decorators import login_required


def index(request):
    username = ''
    logged_in = request.user.is_authenticated()
    if logged_in:
        username = request.user.get_username()

    type = ''
    if logged_in:
        type = UserProfile.objects.get(username = username).type
   
    return render(request, 'books/index.html', 
                  {'logged_in':logged_in, 'username':username, 'type':type})

def sign_up(request):
    registered = False;
    error = False;
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            registered = True
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password1']
            type = user_form.cleaned_data['type']
            user = User.objects.create_user(username, None, password)
            user.set_password(password)
            user.save()
            user_type = UserProfile(username=username,type=type)
            user_type.save()
            user = authenticate(username=username, password=password)
            login(request, user)
        else:
            error = True;
    else:
        user_form = UserForm()

    return render(request, 'books/sign_up.html',
                  {'user_form':user_form,
                   'registered':registered, 'error':error})
                      


def sign_in(request):
    if request.user.is_authenticated():
        return redirect('/')

    error = False;
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
        else:
            error = True;
    return render(request, 'books/sign_in.html', {'error':error})

def user_logout(request):
    logout(request)
    return redirect('/')

def rule(request):
    return render(request, 'books/rule.html')


