from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import Staff, StaffFacilityAssignment

User = get_user_model()

# Custom creation form for Staff that includes User fields
class StaffAdminForm(forms.ModelForm):
    # Add User model fields
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Staff
        fields = []  # Staff model fields if any

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Create User first, then Staff
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        # Create Staff instance
        staff = super().save(commit=False)
        staff.user = user
        if commit:
            staff.save()
        return staff

# TabularInline allows to edit related models directly from the parent model's admin page
class StaffFacilityAssignmentInline(admin.TabularInline):
    model = StaffFacilityAssignment  # The through model for the many-to-many relationship
    extra = 1  # Number of empty forms to display
    autocomplete_fields = ['facility']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    form = StaffAdminForm
    
    # Controls which fields are displayed in the list view
    list_display = ['get_full_name', 'get_email', 'get_phone_number']
    
    # Enables searching through these fields
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'user__phone_number']
    
    # Embeds the facility assignment inline form within the staff admin page
    inlines = [StaffFacilityAssignmentInline]

    # Define which fields to display in the add/edit form
    fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def get_fields(self, request, obj=None):
        # Only show password fields on add, not edit
        if obj:  # editing an existing object
            return ['username', 'email', 'first_name', 'last_name']
        return super().get_fields(request, obj)
    
    # Custom method to display the staff member's full name
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Name'
    
    # Custom method to display the staff member's email
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    # Custom method to display the staff member's phone number
    def get_phone_number(self, obj):
        return obj.user.phone_number
    get_phone_number.short_description = 'Phone'

    def get_readonly_fields(self, request, obj=None):
        # Make username readonly when editing existing staff
        if obj:
            return ['username']
        return []

# Register StaffFacilityAssignment model with the admin site using a decorator
@admin.register(StaffFacilityAssignment)
class StaffFacilityAssignmentAdmin(admin.ModelAdmin):
    # Controls which fields are displayed in the list view
    list_display = ['staff_name', 'facility_name', 'assignment_date', 'shift']
    
    # Adds filters to the right sidebar in the admin list view
    list_filter = ['assignment_date', 'shift', 'facility']
    
    # Enables searching through these fields
    search_fields = ['staff__user__first_name', 'staff__user__last_name', 'facility__facility_name']
    
    # Now that FacilityAdmin has search_fields, we can enable autocomplete for both fields
    autocomplete_fields = ['staff', 'facility']  
    
    # Adds date-based navigation hierarchy above the list
    date_hierarchy = 'assignment_date'
    
    # Custom method to display the staff member's name in a readable format
    def staff_name(self, obj):
        return f"{obj.staff.user.first_name} {obj.staff.user.last_name}"
    staff_name.short_description = 'Staff Member'  # Column header in the admin list view
    
    # Custom method to display the facility name with proper capitalization
    def facility_name(self, obj):
        return obj.facility.facility_name.title() if obj.facility.facility_name else "N/A"
    facility_name.short_description = 'Facility'  # Column header in the admin list view

# IMPORTANT NOTE:
# To enable facility autocomplete in both StaffFacilityAssignmentInline and StaffFacilityAssignmentAdmin,
# you must add search_fields to FacilityAdmin in sportscomplex/admin.py
