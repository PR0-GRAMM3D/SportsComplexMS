from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse

from .models import Staff, StaffFacilityAssignment
from .forms import StaffLoginForm

def staff_login(request):
    """
    Handle staff login requests, supporting both traditional form submission and HTMX requests.
    """
    if request.method == "POST":
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(f"Attempting authentication for username: {username}")
            
            # Use request in authenticate call
            user = authenticate(request=request, username=username, password=password)
            
            if user is not None:
                print(f"User authenticated successfully: {username}")
                try:
                    staff_profile = Staff.objects.get(user=user)
                    login(request, user)
                    print(f"Staff login successful for: {username}")
                    
                    if request.headers.get("HX-Request"):
                        response = HttpResponse()
                        response['HX-Redirect'] = reverse("staff:dashboard")
                        return response
                    
                    return HttpResponseRedirect(reverse("staff:dashboard"))
                    
                except Staff.DoesNotExist:
                    print(f"No staff profile found for user: {username}")
                    if request.headers.get("HX-Request"):
                        return render(request, "staff/partials/login_form_with_messages.html", {
                            "form": form,
                            "server_message": "You are not registered as a staff member."
                        })
                    messages.error(request, "You are not registered as a staff member.")
            else:
                print(f"Authentication failed for username: {username}")
                if request.headers.get("HX-Request"):
                    return render(request, "staff/partials/login_form_with_messages.html", {
                        "form": form,
                        "server_message": "Invalid username or password."
                    })
                messages.error(request, "Invalid username or password.")
        else:
            print("Form validation failed:", form.errors)
            if request.headers.get("HX-Request"):
                return render(request, "staff/partials/login_form_with_messages.html", {
                    "form": form,
                    "server_message": "Please correct the form errors."
                })
            messages.error(request, "Please correct the form errors.")

        return render(request, 'staff/staff_login.html', {'form': form})
    
    else:
        form = StaffLoginForm()
        return render(request, 'staff/staff_login.html', {'form': form})

@login_required
def staff_dashboard(request):
    """
    Display staff dashboard with upcoming assignments and facility information.
    """
    try:
        staff_member = Staff.objects.get(user=request.user)
        today = timezone.now().date()
        assignments = StaffFacilityAssignment.objects.filter(
            staff=staff_member,
            assignment_date__gte=today
        ).order_by('assignment_date', 'shift')
        
        if request.headers.get("HX-Request") and request.GET.get('partial') == 'assignments':
            return render(request, 'staff/partials/assignments_table.html', {
                'assignments': assignments,
                'today': today
            })
        
        context = {
            'staff_member': staff_member,
            'assignments': assignments,
            'today': today
        }
        return render(request, 'staff/staff_dashboard.html', context)
    
    except Staff.DoesNotExist:
        messages.error(request, "You don't have a staff profile. Please contact admin.")
        # Log out the user if they are authenticated but have no staff profile
        # to prevent access to other @login_required staff views.
        # from django.contrib.auth import logout as auth_logout
        # auth_logout(request) 
        return HttpResponseRedirect(reverse('staff:login')) # Or redirect to main site login



@login_required
def toggle_assignment_status(request, assignment_id):
    """
    Toggle the completion status of an assignment via HTMX. INCOMPLETE
    """
    try:
        assignment = StaffFacilityAssignment.objects.get(id=assignment_id, staff__user=request.user)
        assignment.is_completed = not assignment.is_completed
        assignment.save()
        
        if request.headers.get("HX-Request"):
            return render(request, 'staff/partials/assignment_status.html', {
                'assignment': assignment,
                'today': timezone.now().date() # Pass today for consistent status display
            })
        return HttpResponseRedirect(reverse('staff:dashboard'))
    
    except StaffFacilityAssignment.DoesNotExist:
        return HttpResponse("Assignment not found or not authorized.", status=404)
