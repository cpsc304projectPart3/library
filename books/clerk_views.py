from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from books.forms import *
from books.models import *
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta
import time

def clerk(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 1:
        return redirect('/rule')
    
    return render(request, 'books/clerk.html', {'logged_in':logged_in, 'username':username, 'type':type})

# clerk methods
def add_borrower(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username1 = request.user.get_username()
    type = UserProfile.objects.get(username = username1).type
    if type != 1:
        return redirect('/rule')

    registered = False
    error = False
    if request.method == 'POST':
        borrower = BorrowerForm(request.POST)
        if borrower.is_valid():
            username = borrower.cleaned_data['username']
            password = borrower.cleaned_data['password']
            type = borrower.cleaned_data['type']
            name = borrower.cleaned_data['name']
            address = borrower.cleaned_data['address']
            phone = borrower.cleaned_data['phone']
            emailAddress = borrower.cleaned_data['emailAddress']
            sinOrStNo = borrower.cleaned_data['sinOrStNo']
            type = BorrowerType.objects.get(type=type)
            expiryDate = date.today() + timedelta(days = 365)

            # add borrower accounts
            user = User.objects.create_user(username, None, password)
            user.set_password(password)
            user.save()
            user_type = UserProfile(username=username,type=0)
            user_type.save()

            # add borrower table
            borrower_user = Borrower(username = username, password=password,name= name, address=address, phone=phone,emailAddress=emailAddress,sinOrStNo=sinOrStNo, expiryDate = expiryDate, type=type)
            borrower_user.save()
            registered = True
        else:
            error = True;

    else:
        borrower = BorrowerForm()

    return render(request, 'books/clerk/add_borrower.html', {'logged_in':logged_in, 'username':username1, 'type':type, 'error':error, 'borrower':borrower, 'registered':registered})


def checkout(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 1:
        return redirect('/rule')

    return render(request, 'books/clerk/checkout.html', {'logged_in':logged_in, 'username':username, 'type':type})

def process_return(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 1:
        return redirect('/rule')

    return render(request, 'books/clerk/process_return.html', {'logged_in':logged_in, 'username':username, 'type':type})

def overdue(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 1:
        return redirect('/rule')

    return render(request, 'books/clerk/overdue.html', {'logged_in':logged_in, 'username':username, 'type':type})
