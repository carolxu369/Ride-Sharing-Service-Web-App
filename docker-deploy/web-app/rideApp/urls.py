from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register),
    path('welcome', views.homePage),
    path('login',views.login),
    path('startRide', views.startRide),
    path('joinRide', views.joinRide),
    path('sharer_search', views.sharer_search),
    path('user_main', views.user_main),
    path('driver_main', views.driver_main),
    path('reg_driver', views.reg_driver),
    path('driver_profile', views.driver_profile),
    path('driver_search', views.driver_search),
    path('ongoing_ride', views.ongoing_ride),
    path('view_ride/<int:ride_id>', views.view_ride),
    path('logout', views.logout),
    path('edit_ride/<int:ride_id>', views.edit_ride),
    path('complete_ride/<int:ride_id>', views.complete_ride),
    path('owner_edit', views.owner_edit)
]