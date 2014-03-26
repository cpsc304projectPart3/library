from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from books.forms import *
from books.models import *
from django.contrib.auth.decorators import login_required

def borrower(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    
    if type != 0:
        return redirect('/rule')

    return render(request, 'books/borrower.html', {'logged_in':logged_in, 'username':username, 'type':type})


def search(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    
    if type != 0:
        return redirect('/rule')

    return render(request, 'books/borrower/search.html', {'logged_in':logged_in, 'username':username, 'type':type})

def check_account(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    
    if type != 0:
        return redirect('/rule')

    return render(request, 'books/borrower/check_account.html', {'logged_in':logged_in, 'username':username, 'type':type})

def hold(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    
    if type != 0:
        return redirect('/rule')

    return render(request, 'books/borrower/hold.html', {'logged_in':logged_in, 'username':username, 'type':type})

def pay(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    
    if type != 0:
        return redirect('/rule')

    return render(request, 'books/borrower/pay.html', {'logged_in':logged_in, 'username':username, 'type':type})

