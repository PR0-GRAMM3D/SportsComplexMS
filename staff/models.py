from django.db import models
from sportscomplex.models import User, Facility

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")   #user_id
    assignment = models.ManyToManyField(
        Facility, 
        through='StaffFacilityAssignment',
        related_name="staff_assignments"
    )

class StaffFacilityAssignment(models.Model):
    assignment_date = models.DateField()
    shift = models.CharField(max_length=15)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)