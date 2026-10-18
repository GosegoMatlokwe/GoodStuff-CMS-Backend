# Import the built-in csv module to export data
import csv
# Import Django's admin module
from django.contrib import admin
# Import HttpResponse so we can send a file download to the browser
from django.http import HttpResponse
# Import format_html so we can safely render colored HTML text
from django.utils.html import format_html

# Import your models
from .models import CustomerProfile, Inventory, Menu, Staff, Booking, Payment

# Customize the text at the top of the Django Admin Dashboard
admin.site.site_header = "Good Stuff Catering — Management Portal"
admin.site.site_title = "CMS Portal"
admin.site.index_title = "Executive Data & Operations Dashboard"

# Custom action to export selected items to CSV
@admin.action(description="Export Selected to CSV")
def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="booking_data_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Event Type', 'Date', 'Guest Count', 'Status'])
    for obj in queryset:
        writer.writerow([obj.event_type, obj.event_date, obj.guest_count, obj.status])
    return response

# Inventory Admin
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'quantity', 'stock_status')
    search_fields = ('item_name',)
    list_editable = ('quantity',)

    @admin.display(description="System Status")
    def stock_status(self, obj):
        if obj.quantity < 20:
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', "⚠️ LOW BUFFER STOCK")
        return format_html('<span style="color: green; font-weight: bold;">{}</span>', "✅ Optimal")


# Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'event_type', 'event_date', 'guest_count', 'status_badge')
    list_filter = ('status', 'event_type', 'event_date')
    search_fields = ('customer__username', 'event_type')
    filter_horizontal = ('menu_items', 'assigned_staff') 
    actions = [export_to_csv] 

    # FIXED: These methods are now correctly indented INSIDE the class
    @admin.display(description='Customer')
    def customer_name(self, obj):
        return obj.customer.get_full_name() or obj.customer.username

    @admin.display(description='Status')
    def status_badge(self, obj):
        if obj.status == 'Confirmed':
            return format_html('<span style="background-color: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px;">{}</span>', obj.status)
        elif obj.status == 'Pending':
            return format_html('<span style="background-color: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px;">{}</span>', obj.status)
        else:
            return format_html('<span style="background-color: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px;">{}</span>', obj.status)


# Menu Admin
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'price')
    search_fields = ('item_name',)


# Customer Profile Admin
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_email', 'contact_info', 'popia_consent_timestamp')
    
    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or "No Name Provided"

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.user.email


# Staff Admin
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'availability')
    list_filter = ('role', 'availability')
    search_fields = ('user__username',)

# Standard registrations for simple tables
# Note: We commented these out because they are already registered with @admin.register above!
# admin.site.register(CustomerProfile) 
# admin.site.register(Payment)