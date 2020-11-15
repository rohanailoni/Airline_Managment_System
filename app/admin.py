from django.contrib import admin
from app.models import userinfo,enquiry,flight_info,leg,city_code,auto_correction,leg1,comment,one_time_password,login_log,logout_log,shortcuts,passengers,price

# Register your models here.
admin.site.register(userinfo)
admin.site.register(enquiry)
admin.site.register(flight_info)
admin.site.register(leg)
admin.site.register(city_code)
admin.site.register(auto_correction)
admin.site.register(leg1)
admin.site.register(comment)
admin.site.register(one_time_password)
admin.site.register(login_log)
admin.site.register(logout_log)
admin.site.register(shortcuts)
admin.site.register(passengers)
admin.site.register(price)