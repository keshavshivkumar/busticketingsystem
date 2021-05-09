from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('operatorhome', views.operatorhome, name="operatorhome"),
    path('seebuses', views.seebuses, name="seebuses"),
    path('findbus', views.findbus, name="findbus"),
    path('bookings', views.bookings, name="bookings"),
    path('cancellings', views.cancellings, name="cancellings"),
    path('seebookings', views.seebookings, name="seebookings"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('success', views.success, name="success"),
    path('signout', views.signout, name="signout"),
    path('addbus', views.addbus, name="addbus"),
    path('deletebus', views.deletebus, name="deletebus"),
]
