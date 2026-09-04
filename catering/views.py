from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Booking, Menu, Inventory, Staff, Payment, CustomerProfile
from .forms import BookingForm, InventoryUpdateForm, MenuForm, StaffForm

# ---------- Authentication ----------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'catering/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def public_home(request):
    """Render the public marketing homepage."""
    return render(request, 'catering/index.html')

def public_about(request):
    """Render the public about page."""
    return render(request, 'catering/about.html')

# ---------- Dashboard ----------
@login_required
def dashboard(request):
    # Basic stats
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='Pending').count()
    confirmed_bookings = Booking.objects.filter(status='Confirmed').count()
    low_stock_items = Inventory.objects.filter(quantity__lt=20).count()
    total_staff = Staff.objects.count()
    upcoming_events = Booking.objects.filter(event_date__gte=timezone.now().date()).order_by('event_date')[:5]

    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'low_stock_items': low_stock_items,
        'total_staff': total_staff,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'catering/dashboard.html', context)

# ---------- Bookings ----------
@login_required
def booking_list(request):
    bookings = Booking.objects.all().order_by('-event_date')
    return render(request, 'catering/booking_list.html', {'bookings': bookings})

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
    return render(request, 'catering/booking_form.html', {'form': form, 'title': 'Create Booking'})

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
    return render(request, 'catering/booking_form.html', {'form': form, 'title': 'Edit Booking'})

@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted.')
        return redirect('booking_list')
    return render(request, 'catering/confirm_delete.html', {'object': booking, 'type': 'booking'})

# ---------- Inventory ----------
@login_required
def inventory_list(request):
    items = Inventory.objects.all().order_by('item_name')
    return render(request, 'catering/inventory_list.html', {'items': items})

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
    return render(request, 'catering/inventory_update.html', {'form': form, 'item': item})

# ---------- Menu ----------
@login_required
def menu_list(request):
    items = Menu.objects.all().order_by('item_name')
    return render(request, 'catering/menu_list.html', {'items': items})

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
    return render(request, 'catering/menu_form.html', {'form': form, 'title': 'Add Menu Item'})

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
    return render(request, 'catering/menu_form.html', {'form': form, 'title': 'Edit Menu Item'})

@login_required
def menu_delete(request, pk):
    item = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Menu item deleted.')
        return redirect('menu_list')
    return render(request, 'catering/confirm_delete.html', {'object': item, 'type': 'menu item'})

# ---------- Staff ----------
@login_required
def staff_list(request):
    staff_members = Staff.objects.all().select_related('user').order_by('user__first_name')
    return render(request, 'catering/staff_list.html', {'staff_members': staff_members})

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
    return render(request, 'catering/staff_form.html', {'form': form, 'title': 'Add Staff'})

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
    return render(request, 'catering/staff_form.html', {'form': form, 'title': 'Edit Staff'})

@login_required
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff removed.')
        return redirect('staff_list')
    return render(request, 'catering/confirm_delete.html', {'object': staff, 'type': 'staff member'})

# ---------- Reports ----------
@login_required
def reports(request):
    # Financial summary
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_paid_bookings = Payment.objects.count()
    
    # Booking trends by event type
    booking_by_type = Booking.objects.values('event_type').annotate(count=Count('id')).order_by('-count')
    
    # Inventory low stock
    low_stock = Inventory.objects.filter(quantity__lt=20)
    
    # Staff workload: bookings per staff (count assigned)
    staff_workload = Staff.objects.annotate(num_bookings=Count('booking')).order_by('-num_bookings')
    
    context = {
        'total_revenue': total_revenue,
        'total_paid_bookings': total_paid_bookings,
        'booking_by_type': booking_by_type,
        'low_stock': low_stock,
        'staff_workload': staff_workload,
    }
    return render(request, 'catering/reports.html', context)