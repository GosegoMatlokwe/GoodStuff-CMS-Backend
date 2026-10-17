im# Import the 'json' module so we can parse the JSON payload sent by the Android app
import json

# Import JsonResponse to send data back to the Android app in JSON format
from django.http import JsonResponse

# Import csrf_exempt to allow the Android app to make POST requests without a CSRF token
# (Mobile apps don't use web cookies, so Django's default CSRF protection blocks them)
from django.views.decorators.csrf import csrf_exempt

# Import Django's built-in User model to manage authentication and database records
from django.contrib.auth.models import User

# Import Firebase Admin SDK to verify the tokens sent by the Android app
import firebase_admin
from firebase_admin import credentials, auth

# Import your custom models (UNCOMMENTED these so Django can query them)
from .models import CustomerProfile, Menu, Booking

# ==========================================
# INITIALIZE FIREBASE (CRITICAL FOR ANDROID)
# ==========================================
# Check if Firebase is already initialized to prevent the "already exists" error
if not firebase_admin._apps:
    # Load the service account key you downloaded from the Firebase Console
    # (Ensure 'serviceAccountKey.json' is in the same folder as this file)
    cred = credentials.Certificate('serviceAccountKey.json')
    # Initialize the Firebase app with your credentials
    firebase_admin.initialize_app(cred)


# This is a helper function that runs before API requests to verify the user
def verify_firebase_token(request):
    # Get the 'Authorization' header from the incoming HTTP request
    auth_header = request.headers.get('Authorization')
    
    # If the header is missing or doesn't start with "Bearer ", reject the request
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
        
    # Split the string "Bearer <token>" and grab just the token part
    token = auth_header.split(' ')[1]
    
    try:
        # Use Firebase Admin to verify the token. 
        # If valid, it returns a dictionary with the user's Firebase details (UID, email, etc.)
        return auth.verify_id_token(token)
    except Exception:
        # If the token is expired, invalid, or tampered with, return None
        return None


# ------------------------------------------
# ENDPOINT: /api/auth/sync/
# ------------------------------------------
@csrf_exempt # Bypass CSRF protection because mobile apps don't use web cookies
def sync_user(request):
    # Verify the token sent from the Android app
    decoded_token = verify_firebase_token(request)
    
    # If verification fails, return a 401 Unauthorized status to the app
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    # Extract the unique Firebase User ID (UID) from the decoded token
    uid = decoded_token.get('uid')
    
    # Extract the email from the token, or create a placeholder if the user didn't share one
    email = decoded_token.get('email', f"{uid}@placeholder.com")
    
    # Search for the user in PostgreSQL. If they don't exist, create them using the UID as the username.
    # 'get_or_create' returns a tuple: (the_user_object, True_if_created_or_False_if_found)
    user, created = User.objects.get_or_create(username=uid, defaults={'email': email})
    
    # Ensure this user has a CustomerProfile linked to them. Create it if it's missing.
    CustomerProfile.objects.get_or_create(user=user)
    
    # Return a success JSON response to the Android app
    return JsonResponse({"status": "success", "user_id": user.id, "created": created})


# ------------------------------------------
# ENDPOINT: /api/auth/register/
# ------------------------------------------
@csrf_exempt
def register_user(request):
    # Verify the token sent from the Android app
    decoded_token = verify_firebase_token(request)
    
    # Reject the request if the token is invalid
    if not decoded_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    # Check if the Android app sent a POST request (which it does when submitting a form)
    if request.method == 'POST':
        # Parse the JSON body sent from Kotlin (e.g., {"phoneNumber": "082...", "popiaConsent": true})
        data = json.loads(request.body)
        
        # Find the user in the database using the UID from the verified token
        user = User.objects.get(username=decoded_token['uid'])
        
        # Get the CustomerProfile linked to this user
        profile = user.customerprofile
        
        # Update the contact_info field with the phone number sent from Android.
        # We use .get() to safely handle cases where the key might be missing.
        profile.contact_info = data.get('phoneNumber', profile.contact_info)
        
        # If your CustomerProfile model has a field for POPIA compliance, save the timestamp here:
        # profile.popia_consent_timestamp = data.get('consentTimestamp')
        
        # Save the changes to the PostgreSQL database
        profile.save()
        
        # Return success message to the Android app
        return JsonResponse({"status": "registered successfully"})


# ------------------------------------------
# ENDPOINT: /api/menu/
# ------------------------------------------
def get_menu(request):
    # Query the PostgreSQL database to get all menu items
    items = Menu.objects.all()
    
    # IMPORTANT FIX: Your Android app expects 'itemName', not 'name'. 
    # We map the database fields to match the Kotlin DTO exactly.
    data = [{
        "id": item.id, 
        "itemName": item.item_name, # Changed from "name" to "itemName"
        "price": float(item.price),
        "category": "General", # Added missing field expected by Android
        "isAvailable": True    # Added missing field expected by Android
    } for item in items]
    
    # Return the list of dictionaries as a JSON array. 
    # safe=False is required when sending a JSON array (list) instead of a dictionary.
    return JsonResponse(data, safe=False)


# ------------------------------------------
# ENDPOINT: /api/bookings/
# ------------------------------------------
def get_bookings(request):
    # Verify the token sent from the Android app
    decoded_token = verify_firebase_token(request)
    
    # Reject the request if the token is invalid
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    # Find the specific user in the database
    user = User.objects.get(username=decoded_token['uid'])
    
    # Query the database for bookings that belong ONLY to this user
    bookings = Booking.objects.filter(customer=user)
    
    # IMPORTANT FIX: Your Android app expects 'eventDate' and 'eventType'. 
    # We map the database fields to match the Kotlin DTO exactly.
    data = [{
        "id": b.id, 
        "eventType": b.event_type, # Changed from "event_type"
        "eventDate": str(b.event_date), # Changed from "date"
        "status": b.status
    } for b in bookings]
    
    # Return the list of bookings as JSON
    return JsonResponse(data, safe=False)


# ------------------------------------------
# ENDPOINT: /api/bookings/create/
# ------------------------------------------
@csrf_exempt
def create_booking(request):
    # Verify the token sent from the Android app
    decoded_token = verify_firebase_token(request)
    
    # Reject the request if the token is invalid
    if not decoded_token:
         return JsonResponse({"error": "Unauthorized"}, status=401)
         
    # Check if the Android app sent a POST request
    if request.method == 'POST':
        # Parse the JSON body sent from Kotlin
        # Example: {"eventDate": "2026-06-05", "eventType": "Wedding", "guestCount": 150}
        data = json.loads(request.body)
        
        # Find the user in the database
        user = User.objects.get(username=decoded_token['uid'])
        
        # Create a new booking record in the PostgreSQL database
        booking = Booking.objects.create(
            customer=user, # Link to the user
            # IMPORTANT FIX: Android sends 'eventType', not 'event_type'
            event_type=data.get('eventType', 'General Catering'), 
            # IMPORTANT FIX: Android sends 'eventDate', not 'event_date'
            event_date=data.get('eventDate'), 
            # IMPORTANT FIX: Android sends 'guestCount', not 'guest_count'
            guest_count=data.get('guestCount', 50),
            status="Pending" # Set a default status for new bookings
        )
        
        # Return a success response with the new booking ID
        return JsonResponse({"status": "success", "booking_id": booking.id})