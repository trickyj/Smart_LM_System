from django.urls import path, include
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('dashboard', views.dashboard, name='dashboard'),
	path('logout', views.logout),
	path('', include('django.contrib.auth.urls')),
	path('', include('social_django.urls')),
	path('profile', views.profile, name='profile'),
	path('ApplyForLeave', views.ApplyForLeave, name='ApplyForLeave'),
	path('ApproveLeave', views.ApproveLeave, name='ApproveLeave'),
	path('LeaveHistory', views.LeaveHistory, name='LeaveHistory'),
]