# Import Django's built-in models module. 
# Every class we create here will become a table in your database.
from django.db import models

# Import Django's built-in User model. 
# This handles standard things like usernames, passwords, and emails.
from django.contrib.auth.models import User

# ==========================================
# CUSTOMER PROFILE
# ==========================================
# This links to the built-in User model. It stores extra info we need for the app.
class CustomerProfile(models.Model):
    # Link this profile to exactly one User. If the User is deleted, delete this profile too.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Store the user's phone number (sent from the Android registration screen)
    contact_info = models.CharField(max_length=100, blank=True, null=True)
    
    # CRITICAL FOR POPIA: Store exactly when the user clicked "I consent"
    # null=True allows old users to exist without this timestamp, blank=True allows the admin form to be empty
    popia_consent_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        # This makes the admin panel show the username instead of "CustomerProfile object (1)"
        return self.user.username


# ==========================================
# MENU
# ==========================================
# Stores all the food items the catering company offers.
class Menu(models.Model):
    item_name = models.CharField(max_length=100)
    # Max digits=10, decimal_places=2 means it can store up to 99,999,999.99 (perfect for Rands)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.item_name


# ==========================================
# INVENTORY
# ==========================================
# Stores the raw ingredients or equipment the company has in stock.
class Inventory(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.item_name


# ==========================================
# STAFF
# ==========================================
# Stores staff members who work at the events.
class Staff(models.Model):
    # Link to a User account, but allow staff to exist without a login account for now
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=50) # e.g., "Chef", "Waiter", "Driver"
    availability = models.CharField(max_length=50) # e.g., "Available", "On Leave"

    def __str__(self):
        # If they have a user account, show their name; otherwise just show their role
        if self.user:
            return f"{self.user.first_name} {self.user.last_name} ({self.role})"
        return f"Staff ({self.role})"


# ==========================================
# BOOKING
# ==========================================
# This is the core of your app. It stores every event a customer books.
class Booking(models.Model):
    # Link to the User who made the booking. If the user is deleted (POPIA), delete their bookings.
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    
    event_type = models.CharField(max_length=50) # e.g., "Wedding", "Corporate"
    event_date = models.DateField() # Stores just the date (YYYY-MM-DD)
    guest_count = models.IntegerField(default=10)
    
    # Many-to-Many relationship. A booking can have many menu items, and a menu item can be in many bookings.
    menu_items = models.ManyToManyField(Menu, blank=True)
    
    # Many-to-Many relationship for staff assigned to the event.
    assigned_staff = models.ManyToManyField(Staff, blank=True)
    
    # Track the status of the order (Draft, Pending, Confirmed, Out for Delivery, Completed)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.event_type} - {self.customer.username} ({self.event_date})"


# ==========================================
# PAYMENT
# ==========================================
# Tracks the financial side of a booking (Deposits and Final payments).
class Payment(models.Model):
    # Link to the specific booking. If a booking is deleted, delete its payment record.
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    
    # A unique invoice number (e.g., "INV-2026-001")
    invoice_number = models.CharField(max_length=50, unique=True)
    
    # The amount paid
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Automatically record the exact moment the payment was created
    payment_date = models.DateTimeField(auto_now_add=True)
    
    # Track if the payment was successful
    is_successful = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.invoice_number} - R{self.amount}"