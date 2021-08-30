
from django.conf.urls import url, include
from api import views

urlpatterns = [
    url(r'^login/', views.LoginView.as_view()),
    # url(r'^freight_bill/', views.FreightBill.as_view()),
    url(r'^pro/login/', views.ProLoginView.as_view()),
    url(r'^pro/order/', views.ProSearchFreightUsernamePricesView.as_view()),
    url(r'^pro/freight/', views.ProStatisticsFreightView.as_view()),
    url(r'^pro/freight_detail/', views.ProStatisticsFreightDetailView.as_view()),
    url(r'^pro/search_someone/freight_total/', views.ProSearchSomeoneFreightView.as_view()),
    url(r'^pro/contacts/search_name/', views.ProSearchContact.as_view()),
    url(r'^pro/brand/brand', views.ProAllBrand.as_view()),
    # url(r'^pro/slideshow/', views.SlideShow.as_view()),
    # url(r'^pro/contacts/search_detail/', views.ProSearchContactDetail.as_view()),
]

