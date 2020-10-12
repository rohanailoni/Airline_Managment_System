from django.shortcuts import render
import json
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from random import randint
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from random import randint,choice,uniform
import sys,os
from faker import Faker
import datetime
from django.conf import settings
from django.core.mail import send_mail

from AMS1.settings import BASE_DIR
from app.models import userinfo,enquiry,flight_info,leg,city_code,auto_correction,comment,one_time_password,login_log,logout_log,shortcuts
import pytz
from django.utils import timezone
from spellchecker import SpellChecker

# Create your views here.
@login_required(login_url='/login/')
def seat_render(request):
    print(request.path)
    return render(request,'ap/seat_pattern2.html',{"f":"disabled","k":2})

def seat_con(request):
    x=request.POST.get("seat-assignment")

    return HttpResponseRedirect('/seat_booking/')

def login_render(request):
    return render(request,'ap/login.html')

def register_render(request):
    return render(request,'ap/register.html')

def register_auth(request):

    first_name=request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    username = request.POST.get('username')
    password = request.POST.get('pass')
    rep_password = request.POST.get('repeat-pass')
    if password==rep_password:
        if User.objects.filter(username=username).exists():
            messages.info(request,"Username Taken")
            return HttpResponseRedirect('/register/')
        elif User.objects.filter(email=email).exists():
            messages.info(request,"email taken")
            return HttpResponseRedirect('/register/')
        else:
            user = User.objects.create_user(username=username, password=password, first_name=first_name,last_name=last_name, email=email)
            user.save()
            userid=None
            while(True):
                userid=randint(1000,9999)
                if userinfo.objects.filter(userid=userid).exists():
                    pass;
                else:
                    s=userinfo(userid=userid,user=user)
                    s.save()
                    break


            return HttpResponseRedirect('/login/')
    else:
        messages.info(request, "Passwords Didnt Match!!!!!")
        return HttpResponseRedirect('/register/')

def login_auth(request):
    user=authenticate(username=request.POST.get('username'),password=request.POST.get('password'))

    if user is not None:
        login(request,user)
        user1=User.objects.get(username=request.user.username)
        user2=userinfo.objects.get(user=user1)
        while True:
            login_id="IN"+str(randint(1000,4000))
            if login_log.objects.filter(login_id=login_id).exists()==False:
                login_log(login_id=login_id,login_date_time=datetime.datetime.now(),user=user2).save()
                break

        return HttpResponseRedirect('/enqiry/')
    else:
        return HttpResponseRedirect('/login/')

def logout_view(request):
    u=User.objects.get(username=request.user.username)
    u1=userinfo.objects.get(user=u)
    l1=login_log.objects.filter(user=u1)
    mul=[i.login_date_time for i in l1]
    max1=max(mul)
    index=mul.index(max1)
    l1=l1[index]
    logout_log(login_id=l1,logout_date=datetime.datetime.now()).save()
    logout(request)
    return HttpResponseRedirect('/login/')

def enqiury(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        f=True
        arr=[]
        city=city_code.objects.all()
        for i in city:
            arr.append(i.city_name)
        arr.sort()
    else:
        f=False
        arr = []
        city = city_code.objects.all()
        for i in city:
            arr.append(i.city_name)
        arr.sort()
    return render(request,'ap/enqiry.html',{"login":f,'c':arr})

def contact(request):
    f=flight_info.objects.all()
    c=comment.objects.all()
    if 'term' in request.GET:

        qs = auto_correction.objects.filter(Title__icontains=request.GET.get('term'))
        titles = list()
        for product in qs:
            titles.append(product.title)
        # titles = [product.title for product in qs]
        return JsonResponse(titles, safe=False)
    return render(request,"ap/contact.html",{"f":f,"c":c})

#for faking the data
def faker(request):
    all=city_code.objects.all()
    s=[]
    flight_id_array=[]
    classes=["BC","EC","FC"]
    date_dic={1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    for i in all:
        s.append(i.IATA)
    flight_object_array=flight_info.objects.all()
    for i in flight_object_array:
        flight_id_array.append(i.flight_id)

    for i in range(10000):
        c1=choice(s)#for slelcting city code
        c2 = choice(s)
        if c1!=c2:
            d1=city_code.objects.filter(IATA=c1)#whole city code module depearture
            d2=city_code.objects.filter(IATA=c2)#arrival city module
            choice_of_class=choice(classes)
            if choice_of_class=="EC":
                price_of_flight=uniform(10000,60000)
            elif choice_of_class=="BC":
                price_of_flight=uniform(50000,100000)
            else:
                price_of_flight=uniform(90000,200000)

            year=choice([2020,2021])
            date=randint(1,29)
            if year==2020:
                month=randint(10,12)
            else:
                month=randint(1,12)

            fake = Faker()
            departure_datetime=fake.date_time_this_year(after_now=True,before_now=False)
            duration = randint(1, 1740)
            hours=duration//60
            min=(duration/60-hours)*60
            arrival_datetime=departure_datetime+datetime.timedelta(hours=hours,minutes=min)
            flight_id=choice(flight_id_array)
            leg_id=str(departure_datetime)+" "+flight_id
            f=flight_info.objects.get(flight_id=flight_id)

            if leg.objects.filter(flight_id=f, date_time_departure_stamp=departure_datetime,date_time_arrival_stamp=arrival_datetime).exists() == False:
                l = leg(leg_id=leg_id, from_place=c1, to_place=c2, duration=duration, flight_id=f,date_time_departure_stamp=departure_datetime, date_time_arrival_stamp=arrival_datetime)
                l.save()
    return HttpResponseRedirect("/enqiry/")

def show_flights(request):
    if request.user.is_authenticated:
        user=request.user
        dep=request.POST.get('from')
        arr=request.POST.get('to')
        dep_date=request.POST.get("departure")
        arri_date=request.POST.get("return")
        passe=request.POST.get('number')
        way=request.POST.get('trip')
        c1=city_code.objects.get(city_name=dep)
        c2=city_code.objects.get(city_name=arr)
        dep_date=dep_date[6]+dep_date[7]+dep_date[8]+dep_date[9]+"-"+dep_date[0]+dep_date[1]+"-"+dep_date[3]+dep_date[4]
        l=leg.objects.filter(date_time_departure_stamp__startswith=dep_date,from_place=c1.IATA,to_place=c2.IATA)
        u=User.objects.get(username=user)
        u1=userinfo.objects.get(user=u)
        while True:
            id="E"+str(randint(10000,20000))
            if enquiry.objects.filter(enquiry_id=id).exists()==False:
                break




        e=enquiry(user=u1,enquiry_id=id,search_arri_city=dep,search_depa_city=arr,search_date_time=datetime.datetime.now(),search_for_date=dep_date,search_way_type=1)
        e.save()
    if request.user.is_anonymous:
        dep = request.POST.get('from')
        arr = request.POST.get('to')
        dep_date = request.POST.get("departure")
        arri_date = request.POST.get("return")
        passe = request.POST.get('number')
        way = request.POST.get('trip')
        c1 = city_code.objects.get(city_name=dep)
        c2 = city_code.objects.get(city_name=arr)
        dep_date = dep_date[6] + dep_date[7] + dep_date[8] + dep_date[9] + "-" + dep_date[0] + dep_date[1] + "-" + dep_date[3] + dep_date[4]
        u = User.objects.filter(username=user)
        u1 = userinfo.objects.filter(user=u[0])
        while True:
            id = "E" + str(randint(10000, 20000))
            if enquiry.objects.filter(enquiry_id=id).exists() == False:
                break


    return render(request,'ap/search.html',{'l':l,"id":id})

def seat_booking(request,todo_id,enq_id):
    e=enquiry.objects.get(enquiry_id=enq_id)
    print(e.no_of_pass)
    if e.no_of_pass==1:
        return render(request,'ap/seat_pattern.html')
    else:
        return render(request,'ap/seat_pattern2.html')

def process(request):
    spell = SpellChecker()
    # os.path.join(BASE_DIR,"package.json")
    #spell.word_frequency.load_dictionary('./package.json')
    name=request.user.username
    u1=User.objects.get(username=request.user)
    u=userinfo.objects.get(user=u1)
    flight_no=request.POST.get('from')
    f1=flight_info.objects.get(flight_id=flight_no)
    while True:
        comment_id="C"+str(randint(1000,3000))
        if comment.objects.filter(comment_id=comment_id).exists()== False:

            break
    date=request.POST.get('date')

    list1=date.split("/")
    date=list1[2]+"-"+list1[1]+"-"+list1[0]
    comment1=request.POST.get('message')
    comment1=comment1.split(" ")

    index_of_misspelled=[]
    index_of_abbri=[]
    for i in range(len(comment1)):
        if shortcuts.objects.filter(shortcut=comment1[i].lower()).exists():
            c=shortcuts.objects.get(shortcut=comment1[i])
            index_of_abbri.append(i)
            print(c.abbri)
            comment1[i]=c.abbri
    comment2=[]
    for i in range(len(comment1)):
        if i not in index_of_abbri:
            comment2.append(comment1[i])
    misspelled = spell.unknown(comment2)
    misspelled1 = list(misspelled)

    print(comment1)
    print(comment2)
    print(misspelled1)
    for i in range(len(comment1)):
        if comment1[i] in misspelled1 and i not in index_of_abbri:
            index_of_misspelled.append(i)
    print(index_of_misspelled)
    for i in range(len(misspelled1)):
        print(i)
        comment1[index_of_misspelled[i]]=spell.correction(misspelled1[i]).rstrip("\n")
    corrected_code=""


    for i in comment1:
        corrected_code+=i+" "
    c=comment(comment_id=comment_id,user=u,flight_id=f1,date_req=date,org_comm=request.POST.get('message'),exp1=corrected_code)
    c.save()
    return HttpResponseRedirect('/contact/')



#otp process starts here
def otpprocess(request):
    email = request.POST.get('username')
    if User.objects.filter(email=email).exists():
        otp = randint(100000, 200000)
        start_time = datetime.datetime.now()
        expiry_time = start_time + datetime.timedelta(minutes=5)
        u=User.objects.get(email=email)
        subject = 'reset of your flight login password'
        while True:
            otp_id="O"+str(randint(100,999))
            if one_time_password.objects.filter(otp_id=otp_id).exists()==False:
                break

        message = f'Hi {u.username}, your otp for your password change {otp} and otp id{otp_id}(for sequrity purpose). This otp is valid upto 5 min'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [u.email, ]
        send_mail(subject, message, email_from, recipient_list)
        u1=userinfo.objects.get(user=u)
        status="T"
        o=one_time_password(otp=otp,status=status,start_time=start_time,expiry_time=expiry_time,user_id=u1,otp_id=otp_id)
        o.save()
        con="True"
    return render(request,'ap/otp.html',{'con':con})

def name_otp(request):
    return render(request,'ap/name_otp.html')

def check_otp(request):
    otp_id=request.POST.get("otp_id")
    otp=request.POST.get("otp")
    print(type(otp_id),otp_id,type(otp),otp)
    one=one_time_password.objects.get(otp_id=otp_id)

    now=datetime.datetime.now()
    utc = pytz.UTC
    now=timezone.now()


    x=one_time_password.objects.get(user_id=one.user_id,start_time=one.start_time)
    if x.expiry_time>now:
        if x.otp==int(otp):

             return render(request,'ap/change_password.html',{"otp":otp_id})
        else:
            messages.info(request, "otp Null")
            return render(request,'ap/name_otp.html')
    else:
        messages.info(request,"OTP expired")
        return render(request,'ap/name_otp.html')

def change_password(request,otp_id):
    o=one_time_password.objects.get(otp_id=otp_id)
    u=User.objects.get(username=o.user_id.user.username)
    print(o.user_id.user.username)
    if request.POST.get('confirm_password')==request.POST.get('password'):
        password=request.POST.get('password')
        print(type(password))
        u.set_password(password)
        u.save()

        messages.info(request, "Password changed")
        return HttpResponseRedirect('/login/')
    else:
        messages.info(request, "Password Dosent match")
        return HttpResponseRedirect('/change_password/{}/'.format(otp_id))


#otp process ends here

def faker1(request):
    def freq(str):
        str = str.split()
        str2 = []
        for i in str:
            if i not in str2:
                str2.append(i)

        return str.count(str2[0])





    dirpath = os.path.dirname(os.path.abspath(__file__))
    chap_dirpath = os.path.join(BASE_DIR, "engmix.txt")
    f = open( "app/engmix.txt", "r",encoding='utf-8',errors='ignore')

    for i in f:

        auto_correction(title=i,frequency=freq(i)).save()
    f.close()
    return HttpResponseRedirect("/enqiry/")

def dic(request):
    chap_dirpath = os.path.join(BASE_DIR, "package.json")
    string="string"
    spell = SpellChecker(language=None, case_sensitive=False)
    spell.word_frequency.load_dictionary('./package.json')
    misspelled = spell.unknown(['the'])
    for word in misspelled:
        print(spell.correction(word.rstrip("\n")))
    return HttpResponseRedirect("/enqiry/")
