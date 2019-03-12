from django.conf import settings
from rest_framework import serializers
from  django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS

from oauth.models import OAuthQQUser
from users.models import User
import re

class OauthSerializer(serializers.ModelSerializer):
    # 显示指明字段
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    token = serializers.CharField(read_only=True)
    mobile = serializers.CharField(max_length=11)  # 不进行唯一值判断

    access_token = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'password', 'sms_code', 'token', 'access_token')

        extra_kwargs = {
            'username': {
                'read_only': True
            },
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True
            },
        }

    # 验证手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式不正确')
        return value

    def validate(self, attrs):

        # 短信验证
        conn = get_redis_connection('sms_code')
        rel_sms_code = conn.get('sms_code_%s' % attrs['mobile'])
        # 判断短信是否失效
        if not rel_sms_code:
            raise serializers.ValidationError('短信失效')
        # 短信比对
        if attrs['sms_code'] != rel_sms_code.decode():
            raise serializers.ValidationError('短信错误')

        # 解密openid
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(attrs['access_token'])
        except:
            raise serializers.ValidationError('错误的openid值')
        # 从解密后的数据提取openid
        openid = data.get('openid')
        if not openid:
            raise serializers.ValidationError('openid失效')

        # attrs中添加openid
        attrs['openid']=openid

        # 判断用户
        try:
            user = User.objects.get(mobile=attrs['mobile'])
        except:
            # 用户未注册
            return attrs
        else:
            # 用户注册
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码错误')

            attrs['user'] = user
            return attrs

    def create(self, validated_data):

        user = validated_data.get('user')
        if not user:
            # 用户未注册
            user=User.objects.create_user(username=validated_data['mobile'],password=validated_data['password'],mobile=validated_data['mobile'])


        # 绑定
        OAuthQQUser.objects.create(user=user,openid=validated_data['openid'])

        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # user添加token
        user.token = token

        return user