from django.urls import path
from . import views # Import the views we just fixed

urlpatterns = [
    # ==========================================
    # WEB DASHBOARD ROUTES (For the browser)
    # ==========================================
    path('', views.public_home, name='home'), # Home page
    path('about/', views.public_about, name='about'), # About page
    path('login/', views.login_view, name='login'), # Admin login
    path('logout/', views.logout_view, name='logout'), # Admin logout
    path('dashboard/', views.dashboard, name='dashboard'), # Admin dashboard

    # Web Bookings
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/update/', views.booking_update, name='booking_update'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),

    # Web Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/<int:pk>/update/', views.inventory_update, name='inventory_update'),

    # Web Menu
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/create/', views.menu_create, name='menu_create'),
    path('menu/<int:pk>/update/', views.menu_update, name='menu_update'),
    path('menu/<int:pk>/delete/', views.menu_delete, name='menu_delete'),

    # Web Staff
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/create/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/update/', views.staff_update, name='staff_update'),
    path('staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),

    # Web Reports
    path('reports/', views.reports, name='reports'),

    # ==========================================
    # MOBILE APP API ROUTES (For Retrofit in Kotlin)
    # ==========================================
    # These must match the @POST and @GET tags in the Kotlin ApiService.kt exactly!
    path('api/auth/sync/', views.api_sync_user), # Used after Google Login
    path('api/auth/register/', views.api_register_user), # Used to save Phone & POPIA
    path('api/menu/', views.api_get_menu), # Used by MenuDiscoveryScreen
    path('api/bookings/', views.api_get_bookings), # Used by DashboardScreen
    path('api/bookings/create/', views.api_create_booking), # Used by BookingScreen
    path('api/auth/delete-account/', views.api_delete_account), # Used by SettingsScreen (POPIA)
]