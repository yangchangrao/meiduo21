from random import randint
from django.shortcuts import render
# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
#from meiduo_mall.libs.yuntongxun.sms import CCP
from threading import Thread
from celery_tasks.sms.tasks import send_sms_code
from users.models import User
from users.serializers import UserSerializer
# 使用线程执行异步
# def send_sms_code(self, mobile, sms_code):
#     ccp = CCP()
#     ccp.send_template_sms(mobile, [sms_code, '5'], 1)

class SMS_CODEView(APIView):
    #发送短信

    def get(self,request,mobile):
        # 判断发送时间
        conn = get_redis_connection('sms_code')
        flag=conn.get('sms_code_flag_%s'%mobile)
        if flag:
            return Response({'error':'验证码发送频繁'},status=402)
        # 1.获取手机号
        # 2.生成短信验证码
        sms_code= '%06d' % randint(0,999999)
        print(sms_code)
        #3.在redis保存真实的短信验证码
           #生成管道对象
        pl = conn.pipeline()
        pl.setex('sms_code_%s'%mobile, 300 , sms_code)
        pl.setex('sms_code_panduan_%s' % mobile ,60 , 2)
        #链接redis传递数据
        pl.execute()
        #4.发送短信验证
        # ccp=CCP()
        # ccp.send_template_sms(mobile,[sms_code,'5'],1)
        # t=Thread(target=send_sms_code,args=(mobile,sms_code))
        # t.start()
        #celery调用
        send_sms_code.delay(mobile , sms_code)
        #返回结果
        return Response({'message':'ok'})

class UsernameView(APIView):
    # 判断用户名是否重复
    def get(self,request,username):
        # 1.获取用户名
        # 2.根据用户名查询用户对象数量
        count=User.objects.filter(username=username).count()
        # 3.返回数量
        return Response({
            # 'username':username,
            'count':count
        })

class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self,request,mobile):
        count=User.objects.filter(mobile=mobile).count()
        return Response({
            'count':count,
            # 'mobile':mobile
        })

class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = UserSerializer
