# Import the built-in csv module to export data
import csv
# Import Django's admin module
from django.contrib import admin
# Import HttpResponse so we can send a file download to the browser
from django.http import HttpResponse
# Import format_html so we can safely render colored HTML text (like red warning signs) in the admin panel
from django.utils.html import format_html

# --- CRITICAL FIX: UNCOMMENTED THESE ---
# You must import your models here, otherwise Django doesn't know they exist!
from .models import CustomerProfile, Inventory, Menu, Staff, Booking, Payment

# Customize the text at the top of the Django Admin Dashboard
admin.site.site_header = "Good Stuff Catering — Management Portal"
admin.site.site_title = "CMS Portal"
admin.site.index_title = "Executive Data & Operations Dashboard"

# This creates a custom "Action" that appears in a dropdown when you select items in the admin panel.
# It allows the admin to download the selected bookings as an Excel/CSV file.
@admin.action(description="Export Selected to CSV")
def export_to_csv(modeladmin, request, queryset):
    # Create an HTTP response with the CSV content type
    response = HttpResponse(content_type='text/csv')
    # Tell the browser to download this as a file named 'booking_data_export.csv'
    response['Content-Disposition'] = 'attachment; filename="booking_data_export.csv"'
    # Create the CSV writer
    writer = csv.writer(response)
    
    # Write the header row (Column names)
    writer.writerow(['Event Type', 'Date', 'Guest Count', 'Status'])
    
    # Loop through the selected items and write each one as a new row
    for obj in queryset:
        writer.writerow([obj.event_type, obj.event_date, obj.guest_count, obj.status])
    
    # Return the file to the browser
    return response

# --- CRITICAL FIX: UNCOMMENTED @admin.register ---
# This registers the Inventory model and customizes how it looks
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    # Columns to show in the list view
    list_display = ('item_name', 'quantity', 'stock_status')
    # Adds a search bar
    search_fields = ('item_name',)
    # Allows editing the quantity directly from the list view without clicking into the item
    list_editable = ('quantity',)

    # AI/Automation: Automatically flags low buffer stock
    @admin.display(description="System Status")
    def stock_status(self, obj):
        if obj.quantity < 20:
            # Added "{}" and ", obj.quantity" to satisfy Django's format_html
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', "⚠️ LOW BUFFER STOCK")
        return format_html('<span style="color: green; font-weight: bold;">{}</span>', "✅ Optimal")# Registers the Booking model and customizes it
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Columns to show
    list_display = ('id', 'customer', 'event_type', 'event_date', 'guest_count', 'status_badge')
    # Adds a filter sidebar on the right side
    list_filter = ('status', 'event_type', 'event_date')
    # Adds a search bar
    search_fields = ('customer__username', 'event_type')
    # Allows selecting multiple menu items and staff using a nice UI
    filter_horizontal = ('menu_items', 'assigned_staff') 
    # Adds the CSV export tool we created above to the actions dropdown
    actions = [export_to_csv] 

      # UI Upgrade: Converts text status into colored CSS pills
    @admin.display(description='Status')
    def status_badge(self, obj):
        if obj.status == 'Confirmed':
            return format_html('<span style="background-color: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px;">{}</span>', obj.status)
        elif obj.status == 'Pending':
            return format_html('<span style="background-color: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px;">{}</span>', obj.status)
        else:
            return format_html('<span style="background-color: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px;">{}</span>', obj.status)
# Registers the Menu model
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'price')
    search_fields = ('item_name',)

# Registers the Staff model
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'availability')
    list_filter = ('role', 'availability')
    search_fields = ('user__username',)

# Standard registrations for simple tables (These were commented out, so I fixed them)
admin.site.register(CustomerProfile)
admin.site.register(Payment)