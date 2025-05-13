from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError 
from datetime import timedelta


# Create your models here.
#todo, store cms id if student
class Statuses(models.TextChoices):
    #booking statuses
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    COMPLETED = 'completed', 'Completed'
    #Membership statuses
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    TERMINATED = 'terminated', 'Terminated'

class FacilityAvailabilityType(models.TextChoices):
    BOOKING_ONLY = 'booking_only', 'Booking Only'
    MEMBERSHIP_ONLY = 'membership_only', 'Membership Only'
    BOTH = 'both', 'Both Booking and Membership'

class PaymentRates(models.Model):
    facility = models.ForeignKey('Facility', on_delete=models.CASCADE, related_name='payment_rates')
    per_booking_rate = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Standard per booking rate for facility bookings"
    )
    membership_rate = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Standard monthly membership rate"
    )
    
    class Meta:
        verbose_name_plural = "Payment Rates"
    
    def __str__(self):
        facility_name = self.facility.facility_name.capitalize()
        if self.per_booking_rate and self.membership_rate:
            return f"{facility_name} - Booking & Membership Rates"
        elif self.per_booking_rate:
            return f"{facility_name} - Booking Rate"
        else:
            return f"{facility_name} - Membership Rate"
    
    def clean(self):
        """Validate that rates match facility availability type"""
        if self.facility.availability_type == FacilityAvailabilityType.BOOKING_ONLY and self.membership_rate:
            raise ValidationError("Booking-only facilities cannot have membership rates")
        
        if self.facility.availability_type == FacilityAvailabilityType.MEMBERSHIP_ONLY and self.per_booking_rate:
            raise ValidationError("Membership-only facilities cannot have booking rates")
        
        if not self.per_booking_rate and not self.membership_rate:
            raise ValidationError("At least one rate must be specified")
    
    @classmethod
    def get_booking_rate(cls, facility):
        """Get the standard hourly booking rate for a facility"""
        if not facility.is_bookable():
            return None
            
        try:
            return cls.objects.get(facility=facility).per_booking_rate
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_membership_rate(cls, facility, user=None):
        """
        Get the standard monthly membership rate for a facility
        If user is provided, return the user-specific rate
        """
        if not facility.allows_membership():
            return None
        
        # If user is provided, try to get user-specific rate
        if user:
            try:
                # Get user type-based rates
                user_rates = UserTypeRate.objects.get(user_type=user.type)
                
                # Return appropriate rate based on facility
                if facility.facility_name == 'swimming':
                    return user_rates.swimming_rate
                elif facility.facility_name == 'gym':
                    return user_rates.gym_rate
                else:
                    # For other facilities, return the standard rate
                    try:
                        return cls.objects.get(facility=facility).membership_rate
                    except cls.DoesNotExist:
                        return None
                        
            except UserTypeRate.DoesNotExist:
                # Fall back to standard rates if no user-specific rates defined
                pass
        
        # Standard rate logic (existing code)
        try:
            return cls.objects.get(facility=facility).membership_rate
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_combined_membership_rate(cls, facilities, user=None):
        """
        Calculate the membership rate for multiple facilities with special pricing
        for swimming + gym combination basically a mastercard, taking user type into account if provided
        """
        if not facilities or len(facilities) == 0:
            return 0

        # Convert QuerySet to a list of facility names for easier checking
        facility_names = [facility.facility_name for facility in facilities]
        
        # Check if both swimming and gym are selected (Master Card case)
        if 'swimming' in facility_names and 'gym' in facility_names:
            # If user is provided, try to get user-specific master card rate
            if user:
                try:
                    user_rates = UserTypeRate.objects.get(user_type=user.type)
                    return user_rates.master_card_rate
                except UserTypeRate.DoesNotExist:
                    # Fall back to standard master card rate if no user-specific rate defined
                    return 1500
            else:
                # Standard master card rate
                return 1500
        
        # Calculate sum of rates for individual facilities
        total = 0
        for facility in facilities:
            rate = cls.get_membership_rate(facility, user)
            if rate:
                total += rate
        
        return total


class UserTypes(models.TextChoices):
    STAFF = 'staff', "Staff"
    FACULTY = 'faculty', 'Faculty'
    STUDENT = 'student', 'Student'
    ALUMNI = 'alumni', 'Alumni'
    RESIDENT = 'resident', 'Resident'
    NSTP_TENANT_PAKISTANI = 'nstp resident pakistani', 'NSTP Resident Pakistani'
    NSTP_TENANT_FOREIGN = 'nstp resident foreign', 'NSTP Resident Foreign'
    

class FacilityTypes(models.TextChoices):
    SWIMMING = 'swimming', 'Swimming'
    GYM = 'gym', 'Gym'
    BOWLING = 'bowling', 'Bowling'
    BADMINTON = 'badminton', 'Badminton'
    POOL = 'pool', "Pool"
    TABLE_TENNIS = 'table tennis', 'Table Tennis' # for scalability it is required that the typeof facility is also mentioned 

class User(AbstractUser):
    phone_number = models.CharField(max_length=11, blank=True)
    type = models.CharField(max_length=35, choices=UserTypes.choices)

class PaymentMethods(models.TextChoices):
    ONLINE = 'online', 'Online'
    CASH = 'cash', 'Cash'

class Payment(models.Model):
    total_amount = models.PositiveIntegerField()
    date_of_payment = models.DateField(auto_now_add=True)
    due_date = models.DateField(auto_now_add=True)
    method = models.CharField(max_length=6, choices=PaymentMethods.choices)
    payment_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_users")

class Booking(models.Model):
    creation_datetime = models.DateTimeField(auto_now_add=True)
    timing = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Statuses.choices,
        default=Statuses.PENDING
    )
    is_walkin = models.BooleanField()
    booking_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="booking_users")
    booking_payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="booking_payments")
    booking_facility = models.ForeignKey('Facility', on_delete=models.CASCADE, related_name="bookings")
    
    # Adding fields for bowling-specific data
    number_of_players = models.PositiveIntegerField(null=True, blank=True)
    is_mixed_gender = models.BooleanField(default=False)
    alleys_booked = models.PositiveIntegerField(default=1)

        
class Membership(models.Model):
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    status = models.CharField(
        max_length=10,
        choices=[
            (Statuses.ACTIVE, Statuses.ACTIVE.label),
            (Statuses.INACTIVE, Statuses.INACTIVE.label),
            (Statuses.TERMINATED, Statuses.TERMINATED.label)
        ],
        default=Statuses.INACTIVE
    )
    fixed_amount = models.PositiveIntegerField()
    membership_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="membership_users")
    membership_payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="membership_payments")
    membership_facility = models.ManyToManyField('Facility', related_name="membership_facilities")
    

class FacilityCapacity(models.TextChoices):
    BOWLING = '4', 'Bowling Alleys'
    POOL = '3', 'Pool Tables'
    TABLE_TENNIS = '2', 'Table Tennis Tables'

class FacilityCooldown(models.TextChoices):
    BOWLING = 'B60', 'B60 Minutes'  #  B60 for Bowling because values must be unique
    POOL = 'P60', 'P60 Minutes'     # same for pool
    TABLE_TENNIS = 'T30', 'T30 Minutes'  # Changed to T30 for Table Tennis

class Facility(models.Model):
    facility_name = models.CharField(
        max_length=20,
        choices=FacilityTypes.choices
    )
    availability_type = models.CharField( 
        max_length=15,
        choices=FacilityAvailabilityType.choices,
        default=FacilityAvailabilityType.BOTH,
        help_text="Determines if facility is available for booking, membership or both"
    )
    capacity = models.CharField(
        max_length=2,
        choices=FacilityCapacity.choices,
        default=FacilityCapacity.BOWLING,  # Default value this is later overwrriten
        help_text="Total number of units available for this facility",
        null=True
    )
    cooldown_time = models.CharField(
        max_length=3,
        choices=FacilityCooldown.choices,
        default=FacilityCooldown.BOWLING,  # Default value this is later overwritten
        help_text="Cooldown time in minutes between bookings",
        null=True
    )

    def __str__(self):
        return self.facility_name.capitalize()

    def is_bookable(self):
        """Check if facility can be booked on a per-use basis"""
        return self.availability_type in [
            FacilityAvailabilityType.BOOKING_ONLY, 
            FacilityAvailabilityType.BOTH
        ]
    
    def allows_membership(self):
        """Check if facility can be accessed via membership"""
        return self.availability_type in [
            FacilityAvailabilityType.MEMBERSHIP_ONLY, 
            FacilityAvailabilityType.BOTH
        ]

    def get_available_units(self, timing):
        """
        Check how many units (alleys/tables) are available at given time
        considering ongoing bookings and cooldown periods
        """
        
        # Get the facility's cooldown time in minutes
        cooldown_map = {
            'B60': 60,  # Bowling
            'P60': 60,  # Pool
            'T30': 30,  # Table Tennis
        }
        cooldown = cooldown_map.get(self.cooldown_time, 60)  # Default to 60 if not found
        
        # Calculate the time window
        time_start = timing - timedelta(minutes=cooldown)
        time_end = timing + timedelta(minutes=cooldown)
        
        # Get all bookings in this time window
        overlapping_bookings = self.bookings.filter(
            timing__range=(time_start, time_end),
            status__in=['confirmed', 'pending']
        )
        
        # Calculate total units booked in this window
        units_booked = sum(
            booking.alleys_booked if self.facility_name == 'bowling'
            else 1  # For pool and table tennis, each booking uses 1 unit
            for booking in overlapping_bookings
        )
        
        # Return available units
        total_units = int(self.capacity)
        return total_units - units_booked


class UserTypeRate(models.Model):
    """
    Model to store different rates for each user type
    Allows for custom pricing based on user category
    """
    user_type = models.CharField(
        max_length=30,
        choices=UserTypes.choices,
        unique=True,  # One pricing record per user type
        help_text="User type this rate applies to"
    )
    
    # Base rates for individual facilities
    swimming_rate = models.PositiveIntegerField(
        default=1000,
        help_text="Monthly rate for swimming pool access"
    )
    gym_rate = models.PositiveIntegerField(
        default=1000,
        help_text="Monthly rate for gym access"
    )
    
    # Master card rate (combined swimming + gym)
    master_card_rate = models.PositiveIntegerField(
        default=1500,
        help_text="Monthly rate for combined swimming pool and gym access (Master Card)"
    )
    
    # Registration fee (one-time)
    registration_fee = models.PositiveIntegerField(
        default=2000,
        help_text="One-time registration fee"
    )
    
    class Meta:
        verbose_name = "User Type Rate"
        verbose_name_plural = "User Type Rates"
    
    def __str__(self):
        return f"Rate for {self.get_user_type_display()}"