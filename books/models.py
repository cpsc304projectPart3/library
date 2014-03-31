from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    username = models.CharField(max_length = 30)
    type = models.IntegerField() # 0 for borrower, 1 for clerk, 2 lib

 
class Borrower(models.Model):
    username = models.CharField(max_length = 30, primary_key = True)
    password = models.CharField(max_length = 15)
    name = models.CharField(max_length = 30)
    address = models.CharField(max_length = 30)
    phone = models.CharField(max_length = 30)
    emailAddress = models.CharField(max_length = 30)
    sinOrStNo = models.CharField(max_length = 10, unique = True)
    expiryDate = models.DateField()    
    type = models.ForeignKey('BorrowerType') 
 
class BorrowerType(models.Model):
        TYPE = (
        ('ST', 'student'),
        ('FA', 'faculty'),
        ('SF', 'staff'),
    )
        type = models.CharField(max_length = 2, choices = TYPE, primary_key = True)
        bookTimeLimit = models.IntegerField()
 
class Book(models.Model):
        #callNumber = models.CharField(max_length = 30, primary_key = True)
        isbn = models.CharField(max_length = 30, unique = True)
        title = models.CharField(max_length = 30)
        mainAuthor = models.CharField(max_length = 30)
        publisher = models.CharField(max_length = 30)
        year = models.IntegerField()
 
class HasAuthor(models.Model):
        callNumber = models.ForeignKey('Book')
        name = models.CharField(max_length = 30)
        class Meta:
            unique_together = (("callNumber", "name"),)
 
class HasSubject(models.Model):
        callNumber = models.ForeignKey('Book')
        subject = models.CharField(max_length = 30)
        class Meta:
            unique_together = (("callNumber", "subject"),)
 
class BookCopy(models.Model):
        STATUS = (
        ('ON', 'on-hold'),
        ('IN', 'in'),
        ('OUT', 'out'),
    )
        callNumber = models.ForeignKey('Book')
        copyNo = models.IntegerField()
        status = models.CharField(max_length = 3, choices = STATUS)
        class Meta:
            unique_together = (("callNumber", "copyNo"),)
 
class HoldRequest(models.Model):
       # hid = models.CharField(max_length = 30, primary_key = True)
        bid = models.ForeignKey('Borrower')
        callNumber = models.ForeignKey('Book')
        issuedDate = models.DateField()
 
class Borrowing(models.Model):
       # borid = models.CharField(max_length = 30, primary_key = True)
        bid = models.ForeignKey('Borrower')
        callNumber = models.ForeignKey('Book')
        copyNo = models.ForeignKey('BookCopy')
        outDate = models.DateField(auto_now_add=True)
        inDate = models.DateField(null = True)
        dueDate = models.DateField()

class Fine(models.Model):
       # fid = models.CharField(max_length = 30, primary_key = True)
        amount = models.IntegerField()
        issuedDate = models.DateField()
        paidDate = models.DateField(null = True)
        borid = models.ForeignKey('Borrowing', on_delete = models.PROTECT)
		

