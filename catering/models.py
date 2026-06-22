from django.db import models
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_info = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Inventory(models.Model):
    item_name = models.CharField(max_length=30, unique=True)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.item_name} ({self.quantity} in stock)"

class Menu(models.Model):
    item_name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.item_name} - R{self.price}"

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20) 
    availability = models.CharField(max_length=10) 

    def __str__(self):
        return f"{self.user.first_name} ({self.role})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=25)
    event_date = models.DateField()
    guest_count = models.IntegerField(default=50)
    menu_items = models.ManyToManyField(Menu)
    assigned_staff = models.ManyToManyField(Staff, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.event_type} on {self.event_date}"

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=10, unique=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"