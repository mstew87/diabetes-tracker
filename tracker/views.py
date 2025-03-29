from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone

import pytz
from datetime import datetime

from .models import GlucoseReading
from .forms import GlucoseReadingForm


@login_required
def reading_list(request):
    readings = GlucoseReading.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(readings, 10)  # Show 10 readings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'readings': page_obj.object_list,
    }
    
    return render(request, 'tracker/reading_list.html', context)

@login_required
def reading_detail(request, pk):
    reading = get_object_or_404(GlucoseReading, pk=pk, user=request.user)
    return render(request, 'tracker/reading_detail.html', {'reading': reading})

@login_required
def add_reading(request):
    if request.method == 'POST':
        form = GlucoseReadingForm(request.POST)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.user = request.user
            
            # Create timestamp from date and time fields
            reading_date = form.cleaned_data['reading_date']
            reading_time = form.cleaned_data['time_of_reading']
            
            # Combine date and time into a datetime object (naive)
            combined_datetime = datetime.combine(reading_date, reading_time)
            
            # Get user's current timezone
            current_tz = timezone.get_current_timezone()
            
            # Localize the datetime to user's timezone
            localized_datetime = current_tz.localize(combined_datetime)
            
            # Set the timestamp
            reading.timestamp = localized_datetime
            
            reading.save()
            messages.success(request, 'Reading added successfully!')
            return redirect('reading_list')
    else:
        # Get current time in user's timezone
        current_local_time = timezone.localtime(timezone.now())
        
        # Initialize form with user's local time
        form = GlucoseReadingForm(initial={
            'reading_date': current_local_time.date(),
            'time_of_reading': current_local_time.strftime('%H:%M'),
        })
    
    return render(request, 'tracker/reading_form.html', {'form': form, 'title': 'Add Reading'})

@login_required
def edit_reading(request, pk):
    reading = get_object_or_404(GlucoseReading, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = GlucoseReadingForm(request.POST, instance=reading)
        if form.is_valid():
            updated_reading = form.save(commit=False)
            
            # Create timestamp from date and time fields
            reading_date = form.cleaned_data['reading_date']
            reading_time = form.cleaned_data['time_of_reading']
            
            # Combine date and time into a datetime object (naive)
            combined_datetime = datetime.combine(reading_date, reading_time)
            
            # Get user's current timezone
            current_tz = timezone.get_current_timezone()
            
            # Localize the datetime to user's timezone
            localized_datetime = current_tz.localize(combined_datetime)
            
            # Set the timestamp
            updated_reading.timestamp = localized_datetime
            
            updated_reading.save()
            messages.success(request, 'Reading updated successfully!')
            return redirect('reading_list')
    else:
        # Convert stored UTC time to user's local timezone
        local_timestamp = timezone.localtime(reading.timestamp)
        
        # Populate date and time fields from existing timestamp in user's timezone
        initial_data = {
            'reading_date': local_timestamp.date(),
            'time_of_reading': local_timestamp.time(),
        }
        form = GlucoseReadingForm(instance=reading, initial=initial_data)
    
    return render(request, 'tracker/reading_form.html', {'form': form, 'title': 'Edit Reading'})

@login_required
def delete_reading(request, pk):
    reading = get_object_or_404(GlucoseReading, pk=pk, user=request.user)
    
    if request.method == 'POST':
        reading.delete()
        messages.success(request, 'Reading deleted successfully!')
        return redirect('reading_list')
    
    return render(request, 'tracker/reading_confirm_delete.html', {'reading': reading})
