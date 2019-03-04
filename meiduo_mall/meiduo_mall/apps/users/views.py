from random import randint

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall.libs.yuntongxun.sms import CCP
from threading import Thread



class SMS_CODEView(APIView):
    #发送短信
    def get(self,request,mobile):
        # 1.获取手机号
        # 2.生成短信验证码
        sms_code= '%06d' % randint(0,999999)
        #3.在redis保存真实的短信验证码
        conn=get_redis_connection('sms_code')
        conn.setex('sms_code_%s'%mobile,300,sms_code)
        #4.发送短信验证
        ccp=CCP()
        ccp.send_template_sms(mobile,[sms_code,'5'],1)
        #返回结果
        return Response({'message':'ok'})