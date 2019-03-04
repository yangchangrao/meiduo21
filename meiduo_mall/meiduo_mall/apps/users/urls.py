from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMS_CODEView.as_view()),
url(r'^username/(?P<username>\w+)/$', views.UsernameView.as_view()),url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),

]