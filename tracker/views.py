from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import GlucoseReading
from .forms import GlucoseReadingForm
from django.urls import reverse
from django.core.paginator import Paginator


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
            reading.save()
            messages.success(request, 'Reading added successfully!')
            return redirect('reading_list')
    else:
        form = GlucoseReadingForm()
    
    return render(request, 'tracker/reading_form.html', {'form': form, 'title': 'Add Reading'})

@login_required
def edit_reading(request, pk):
    reading = get_object_or_404(GlucoseReading, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = GlucoseReadingForm(request.POST, instance=reading)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reading updated successfully!')
            return redirect('reading_list')
    else:
        form = GlucoseReadingForm(instance=reading)
    
    return render(request, 'tracker/reading_form.html', {'form': form, 'title': 'Edit Reading'})

@login_required
def delete_reading(request, pk):
    reading = get_object_or_404(GlucoseReading, pk=pk, user=request.user)
    
    if request.method == 'POST':
        reading.delete()
        messages.success(request, 'Reading deleted successfully!')
        return redirect('reading_list')
    
    return render(request, 'tracker/reading_confirm_delete.html', {'reading': reading})
