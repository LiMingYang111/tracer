from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
from django.conf import settings

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def send_sms_single(phone_num, template_id, template_param_list):
    """
    :param phone_num: 手机号
    :param template_id: 腾讯云短信模板ID
    :param template_param_list: 短信模板所需参数列表
    :return:
    """
    appid = settings.TENCENT_SMS_APP_ID
    appkey = settings.TENCENT_SMS_APP_KEY
    sms_sign = settings.TENCENT_SMS_SIGN
    print(appid, appkey, sms_sign)
    sender = SmsSingleSender(appid, appkey)
    try:
        response = sender.send_with_param(86, phone_num, template_id, template_param_list, sign=sms_sign)
    except HTTPError as e:
        response = {'result': 1000, 'errmsg': "网络异常发送失败"}
    return response

