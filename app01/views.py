from django.shortcuts import render, HttpResponse
from utils.Tencent import sms
from django.conf import settings
import random

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
