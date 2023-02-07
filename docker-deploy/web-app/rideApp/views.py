from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.validators import validate_email
from . import models, form
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q
import json

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect


def homePage(request):
    return render(request, 'welcome.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        email = request.POST.get('email')
        pwd = request.POST.get('pwd')
        re_pwd = request.POST.get('re_pwd')
        try:
            validate_email(email)
        except ValidationError:
            messages.info(request, 'Email is invalid!')
            return render(request, 'register.html')
        # check whether email is unique
        old_email = models.User.objects.filter(email=email)
        if old_email:
            messages.info(request, 'Email has already exist. Please log in.')
            return render(request, 'register.html')
        if not username:
            messages.info(request, 'Please enter username')
            return render(request, 'register.html')
        if pwd != re_pwd:
            messages.info(request, 'Password does not match!')
            return render(request, 'register.html')
        # create object
        try:
            models.User.objects.create(
                username=username, email=email, password=pwd)
            print('create a user')
        except ValidationError:
            messages.info(request, 'Email has already exist. Please log in.')
            return render(request, 'register.html')

        return render(request, 'login.html', locals())
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        pwd = request.POST['pwd']
        try:
            find_user = models.User.objects.get(email=email)
        except Exception:
            messages.info(request, 'Email does not exist. Please try again.')
            return render(request, 'login.html')

        if pwd != find_user.password:
            messages.info(request, 'Incorrect password. Please try again.')
            return render(request, 'login.html')
        # save session
        request.session['email'] = email
        request.session['user_id'] = find_user.id


        if (find_user.is_driver == False):
            return render(request, 'user_main.html', locals())
        elif (find_user.is_driver == True):
            return render(request, 'driver_main.html', locals())

    return render(request, 'login.html')


def check_login(f):
    def wrap(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return render(request, 'login.html')
        return f(request, *args, **kwargs)
    return wrap

# view function for log out
def logout(request):
    if ('email' in request.session):
        del request.session['email']
    if ('user_id' in request.session):
        del request.session['user_id']
    if ('passenger_number' in request.session):
        del request.session['passenger_number']

    return HttpResponseRedirect('/welcome')

@check_login
def startRide(request):
    if request.method == 'POST':
        ride_form = form.start_ride_form(request.POST)
        user = models.User.objects.get(id=request.session['user_id'])
        if ride_form.is_valid():
            data = ride_form.cleaned_data
            arrival_time = data.get('arrival_time')
            passenger_number = data.get('passenger_number')
            vehicle_type = data.get('vehicle_type')
            is_share = data.get('is_share')
            des = data.get('des')
            special_request = request.POST.get('special_request')
            # update
            # create a ride
            try:
                models.Ride.objects.create(owner=user, is_shared=is_share, arrival_time=arrival_time, dest_addr=des,
                                           total_passenger=passenger_number, owner_passenger = passenger_number, vehicle_type=vehicle_type,
                                           owner_special_request=special_request, status=1)
                if (user.is_driver == False):
                    return render(request, 'user_main.html', locals())
                elif (user.is_driver == True):
                    return render(request, 'driver_main.html', locals())
            except ValidationError:
                return HttpResponse('create ride failure')
        else:
            error = ride_form.errors
            return render(request, 'startRide.html', {"errors": error})
    # request.method == GET
    return render(request, 'startRide.html')

@check_login
def joinRide(request):
    if request.method == 'POST':
        search_form = form.join_ride_form(request.POST)
        if search_form.is_valid():
            data = search_form.cleaned_data
            des = data.get('des')
            request.session['passenger_number'] = data.get('passenger_number')
            ealiest_time = data.get('ealiest_time')
            latest_time = data.get('latest_time')
            # search proper riders(must be open/ des/arrival time)
            rides = models.Ride.objects.filter(dest_addr=des, arrival_time__range=(
                ealiest_time, latest_time), is_shared=True, status=1)
            if rides:
                is_exist = 1
                print('find proper ride successfully')
            else:
                is_exist = 0
            return render(request, 'sharer_search.html', locals())
        else:
            error = search_form.errors
            print('join failures')
            return render(request, 'joinRide.html', {"errors": error})
    return render(request, 'joinRide.html')

@check_login
def sharer_search(request):
    if request.method == 'POST':
        # updata database
        ride_id = request.POST['ride_id']
        ride = models.Ride.objects.get(id=ride_id)
        original_num = ride.total_passenger
        sharer = models.User.objects.get(id=request.session['user_id'])
        join_num = request.session.get('passenger_number')
        ride.total_passenger = original_num + join_num
        # update sharer party number
        try:
            dic = json.loads(ride.sharer_num)
        except:
            dic = {}
        
        if sharer.username in dic:
            dic[sharer.username] += join_num
        else:
            dic[sharer.username] = join_num
        ride.sharer_num = json.dumps(dic, indent = 4)
        ride.save()
        ride.sharers.add(sharer)

        user = models.User.objects.get(id = request.session['user_id'])
        if (user.is_driver == False):
            return render(request, 'user_main.html', locals())
        elif (user.is_driver == True):
            return render(request, 'driver_main.html', locals())

# the view function for user_main page
@check_login
def user_main(request):
    if (request.method == 'GET'):
        return render(request, 'user_main.html')

# the view function for driver_main page
@check_login
def driver_main(request):
    if (request.method == 'GET'):
        return render(request, 'driver_main.html')

# the view function for reg_driver page
@check_login
def reg_driver(request):
    if request.method == 'POST':
        reg_form = form.reg_driver_form(request.POST)
        if (reg_form.is_valid()):
            data = reg_form.cleaned_data
            driver_name = data.get('driver_name')
            vehicle_type = data.get('vehicle_type')
            lpn = data.get('lpn')
            max_passenger = data.get('max_passenger')
            special_info = request.POST.get('special_info')
            # update database object
            try:
                user = models.User.objects.get(id = request.session['user_id'])
                user.is_driver = True
                user.driver_name=driver_name
                user.driver_vehicle=vehicle_type
                user.driver_plate_num=lpn
                user.driver_max_passenger=max_passenger
                user.driver_special_vehicle_info=special_info
                user.save()
                
                # print("This user has successfully registered as a driver.")
                return render(request, 'driver_main.html')

            except Exception:
                return HttpResponse("The user doesn't exist.")

        else:
            error = reg_form.errors
            return render(request, 'reg_driver.html', {"errors": error})

    return render(request, 'reg_driver.html')

# the view function for driver_main page
@check_login
def driver_profile(request):
    if request.method == 'POST':
        driver_name = request.POST.get('driver_name')
        vehicle_type = request.POST.get('vehicle_type')
        lpn = request.POST.get('lpn')
        max_passenger = request.POST.get('max_passenger')
        special_info = request.POST.get('special_info')

        try:
            user = models.User.objects.get(id = request.session['user_id'])
        except Exception:
            return HttpResponse("The user doesn't exist.")

        if (driver_name != ""):
            user.driver_name=driver_name

        if (vehicle_type != ""):
            user.vehicle_type=vehicle_type

        if (lpn != ""):
            user.driver_plate_num=lpn

        if (max_passenger != ""):
            if (max_passenger.isdigit()):
                if (int(max_passenger) >= 1):
                    user.driver_max_passenger=max_passenger
                else:
                    messages.info(request, 'The maximum number of passengers need to be >= 1. Please enter again.')
                    return render(request, 'driver_profile.html')
            else:
                messages.info(request, 'The maximum number of passengers should be an integer. Please enter again.')
                return render(request, 'driver_profile.html')

        if (special_info != ""):
            user.driver_special_vehicle_info=special_info

        user.save()
        return render(request, 'driver_main.html', locals())

    return render(request, 'driver_profile.html')

# driver search open ride requests
@check_login
def driver_search(request):
    if request.method == 'GET':
        driver = models.User.objects.get(id=request.session['user_id'])
        rides = models.Ride.objects.filter(vehicle_type=driver.driver_vehicle,
                                           status = 1,
                                           total_passenger__lt=driver.driver_max_passenger)
        if rides:
            is_exist = 1
            print('find proper ride successfully')
        else:
            is_exist = 0
        return render(request, 'driver_search.html', locals())
    if request.method == 'POST':
        # updata database: status->confirm
        ride_id = request.POST['ride_id']
        ride = models.Ride.objects.get(id=ride_id)
        ride.status = 2
        # updata database: driver info
        driver = models.User.objects.get(id=request.session['user_id'])
        ride.driver = driver
        ride.save()
        # email owner and sharer
        subject = 'Your ride has been confirmed'
        mess = 'Dear User,\n  Your ride has been confirmed!\n Best,\n RideTogether'
        from_email = 'tryagainece568@outlook.com'
        receiver = [ride.owner.email]
        for r in ride.sharers.all():
            receiver.append(r.email)
        try:
            send_mail(subject, mess, from_email, receiver)
        except BadHeaderError:
            return HttpResponse('Send email failure')
        
        return render(request, 'driver_main.html')

@check_login
def ongoing_ride(request):
    if request.method == 'GET':
        user = models.User.objects.get(id=request.session['user_id'])
        rides = models.Ride.objects.filter(Q(owner = user)|Q(driver = user)|Q(sharers__id__exact = user.id), ~Q(status=3)).distinct()
        if rides:
            is_exist = 1
            print('find proper ride successfully')
        else:
            is_exist = 0

        return render(request, 'ongoing_ride.html', locals())
        
@check_login
def view_ride(request, ride_id):
    if request.method == 'GET':
        ride = models.Ride.objects.get(id=ride_id)
        is_sharer = ride.sharers.all().filter(id = request.session['user_id'])
        owner_name = ride.owner.username
        if ride.driver:
            if ride.driver.id == request.session['user_id']:
                # version1: driver confirm ride
                if ride.sharer_num:
                    dic = json.loads(ride.sharer_num)
                    # print(dic)
                    
                    version = 1
                else:    
                    version = 0
        if ride.owner.id == request.session['user_id'] or is_sharer:
            if ride.status == 1:
                # version 2: owner/sharer open ride
                version = 2
            if ride.status == 2:
                # version 3: owner/sharer confirm ride
                version = 3
        return render(request, 'view_ride.html', locals())
        
@check_login
def edit_ride(request, ride_id):
    ride = models.Ride.objects.get(id=ride_id)
    if request.method == 'POST':
        ride_form = form.start_ride_form(request.POST)
        user = models.User.objects.get(id=request.session['user_id'])

        if ride_form.is_valid():
            data = ride_form.cleaned_data
            arrival_time = data.get('arrival_time')
            passenger_number = data.get('passenger_number')
            vehicle_type = data.get('vehicle_type')
            is_share = data.get('is_share')
            des = data.get('des')
            special_request = request.POST.get('special_request')

            # update the ride
            try:
                ride.arrival_time =  arrival_time
                ride.dest_addr=des
                # if the ride is still sharing
                if (is_share == True):
                    ride.total_passenger = ride.total_passenger - ride.owner_passenger + passenger_number
                else: # if the owner change to not sharing
                    ride.total_passenger=passenger_number
                ride.owner_passenger = passenger_number
                ride.vehicle_type=vehicle_type
                ride.owner_special_request=special_request
                ride.is_shared=is_share
                ride.save()

                if (user.is_driver == False):
                    return render(request, 'user_main.html', locals())
                elif (user.is_driver == True):
                    return render(request, 'driver_main.html', locals())

            except ValidationError:
                return HttpResponse('modify ride failure')

        else:
            error = ride_form.errors
            return render(request, 'owner_edit.html')
            # return render(request, 'edit_ride.html', {"errors": error})

    if (ride.owner.id == request.session['user_id'] and ride.status == 1):
        version = 1

    elif (ride.owner.id == request.session['user_id'] and ride.status != 1):
        version = 2

    else:
        version = 3

    return render(request, 'edit_ride.html', locals())

@check_login
def complete_ride(request, ride_id):
    ride = models.Ride.objects.get(id=ride_id)

    # the case when the user is the driver
    if (ride.driver and ride.driver.id == request.session['user_id'] and ride.status == 2):
        ride.status = 3
        ride.save()
        version = 1
    else:
        version = 2

    return render(request, 'complete_ride.html', locals())

@check_login
def owner_edit(request):
    return render(request, 'owner_edit.html', locals())



