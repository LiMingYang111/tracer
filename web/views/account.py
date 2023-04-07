from django.shortcuts import render, HttpResponse

from web.forms import account

def register(req):
    form = account.RegisterModelForm()
    return render(req, 'web/register.html', {'form': form,})