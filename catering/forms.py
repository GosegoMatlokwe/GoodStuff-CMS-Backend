from django import forms
from django.contrib.auth.models import User
from .models import Booking, Menu, Inventory, Staff, CustomerProfile

class DateInput(forms.DateInput):
    input_type = 'date'

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['customer', 'event_type', 'event_date', 'guest_count', 'menu_items', 'assigned_staff', 'status']
        widgets = {
            'event_date': DateInput(),
            'menu_items': forms.CheckboxSelectMultiple(),
            'assigned_staff': forms.CheckboxSelectMultiple(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = User.objects.all()
        self.fields['menu_items'].queryset = Menu.objects.all()
        self.fields['assigned_staff'].queryset = Staff.objects.all()
        # Optionally filter customer to those with CustomerProfile

class InventoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['quantity']

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['item_name', 'price']

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user', 'role', 'availability']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all()