# Import Django's built-in form tools
from django import forms
# Import the built-in User model (for dropdowns)
from django.contrib.auth.models import User
# Import your database models so the forms know what to save to
from .models import Booking, Menu, Inventory, Staff, CustomerProfile

# Create a custom DateInput widget. This tells the browser to show a 
# native calendar popup when the user clicks on a date field.
class DateInput(forms.DateInput):
    input_type = 'date'

# This form handles creating and updating a Booking on the website
class BookingForm(forms.ModelForm):
    # Meta class tells Django which model to use and which fields to show
    class Meta:
        model = Booking
        # These are the fields that will appear on the web form
        fields = ['customer', 'event_type', 'event_date', 'guest_count', 'menu_items', 'assigned_staff', 'status']
        # Widgets customize how the HTML inputs look
        widgets = {
            'event_date': DateInput(), # Uses the custom calendar widget above
            'menu_items': forms.CheckboxSelectMultiple(), # Shows a list of checkboxes instead of a boring list
            'assigned_staff': forms.CheckboxSelectMultiple(),
        }
    
    # The __init__ method runs when the form is first created.
    # We use it to customize what data is loaded into the dropdown menus.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load ALL users into the 'customer' dropdown
        self.fields['customer'].queryset = User.objects.all()
        # Load ALL menu items into the 'menu_items' checkboxes
        self.fields['menu_items'].queryset = Menu.objects.all()
        # Load ALL staff into the 'assigned_staff' checkboxes
        self.fields['assigned_staff'].queryset = Staff.objects.all()
        # Optionally filter customer to those with CustomerProfile (You left this as a comment)

# A simple form just to update stock quantity
class InventoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['quantity'] # Only shows the quantity field

# A simple form to add/edit a Menu Item
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['item_name', 'price']

# A form to manage Staff members
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user', 'role', 'availability']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load all users into the user dropdown
        self.fields['user'].queryset = User.objects.all()