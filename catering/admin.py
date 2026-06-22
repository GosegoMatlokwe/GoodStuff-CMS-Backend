from django.contrib import admin
from .models import CustomerProfile, Inventory, Menu, Staff, Booking, Payment

# Branding the dashboard
admin.site.site_header = "Good Stuff Catering — Management Portal"
admin.site.site_title = "CMS Portal"
admin.site.index_title = "Executive Data & Operations Dashboard"

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'quantity', 'stock_status')
    list_editable = ('quantity',) 

    @admin.display(description="System Status")
    def stock_status(self, obj):
        if obj.quantity < 20:
            return "LOW BUFFER STOCK"
        return "Optimal"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'event_type', 'event_date', 'guest_count', 'status')
    list_filter = ('status', 'event_type', 'event_date')
    list_editable = ('status',)
    filter_horizontal = ('menu_items', 'assigned_staff') 

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'price')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'availability')
    list_filter = ('role', 'availability')

admin.site.register(CustomerProfile)
admin.site.register(Payment)
