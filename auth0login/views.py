from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout as log_out
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .models import LeaveRequest
from .context_processors import is_leave_approver

from datetime import datetime
import json
# Create your views here.

def index(request):
	user = request.user
	if user.is_authenticated:
		return redirect(dashboard)
	else:
		return render(request, 'S_LMS/index.html')

def is_admin(user):
    return user.is_staff
# This below code loads the home page and display the logged in users data. User ID, name, picture and email.

# @login_required
# def dashboard(request):
#     user = request.user
#     auth0user = user.social_auth.get(provider='auth0')
#     userdata = {
#         'user_id': auth0user.uid,
#         'name': user.first_name,
#         'picture': auth0user.extra_data['picture'],
#         'email': auth0user.extra_data['email']
#     }

#     return render(request, 'S_LMS/home.html', {
#         'auth0User': auth0user,
#         'userdata': json.dumps(userdata, indent=4)
#     })

@login_required
def dashboard(request):
    user = request.user
    try:
        auth0user = user.social_auth.get(provider='auth0')
        userdata = {
            'user_id': auth0user.uid,
            'name': user.first_name or user.username,
            'picture': auth0user.extra_data.get('picture', ''),
            'email': auth0user.extra_data.get('email', user.email)
        }
    except user.social_auth.model.DoesNotExist:
        # fallback if no Auth0 profile is linked
        auth0user = None
        userdata = {
            'user_id': user.id,
            'name': user.first_name or user.username,
            'picture': '',
            'email': user.email,
            'note': 'Auth0 data not found'
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

# @login_required
# def profile(request):
#     user = request.user
#     auth0user = user.social_auth.get(provider='auth0')
#     userdata = {
#         'user_id': auth0user.uid,
#         'name': user.first_name,
#         'picture': auth0user.extra_data['picture'],
#         'email': auth0user.extra_data['email']
#     }

#     return render(request, 'S_LMS/profile.html', {
#         'auth0User': auth0user,
#         'userdata': json.dumps(userdata, indent=4)
#     })

@login_required
def profile(request):
    user = request.user
    try:
        auth0user = user.social_auth.get(provider='auth0')
        userdata = {
            'user_id': auth0user.uid,
            'name': user.first_name or user.username,
            'picture': auth0user.extra_data.get('picture', ''),
            'email': auth0user.extra_data.get('email', user.email)
        }
    except user.social_auth.model.DoesNotExist:
        auth0user = None
        userdata = {
            'user_id': user.id,
            'name': user.first_name or user.username,
            'picture': '',
            'email': user.email,
            'note': 'Auth0 data not found'
        }

    return render(request, 'S_LMS/profile.html', {
        'auth0User': auth0user,
        'userdata': json.dumps(userdata, indent=4)
    })


@login_required
def ApplyForLeave(request):
    if request.method == 'POST':
        leave_type = request.POST.get('leaveOption')
        begin_date = request.POST.get('BeginDate')
        end_date = request.POST.get('EndDate')
        reason = request.POST.get('Reason')

        if not leave_type:
            return render(request, 'S_LMS/ApplyForLeave.html', {
                'error': 'Please select a leave type.',
                'available_days': available_days,
                'leave_requests': leave_requests
            })
            
        # Calculate requested days
        requested_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(begin_date, '%Y-%m-%d')).days + 1

        # Save the leave request
        LeaveRequest.objects.create(
            user=request.user,
            leave_type=leave_type,
            begin_date=begin_date,
            end_date=end_date,
            requested_days=requested_days,
            reason=reason
        )

        return redirect('ApplyForLeave')  # Redirect to the same page or another page
    
    # Fetch leave requests for the logged-in user
    leave_requests = LeaveRequest.objects.filter(user=request.user).order_by('-begin_date')

    # Calculate available days
    total_leaves = 10  # Example: Total leaves allocated to the user
    used_leaves = LeaveRequest.objects.filter(user=request.user).aggregate(Sum('requested_days'))['requested_days__sum'] or 0
    available_days = total_leaves - used_leaves

    return render(request, 'S_LMS/ApplyForLeave.html', {
        'leave_requests': leave_requests,
        'available_days': available_days

  
    })

@login_required
@user_passes_test(is_leave_approver)  # Restrict access to leave approvers
def ApproveLeave(request):
    if request.method == 'POST':
        # Handle approval
        if 'approveList' in request.GET:
            leave_id = request.GET.get('approveList')
            leave_request = get_object_or_404(LeaveRequest, id=leave_id, status='Pending')
            leave_request.status = 'Approved'
            leave_request.save()
        # Handle decline
        elif 'declineList' in request.GET:
            leave_id = request.GET.get('declineList')
            leave_request = get_object_or_404(LeaveRequest, id=leave_id, status='Pending')
            leave_request.status = 'Declined'
            leave_request.save()

        return redirect('ApproveLeave')  # Redirect back to the same page

    # Fetch all pending leave requests
    pending_leaves = LeaveRequest.objects.filter(status='Pending').order_by('-begin_date')

    return render(request, 'S_LMS/ApproveLeave.html', {'leavesArray2': pending_leaves})



@login_required
@user_passes_test(is_admin)
def LeaveHistory(request):
    selected_user = request.GET.get('user', '')
    
    if selected_user:
        leaves = LeaveRequest.objects.filter(user__username=selected_user).exclude(status='Pending').order_by('-begin_date')
    else:
        leaves = LeaveRequest.objects.exclude(status='Pending').order_by('-begin_date')
    
    users = LeaveRequest.objects.values_list('user__username', flat=True).distinct()

    return render(request, 'S_LMS/LeaveHistory.html', {
        'leavesArray': leaves,
        'users': users,
        'selected_user': selected_user
    })


# def ApproveLeave(request):
#     return render (request, 'S_LMS/ApproveLeave.html')

def handler404(request, *args, **argv):
    return render(request, '404.html', status=404)


def handler500(request, *args, **argv):
    return render(request, '500.html', status=500)
