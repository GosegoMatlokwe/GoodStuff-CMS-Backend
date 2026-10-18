# Import standard Python modules
import json
import os
from datetime import datetime

# Import Django tools for web views, API responses, and database queries
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

# Import Firebase Admin SDK to verify Android app tokens
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
    # Verify the user's Firebase token
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    # Get the unique Firebase ID and email
    uid = decoded_token.get('uid')
    email = decoded_token.get('email', f"{uid}@placeholder.com")
    
    # Create the user in the database if they don't exist
    user, created = User.objects.get_or_create(username=uid, defaults={'email': email})
    # Create a profile for the user if it doesn't exist
    CustomerProfile.objects.get_or_create(user=user)
    
    # Return success to the Android app
    return JsonResponse({"status": "success", "user_id": user.id, "created": created})

@csrf_exempt
def api_register_user(request):
    # Verify the user's token
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    if request.method == 'POST':
        try:
            # Parse the JSON body from Kotlin
            data = json.loads(request.body)
            
            # Find the user in the database
            user = User.objects.get(username=decoded_token['uid'])
            profile = user.customerprofile
            
            # 1. Save the phone number (Kotlin sends 'phoneNumber')
            if 'phoneNumber' in data:
                profile.contact_info = data.get('phoneNumber')
            
            # 2. Handle the POPIA Timestamp safely (Fixes the 500 Error)
            if 'consentTimestamp' in data and data.get('consentTimestamp') is not None:
                timestamp_ms = data.get('consentTimestamp')
                try:
                    # Convert milliseconds to seconds (float)
                    timestamp_sec = float(timestamp_ms) / 1000.0
                    # Create a datetime object from the timestamp
                    dt_object = datetime.fromtimestamp(timestamp_sec)
                    # Make it timezone-aware (required by Django's DateTimeField)
                    profile.popia_consent_timestamp = timezone.make_aware(dt_object)
                except Exception as e:
                    print(f"Error converting timestamp: {e}")
                    # If conversion fails, default to the current time so it doesn't crash
                    profile.popia_consent_timestamp = timezone.now()
            else:
                # If no timestamp was sent, default to the current time
                profile.popia_consent_timestamp = timezone.now()
                
            # Save to the database
            profile.save()
            
            # Return success to the Android app
            return JsonResponse({"status": "registered successfully"})

        except Exception as e:
            # If ANYTHING fails, print it to the VS Code terminal and send a detailed error
            print(f"🚨 REGISTRATION ERROR: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

def api_get_menu(request):
    # Get all menu items from the database
    items = Menu.objects.all()
    # Match Kotlin DTO: itemName
    data = [{
        "id": item.id, 
        "itemName": item.item_name, 
        "price": float(item.price)
    } for item in items]
    # Return the JSON array to the Android app
    return JsonResponse(data, safe=False)

@csrf_exempt
def api_get_bookings(request):
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    user = User.objects.get(username=decoded_token['uid'])
    bookings = Booking.objects.filter(customer=user)
    
    data = [{
        "id": b.id, 
        "eventType": b.event_type, 
        "eventDate": str(b.event_date),
        "status": b.status,
        "guestCount": b.guest_count, # NEW
        "totalCost": (b.guest_count * 150.0) # Simulated cost (e.g., R150 per head)
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
        
        # FIX: Replace slashes with hyphens so Django accepts the date no matter what
        raw_date = data.get('eventDate', '')
        safe_date = raw_date.replace('/', '-')
        
        try:
            booking = Booking.objects.create(
                customer=user,
                event_type=data.get('eventType', 'General Catering'),
                event_date=safe_date,
                guest_count=data.get('guestCount', 50),
                status="Pending"
            )
            return JsonResponse({
                "status": "success", 
                "booking_id": booking.id,
                "eventType": booking.event_type,
                "eventDate": str(booking.event_date)
            })
        except Exception as e:
            # If the date is still invalid (e.g., "2026-13-45"), catch it safely
            print(f"🚨 BOOKING ERROR: {str(e)}")
            return JsonResponse({"error": "Invalid date format."}, status=400)

@csrf_exempt
def api_delete_account(request):
    # Verify the user's token
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    try:
        # Find the user and delete them (POPIA compliance)
        user = User.objects.get(username=decoded_token['uid'])
        user.delete() # Cascades and deletes profile and bookings
        return JsonResponse({"status": "Account and POPIA data deleted"})
    except User.DoesNotExist:
        # If they were already deleted, just return a success status
        return JsonResponse({"status": "User already deleted"}, status=404)


@csrf_exempt
def api_delete_booking(request, booking_id):
    # 1. Verify the user's Firebase token
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
         
    if request.method == 'DELETE':
        try:
            # 2. Find the user in the database
            user = User.objects.get(username=decoded_token['uid'])
            
            # 3. Find the specific booking that belongs to this user
            # (We include customer=user so one user can't delete another user's booking)
            booking = Booking.objects.get(id=booking_id, customer=user)
            
            # 4. Delete it
            booking.delete()
            return JsonResponse({"status": "success", "message": "Booking deleted successfully"})
            
        except Booking.DoesNotExist:
            # If the booking ID doesn't exist or doesn't belong to this user
            return JsonResponse({"error": "Booking not found or unauthorized"}, status=404)
        except Exception as e:
            print(f"🚨 DELETE ERROR: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
            
    # If they try to use a GET or POST request instead of DELETE
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def api_update_profile(request):
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
         
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.get(username=decoded_token['uid'])
            profile = user.customerprofile
            
            # Update Django User's First and Last Name
            user.first_name = data.get('firstName', user.first_name)
            user.last_name = data.get('lastName', user.last_name)
            user.save()
            
            # Update Customer Profile's Phone Number
            profile.contact_info = data.get('phoneNumber', profile.contact_info)
            profile.save()
            
            return JsonResponse({"status": "success", "message": "Profile updated successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def api_sync_user(request):
    decoded_token = verify_firebase_token(request)
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    uid = decoded_token.get('uid')
    email = decoded_token.get('email', f"{uid}@placeholder.com")
    
    # Get the name sent from the Android app
    if request.method == 'POST':
        data = json.loads(request.body)
        full_name = data.get('name', '')
        # Split the name into first and last
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Create or update the user with their real name
        user, created = User.objects.get_or_create(username=uid, defaults={'email': email})
        
        if not user.first_name and first_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

    CustomerProfile.objects.get_or_create(user=user)
    
    return JsonResponse({"status": "success", "user_id": user.id, "created": created})
