from django.conf.urls import patterns, include, url
from books.views import *
from books.clerk_views import *
from books.borrower_views import *
from books.librarian_views import *

urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^sign_up/$', sign_up, name='sign_up'),
    url(r'^sign_in/$', sign_in, name='sign_in'),                   
    url(r'^logout/$', user_logout, name='logout'),
    url(r'^borrower/$', borrower, name='borrower'),
    url(r'^clerk/$', clerk, name='clerk'),
    url(r'^librarian/$', librarian, name='librarian'),
    url(r'^rule/$', rule, name='rule'), 
    url(r'^clerk/add_borrower/$', add_borrower),
    url(r'^clerk/checkout/$', checkout),
    url(r'^clerk/process_return/$', process_return),
    url(r'^clerk/overdue/$', overdue),
    url(r'^librarian/add_book/$', add_book),
    url(r'^librarian/book_report/$', book_report),
    url(r'^librarian/popular_book/$', popular_book),
    url(r'^borrower/search/$', search),
    url(r'^borrower/check_account/$',check_account ),
    url(r'^borrower/hold/$', hold),
    url(r'^borrower/pay/$', pay),
                      )


