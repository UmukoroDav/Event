from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('ticket/', views.ticket, name='ticket'),
    path('logout/', views.applogout, name='logout'),
    path('login/', views.applogin, name='applogin'),
    path('edit-profile/', views.edituser, name='edituser'),
    path('register/', views.appregister, name='appregister'),
    path('buy-ticket/<int:ticket_id>/', views.initiate_payment, name='ticket_purchase'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
]
