from django.db.models import Q
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.models import User,auth
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from datetime import date
from datetime import datetime, timedelta, time
import random
# Create your views here.

def Index(request):
    return render(request, 'index.html')

def register(request):
    if(request.method == 'POST'):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        if password1 == password2:
            if(User.objects.filter(username=username).exists()):
                messages.info(request,'User name is not available')
                return redirect('register')
                # print('User Name is not available')
            elif(User.objects.filter(email=email).exists()):
                messages.info(request,'Email id is already taken')
                return redirect('register')
                # print('Email id is already taken')
            else:
                user=User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=last_name)
                user.save()
                print('User Created')
        else:
            messages.info(request,'Passworld not matching')
            return redirect('register')
            # print('Terminal Message : Password not matching.')
        return redirect('index')

    else:
        return render(request,'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password'] 

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect("index")
        else:
            messages.info(request,'Wrong Username or Password')
            return redirect('login')
    else:
        return render(request, 'login.html')

def go(request):
    auth.logout(request)    
    return redirect('login')

def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'do_contact.html')

def admin_login(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['username']
        p = request.POST['password']
        user = authenticate(username=u, password=p)
        try:
            if user.is_superuser:
                auth.login(request,user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'admin_login.html', d)


def admin_home(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    today = datetime.now().date()
    yesterday = today - timedelta(1)
    lasts = today - timedelta(7)

    tv = Vehicle.objects.filter(pdate=today).count()
    yv = Vehicle.objects.filter(pdate=yesterday).count()
    ls = Vehicle.objects.filter(pdate__gte=lasts,pdate__lte=today).count()
    totalv = Vehicle.objects.all().count()

    d = {'tv':tv,'yv':yv,'ls':ls,'totalv':totalv}
    return render(request,'admin_home.html',d)


def admin_logout(request):
    auth.logout(request)    
    return redirect('admin_login')



def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')
    error = ""
    if request.method == "POST":
        o = request.POST['currentpassword']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = "not"
        except:
            error = "yes"
    d = {'error': error}
    return render(request,'change_password.html',d)


def add_category(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    if request.method=="POST":
        cn = request.POST['categoryname']
        cp = request.POST['categoryprice']
        try:
            Category.objects.create(categoryname=cn,price=cp)
            error = "no"
        except:
            error = "yes"
    d = {'error':error}
    return render(request, 'add_category.html', d)

def manage_category(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    category = Category.objects.all()
    d = {'category':category}
    return render(request, 'manage_category.html', d)


def delete_category(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    category = Category.objects.get(id=pid)
    category.delete()
    return redirect('manage_category')

def delete_vehicle(request,pid):
    if not request.user.is_authenticated:
        return redirect('login')
    vehicle = Vehicle.objects.get(id=pid)
    vehicle.delete()
    return redirect('show_bookings')

def edit_category(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    category = Category.objects.get(id=pid)
    error = ""
    if request.method == 'POST':
        cn = request.POST['categoryname']
        cp = request.POST['categoryprice']
        category.categoryname = cn
        category.price = cp
        try:
            category.save()
            error = "no"
        except:
            error = "yes"
    d = {'error': error,'category':category}
    return render(request, 'edit_category.html',d)

def add_vehicle(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    category1 = Category.objects.all()
    categories_json = json.dumps(list(category1.values('categoryname', 'price')),cls=DjangoJSONEncoder)
    if request.method=="POST":
        pn = str(random.randint(10000000, 99999999))
        un = request.POST['u_name']
        ct = request.POST['category']
        vc = request.POST['vehiclecompany']
        rn = request.POST['regno']
        on = request.POST['ownername']
        oc = request.POST['ownercontact']
        pd = request.POST['pdate']
        it = request.POST['intime']
        pc = request.POST['pricedisplay1']

        status = "In"
        category = Category.objects.get(categoryname=ct)

        try:
            Vehicle.objects.create(parkingnumber=pn,username=un,category=category,vehiclecompany=vc,regno=rn,ownername=on,ownercontact=oc,pdate=pd,intime=it,outtime='',parkingcharge=pc,remark='',status=status)
            error = "no"
        except:
            error = "yes"
    d = {'error':error,'category1':category1,'categories_json':categories_json}
    return render(request, 'add_vehicle.html', d)

def manage_incomingvehicle(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    vehicle = Vehicle.objects.filter(status="In")
    d = {'vehicle':vehicle}
    return render(request, 'manage_incomingvehicle.html', d)

def show_bookings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    vehicle = Vehicle.objects.filter(status="In",username=request.user.username)
    d = {'vehicle':vehicle}
    return render(request, 'manage_booked_vehicle.html', d)

def view_incomingdetail(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_home')
    error = ""
    category1 = Category.objects.all()
    categories_json = json.dumps(list(category1.values('categoryname', 'price')),cls=DjangoJSONEncoder)
    vehicle = Vehicle.objects.get(id=pid)
 
    if request.method == 'POST':
        rm = request.POST['remark']
        ot = request.POST['outtime']
        pc = request.POST['parkingcharge']
        status = request.POST['status']
        vcom = request.POST['vehiclecompany']
        rn = request.POST['regno']
        on = request.POST['ownername']
        oc = request.POST['ownercontact']
        it = request.POST['intime']
        vehicle.remark = rm
        vehicle.outtime = ot
        vehicle.parkingcharge = pc
        vehicle.status = status
        vehicle.vehiclecompany = vcom
        vehicle.regno = rn
        vehicle.ownername = on
        vehicle.ownercontact = oc
        vehicle.intime = it
        try:
            vehicle.save()
            error = "no"
        except:
            error = "yes"

    d = {'vehicle': vehicle,'error':error, 'categories_json':categories_json}
    return render(request,'view_incomingdetail.html', d)

def edit_incomingdetail(request,pid):
    if not request.user.is_authenticated:
        return redirect('login')
    error = ""
    vehicle = Vehicle.objects.get(id=pid)
    # category = Category.objects.all()
    if request.method == 'POST':
        # vcat = request.POST['category']
        # cat = Category.objects.get(categoryname == vcat)
        vcom = request.POST['vehiclecompany']
        rn = request.POST['regno']
        on = request.POST['ownername']
        oc = request.POST['ownercontact']
        it = request.POST['intime']
        try:
            # vehicle.category = vcat
            vehicle.vehiclecompany = vcom
            vehicle.regno = rn
            vehicle.ownername = on
            vehicle.ownercontact = oc
            vehicle.intime = it
            vehicle.save()
            error = "no"
        except:
            error = "yes"
    d = {'vehicle': vehicle,'error':error}
    return render(request,'edit_incomingdetail.html', d)

def manage_outgoingvehicle(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    vehicle = Vehicle.objects.filter(status="Out")
    d = {'vehicle':vehicle}
    return render(request, 'manage_outgoingvehicle.html', d)


def view_outgoingdetail(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    vehicle = Vehicle.objects.get(id=pid)

    d = {'vehicle': vehicle}
    return render(request,'view_outgoingdetail.html', d)

def show_outgoingdetail(request):
    if not request.user.is_authenticated:
        return redirect('login')
    vehicle = Vehicle.objects.filter(status="Out",username=request.user.username)
    d = {'vehicle': vehicle}
    return render(request,'h_outgoingdetail.html', d)


def print_detail(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    vehicle = Vehicle.objects.get(id=pid)

    d = {'vehicle': vehicle}
    return render(request,'print.html', d)


def search(request):
    q = None
    if request.method == 'POST':
        q = request.POST['searchdata']
    try:
        vehicle = Vehicle.objects.filter(Q(parkingnumber=q))
        vehiclecount = Vehicle.objects.filter(Q(parkingnumber=q)).count()

    except:
        vehicle = ""
    d = {'vehicle': vehicle,'q':q,'vehiclecount':vehiclecount}
    return render(request, 'search.html',d)


def betweendate_reportdetails(request):
    if not request.user.is_authenticated:
        return redirect('index')
    return render(request, 'betweendate_reportdetails.html')



def betweendate_report(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        fd = request.POST['fromdate']
        td = request.POST['todate']
        vehicle = Vehicle.objects.filter(Q(pdate__gte=fd) & Q(pdate__lte=td))
        vehiclecount = Vehicle.objects.filter(Q(pdate__gte=fd) & Q(pdate__lte=td)).count()
        d = {'vehicle': vehicle,'fd':fd,'td':td,'vehiclecount':vehiclecount}
        return render(request, 'betweendate_reportdetails.html', d)
    return render(request, 'betweendate_report.html')