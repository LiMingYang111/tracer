import random

from django.core.validators import RegexValidator
from django.shortcuts import render, HttpResponse
from django.conf import settings
from django import forms

from utils.Tencent import sms
from app01 import models

# Create your views here.
def send_sms(request):
    tpl = request.GET.get('tpl')
    tpl_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    if not tpl_id:
        return HttpResponse('模板不存在')
    code = random.randrange(1000, 9999)
    res = sms.send_sms_single('15562550129', tpl_id, [code,])
    print(res)
    if res['result'] == 0:
        return HttpResponse('成功')
    else:
        return HttpResponse(res['errmsg'])

class RegisterModelForm(forms.ModelForm):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^1[3456789]\d{9}$', '手机号格式错误'),])
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput())
    code = forms.CharField(label='验证码', widget=forms.TextInput())
    class Meta:
        model = models.UserInfo
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{}'.format(field.label)

def register(req):
    form = RegisterModelForm()
    return render(req, 'app01/register.html', {'form': form})

