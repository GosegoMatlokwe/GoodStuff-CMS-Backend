# Import tools to send JSON responses and bypass CSRF protection (required for mobile apps)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import JSON so we can read the data sent from the Android app
import json

# Import Firebase Admin SDK to verify the tokens sent from the Android app
import firebase_admin
from firebase_admin import credentials, auth

# Import Django shortcuts for rendering web pages and getting database objects
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Import database tools for querying data
from django.db.models import Sum, Count, Q
from django.utils import timezone

# Uncommented your models because you need them to query the database!
from .models import Booking, Menu, Inventory, Staff, Payment, CustomerProfile
# Import your forms for the web dashboard
from .forms import BookingForm, InventoryUpdateForm, MenuForm, StaffForm

# ==========================================
# INITIALIZE FIREBASE (Crucial for Android)
# ==========================================
# This checks if Firebase is already initialized. If not, it uses your service account key.
# YOU MUST DOWNLOAD THIS KEY FROM FIREBASE CONSOLE AND PLACE IT IN YOUR DJANGO FOLDER.
import os
if not firebase_admin._apps:
    # Get the path to the JSON file you will download from Firebase (Service Accounts)
    cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    # Initialize it with the credentials
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


# ==========================================
# WEB DASHBOARD VIEWS (For the Partner Website)
# ==========================================

# Handles the login page for the admin website
def login_view(request):
    # If the user is already logged in, send them to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    # If the user submitted the login form
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Check if the username and password match a user in the database
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user) # Log them in
            return redirect('dashboard') # Send to dashboard
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

# Handles logging out of the website
def logout_view(request):
    logout(request)
    return redirect('login')

# Renders the public landing page
def public_home(request):
    return render(request, 'index.html')

# Renders the about page
def public_about(request):
    return render(request, 'about.html')

# Shows the admin dashboard with stats
@login_required
def dashboard(request):
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='Pending').count()
    confirmed_bookings = Booking.objects.filter(status='Confirmed').count()
    low_stock_items = Inventory.objects.filter(quantity__lt=20).count()
    total_staff = Staff.objects.count()
    upcoming_events = Booking.objects.filter(event_date__gte=timezone.now().date()).order_by('event_date')[:5]

    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'low_stock_items': low_stock_items,
        'total_staff': total_staff,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'dashboard.html', context)

# Shows a list of all bookings
@login_required
def booking_list(request):
    bookings = Booking.objects.all().order_by('-event_date')
    return render(request, 'booking_list.html', {'bookings': bookings})

# Create a new booking via the website
@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking created successfully.')
            return redirect('booking_list')
    else:
        form = BookingForm()
    return render(request, 'booking_form.html', {'form': form, 'title': 'Create Booking'})

# Update an existing booking
@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated.')
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'booking_form.html', {'form': form, 'title': 'Edit Booking'})

# Delete a booking
@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted.')
        return redirect('booking_list')
    return render(request, 'confirm_delete.html', {'object': booking, 'type': 'booking'})

# Inventory list
@login_required
def inventory_list(request):
    items = Inventory.objects.all().order_by('item_name')
    return render(request, 'inventory_list.html', {'items': items})

# Update inventory
@login_required
def inventory_update(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = InventoryUpdateForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Stock updated for {item.item_name}.')
            return redirect('inventory_list')
    else:
        form = InventoryUpdateForm(instance=item)
    return render(request, 'inventory_update.html', {'form': form, 'item': item})

# Menu list
@login_required
def menu_list(request):
    items = Menu.objects.all().order_by('item_name')
    return render(request, 'menu_list.html', {'items': items})

# Create menu item
@login_required
def menu_create(request):
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item added.')
            return redirect('menu_list')
    else:
        form = MenuForm()
    return render(request, 'menu_form.html', {'form': form, 'title': 'Add Menu Item'})

# Update menu item
@login_required
def menu_update(request, pk):
    item = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated.')
            return redirect('menu_list')
    else:
        form = MenuForm(instance=item)
    return render(request, 'menu_form.html', {'form': form, 'title': 'Edit Menu Item'})

# Delete menu item
@login_required
def menu_delete(request, pk):
    item = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Menu item deleted.')
        return redirect('menu_list')
    return render(request, 'confirm_delete.html', {'object': item, 'type': 'menu item'})

# Staff list
@login_required
def staff_list(request):
    staff_members = Staff.objects.all().select_related('user').order_by('user__first_name')
    return render(request, 'staff_list.html', {'staff_members': staff_members})

# Create staff
@login_required
def staff_create(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member added.')
            return redirect('staff_list')
    else:
        form = StaffForm()
    return render(request, 'staff_form.html', {'form': form, 'title': 'Add Staff'})

# Update staff
@login_required
def staff_update(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff updated.')
            return redirect('staff_list')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'staff_form.html', {'form': form, 'title': 'Edit Staff'})

# Delete staff
@login_required
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff removed.')
        return redirect('staff_list')
    return render(request, 'confirm_delete.html', {'object': staff, 'type': 'staff member'})

# Reports page
@login_required
def reports(request):
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_paid_bookings = Payment.objects.count()
    booking_by_type = Booking.objects.values('event_type').annotate(count=Count('id')).order_by('-count')
    low_stock = Inventory.objects.filter(quantity__lt=20)
    staff_workload = Staff.objects.annotate(num_bookings=Count('booking')).order_by('-num_bookings')
    
    context = {
        'total_revenue': total_revenue,
        'total_paid_bookings': total_paid_bookings,
        'booking_by_type': booking_by_type,
        'low_stock': low_stock,
        'staff_workload': staff_workload,
    }
    return render(request, 'reports.html', context)


# ==========================================
# ---------- MOBILE APP API ENDPOINTS ------
# ==========================================

# This helper function verifies the Firebase token sent in the Authorization header
def verify_firebase_token(request):
    # Get the 'Authorization' header from the request
    auth_header = request.headers.get('Authorization')
    # If it doesn't exist or doesn't start with "Bearer ", reject it
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    # Split the string to extract just the token part
    token = auth_header.split(' ')[1]
    try:
        # Use Firebase Admin to verify the token. If valid, it returns the decoded user info.
        return auth.verify_id_token(token)
    except Exception:
        # If the token is invalid or expired, return None
        return None

# Endpoint: /api/auth/sync/
@csrf_exempt # Bypass CSRF protection because mobile apps don't use CSRF tokens
def api_sync_user(request):
    # Verify the user's Firebase token
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    # Extract the unique Firebase ID and email
    uid = decoded_token.get('uid')
    email = decoded_token.get('email', f"{uid}@placeholder.com")
    
    # Import Django's User model
    from django.contrib.auth.models import User
    # Get or create a user in the database using the Firebase UID as the username
    user, created = User.objects.get_or_create(username=uid, defaults={'email': email})
    # Create a customer profile for this user if it doesn't exist
    CustomerProfile.objects.get_or_create(user=user)
    
    # Return success JSON to the Android app
    return JsonResponse({"status": "success", "user_id": user.id, "created": created})

# Endpoint: /api/auth/register/
@csrf_exempt
def api_register_user(request):
    # Verify the user's token
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # Ensure the app is sending a POST request
    if request.method == 'POST':
        # Parse the JSON body sent from Kotlin
        data = json.loads(request.body)
        from django.contrib.auth.models import User
        # Find the user
        user = User.objects.get(username=decoded_token['uid'])
        # Get their profile
        profile = user.customerprofile
        
        # FIX: Android sends 'phoneNumber' and 'popiaConsent'. We need to save them.
        # (Assuming your CustomerProfile model has a field for consent_timestamp)
        profile.contact_info = data.get('phoneNumber', profile.contact_info)
        
        # If your model has this field, uncomment it to save POPIA compliance:
        # profile.popia_consent_timestamp = data.get('consentTimestamp')
        
        profile.save()
        return JsonResponse({"status": "registered successfully"})

# Endpoint: /api/menu/
def api_get_menu(request):
    # Get all menu items from the database
    items = Menu.objects.all()
    # FIX: Android expects 'itemName', not 'name'. We map the database fields to the Kotlin DTO.
    data = [{
        "id": item.id, 
        "itemName": item.item_name, 
        "price": float(item.price),
        "category": "General", # Add category if your model has it
        "isAvailable": True
    } for item in items]
    # Return the JSON array to the Android app
    return JsonResponse(data, safe=False)

# Endpoint: /api/bookings/
def api_get_bookings(request):
    # Verify token
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    from django.contrib.auth.models import User
    # Find the user and filter bookings to only show theirs
    user = User.objects.get(username=decoded_token['uid'])
    bookings = Booking.objects.filter(customer=user)
    
    # FIX: Android expects 'eventDate', 'eventType'. We map them here.
    data = [{
        "id": b.id, 
        "eventType": b.event_type, 
        "eventDate": str(b.event_date),
        "status": b.status
    } for b in bookings]
    return JsonResponse(data, safe=False)

# Endpoint: /api/bookings/create/
@csrf_exempt
def api_create_booking(request):
    # Verify token
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    if request.method == 'POST':
        # Parse JSON sent from Kotlin
        data = json.loads(request.body)
        from django.contrib.auth.models import User
        user = User.objects.get(username=decoded_token['uid'])
        
        # FIX: Android sends 'eventType', 'eventDate', 'guestCount'. We map them to the database models.
        booking = Booking.objects.create(
            customer=user,
            event_type=data.get('eventType', 'App Booking'),
            event_date=data.get('eventDate'), 
            guest_count=data.get('guestCount', 10),
            status="Pending" # Default status
        )
        return JsonResponse({"status": "success", "booking_id": booking.id, "eventDate": str(booking.event_date), "eventType": booking.event_type})

# Endpoint: /api/auth/delete-account/
@csrf_exempt
def api_delete_account(request):
    # Verify token
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    from django.contrib.auth.models import User
    try:
        # Find the user
        user = User.objects.get(username=decoded_token['uid'])
        # Delete the user from the database. 
        # (Assuming your models have CASCADE delete set up, this deletes their profile and bookings too)
        user.delete() 
        return JsonResponse({"status": "Account and POPIA data deleted successfully"})
    except User.DoesNotExist:
        return JsonResponse({"status": "User already deleted"}, status=404)