from django.conf.urls import url

from app01 import views

urlpatterns = [
    url(r'^register/', views.register),
    url(r'^send/sms/', views.send_sms),
]