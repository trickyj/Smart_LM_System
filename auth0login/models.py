from django.db import models
from django.contrib.auth.models import User

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('Personal', 'Personal'),
        ('Annual', 'Annual'),
        ('Military', 'Military'),
        ('PDL', 'Pregnancy Disability Leave'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPES)
    begin_date = models.DateField()
    end_date = models.DateField()
    requested_days = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default='Pending')  # e.g., Pending, Approved, Rejected

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.begin_date} to {self.end_date})"