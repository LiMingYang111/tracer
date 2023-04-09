import random

from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django_redis import get_redis_connection

from web import models
from web.forms import bootstrap
from utils.Tencent import sms
from utils.encrypt import md5

class RegisterModelForm(bootstrap.BootstrapForm, forms.ModelForm):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')])
    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': '密码长度不能小于8个字符',
            'max_length': '密码长度不能大于64个字符'},
        widget=forms.PasswordInput(),)
    confirm_password = forms.CharField(
        label='确认密码',
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': '密码长度不能小于8个字符',
            'max_length': '密码长度不能大于64个字符'},
        widget=forms.PasswordInput(),)
    code = forms.CharField(label='验证码', widget=forms.TextInput())

    class Meta:
        model = models.UserInfo
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'code']

    def clean_username(self):
        username = self.cleaned_data['username']
        exist = models.UserInfo.objects.filter(username=username).exists()
        if exist:
            raise ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exist = models.UserInfo.objects.filter(email=email).exists()
        if exist:
            raise ValidationError('邮箱已存在')
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        return md5(password)

    def clean_confirm_password(self):
        password, confirm_password = self.cleaned_data.get('password'), self.cleaned_data['confirm_password']
        confirm_password = md5(confirm_password)
        if confirm_password != password:
            raise ValidationError('两次密码不一致')
        return confirm_password

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists():
            raise ValidationError('手机号已注册')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data['mobile_phone']
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新获取')
        redis_str_code = redis_code.decode('utf8')
        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误')
        return code

class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')])

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        tpl = self.data.get('tpl')
        tpl_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not tpl_id:
            raise ValidationError('短信模板错误')

        # print(self.cleaned_data)
        exist = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl == 'register':
            if exist:
                raise ValidationError('手机号已存在')
        if tpl == 'login':
            if not exist:
                raise ValidationError('手机号未注册')

        # 发送短信
        code = random.randrange(1000, 9999)
        response = sms.send_sms_single(mobile_phone, tpl_id, [code,])
        if response.get('result') != 0:
            print(response)
            raise ValidationError('短信发送失败，{}'.format(response['errmsg']))
        # 短信写入Redis
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)

        return mobile_phone

class LoginSmsForm(bootstrap.BootstrapForm, forms.Form):
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')])
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput())

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        # 返回数据库的一行数据对象
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not user_object:
            raise ValidationError('手机号未注册')
        return user_object

    def clean_code(self):
        code = self.cleaned_data['code']
        user_object = self.cleaned_data.get('mobile_phone')
        if not user_object:
            return code
        mobile_phone = user_object.mobile_phone

        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新获取')
        if redis_code.decode('utf8') != code.strip():
            raise ValidationError('验证码错误')
        return code

