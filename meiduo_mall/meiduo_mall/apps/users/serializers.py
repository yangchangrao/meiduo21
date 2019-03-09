from django_redis import get_redis_connection
from rest_framework import serializers
from users.models import User
from rest_framework_jwt.settings import api_settings
import re

class UserSerializer(serializers.ModelSerializer):
    #显示致命字段
    password2 = serializers.CharField(max_length=20,min_length=8,write_only=True)
    sms_code = serializers.CharField(max_length=6,min_length=6,write_only=True)
    allow = serializers.CharField(write_only=True)

    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id','username','mobile','password','password2','sms_code','allow')
        extra_kwargs = {
            'username':{
                'max_length':20,
                'min_length':5
            },
        'password':{
            'max_length': 20,
            'min_length': 8,
            'write_only':True
            },
        }

    #验证手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError("手机格式不正确")
        return value
    #验证协议状态
    def validate_allow(self, value):

        if value != 'true':
            raise serializers.ValidationError("协议未同意")
        return value

    def validate(self, attrs):
        #判断手机号和用户名是否一致
        if re.match(r'1[3-9]\d{9}$',attrs['username']):
            if attrs['username'] != attrs['mobile']:
                raise serializers.ValidationError('手机号和用户名不一致')
        # 密码验证
        if attrs['password2'] != attrs['password']:
            raise serializers.ValidationError('密码不一致')

        # 短信验证
        conn = get_redis_connection('sms_code')
        rel_sms_code = conn.get('sms_code_%s' % attrs['mobile'])
        # 判断短信是否失效
        if not rel_sms_code:
            raise serializers.ValidationError('短信失效')
        # 短信比对
        if attrs['sms_code'] != rel_sms_code.decode():
            raise serializers.ValidationError('短信错误')

        return attrs

    def create(self, validated_data):

        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # user=User.objects.create(**validated_data)  # 不会加密密码
        user = User.objects.create_user(**validated_data)  # 加密密码
        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # user添加token
        user.token = token

        return user
