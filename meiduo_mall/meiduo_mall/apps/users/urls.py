from django.conf.urls import url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    #短信验证码
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMS_CODEView.as_view()),
    #用户名判断
    url(r'^usernames/(?P<username>\w+)/count/$', views.UsernameView.as_view()),
    #手机号判断
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    #注册
    url(r'^users/$',views.UserView.as_view()),
    #登录
    url(r'^authorizations/',obtain_jwt_token),
]