# Import standard python modules
import json
import os

# Import Django tools for web views and API responses
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone

# Import your database models and forms
from .models import CustomerProfile, Menu, Booking, Inventory, Staff, Payment
from .forms import BookingForm, InventoryUpdateForm, MenuForm, StaffForm

# Import Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, auth

# ==========================================
# SAFE FIREBASE INITIALIZATION
# ==========================================
# Build the absolute path to the JSON file inside the 'catering' folder
cred_path = os.path.join(settings.BASE_DIR, 'catering', 'serviceAccountKey.json')

if not firebase_admin._apps:
    if os.path.exists(cred_path):
        # If the file exists, load it and start Firebase
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # If it's missing, print a warning but let the server run so you can fix it
        print(f"\n🚨 WARNING: Firebase key NOT FOUND at {cred_path}")
        print("🚨 App API endpoints will fail until you place it in the folder.\n")


# ==========================================
# WEBSITE DASHBOARD VIEWS (For your laptop)
# ==========================================

def login_view(request):
    # If the user is already logged in, go straight to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    # If the user submitted the login form
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Verify the credentials against the database
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    # Load the login HTML page
    return render(request, 'login.html')

def logout_view(request):
    # Log the user out and send them back to the login page
    logout(request)
    return redirect('login')

def public_home(request):
    # Loads the public landing page (index.html)
    return render(request, 'index.html')

def public_about(request):
    # Loads the about page (about.html)
    return render(request, 'about.html')

@login_required
def dashboard(request):
    # Count total bookings, pending, and confirmed
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='Pending').count()
    confirmed_bookings = Booking.objects.filter(status='Confirmed').count()
    # Check for inventory running low (less than 20)
    low_stock_items = Inventory.objects.filter(quantity__lt=20).count()
    total_staff = Staff.objects.count()
    # Get the next 5 upcoming events sorted by date
    upcoming_events = Booking.objects.filter(event_date__gte=timezone.now().date()).order_by('event_date')[:5]

    # Pass this data to the HTML template
    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'low_stock_items': low_stock_items,
        'total_staff': total_staff,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'dashboard.html', context)

@login_required
def booking_list(request):
    bookings = Booking.objects.all().order_by('-event_date')
    return render(request, 'booking_list.html', {'bookings': bookings})

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

@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted.')
        return redirect('booking_list')
    return render(request, 'confirm_delete.html', {'object': booking, 'type': 'booking'})

@login_required
def inventory_list(request):
    items = Inventory.objects.all().order_by('item_name')
    return render(request, 'inventory_list.html', {'items': items})

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

@login_required
def menu_list(request):
    items = Menu.objects.all().order_by('item_name')
    return render(request, 'menu_list.html', {'items': items})

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

@login_required
def menu_delete(request, pk):
    item = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Menu item deleted.')
        return redirect('menu_list')
    return render(request, 'confirm_delete.html', {'object': item, 'type': 'menu item'})

@login_required
def staff_list(request):
    staff_members = Staff.objects.all().select_related('user').order_by('user__first_name')
    return render(request, 'staff_list.html', {'staff_members': staff_members})

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

@login_required
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff removed.')
        return redirect('staff_list')
    return render(request, 'confirm_delete.html', {'object': staff, 'type': 'staff member'})

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
# MOBILE APP API ENDPOINTS (For Android)
# ==========================================

def verify_firebase_token(request):
    # Get the Authorization header from the request
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None # No token provided
    
    # Extract just the token string
    token = auth_header.split(' ')[1]
    
    try:
        # Verify the token with Firebase. If valid, returns a dictionary with user info.
        return auth.verify_id_token(token)
    except Exception:
        return None # Invalid or expired token

@csrf_exempt # Allow mobile apps to POST without CSRF tokens
def api_sync_user(request):
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    # Get the unique Firebase ID and email
    uid = decoded_token.get('uid')
    email = decoded_token.get('email', f"{uid}@placeholder.com")
    
    # Create the user in the database if they don't exist
    user, created = User.objects.get_or_create(username=uid, defaults={'email': email})
    CustomerProfile.objects.get_or_create(user=user)
    
    return JsonResponse({"status": "success", "user_id": user.id, "created": created})

@csrf_exempt
def api_register_user(request):
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    if request.method == 'POST':
        # Parse the JSON body from Kotlin
        data = json.loads(request.body)
        user = User.objects.get(username=decoded_token['uid'])
        profile = user.customerprofile
        
        # Save the phone number (Kotlin sends 'phoneNumber')
        profile.contact_info = data.get('phoneNumber', profile.contact_info)
        
        # Save POPIA consent timestamp if provided
        if 'consentTimestamp' in data:
            profile.popia_consent_timestamp = data.get('consentTimestamp')
            
        profile.save()
        return JsonResponse({"status": "registered successfully"})

def api_get_menu(request):
    items = Menu.objects.all()
    # Match Kotlin DTO: itemName
    data = [{
        "id": item.id, 
        "itemName": item.item_name, 
        "price": float(item.price)
    } for item in items]
    return JsonResponse(data, safe=False)

def api_get_bookings(request):
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    user = User.objects.get(username=decoded_token['uid'])
    bookings = Booking.objects.filter(customer=user)
    
    # Match Kotlin DTO: eventType, eventDate
    data = [{
        "id": b.id, 
        "eventType": b.event_type, 
        "eventDate": str(b.event_date),
        "status": b.status
    } for b in bookings]
    return JsonResponse(data, safe=False)

@csrf_exempt
def api_create_booking(request):
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    if request.method == 'POST':
        data = json.loads(request.body)
        user = User.objects.get(username=decoded_token['uid'])
        
        # Create the booking using Kotlin's JSON keys
        booking = Booking.objects.create(
            customer=user,
            event_type=data.get('eventType', 'General Catering'),
            event_date=data.get('eventDate'), 
            guest_count=data.get('guestCount', 50),
            status="Pending"
        )
        return JsonResponse({
            "status": "success", 
            "booking_id": booking.id,
            "eventType": booking.event_type,
            "eventDate": str(booking.event_date)
        })

@csrf_exempt
def api_delete_account(request):
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    try:
        user = User.objects.get(username=decoded_token['uid'])
        user.delete() # Cascades and deletes profile and bookings
        return JsonResponse({"status": "Account and data deleted"})
    except User.DoesNotExist:
        return JsonResponse({"status": "User already deleted"}, status=404)