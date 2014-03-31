from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from books.forms import *
from books.models import *
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta
import time
from django.db import connection, transaction, DatabaseError, IntegrityError
from django.core.exceptions import *


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
            type0 = borrower.cleaned_data['type']
            name = borrower.cleaned_data['name']
            address = borrower.cleaned_data['address']
            phone = borrower.cleaned_data['phone']
            emailAddress = borrower.cleaned_data['emailAddress']
            sinOrStNo = borrower.cleaned_data['sinOrStNo']
            cursor = connection.cursor()
            try:
                type = BorrowerType.objects.get(type=type0)
            except ObjectDoesNotExist:
                if type0 == 'ST':
                    bookTimeLimit = 14
                elif type0 == 'FA':
                    bookTimeLimit = 84
                elif type0 == 'SF':
					bookTimeLimit = 42
                cursor.execute("INSERT INTO books_borrowertype (type, bookTimeLimit) VALUES ('%s', '%s') " %(type0, bookTimeLimit))
                transaction.commit_on_success()
                type = BorrowerType.objects.get(type=type0)
            
            # we assume the expiry date for every borrower is one year
            expiryDate = date.today() + timedelta(days = 365)
            
            # add borrower table
            borrower_user = Borrower(username = username, password=password,name= name, address=address, phone=phone,emailAddress=emailAddress,sinOrStNo=sinOrStNo, expiryDate = expiryDate, type=type)
            borrower_user.save()
            #try:
            #cursor.execute("INSERT INTO books_borrower (username, password, name, address, phone, emailAddress,sinOrStNo, expiryDate, type) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s) " %(username, password, name, address, phone, emailAddress,sinOrStNo, expiryDate, type))
            #transaction.commit_on_success()
            #except:
            #error = False;
            
            # add borrower accounts
            user = User.objects.create_user(username, None, password)
            user.set_password(password)
            user.save()
            user_type = UserProfile(username=username,type=0)
            user_type.save()
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
    
    
    error = False
    cursor = connection.cursor()
    flag = False
    dueDate =''
    callNumber = 0
    
    if request.method == 'POST':
        checkout = CheckoutForm(request.POST)
        if checkout.is_valid():
            username1 = checkout.cleaned_data['username']
            callNumber = checkout.cleaned_data['callNumber']
            try:
                borrower = Borrower.objects.get(username = username1, expiryDate__gt = date.today())
            except:
                error = True
            else:
                type = borrower.type.type
                
                cursor.execute("SELECT bookTimeLimit  FROM books_borrowertype WHERE type ='%s' " %(type))
                time_limit = cursor.fetchone()[0]
                
                # cursor.execute("SELECT BC.copyNo FROM books_bookcopy as BC WHERE BC.callNumber_id = %s AND BC.status = 'IN'" %(callNumber))
                try:
                    copyNo = BookCopy.objects.filter(callNumber_id = callNumber, status ='IN')[0].copyNo
                except IndexError:
                    error = True
                    copyNo = 'b'
                else:
                    cursor.execute("UPDATE books_bookcopy SET status='OUT' WHERE callNumber_id = %s AND copyNo = %s" %(callNumber, copyNo))
                    
                    dueDate =  date.today() + timedelta(days = time_limit)
                    borrowing = Borrowing(bid = borrower, callNumber_id = callNumber, copyNo_id = copyNo, outDate = date.today(), inDate = None, dueDate = dueDate)
                    borrowing.save()
                    flag = True
        else:
            error = True
    else:
        checkout = CheckoutForm()
    
    return render(request, 'books/clerk/checkout.html', {'logged_in':logged_in, 'username':username, 'type':type, 'checkout':checkout,'error':error, 'dueDate':dueDate, 'callNumber':callNumber, 'flag':flag})

def process_return(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 1:
        return redirect('/rule')
    
    error = False
    flag = False
    dueDate =''
    callNumber = 0
    borrowing = 0
    
    if request.method == 'POST':
        return_form = ReturnForm(request.POST)
        if return_form.is_valid():
            callNumber = return_form.cleaned_data['callNumber']
            copyNo = return_form.cleaned_data['copyNo']
            try:
                borrowing = Borrowing.objects.filter(callNumber_id = callNumber, copyNo_id = copyNo, inDate = None)[0]
            except:
                error = True
            else:
                flag = True
                copy = BookCopy.objects.get(callNumber_id = callNumber, copyNo = copyNo)
                copy.status = 'IN'
                copy.save()
                borrowing.inDate = date.today()
                borrowing.save()
                if borrowing.dueDate <= date.today():
                    delta = (borrowing.dueDate - date.today()).days
                    fine = Fine(amount = delta, issuedDate = date.today(), paidDate = None, borid_id = borrowing.id)
                    fine.save()
                    holds = HoldRequest.objects.filter(callNumber_id = callNumber)
                    if len(holds) > 0:
                        hold = holds[0]
                        hold.delete()
                        book = BookCopy.objects.get(callNumber_id = callNumber, copyNo = copyNo)
                        book.status = 'ON'
                        book.save()
        else:
            error = True
    else:
        return_form = ReturnForm()
    
    return render(request, 'books/clerk/process_return.html', {'logged_in':logged_in, 'username':username, 'type':type, 'return_form':return_form,'error':error, 'dueDate':dueDate, 'callNumber':callNumber, 'flag':flag})


def overdue(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 1:
        return redirect('/rule')
            
    cursor = connection.cursor()
    cursor.execute("SELECT bid_id, callNumber_id, copyNo_id FROM books_borrowing WHERE dueDate < CURTIME()" )
    books = cursor.fetchall()
    return render(request, 'books/clerk/overdue.html', {'logged_in':logged_in, 'username':username, 'type':type, 'books':books})
