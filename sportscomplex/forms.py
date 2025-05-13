# here we make forms to be inserted into html

from django import forms
from .models import UserTypes
from django.utils import timezone
from datetime import time

from django import forms
from .models import (
    Booking, 
    Facility, 
    PaymentMethods, 
    Membership, 
    FacilityAvailabilityType, 
    UserTypes
)

class NewUserForm(forms.Form):
    username = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Username'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        max_length=20,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Password'
        })
    )
    confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Confirm Password'
        })
    )
    phone_number = forms.CharField(
        min_length=11,
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Phone Number'
        })
    )
    first_name = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Last Name'
        })
    )
    type = forms.ChoiceField(
        choices=[choice for choice in UserTypes.choices if choice[0] != 'staff'],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border rounded',
        })
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        max_length=20,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Password'
        })
    )


class BookingFacilityForm(forms.ModelForm):
    # Define business hours for facilities
    FACILITY_HOURS = {
        'bowling': {
            # Monday to Thursday (0-3): 13:00 to 21:00
            0: (time(13, 0), time(21, 0)),
            1: (time(13, 0), time(21, 0)),
            2: (time(13, 0), time(21, 0)),
            3: (time(13, 0), time(21, 0)),
            # Friday (4): 14:30 to 21:00
            4: (time(14, 30), time(21, 0)),
            # Saturday (5): 13:00 to 21:00
            5: (time(13, 0), time(21, 0)),
            # Sunday (6): Closed
            6: (None, None),
        }
    }

    class Meta:
        model = Booking
        fields = ['booking_facility', 'timing']

    # Add total_amount field to store the booking rate
    total_amount = forms.IntegerField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'readonly': 'readonly',
        }),
        label="Booking Fee (Rs)",
        required=False  # We'll calculate this automatically
    )

    payment_method = forms.ChoiceField(
        choices=PaymentMethods.choices,
        widget=forms.RadioSelect(attrs={'class': 'mr-2'}),
        label="Payment Method"
    )

    booking_facility = forms.ModelChoiceField(
        queryset=Facility.objects.filter(facility_name__in=['bowling', 'badminton', 'table tennis', 'pool']),
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        label="Facility"
    )

    timing = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'type': 'datetime-local',
        }),
        label="Booking Time"
    )

    def clean(self):
        cleaned_data = super().clean()
        facility = cleaned_data.get('booking_facility')
        timing = cleaned_data.get('timing')

        if facility and timing:
            facility_name = facility.facility_name

            # Check if the facility has defined business hours
            if facility_name in self.FACILITY_HOURS:
                # Get the day of the week (0=Monday, 6=Sunday)
                day_of_week = timing.weekday()
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

                # Get business hours for the selected day
                open_time, close_time = self.FACILITY_HOURS[facility_name].get(day_of_week, (None, None))

                # Check if the facility is closed on the selected day
                if open_time is None or close_time is None:
                    raise forms.ValidationError(
                        f"{facility.get_facility_name_display()} is closed on {day_names[day_of_week]}."
                    )

                # Check if the booking time is within business hours
                booking_time = timing.time()
                if booking_time < open_time or booking_time > close_time:
                    open_str = open_time.strftime('%H:%M')
                    close_str = close_time.strftime('%H:%M')
                    raise forms.ValidationError(
                        f"{facility.get_facility_name_display()} is only open from {open_str} to {close_str} on {day_names[day_of_week]}."
                    )

            # Check facility availability
            units_needed = (
                cleaned_data.get('alleys_needed', 1) 
                if facility.facility_name == 'bowling'
                else 1  # Pool and table tennis always need 1 unit
            )
            
            available_units = facility.get_available_units(timing)
            
            if available_units < units_needed:
                if facility.facility_name == 'bowling':
                    raise forms.ValidationError(
                        f"Only {available_units} bowling alleys available at this time. "
                        f"You requested {units_needed} alleys."
                    )
                else:
                    raise forms.ValidationError(
                        f"No {facility.get_facility_name_display()} tables available at this time. "
                        f"Please choose a different time."
                    )

        return cleaned_data

    # Add field for number of players (only for bowling)
    number_of_players = forms.IntegerField(
        min_value=1, 
        max_value=8,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Number of players (1-8)',
            #'style': 'display: none;',  Hide initially
        }),
        label="Number of Players"
    )
    
    # Add field for mixed gender group
    is_mixed_gender = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2',
            #'style': 'display: none;'
        }),
        label="Mixed Gender Group (will book 2 alleys)"
    )
    
    # Hidden field to store number of alleys needed
    alleys_needed = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(),
        initial=1
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add min datetime
        now = timezone.now().strftime('%Y-%m-%dT%H:%M')  
        self.fields['timing'].widget.attrs['min'] = now

        # Only show bookable facilities with their rates
        self.fields['booking_facility'].queryset = Facility.objects.filter(
            facility_name__in=['bowling', 'badminton', 'table tennis', 'pool'] 
        )

    # Add a custom clean method for form validation
    def clean(self):
        cleaned_data = super().clean()
        facility = cleaned_data.get('booking_facility')
        players = cleaned_data.get('number_of_players')
        is_mixed = cleaned_data.get('is_mixed_gender')
        
        # Validate bowling-specific fields
        if facility and facility.facility_name == 'bowling':
            if not players:
                self.add_error('number_of_players', 'Please specify the number of players')
                
            # Calculate number of alleys needed
            alleys = 1
            if is_mixed:
                alleys = 2  # Mixed gender groups always get 2 alleys
            elif players and players > 4:
                alleys = 2  # More than 4 players need 2 alleys
                
            cleaned_data['alleys_needed'] = alleys
            
            # Update total_amount based on number of alleys
            if 'total_amount' in cleaned_data:
                cleaned_data['total_amount'] = 800 * alleys
        
        return cleaned_data

    # Add JavaScript to update price when facility selection changes
    class Media:
        js = ('js/booking_pricing.js',)


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['start_date', 'membership_facility']
        # Change to handle multiple facilities
        widgets = {
            'membership_facility': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date().strftime('%Y-%m-%d')
        self.fields['start_date'].widget.attrs['min'] = today
        self.fields['start_date'].widget.attrs['max'] = today
        self.fields['start_date'].initial = today

        # Only show membership-eligible facilities (swimming and gym)
        self.fields['membership_facility'].queryset = Facility.objects.filter(
            facility_name__in=['swimming', 'gym']
        )

        # Add a custom field to show calculated price
        self.fields['fixed_amount'] = forms.IntegerField(
            required=False,  # We'll calculate this
            widget=forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded',
                'readonly': 'readonly',  # Make it read-only
            }),
            label="Membership Fee (Rs)"
        )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'type': 'date',
        }),
        label="Start Date"
    )

    payment_method = forms.ChoiceField(
        choices=PaymentMethods.choices,
        widget=forms.RadioSelect(attrs={'class': 'mr-2'}),
        label="Payment Method"
    )

    # Add JavaScript to update price when selection changes
    class Media:
        js = ('js/membership_pricing.js',)