"""AMS1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import seat_render,seat_con,login_render,register_render,register_auth,login_auth,logout_view,enqiury,contact,faker,show_flights,seat_booking,process,otpprocess,name_otp,check_otp,faker1,dic,change_password
admin.site.site_header = 'flight admin'
admin.site.site_title = 'flight admin'
admin.site.site_url = 'http://flight.com/'
admin.site.index_title = 'Flight administration'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('seat_booking/',seat_render),
    path('seat-con/',seat_con),
    path('login/',login_render),
    path('register/',register_render),
    path('reg_auth/',register_auth),
    path('login_auth/',login_auth),
    path('logout/',logout_view),
    path('enqiry/',enqiury),
    path('contact/',contact,name='contact'),
    path('faker/',faker),
    path('search/',show_flights),
    path('search/<str:todo_id>/<str:enq_id>/',seat_booking),
    path('comment_process/',process),
    path('forgot_password/',name_otp),
    path('check_email/',otpprocess),
    path('check_otp/',check_otp),
    path('faker1/',faker1),
    path('dic/',dic),
    path('change_password/<str:otp_id>/',change_password)

]
