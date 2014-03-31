from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from books.forms import *
from books.models import *
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction, DatabaseError, IntegrityError
from datetime import date, datetime, timedelta
import time
from django.core.exceptions import *


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


    flag = False
    error = False
    books = {}
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            flag = True
            key_word = form.cleaned_data['key_word']
            type = form.cleaned_data['key_word_type']
            
            cursor = connection.cursor()
            if type == 'A':
                cursor.execute("SELECT bk.id, bk.title, COUNT(bk.id) as num FROM books_book bk, books_bookcopy bc WHERE bc.callNumber_id = bk.id AND bc.status = 'IN' AND bc.callNumber_id IN (SELECT callNumber_id FROM books_hasauthor WHERE name LIKE '%s') GROUP BY bk.id" %(key_word))
            if type == 'T':
                cursor.execute("SELECT bk.id, bk.title, COUNT(bk.id) as num FROM books_book bk, books_bookcopy bc WHERE bc.callNumber_id = bk.id AND bc.status = 'IN' AND bk.title LIKE '%s' GROUP BY bk.id" %(key_word))
            if type == 'S':
                cursor.execute("SELECT bk.id, bk.title, COUNT(bk.id) as num FROM books_book bk, books_bookcopy bc WHERE bc.callNumber_id = bk.id AND bc.status = 'IN' AND bc.callNumber_id IN (SELECT callNumber_id FROM books_hassubject WHERE subject LIKE '%s') GROUP BY bk.id" %(key_word))

            books = cursor.fetchall()
        else:
            error = True
    else:
        form = SearchForm()


    return render(request, 'books/borrower/search.html', {'logged_in':logged_in, 'username':username, 'type':type, 'flag':flag, 'form':form, 'error':error, 'books':books})

def check_account(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    
    if type != 0:
        return redirect('/rule')

    books = Borrowing.objects.filter(bid_id = username, inDate = None)
    cursor = connection.cursor()
    cursor.execute("SELECT amount, issuedDate FROM books_fine f, books_borrowing br WHERE f.paidDate IS NULL AND f.borid_id = br.id AND br.bid_id = '%s'" %(username))
    fines = cursor.fetchall()

    holds = HoldRequest.objects.filter(bid_id = username)

    return render(request, 'books/borrower/check_account.html', {'logged_in':logged_in, 'username':username, 'type':type, 'books':books,'fines':fines,'holds':holds})

def hold(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    
    if type != 0:
        return redirect('/rule')

    error = False
    flag = False
    callNumber = 0

    if request.method == 'POST':
        hold = HoldForm(request.POST)
        if hold.is_valid():
            callNumber = hold.cleaned_data['callNumber']

            book1 = Book.objects.filter(pk = callNumber).count()
            book2 = BookCopy.objects.filter(callNumber_id = callNumber, status = 'IN').count()
            if book1 == 0 or book2 > 0:
                error = True
            else:
            # book unavailable, request ok
                flag = True
                hold_request = HoldRequest(bid_id = username, callNumber_id = callNumber, issuedDate = date.today())
                hold_request.save()
        else:
            error = True
    else:
        hold = HoldForm()


    return render(request, 'books/borrower/hold.html', {'logged_in':logged_in, 'username':username, 'type':type, 'error':error, 'flag':flag, 'hold':hold, 'callNumber':callNumber})

def pay(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    
    if type != 0:
        return redirect('/rule')

    cursor = connection.cursor()
    cursor.execute("UPDATE books_fine SET paidDate = '%s' WHERE borid_id IN (SELECT br.id FROM books_borrowing br WHERE bid_id = '%s')" %(date.today(), username))
    transaction.commit_on_success() 

    return render(request, 'books/borrower/pay.html', {'logged_in':logged_in, 'username':username, 'type':type})

