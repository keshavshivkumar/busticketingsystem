from django.shortcuts import render
from decimal import Decimal
import re 
# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Bus, Book, Operator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserLoginForm, UserRegisterForm, OperatorForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db import IntegrityError

def home(request):
    if request.user.is_authenticated:
        return render(request, 'myapp/home.html')
    else:
        return render(request, 'myapp/signin.html')


def operatorhome(request):
    if request.user.is_authenticated:
        return render(request, 'myapp/operatorhome.html')
    else:
        return render(request, 'myapp/signin.html')


# @login_required(login_url='signin')
def findbus(request):
    context = {}
    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')
        if source_r and dest_r and date_r:
            bus_list = Bus.objects.filter(
                source=source_r, dest=dest_r, date=date_r)
        elif source_r and dest_r:
            bus_list = Bus.objects.filter(source=source_r, dest=dest_r)
        elif source_r and date_r:
            bus_list = Bus.objects.filter(source=source_r, date=date_r)
        elif source_r:
            bus_list = Bus.objects.filter(source=source_r)
        elif dest_r and date_r:
            bus_list = Bus.objects.filter(dest=dest_r, date=date_r)
        elif dest_r:
            bus_list = Bus.objects.filter(dest=dest_r)
        elif date_r:
            bus_list = Bus.objects.filter(date=date_r)
        else:
            bus_list = Bus.objects.all()
        if bus_list:
            return render(request, 'myapp/list.html', locals())
        else:
            #context["error"] = "Sorry no buses availiable from" + source_r + "to" + dest_r
            return render(request, 'myapp/findbus.html', {'error': "Sorry no buses availiable", 'buses': Bus.objects.all()})
    else:
        buses = Bus.objects.all()
        return render(request, 'myapp/findbus.html', {'buses': buses})


@login_required(login_url='signin')
def bookings(request):
    context = {}
    if request.method == 'POST':
        try:    
            id_r = request.POST.get('bus_id')
            if request.POST.get('no_seats') == "":
                seats_r = 0
            else:
                seats_r = int(request.POST.get('no_seats'))
            bus = Bus.objects.get(id=id_r)
            if bus:
                if bus.rem > int(seats_r):
                    name_r = bus.bus_name
                    cost = int(seats_r) * bus.price
                    source_r = bus.source
                    dest_r = bus.dest
                    nos_r = Decimal(bus.nos)
                    price_r = bus.price
                    date_r = bus.date
                    time_r = bus.time
                    username_r = request.user.username
                    email_r = request.user.email
                    userid_r = request.user.id
                    rem_r = bus.rem - seats_r
                    Bus.objects.filter(id=id_r).update(rem=rem_r)
                    book = Book.objects.create(name=username_r, email=email_r, userid=userid_r, bus_name=name_r,
                                            source=source_r, busid=id_r,
                                            dest=dest_r, price=price_r, nos=seats_r, date=date_r, time=time_r,
                                            status='BOOKED')
                    print('------------book id-----------', book.id)
                    # book.save()
                    return render(request, 'myapp/bookings.html', locals())
                else:
                    context["error"] = "Sorry select fewer number of seats"
                    return render(request, 'myapp/list.html', {'error': "Sorry select fewer number of seats", 'bus_list': Bus.objects.all()})
        except:
            if seats_r == 0:
                return render(request, 'myapp/list.html', {'error': "Book atleast 1 seat to proceed", 'bus_list': Bus.objects.all()})
            else:
                return render(request, 'myapp/list.html', {'error': "Incorrect bus ID. Please refer to the table above before entering.", 'bus_list': Bus.objects.all()})
    else:
        buses = Bus.objects.all()
        return render(request, 'myapp/findbus.html', {'buses': buses})


def seebuses(request):
    context = {}

    name = request.user.username
    op = Operator.objects.filter(name=name)

    buses = Bus.objects.filter(name=name)
    return render(request, 'myapp/seebuses.html', {'buses': buses, 'user': name})


@login_required(login_url='signin')
def cancellings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        #seats_r = int(request.POST.get('no_seats'))

        try:
            book = Book.objects.get(id=id_r)
            bus = Bus.objects.get(id=book.busid)
            rem_r = bus.rem + book.nos
            Bus.objects.filter(id=book.busid).update(rem=rem_r)
            #nos_r = book.nos - seats_r
            Book.objects.filter(id=id_r).update(status='CANCELLED')
            Book.objects.filter(id=id_r).update(nos=0)
            return redirect(seebookings)
        except:
            context["error"] = "Sorry You have not booked that bus"
            return render(request, 'myapp/error.html', context)
    else:
        buses = Bus.objects.all()
        return render(request, 'myapp/findbus.html', {'buses': buses})


@login_required(login_url='signin')
def seebookings(request, new={}):
    context = {}
    id_r = request.user.id
    book_list = Book.objects.filter(userid=id_r)
    if book_list:
        return render(request, 'myapp/booklist.html', locals())

    else:
        context["error"] = "Sorry no buses booked"
        return render(request, 'myapp/findbus.html', {'error': "Sorry no buses booked", 'buses': Bus.objects.all()})


def signup(request):
    context = {}
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if request.method == 'POST':
        name_r = request.POST.get('name')
        email_r = request.POST.get('email')
        if not (re.search(regex,email_r)):
            context["error"] = "Invalid email"
            return render(request, 'myapp/signup.html', context)
        password_r = request.POST.get('password')
        operator = request.POST.get('check')
        try:    
            user = User.objects.create_user(name_r, email_r, password_r,)
        except:
            context["error"] = "Username is not unique"
            return render(request, 'myapp/signup.html', context)
        if user:
            login(request, user)
            if operator:
                operator = Operator(email=email_r, name=name_r)
                operator.save()
                op = 1
                return render(request, 'myapp/operatorbase.html')
            return render(request, 'myapp/thank.html')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signup.html', context)
    else:
        return render(request, 'myapp/signup.html', context)


def signin(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        user = authenticate(request, username=name_r, password=password_r)
        operator = request.POST.get('check')
        try:
            error = 0
            opname = Operator.objects.get(name = name_r)
        except:
            error = 1
        if user:
            login(request, user)
            # username = request.session['username']
            context["user"] = name_r
            context["id"] = request.user.id
            if(operator and error == 0):
                op = 1
                return render(request, 'myapp/operatorbase.html',{'operator': opname.name})
            elif operator and error == 1:
                context["error"] = "You do not have an account registered as an operator."
                return render(request, 'myapp/signin.html', context)
            return render(request, 'myapp/success.html', context)
            # return HttpResponseRedirect('success')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signin.html', context)
    else:
        context["error"] = "You are not logged in"
        return render(request, 'myapp/signin.html', context)


def signout(request):
    context = {}
    logout(request)
    context['error'] = "You have been logged out"
    op = 0
    return render(request, 'myapp/signin.html', context)


def success(request):
    context = {}
    context['user'] = request.user
    return render(request, 'myapp/success.html', context)


def addbus(request):
    name = request.user.username
    ops = Operator.objects.get(name=name)
    email = ops.email
    form = OperatorForm(request.POST or None, initial={'name': name})
    buses = Bus.objects.filter(name=name)
    if form.is_valid():
        form.save()
        return render(request, 'myapp/seebuses.html', {'buses': buses, 'user': name})
    context = {'form': form}
    return render(request, 'myapp/addbus.html', context)
def deletebus(request):
    if request.method == 'POST':
         name = request.user.username
         buses = Bus.objects.filter(name=name)
         bus_name = request.POST['bus_name']
         Bus.objects.filter(bus_name = bus_name).delete()
         return render(request, 'myapp/seebuses.html', {'buses': buses, 'user': name})

