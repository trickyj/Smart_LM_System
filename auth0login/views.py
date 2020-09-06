from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as log_out
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
import json
# Create your views here.

def index(request):
	user = request.user
	if user.is_authenticated:
		return redirect(dashboard)
	else:
		return render(request, 'S_LMS/index.html')

# This below code loads the home page and display the logged in users data. User ID, name, picture and email.

@login_required
def dashboard(request):
    user = request.user
    auth0user = user.social_auth.get(provider='auth0')
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture'],
        'email': auth0user.extra_data['email']
    }

    return render(request, 'S_LMS/home.html', {
        'auth0User': auth0user,
        'userdata': json.dumps(userdata, indent=4)
    })

# this below given code will logout the user. 

def logout(request):
    log_out(request)
    return_to = urlencode({'returnTo': request.build_absolute_uri('/')})
    logout_url = 'https://%s/v2/logout?client_id=%s&%s' % \
                 (settings.SOCIAL_AUTH_AUTH0_DOMAIN, settings.SOCIAL_AUTH_AUTH0_KEY, return_to)
    return HttpResponseRedirect(logout_url)

#this below given code will load the users profile details.

@login_required
def profile(request):
    user = request.user
    auth0user = user.social_auth.get(provider='auth0')
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture'],
        'email': auth0user.extra_data['email']
    }

    return render(request, 'S_LMS/profile.html', {
        'auth0User': auth0user,
        'userdata': json.dumps(userdata, indent=4)
    })

def ApplyForLeave(request):
    return render (request, 'S_LMS/ApplyForLeave.html')

def ApproveLeave(request):
    return render (request, 'S_LMS/ApproveLeave.html')

def handler404(request, *args, **argv):
    return render(request, '404.html', status=404)


def handler500(request, *args, **argv):
    return render(request, '500.html', status=500)
