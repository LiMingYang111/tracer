from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

from web.forms import account


def register(req):
    if req.method == 'GET':
        form = account.RegisterModelForm()
        return render(req, 'web/register.html', {'form': form})
    print(req.POST)
    form = account.RegisterModelForm(data=req.POST)
    if form.is_valid():
        # print(form.cleaned_data)
        # instance = form.save()  会返回当前存入数据库的那条数据，并且只会存储数据库中有的字段
        form.save()
        return JsonResponse({'status': True, 'data': '/web/login/'})
        print(form.errors)
    return JsonResponse({'status': False, 'error': form.errors})

def send_sms(req):
    print(req.GET)
    form = account.SendSmsForm(data=req.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})

def login_sms(req):
    if req.method == 'GET':
        form = account.LoginSmsForm()
        return render(req, 'web/login_sms.html', {'form': form})

    form = account.LoginSmsForm(data=req.POST)
    if form.is_valid():
        return JsonResponse({'status': True, 'data': '/web/index/'})
    return JsonResponse({'status': False, 'error': form.errors})