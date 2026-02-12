from django.contrib import admin
from .models import LeaveRequest
from django.urls import path
from .import views
admin.site.register(LeaveRequest)
urlpatterns = [
    # Other URLs...
    path('ApproveLeave/', views.ApproveLeave, name='ApproveLeave'),
]
