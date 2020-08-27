from django.shortcuts import render, redirect

# Create your views here.

def index(request):
	return render(request, 'S_LMS/index.html')