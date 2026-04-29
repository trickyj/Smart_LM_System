from .models import LeaveRequest

LEAVE_APPROVER_GROUP = "LeaveApprovers"


def is_leave_approver(user):
    if not user.is_authenticated:
        return False

    return user.is_staff or user.groups.filter(name=LEAVE_APPROVER_GROUP).exists()


def leave_notifications(request):
    user = request.user
    if not is_leave_approver(user):
        return {
            "show_leave_notifications": False,
            "pending_leave_count": 0,
            "pending_leave_requests": [],
        }

    pending_requests = list(
        LeaveRequest.objects.filter(status="Pending")
        .select_related("user")
        .order_by("-id")[:5]
    )

    return {
        "show_leave_notifications": True,
        "pending_leave_count": LeaveRequest.objects.filter(status="Pending").count(),
        "pending_leave_requests": pending_requests,
    }
