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
    
    flag = False
    books = {}
    subject=1
    if request.method == 'POST':
        flag = True
        subject = request.POST['subject']
        cursor = connection.cursor()
        if subject:
            cursor.execute("SELECT br.callNumber_id as id, br.outDate as outdate, br.dueDate as duedate FROM books_borrowing br, books_hassubject hs WHERE br.callNumber_id = hs.callNumber_id AND hs.subject LIKE '%s' AND br.inDate IS NULL " %(subject))
            books = cursor.fetchall()
        else:
            cursor.execute("SELECT br.callNumber_id as id, br.outDate as outdate, br.dueDate as duedate FROM books_borrowing br, books_hassubject hs WHERE br.callNumber_id = hs.callNumber_id AND br.inDate IS NULL")
            books = cursor.fetchall()

    return render(request, 'books/librarian/book_report.html', {'logged_in':logged_in, 'username':username, 'type':type, 'books':books,'flag':flag})

def popular_book(request):
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return redirect('/sign_in')
    username = request.user.get_username()
    type = UserProfile.objects.get(username = username).type
    if type != 2:
        return redirect('/rule')

    flag = False
    error = False
    books = {}
    year = ''
    if request.method == 'POST':
        form = PopularForm(request.POST)
        if form.is_valid():
            flag = True
            year = form.cleaned_data['year']
            num = form.cleaned_data['limit']

            cursor = connection.cursor()
            cursor.execute("SELECT br.callNumber_id, bk.title, COUNT(br.callNumber_id) as borrows FROM books_borrowing br, books_book bk WHERE bk.id = br.callNumber_id AND year(br.outDate) = %s GROUP BY br.callNumber_id ORDER BY borrows DESC LIMIT %s" %(year, num) )
            books = cursor.fetchall()
        else:
            error = True
    else:
        form = PopularForm()
    
    return render(request, 'books/librarian/popular_book.html', {'logged_in':logged_in, 'username':username, 'type':type, 'books':books, 'flag':flag, 'error':error, 'form':form, 'year':year})

