from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.public_home, name='home'),
    path('about/', views.public_about, name='about'),

    # Authentication (admin dashboard login)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Bookings
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/update/', views.booking_update, name='booking_update'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),

    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/<int:pk>/update/', views.inventory_update, name='inventory_update'),

    # Menu
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/create/', views.menu_create, name='menu_create'),
    path('menu/<int:pk>/update/', views.menu_update, name='menu_update'),
    path('menu/<int:pk>/delete/', views.menu_delete, name='menu_delete'),

    # Staff
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/create/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/update/', views.staff_update, name='staff_update'),
    path('staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),

    # Reports
    path('reports/', views.reports, name='reports'),
]