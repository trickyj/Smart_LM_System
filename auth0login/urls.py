from django.urls import path, include
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
	path('',views.index, name='index'),
	path('dashboard', views.dashboard, name='dashboard'),
	path('logout', views.logout),
	path('', include('django.contrib.auth.urls')),
	path('', include('social_django.urls')),
	path('profile', views.profile, name='profile'),
	path('ApplyForLeave', csrf_exempt(views.ApplyForLeave), name='ApplyForLeave'),
	path('ApproveLeave', csrf_exempt(views.ApproveLeave), name='ApproveLeave'),
    path('LeaveHistory', csrf_exempt(views.LeaveHistory), name='LeaveHistory'),


]