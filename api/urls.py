
from django.conf.urls import url, include
from api import views

urlpatterns = [
    url(r'^login/', views.LoginView.as_view()),
    url(r'^freight_bill/', views.FreightBill.as_view()),
]
