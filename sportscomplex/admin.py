from django.contrib import admin
from .models import (
    User, 
    Booking, 
    Facility, 
    Payment, 
    Membership, 
    PaymentRates,
    UserTypeRate  # Add the new model import
)

# custom admin classes for better display
class FacilityAdmin(admin.ModelAdmin):
    search_fields = ['facility_name', 'id']
    list_display = ('facility_name', 'availability_type')
    list_filter = ('availability_type',)
    
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'type')
    list_filter = ('type',)
    search_fields = ('username', 'email', 'first_name', 'last_name')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_user', 'booking_facility', 'timing', 'status', 'is_walkin')
    list_filter = ('status', 'booking_facility', 'is_walkin')
    search_fields = ('booking_user__username', 'booking_facility__facility_name')
    date_hierarchy = 'timing'


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_user', 'total_amount', 'date_of_payment', 'method')
    list_filter = ('method',)
    search_fields = ('payment_user__username',)
    date_hierarchy = 'date_of_payment'

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('membership_user', 'start_date', 'end_date', 'status', 'fixed_amount')
    list_filter = ('status',)
    search_fields = ('membership_user__username',)
    date_hierarchy = 'start_date'
    filter_horizontal = ('membership_facility',)


class PaymentRatesAdmin(admin.ModelAdmin):
    list_display = ('facility', 'per_booking_rate', 'membership_rate')
    list_filter = ('facility',)

# New admin class for UserTypeRate
class UserTypeRateAdmin(admin.ModelAdmin):
    list_display = ('get_user_type_display', 'swimming_rate', 'gym_rate', 'master_card_rate', 'registration_fee')
    list_filter = ('user_type',)
    
    def get_user_type_display(self, obj):
        return obj.get_user_type_display()
    get_user_type_display.short_description = 'User Type'

# Register models with custom admin classes
admin.site.register(User, UserAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Facility, FacilityAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(PaymentRates, PaymentRatesAdmin)
admin.site.register(UserTypeRate, UserTypeRateAdmin)  # Register the new model