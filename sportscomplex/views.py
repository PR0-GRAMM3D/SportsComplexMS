from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import  HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from .models import (
    User, 
    Payment, 
    Booking, 
    Membership, 
    Facility, 
    UserTypes, 
    Statuses, 
    PaymentMethods, 
    PaymentRates,
    UserTypeRate
)
from .forms import NewUserForm, LoginForm, BookingFacilityForm, MembershipForm
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import time


# Create your views here.
@login_required
def dashboard(request):
    user_bookings = Booking.objects.filter(booking_user = request.user) 
    return render(request, "sportscomplex/dashboard.html", {
        "user_bookings": user_bookings
    })

def home(request):
    return render(request, "sportscomplex/home.html")

def login_view(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST) #forms.py 
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if request.headers.get("HX-Request"):
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse("dashboard") #HttpResponseRedirect(reverse(name of url))
                    return response
                return HttpResponseRedirect(reverse("dashboard"))
            else:
                context = {
                    "Message": "Invalid Credentials",
                    "form": login_form
                }
                if request.headers.get("HX-Request"):
                    return render(request, "sportscomplex/partials/login_form.html", context)
                return render(request, "sportscomplex/login.html", context)
        else:
            context = {
                "Message": "Please correct the form errors.",
                "form": login_form
            }
            if request.headers.get("HX-Request"):
                return render(request, "sportscomplex/partials/login_form.html", context)
            return render(request, "sportscomplex/login.html", context)
    else:
        login_form = LoginForm()
        return render(request, "sportscomplex/login.html", {
            "form": login_form
        })

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def register(request):
    if request.method == "POST":
        register_form = NewUserForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data["username"]
            email = register_form.cleaned_data["email"]
            password = register_form.cleaned_data["password"]
            confirmation = register_form.cleaned_data["confirmation"]
            
            if password != confirmation:
                context = {
                    "Message": "Password Fields Do Not Match!",
                    "form": register_form
                }
                if request.headers.get("HX-Request"):
                    return render(request, "sportscomplex/partials/register_form.html", context)
                return render(request, "sportscomplex/register.html", context)

            try:
                # Creating user first
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Then setting the additional fields
                user.phone_number = register_form.cleaned_data["phone_number"]
                user.first_name = register_form.cleaned_data["first_name"]
                user.last_name = register_form.cleaned_data["last_name"]
                user.type = register_form.cleaned_data["type"]
                user.save()
                
                login(request, user)
                
                # Handle HTMX request
                if request.headers.get("HX-Request"):
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse("dashboard")
                    return response
                return HttpResponseRedirect(reverse("dashboard"))
                
            except IntegrityError:
                context = {
                    "Message": "Username Already Exists",
                    "form": register_form
                }
                if request.headers.get("HX-Request"):
                    return render(request, "sportscomplex/partials/register_form.html", context)
                return render(request, "sportscomplex/register.html", context)
    else:
        register_form = NewUserForm()
        return render(request, "sportscomplex/register.html", {
            "form": register_form
        })


@login_required
def booking(request):
    if request.method == "POST":
        booking_form = BookingFacilityForm(request.POST)
        if booking_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.booking_user = request.user
            payment_method = booking_form.cleaned_data["payment_method"]
            
            # Add bowling specific data
            facility = booking.booking_facility
            if facility.facility_name == 'bowling':
                booking.number_of_players = booking_form.cleaned_data.get('number_of_players')
                booking.is_mixed_gender = booking_form.cleaned_data.get('is_mixed_gender', False)
                booking.alleys_booked = booking_form.cleaned_data.get('alleys_needed', 1)
                
                # Double check that the total_amount matches the number of alleys
                total_amount = 800 * booking.alleys_booked
            else:
                # For other facilities use the regular total_amount
                total_amount = booking_form.cleaned_data.get('total_amount', 0)
            
            #Creating payment object to feed into Booking object
            payment = Payment(
                total_amount = total_amount,
                method = payment_method,
                payment_user = booking.booking_user
            )
            payment.save()
            
            booking.booking_payment = payment  # Set the payment
            booking.is_walkin = (payment_method == PaymentMethods.CASH)
            
            if booking.is_walkin:
                booking.status = Statuses.CONFIRMED
                booking.save()
                # HTMX: Return confirmation snippet if HTMX request
                if request.headers.get("HX-Request"):
                    return render(request, "sportscomplex/partials/booking_confirmed.html", {
                        "booking": booking
                    })
            else:       #API KEY NEEDED FOR HANDLING ONLINE PAYMENTS
                booking.status = Statuses.CONFIRMED
                booking.save()
                # HTMX: Return confirmation or redirect
                if request.headers.get("HX-Request"):
                    return render(request, "sportscomplex/partials/booking_confirmed.html", {
                        "booking": booking
                    })
                
                return HttpResponseRedirect(reverse("dashboard"))
            
            # Non-HTMX fallback
            return HttpResponseRedirect(reverse("dashboard"))
    else:
        booking_form = BookingFacilityForm()
        return render(request, "sportscomplex/booking.html", {
            "form": booking_form
    })

@login_required
def membership(request):
    # Check if user already has an active membership
    existing_membership = Membership.objects.filter(
        membership_user=request.user,
        status=Statuses.ACTIVE
    ).first()
    
    # If user has an active membership, redirect to view_membership
    if existing_membership:
        return view_membership(request, existing_membership.id)
    
    # Get user-specific rates (for pre-populating the price display)
    try:
        user_rates = UserTypeRate.objects.get(user_type=request.user.type)
        rates = {
            'swimming_rate': user_rates.swimming_rate,
            'gym_rate': user_rates.gym_rate,
            'master_card_rate': user_rates.master_card_rate,
            'registration_fee': user_rates.registration_fee,
            'user_type': request.user.get_type_display()
        }
    except UserTypeRate.DoesNotExist:
        # Fall back to default rates
        rates = {
            'swimming_rate': 1000,
            'gym_rate': 1000,
            'master_card_rate': 1500,
            'registration_fee': 2000,
            'user_type': 'Default'
        }
    
    # Create a JSON string of just the rate values for JavaScript
    rates_js = {
        'swimming': rates['swimming_rate'],
        'gym': rates['gym_rate'],
        'masterCard': rates['master_card_rate'],
        'registration': rates['registration_fee']
    }
    
    # Convert to JSON string
    rates_json = json.dumps(rates_js)
    
    # Handle POST request (existing code)
    if request.method == "POST":
        membership_form = MembershipForm(request.POST)
        if membership_form.is_valid():
            # Get form data
            start_date = membership_form.cleaned_data['start_date']
            payment_method = membership_form.cleaned_data['payment_method']
            facilities = membership_form.cleaned_data['membership_facility']
            
            # Calculate total amount based on selected facilities AND user type
            total_amount = PaymentRates.get_combined_membership_rate(
                facilities, 
                user=request.user  # Pass the user to consider user type
            )
            
            # Add the registration fee to the total amount
            registration_fee = rates['registration_fee']
            total_amount += registration_fee
            
            # Create payment record
            payment = Payment.objects.create(
                total_amount=total_amount,
                method=payment_method,
                payment_user=request.user
            )
            
            # Create membership record
            membership = Membership.objects.create(
                membership_user=request.user,
                start_date=start_date,
                # Set end_date to one month later
                end_date=start_date + timezone.timedelta(days=30), # This can be changed 
                fixed_amount=total_amount,
                membership_payment=payment,
                status=Statuses.ACTIVE
            )
            
            # Add the facilities to the membership
            membership.membership_facility.set(facilities)
            
            # Redirect or show confirmation
            if request.headers.get("HX-Request"):
                return render(request, "sportscomplex/partials/membership_confirmed.html", {
                    "membership": membership
                })
            
            return HttpResponseRedirect(reverse("dashboard"))
    else:
        membership_form = MembershipForm()
    
    timestamp = int(time.time())  # Current timestamp
    
    return render(request, "sportscomplex/membership.html", {
        "form": membership_form,
        "rates": rates,  # Pass rates to the template
        "rates_json": rates_json,  # Pass the JSON string
        "timestamp": timestamp  # Add timestamp for cache busting
    })


@login_required
def view_membership(request, membership_id=None):
    """
    View details of a user's membership
    If membership_id is provided, shows that specific membership
    Otherwise, shows the user's active membership
    """
    try:
        # If membership_id is provided, use that
        if membership_id:
            membership = Membership.objects.get(id=membership_id)
        else:
            # Otherwise, get user's active membership
            membership = Membership.objects.get(
                membership_user=request.user,
                status=Statuses.ACTIVE
            )
        
        # Ensure the membership belongs to the current user
        if membership.membership_user != request.user:
            return HttpResponseRedirect(reverse("dashboard"))
            
        # Calculate days left until expiration
        days_left = (membership.end_date - timezone.now().date()).days
        
        # Get all membership details
        facilities = membership.membership_facility.all()
        payment = membership.membership_payment
        
        return render(request, "sportscomplex/view_membership.html", {
            "membership": membership,
            "facilities": facilities,
            "payment": payment,
            "days_left": days_left,
            "facility_names": ", ".join(f.get_facility_name_display() for f in facilities)
        })
        
    except Membership.DoesNotExist:
        # If no membership found, redirect to membership registration
        return HttpResponseRedirect(reverse("membership"))

@login_required
def payment(request):
    pass

#API For Getting Prices
@csrf_exempt
def get_facility_rate(request):
    """API endpoint to get rate for a specific facility"""
    facility_id = request.GET.get('facility_id')
    if not facility_id:
        return JsonResponse({'error': 'Facility ID is required'}, status=400)
    
    try:
        facility = Facility.objects.get(id=facility_id)
        
        # Default response
        response = {
            'facility_name': facility.facility_name,
            'booking_rate': None,
            'membership_rate': None
        }
        
        # Get booking rate if applicable
        if facility.is_bookable():
            booking_rate = PaymentRates.get_booking_rate(facility)
            response['booking_rate'] = booking_rate
        
        # Get membership rate if applicable (user-specific)
        if facility.allows_membership():
            if request.user.is_authenticated:
                membership_rate = PaymentRates.get_membership_rate(facility, user=request.user)
            else:
                membership_rate = PaymentRates.get_membership_rate(facility)
            response['membership_rate'] = membership_rate
        
        return JsonResponse(response)
    
    except Facility.DoesNotExist:
        return JsonResponse({'error': 'Facility not found'}, status=404)

@csrf_exempt
def get_combined_membership_rate(request):
    """API endpoint to calculate rate for multiple facilities with user-specific pricing"""
    facility_ids = request.GET.getlist('facility_ids')
    include_registration = request.GET.get('include_registration', 'false').lower() == 'true'
    
    if not facility_ids:
        return JsonResponse({'rate': 0})
    
    facilities = Facility.objects.filter(id__in=facility_ids)
    
    # Calculate rate considering user type if authenticated
    if request.user.is_authenticated:
        rate = PaymentRates.get_combined_membership_rate(
            facilities, 
            user=request.user,
            include_registration_fee=include_registration
        )
    else:
        rate = PaymentRates.get_combined_membership_rate(
            facilities,
            include_registration_fee=include_registration
        )
    
    return JsonResponse({'rate': rate})

@login_required
def check_availability(request):
    """API endpoint to check facility availability"""
    facility_id = request.GET.get('facility_id')
    timing_str = request.GET.get('timing')
    
    if not facility_id or not timing_str:
        return JsonResponse({
            'available': False,
            'message': 'Missing required parameters'
        })
    
    try:
        facility = Facility.objects.get(id=facility_id)
        timing = timezone.datetime.fromisoformat(timing_str)
        
        available_units = facility.get_available_units(timing)
        total_units = int(facility.capacity)
        
        return JsonResponse({
            'available': available_units > 0,
            'available_units': available_units,
            'total_units': total_units,
            'message': (
                f"{available_units} out of {total_units} "
                f"{facility.get_facility_name_display()} units available"
            )
        })
    
    except (Facility.DoesNotExist, ValueError) as e:
        return JsonResponse({
            'available': False,
            'message': str(e)
        })


