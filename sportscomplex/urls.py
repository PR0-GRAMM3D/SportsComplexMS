from django.urls import path
from . import views

urlpatterns = [
    path("home", views.home, name="home"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("", views.login_view, name="login"), 
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("booking", views.booking, name="booking"),
    path("membership", views.membership, name="membership"),
    path("api/facility-rate", views.get_facility_rate, name="facility_rate"),
    path("api/combined-membership-rate", views.get_combined_membership_rate, name="combined_membership_rate"),
    #include the optional parameter
    path("view_membership/<int:membership_id>", views.view_membership, name="view_membership_with_id"),
    # original path for the default behavior (showing active membership)
    path("view_membership", views.view_membership, name="view_membership"),
    path('check-availability/', views.check_availability, name='check-availability'),
]