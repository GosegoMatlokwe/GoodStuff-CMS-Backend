import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import CustomerProfile, Inventory, Menu, Staff, Booking, Payment


admin.site.site_header = "Good Stuff Catering — Management Portal"
admin.site.site_title = "CMS Portal"
admin.site.index_title = "Executive Data & Operations Dashboard"

@admin.action(description="Export Selected to CSV")
def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="booking_data_export.csv"'
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['Event Type', 'Date', 'Guest Count', 'Status'])
    
    # Write the data rows
    for obj in queryset:
        writer.writerow([obj.event_type, obj.event_date, obj.guest_count, obj.status])
    
    return response


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'quantity', 'stock_status')
    search_fields = ('item_name',)
    list_editable = ('quantity',) 

    # AI/Automation: Automatically flags low buffer stock
    @admin.display(description="System Status")
    def stock_status(self, obj):
        if obj.quantity < 20:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ LOW BUFFER STOCK</span>')
        return format_html('<span style="color: green; font-weight: bold;">✅ Optimal</span>')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'event_type', 'event_date', 'guest_count', 'status_badge')
    list_filter = ('status', 'event_type', 'event_date')
    search_fields = ('customer__username', 'event_type')
    filter_horizontal = ('menu_items', 'assigned_staff') 
    actions = [export_to_csv] # Injects the CSV export tool

    # UI Upgrade: Converts text status into colored CSS pills
    @admin.display(description='Status')
    def status_badge(self, obj):
        if obj.status == 'Confirmed':
            return format_html('<span class="badge badge-success" style="font-size: 14px; padding: 8px;">{}</span>', obj.status)
        elif obj.status == 'Pending':
            return format_html('<span class="badge badge-warning" style="font-size: 14px; padding: 8px;">{}</span>', obj.status)
        else:
            return format_html('<span class="badge badge-danger" style="font-size: 14px; padding: 8px;">{}</span>', obj.status)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'price')
    search_fields = ('item_name',)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'availability')
    list_filter = ('role', 'availability')
    search_fields = ('user__username',)

# Standard registrations for simple tables
admin.site.register(CustomerProfile)
admin.site.register(Payment)