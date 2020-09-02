from django.urls import path, include
from . import views

urlpatterns = [
	path('',views.index, name='index'),
	path('dashboard', views.dashboard, name='dashboard'),
	path('logout', views.logout),
	path('', include('django.contrib.auth.urls')),
	path('', include('social_django.urls')),
	path('profile', views.profile, name='profile')


]