from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from books.forms import *
from books.models import *
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction, DatabaseError, IntegrityError


def librarian(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 2:
        return redirect('/rule')
    
    return render(request, 'books/librarian.html', {'logged_in':logged_in, 'username':username, 'type':type})

def add_book(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 2:
        return redirect('/rule')

    registered = False
    error = False
    if request.method == 'POST':
        book = BookForm(request.POST)
        if book.is_valid():
            isbn = book.cleaned_data['isbn']
            title = book.cleaned_data['title']
            mainAuthor = book.cleaned_data['mainAuthor']
            publisher = book.cleaned_data['publisher']
            year = book.cleaned_data['year']
            subject = book.cleaned_data['subject']

            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO books_book (isbn, title, mainAuthor, publisher, year) VALUES ('%s', '%s', '%s', '%s', %s) " %(isbn, title, mainAuthor, publisher, year))
                transaction.commit_unless_managed()
                cursor.execute("SELECT LAST_INSERT_ID() as id");
                id = cursor.fetchone()[0]
            except IntegrityError:
                id = Book.objects.get(isbn=isbn).id
                cursor.execute('SELECT MAX(copyNO) as num FROM books_bookCopy WHERE callNumber_id = %s', [id])
                maxCopyNo = cursor.fetchone()[0] + 1
            else:
                maxCopyNo = 1
                cursor.execute("INSERT INTO books_hasauthor (callNumber_id, name) VALUES (%s, '%s')" %(id, mainAuthor))
                transaction.commit_on_success()
                cursor.execute("INSERT INTO books_hassubject (callNumber_id, subject) VALUES (%s, '%s')"% (id, subject))
                transaction.commit_on_success()

            cursor.execute("INSERT INTO books_bookcopy (callNumber_id, copyNo, status) VALUES (%s,%s, 'IN')" %(id, maxCopyNo))
            transaction.commit_on_success()
            registered = True
        else:
            error = True
    else:
        book = BookForm()
    
    return render(request, 'books/librarian/add_book.html', {'logged_in':logged_in, 'username':username, 'type':type, 'registered':registered, 'error':error, 'book':book})


def book_report(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 2:
        return redirect('/rule')
    
    return render(request, 'books/librarian/book_report.html', {'logged_in':logged_in, 'username':username, 'type':type})

def popular_book(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 2:
        return redirect('/rule')
    
    return render(request, 'books/librarian/popular_book.html', {'logged_in':logged_in, 'username':username, 'type':type})

