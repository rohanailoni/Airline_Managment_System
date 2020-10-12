from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
#creates userid
class userinfo(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    userid=models.IntegerField(unique=True,primary_key=True)
    def __str__(self):
        return self.user.username
#unchange
class enquiry(models.Model):
    user=models.ForeignKey(userinfo,on_delete=models.CASCADE)
    enquiry_id=models.CharField(primary_key=True,max_length=6)
    search_arri_city=models.CharField(max_length=50)
    search_depa_city=models.CharField(max_length=50)
    search_date_time=models.DateTimeField()             #search date and time
    search_for_date=models.DateField()                  #search of date
    search_way_type=models.IntegerField()               #for booking either one way(1) or two way(2)
    no_of_pass=models.IntegerField(default=1)

class flight_info(models.Model):
    flight_id = models.CharField(max_length=6)  # completed
    models_type = models.CharField(max_length=4, default="tour")
    total_seats = models.IntegerField(default=50)


class leg(models.Model):
    leg_id=models.CharField(max_length=200,primary_key=True)
    from_place=models.CharField(max_length=150)#completed
    to_place=models.CharField(max_length=150)#completed
    duration=models.IntegerField(default=0)#completed
    flight_id=models.ForeignKey(flight_info,on_delete=models.CASCADE)
    date_time_departure_stamp=models.DateTimeField()
    date_time_arrival_stamp = models.DateTimeField()




class city_code(models.Model):
    IATA=models.CharField(max_length=3,primary_key=True,unique=True)
    city_name=models.CharField(max_length=100)
    country=models.CharField(max_length=200,default="United Arab Emirates")
    airport_name=models.CharField(max_length=150,default="null")
    def __str__(self):
        return self.city_name


class auto_correction(models.Model):
    title=models.CharField(max_length=100)
    frequency=models.IntegerField()
    table1=models.CharField(max_length=100,null=True,blank=True)
    table2=models.CharField(max_length=100,null=True,blank=True)
    table3=models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.title


class leg1(models.Model):
    leg_id=models.ForeignKey(leg,on_delete=models.CASCADE)

    seats=models.JSONField(default={"1": "T", "2": "F", "3": "T", "4": "T", "5": "F", "6": "T", "7": "T", "8": "F", "9": "T", "10": "T", "11": "F", "12": "T", "13": "T", "14": "F", "15": "T", "16": "T", "17":  "F", "18": "T", "19": "T", "20": "F", "21": "T", "22": "T", "23": "F", "24": "T", "25": "T", "26": "F", "27": "T", "28": "T", "29": "F", "30": "T", "31": "T", "32": "F", "33": "T", "34": "T", "35": "F", "36": "T", "37": "T", "38": "F", "39": "T", "40": "T", "41": "F", "42": "T", "43": "T", "44": "F", "45": "T", "46": "T", "47": "F", "48": "T","49": "T", "50": "F", "51": "T", "52": "T", "53": "F", "54": "T", "55": "T", "56": "F", "57": "T", "58": "T", "59": "F", "60": "T", "61": "T", "62": "F", "63": "T", "64": "T", "65": "F", "66": "T", "67": "T", "68": "F", "69": "T", "70": "T", "71": "F", "72": "T"} )


class comment(models.Model):
    comment_id=models.CharField(primary_key=True,max_length=5)
    user=models.ForeignKey(userinfo,on_delete=models.CASCADE)
    flight_id=models.ForeignKey(flight_info,on_delete=models.CASCADE)
    date_req=models.DateField()
    org_comm=models.TextField()
    exp1=models.TextField(null=True)
    exp2=models.TextField(null=True)
    exp3=models.TextField(null=True)

class login_log(models.Model):
    login_id=models.CharField(max_length=6)
    user=models.ForeignKey(userinfo,on_delete=models.CASCADE)
    login_date_time=models.DateTimeField()

class logout_log(models.Model):
    login_id=models.ForeignKey(login_log,on_delete=models.CASCADE)
    logout_date=models.DateTimeField()



class one_time_password(models.Model):
    otp_id=models.CharField(max_length=4,primary_key=True)
    otp=models.IntegerField()
    start_time=models.DateTimeField()
    expiry_time=models.DateTimeField()
    user_id=models.ForeignKey(userinfo,on_delete=models.CASCADE)
    status=models.CharField(max_length=1)
class shortcuts(models.Model):
    shortcut=models.CharField(max_length=100,primary_key=True)
    abbri=models.CharField(max_length=200)
