from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('login', views.staff_login, name='login'),
    path('dashboard', views.staff_dashboard, name='dashboard'),
    path('toggle-assignment/<int:assignment_id>/', views.toggle_assignment_status, name='toggle_assignment_status'),
]