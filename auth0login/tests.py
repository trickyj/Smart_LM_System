from datetime import date

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .context_processors import is_leave_approver, leave_notifications
from .models import LeaveRequest


class LeaveNotificationsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.employee = User.objects.create_user(username="tushar", password="pwd")
        self.approver = User.objects.create_user(username="vicky", password="pwd")

    def test_is_leave_approver_for_named_user(self):
        self.assertTrue(is_leave_approver(self.approver))
        self.assertFalse(is_leave_approver(self.employee))

    def test_context_processor_counts_pending_leave_for_approver(self):
        LeaveRequest.objects.create(
            user=self.employee,
            leave_type="Personal",
            begin_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),
            requested_days=2,
            reason="Family work",
            status="Pending",
        )

        request = self.factory.get("/")
        request.user = self.approver

        context = leave_notifications(request)

        self.assertTrue(context["show_leave_notifications"])
        self.assertEqual(context["pending_leave_count"], 1)
        self.assertEqual(len(context["pending_leave_requests"]), 1)

    def test_context_processor_hides_notifications_for_non_approver(self):
        request = self.factory.get("/")
        request.user = self.employee

        context = leave_notifications(request)

        self.assertFalse(context["show_leave_notifications"])
        self.assertEqual(context["pending_leave_count"], 0)


class ApproveLeaveViewTests(TestCase):
    def setUp(self):
        self.employee = User.objects.create_user(username="biplab", password="pwd")
        self.approver = User.objects.create_user(username="mounia", password="pwd")

    def test_named_approver_can_open_approve_leave_page(self):
        self.client.force_login(self.approver)

        response = self.client.get(reverse("ApproveLeave"))

        self.assertEqual(response.status_code, 200)

    def test_non_approver_cannot_open_approve_leave_page(self):
        self.client.force_login(self.employee)

        response = self.client.get(reverse("ApproveLeave"))

        self.assertEqual(response.status_code, 302)

    def test_approving_leave_changes_status(self):
        leave = LeaveRequest.objects.create(
            user=self.employee,
            leave_type="Annual",
            begin_date=date(2026, 2, 10),
            end_date=date(2026, 2, 12),
            requested_days=3,
            reason="Vacation",
            status="Pending",
        )

        self.client.force_login(self.approver)
        response = self.client.post(f"{reverse('ApproveLeave')}?approveList={leave.id}")

        leave.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(leave.status, "Approved")
