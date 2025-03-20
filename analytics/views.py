from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tracker.models import GlucoseReading
from django.db.models import Avg, Max, Min, Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from datetime import datetime, timedelta
import json
from .ml import predict_next_glucose

@login_required
def dashboard(request):
    # Get user's readings for the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    readings = GlucoseReading.objects.filter(
        user=request.user, 
        timestamp__gte=thirty_days_ago
    ).order_by('timestamp')
    
    # Calculate statistics
    stats = {
        'total_readings': readings.count(),
        'avg_glucose': readings.aggregate(Avg('glucose_level'))['glucose_level__avg'],
        'max_glucose': readings.aggregate(Max('glucose_level'))['glucose_level__max'],
        'min_glucose': readings.aggregate(Min('glucose_level'))['glucose_level__min'],
    }
    
    # Format for chart.js
    dates = [reading.timestamp.strftime('%Y-%m-%d %H:%M') for reading in readings]
    glucose_values = [reading.glucose_level for reading in readings]
    
    # Group by reading_time
    reading_time_data = {}
    for choice in GlucoseReading.READING_TIME_CHOICES:
        code, label = choice
        readings_by_time = readings.filter(reading_time=code)
        if readings_by_time.exists():
            avg = readings_by_time.aggregate(Avg('glucose_level'))['glucose_level__avg']
            reading_time_data[label] = avg
    
    context = {
        'stats': stats,
        'dates_json': json.dumps(dates),
        'glucose_values_json': json.dumps(glucose_values),
        'reading_time_data': reading_time_data,
        'reading_time_labels_json': json.dumps(list(reading_time_data.keys())),
        'reading_time_values_json': json.dumps(list(reading_time_data.values())),
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def trends(request):
    # Get filter period from query params (default to 30 days)
    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Get readings within the period
    readings = GlucoseReading.objects.filter(
        user=request.user,
        timestamp__gte=start_date
    )
    
    # Daily averages
    daily_avg = (
        readings
        .annotate(day=TruncDay('timestamp'))
        .values('day')
        .annotate(avg_glucose=Avg('glucose_level'))
        .order_by('day')
    )
    
    # Weekly averages
    weekly_avg = (
        readings
        .annotate(week=TruncWeek('timestamp'))
        .values('week')
        .annotate(avg_glucose=Avg('glucose_level'))
        .order_by('week')
    )
    
    # Time of day patterns
    time_patterns = {}
    for choice in GlucoseReading.READING_TIME_CHOICES:
        code, label = choice
        time_readings = readings.filter(reading_time=code)
        if time_readings.exists():
            time_patterns[label] = time_readings.aggregate(Avg('glucose_level'))['glucose_level__avg']
    
    # Prepare chart data
    daily_dates = [item['day'].strftime('%Y-%m-%d') for item in daily_avg]
    daily_values = [item['avg_glucose'] for item in daily_avg]
    
    weekly_dates = [item['week'].strftime('%Y-%m-%d') for item in weekly_avg]
    weekly_values = [item['avg_glucose'] for item in weekly_avg]
    
    context = {
        'days': days,
        'daily_dates_json': json.dumps(daily_dates),
        'daily_values_json': json.dumps(daily_values),
        'weekly_dates_json': json.dumps(weekly_dates),
        'weekly_values_json': json.dumps(weekly_values),
        'time_pattern_labels_json': json.dumps(list(time_patterns.keys())),
        'time_pattern_values_json': json.dumps(list(time_patterns.values())),
    }
    
    return render(request, 'analytics/trends.html', context)

@login_required
def reports(request):
    # Stats for different time periods
    today = datetime.now()
    
    periods = {
        'week': today - timedelta(days=7),
        'month': today - timedelta(days=30),
        'quarter': today - timedelta(days=90),
        'year': today - timedelta(days=365),
    }
    
    stats = {}
    
    for period_name, start_date in periods.items():
        period_readings = GlucoseReading.objects.filter(
            user=request.user,
            timestamp__gte=start_date
        )
        
        if period_readings.exists():
            stats[period_name] = {
                'count': period_readings.count(),
                'avg': period_readings.aggregate(Avg('glucose_level'))['glucose_level__avg'],
                'min': period_readings.aggregate(Min('glucose_level'))['glucose_level__min'],
                'max': period_readings.aggregate(Max('glucose_level'))['glucose_level__max'],
            }
    
    context = {
        'stats': stats,
    }
    
    return render(request, 'analytics/reports.html', context)

@login_required
def prediction(request):
    # Get prediction hours from form or default to 2
    hours_ahead = 2
    if request.method == 'POST':
        try:
            hours_ahead = int(request.POST.get('hours_ahead', 2))
            if hours_ahead < 1:
                hours_ahead = 1
            elif hours_ahead > 24:
                hours_ahead = 24
        except (ValueError, TypeError):
            hours_ahead = 2
    
    # Get prediction
    prediction_result = predict_next_glucose(request.user, hours_ahead)
    
    # Get recent readings for context
    recent_readings = GlucoseReading.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:10]
    
    context = {
        'prediction': prediction_result,
        'hours_ahead': hours_ahead,
        'recent_readings': recent_readings,
    }
    
    return render(request, 'analytics/prediction.html', context)
